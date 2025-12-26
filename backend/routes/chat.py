from flask import Blueprint, request, jsonify
from backend.memory.session_store import get_session

chat_bp = Blueprint("chat", __name__, url_prefix="/api")


def compute_disease_confidence(symptoms):
    DISEASES = {
        "Flu": {
            "required": ["fever", "cough"],
            "optional": ["fatigue", "body pain", "headache"]
        },
        "Migraine": {
            "required": ["headache"],
            "optional": [
                "light_sensitivity",
                "nausea",
                "movement_worsens_headache",
                "unilateral_headache",
                "relieved_by_darkness"
            ]
        },
        "Food Poisoning": {
            "required": ["nausea", "vomiting"],
            "optional": ["diarrhea", "stomach pain"]
        }
    }

    scores = {}

    for disease, info in DISEASES.items():
        req_matches = sum(1 for s in info["required"] if s in symptoms)
        opt_matches = sum(1 for s in info["optional"] if s in symptoms)

        score = 0
        score += req_matches * 2
        score += opt_matches * 1
        if disease == "Migraine" and "light_sensitivity" in symptoms:
            score += 2
        if disease == "Food Poisoning":
            gi_cluster = any(
                s in symptoms for s in ["vomiting", "diarrhea", "stomach pain"]
            )
            if not gi_cluster:
                score *= 0.4

        scores[disease] = score

    scores = {d: s for d, s in scores.items() if s > 0}

    if not scores:
        return {d: 0 for d in DISEASES}

    total = sum(scores.values())
    return {
        d: round((scores.get(d, 0) / total) * 100)
        for d in DISEASES
    }


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    session_id = data.get("session_id")
    message = data.get("message", "").strip()
    lower_msg = message.lower()

    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session"}), 400

    state = session["patient_state"]

    if lower_msg.startswith("diagnosis"):
        if not state.get("ready_for_diagnosis", False):
            return jsonify({"error": "Diagnosis is not allowed yet."})

        from backend.agents.evaluator_agent import EvaluatorAgent

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
            )
        })

    if lower_msg.startswith("treatment"):
        if not state.get("diagnosis_confirmed", False):
            return jsonify({
                "error": "Treatment cannot be prescribed before diagnosis."
            })

        from backend.agents.treatment_agent import TreatmentAgent

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
            )
        })

    graph = session["graph"]

    graph_input = {
        **state,
        "last_user_message": message
    }

    new_state = graph.invoke(graph_input)
    state.update(new_state)

    return jsonify({
        "reply": new_state.get("reply"),
        "questions_asked": new_state.get("questions_asked"),
        "ready_for_diagnosis": new_state.get("ready_for_diagnosis"),
        "next_action": new_state.get("next_action"),
        "symptoms_revealed": list(state.get("symptoms_revealed", [])),
        "disease_confidence": compute_disease_confidence(
            state.get("symptoms_revealed", [])
        )
    })
