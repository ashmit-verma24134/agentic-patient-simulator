from flask import Blueprint, jsonify
from memory.session_store import create_session

session_bp =Blueprint("session", __name__, url_prefix="/api")  #blueprints for session

@session_bp.route("/create_session", methods=["POST"])  #when frontend sends posts requestes this runs until then its registered as blueprints
def create():
    session_id = create_session()
    return jsonify({"session_id": session_id})
