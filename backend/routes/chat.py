from flask import Blueprint, request, jsonify
from memory.session_store import get_session

chat_bp = Blueprint("chat", __name__)


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

    # =====================================================
    # 🩺 DIAGNOSIS ATTEMPT
    # =====================================================
    if lower_msg.startswith("diagnosis"):
        if not state.get("ready_for_diagnosis", False):
            return jsonify({
                "error": "Diagnosis is not allowed yet."
            })

        from agents.evaluator_agent import EvaluatorAgent

        evaluator = EvaluatorAgent(state)
        result = evaluator.evaluate(lower_msg)

        if result["verdict"] == "correct":
            state["diagnosis_confirmed"] = True
            state["next_action"] = "accept_treatment"

        return jsonify({
            "evaluation": result,
            "next_action": state.get("next_action")
        })

    # =====================================================
    # 💊 TREATMENT HANDLING (Agent-based)
    # =====================================================
    if lower_msg.startswith("treatment"):
        if not state.get("diagnosis_confirmed", False):
            return jsonify({
                "error": "Treatment cannot be prescribed before diagnosis."
            })

        from agents.treatment_agent import TreatmentAgent

        treatment_agent = TreatmentAgent(state)
        result = treatment_agent.evaluate(lower_msg)

        if result["verdict"] == "accepted":
            state["treatment_accepted"] = True
            state["next_action"] = "session_complete"

        return jsonify({
            "reply": result["reply"],
            "treatment_verdict": result["verdict"],
            "next_action": state.get("next_action")
        })

    # =====================================================
    # 🧠 NORMAL QUESTION FLOW (LangGraph)
    # =====================================================
    graph = session["graph"]

    graph_input = {
        **state,
        "last_user_message": message
    }

    new_state = graph.invoke(graph_input)

    # persist updated state
    state.update(new_state)

    return jsonify({
        "reply": new_state.get("reply"),
        "questions_asked": new_state.get("questions_asked"),
        "ready_for_diagnosis": new_state.get("ready_for_diagnosis"),
        "next_action": new_state.get("next_action")
    })
