from flask import Blueprint, jsonify
from backend.memory.session_store import create_session

session_bp = Blueprint("session", __name__)

@session_bp.route("/create_session", methods=["POST"])
def create():
    session_id = create_session()
    return jsonify({"session_id": session_id})
