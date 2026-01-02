from flask import Blueprint, request, jsonify
from memory.session_store import get_session #to get data of a particular session id
from agents.treatment_agent import TreatmentAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.llm_client import llm_speak

chat_bp = Blueprint("chat", __name__, url_prefix="/api")    #blueprints for chat

# confidence engine
# Looks at symptoms and guesses which disease is likely
# its for the confidence bar in UI
def compute_disease_confidence(symptoms):
    DISEASES = {
        "Flu":{
            "required": ["fever", "cough"],
            "optional": ["fatigue", "body pain", "headache"],
        },
        "Migraine":{
            "required": ["headache"],
            "optional": [
                "light_sensitivity",
                "nausea",
                "movement_worsens_headache",
                "unilateral_headache",
                "relieved_by_darkness",
            ],
        },
        "Food Poisoning":{
            "required": ["nausea", "vomiting"],
            "optional": ["diarrhea", "stomach pain"],
        },
    }
    scores = {}
    for disease, info in DISEASES.items():
        req =sum(1 for s in info["required"] if s in symptoms)  #checks required symptoms of input
        opt =sum(1 for s in info["optional"] if s in symptoms)  #checks opt symptoms of input
        scores[disease]=req*3 + opt

    total = sum(scores.values()) or 1
    return {d: round((scores.get(d, 0) / total) * 100) for d in DISEASES}

    #It looks at the symptoms the patient has revealed and guesses which disease is most likely (in percentages).


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data =request.json or {}
    session_id =data.get("session_id")       #gets which patient
    message =(data.get("message") or "").strip()  #gets the message of doctor

    if not message:
        return jsonify({"reply": "Please ask a medical question."})

    session =get_session(session_id)   #finding correct patient
          
    if not session:
        return jsonify({"error": "Invalid session"}), 400

    #loading patient memory and state of that particular active session
    state= session["patient_state"]
    graph= session["graph"]
    msg= message.lower().strip()

    # DIAGNOSIS HANDLER
    if msg.startswith("diagnosis"):
        evaluator= EvaluatorAgent(state)  #evaluatoragent will check if diagnosis is correct
        result= evaluator.evaluate(message) #will check if patient is ready

        return jsonify({
            "verdict": result["verdict"],
            "reason": result.get("reason", ""),  #correct diagnosis has no reason
            "reply": (
                "Diagnosis accepted. Please prescribe treatment."
                if result["verdict"] == "correct"
                else result.get("reason", "Diagnosis not accepted.")
            )
        })

    # TREATMENT HANDLER

    if msg.startswith("treatment"):
        agent = TreatmentAgent(state)
        result = agent.evaluate(message)

        #Language generation happens HERE (credits groq AI) (LLM COMES IN ACTION)
        reply= llm_speak(
            system_prompt=(
                "ROLE: Patient\n"
                "TASK: Respond naturally to a doctor's treatment.\n\n"
                "RULES:\n"
                "- First person only\n"
                "- One sentence only\n"  #I kept the prompt rigid so that it doesn't hallucinates
                "- Neutral human tone\n"
                "- Do NOT add symptoms\n"
                "- Do NOT give advice\n"
                "- Do NOT diagnose\n"
                "- Do NOT express strong emotion\n"
            ),
            user_prompt=result["semantic_reply"],
        )

        return jsonify({
            "verdict": result["verdict"],   #The session continues because frontend keeps sending messages until patient accepts treatment.
            "treatment_verdict": result["verdict"],
            "reply": reply
        })

    # NORMAL LANGGRAPH FLOW  (for normal questions)

    config= {"configurable": {"thread_id":session_id}}  #thread id mapping with session_id

    new_state= graph.invoke(                 #Patient graph call
        {**state, "last_user_message": message},         #IMP:It takes the current full state and add the latest doctor message and gives it to langraph through graph invoke and decides the next state
        config=config
    )

    state.update(new_state)

    return jsonify({            #Sending data back to frontend
        "reply":state.get("reply"),
        "questions_asked":state.get("questions_asked", 0),
        "ready_for_diagnosis":state.get("ready_for_diagnosis"),
        "next_action":state.get("next_action"),
        "symptoms_revealed":list(state.get("symptoms_revealed", [])),
        "disease_confidence":compute_disease_confidence(state.get("symptoms_revealed",[])),})
