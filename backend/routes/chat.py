from flask import Blueprint, request, jsonify
from memory.session_store import get_session

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    session_id = data.get("session_id")
    message = data.get("message", "")  # ✅ FIX

    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Invalid session"}), 400

    # ---------- NORMAL QUESTION FLOW ----------
    graph = session["graph"]

    state = {
        **session["patient_state"],
        "last_user_message": message  # ✅ now defined
    }

    new_state = graph.invoke(state)
    session["patient_state"].update(new_state)

    return jsonify({
        "reply": new_state.get("reply"),
        "questions_asked": new_state.get("questions_asked"),
        "ready_for_diagnosis": new_state.get("ready_for_diagnosis"),
    })
