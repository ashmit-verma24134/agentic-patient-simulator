import uuid
import random

from backend.data.diseases import DISEASES
from backend.graph.patient_graph import build_patient_graph

sessions = {}


def create_session():
    session_id = str(uuid.uuid4())
    disease_name = random.choice(list(DISEASES.keys()))

    graph = build_patient_graph()

    sessions[session_id] = {
        "graph": graph,
        "patient_state": {
            "disease": disease_name,
            "symptoms_revealed": [],
            "questions_asked": 0,
            "ready_for_diagnosis": False,
            "diagnosis_confirmed": False,
            "treatment_accepted": False,
            "next_action": None,
        }
    }

    return session_id


def get_session(session_id):
    return sessions.get(session_id)
