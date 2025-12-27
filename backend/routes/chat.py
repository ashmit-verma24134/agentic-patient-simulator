from flask import Blueprint, request, jsonify
from memory.session_store import get_session   # ✅ FIXED IMPORT

chat_bp = Blueprint("chat", __name__, url_prefix="/api")


def compute_disease_confidence(symptoms):
    DISEASES = {
        "Flu": {
            "required": ["fever", "cough"],
            "optional": ["fatigue", "body pain", "headache"],
        },
        "Migraine": {
            "required": ["headache"],
            "optional": [
                "light_sensitivity",
                "nausea",
                "movement_worsens_headache",
                "unilateral_headache",
                "relieved_by_darkness",
            ],
        },
        "Food Poisoning": {
            "required": ["nausea", "vomiting"],
            "optional": ["diarrhea", "stomach pain"],
        },
    }

    scores = {}

    for disease, info in DISEASES.items():
        req_matches = sum(1 for s in info["required"] if s in symptoms)
        opt_matches = sum(1 for s in info["optional"] if s in symptoms)

        score = req_matches * 2 + opt_matches

        if disease == "Migraine" and "light_sensitivity" in symptoms:
            score += 2

        if disease == "Food Poisoning":
            if not any(s in symptoms for s in ["vomiting", "diarrhea", "stomach pain"]):
                score *= 0.4

        scores[disease] = score

    scores = {d: s for d, s in scores.items() if s > 0}

    if not scores:
        return {d: 0 for d in DISEASES}

    total = sum(scores.values())
    return {d: round((scores.get(d, 0) / total) * 100) for d in DISEASES}


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}   # ✅ FIX 1
    session_id = data.get("session_id")
    message = data.get("message", "").strip()

    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session"}), 400

    state = session["patient_state"]
    lower_msg = message.lower()

    if lower_msg.startswith("diagnosis"):
        if not state.get("ready_for_diagnosis"):
            return jsonify({"error": "Diagnosis is not allowed yet."})

        from agents.evaluator_agent import EvaluatorAgent   # ✅ FIXED IMPORT

        evaluator = EvaluatorAgent(state)
        result = evaluator.evaluate(lower_msg)

        if result["verdict"] == "correct":
            state["diagnosis_confirmed"] = True
            state["next_action"] = "accept_treatment"

        return jsonify({
            "evaluation": result,
            "next_action": state.get("next_action"),
            "symptoms_revealed": list(state.get("symptoms_revealed", [])),
            "disease_confidence": compute_disease_confidence(
                state.get("symptoms_revealed", [])
            ),
        })

    if lower_msg.startswith("treatment"):
        if not state.get("diagnosis_confirmed"):
            return jsonify({"error": "Treatment cannot be prescribed before diagnosis."})

        from agents.treatment_agent import TreatmentAgent   # ✅ FIXED IMPORT

        treatment_agent = TreatmentAgent(state)
        result = treatment_agent.evaluate(lower_msg)

        if result["verdict"] == "accepted":
            state["treatment_accepted"] = True
            state["next_action"] = "session_complete"

        return jsonify({
            "reply": result["reply"],
            "treatment_verdict": result["verdict"],
            "next_action": state.get("next_action"),
            "symptoms_revealed": list(state.get("symptoms_revealed", [])),
            "disease_confidence": compute_disease_confidence(
                state.get("symptoms_revealed", [])
            ),
        })

    graph = session["graph"]

    new_state = graph.invoke({**state, "last_user_message": message})
    state.update(new_state)

    return jsonify({
        "reply": new_state.get("reply"),
        "questions_asked": new_state.get("questions_asked"),
        "ready_for_diagnosis": new_state.get("ready_for_diagnosis"),
        "next_action": new_state.get("next_action"),
        "symptoms_revealed": list(state.get("symptoms_revealed", [])),
        "disease_confidence": compute_disease_confidence(
            state.get("symptoms_revealed", [])
        ),
    })
