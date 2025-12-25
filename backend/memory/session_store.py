import uuid
import random
from data.diseases import DISEASES
from graph.patient_graph import build_patient_graph

sessions = {}


def create_session():
    session_id = str(uuid.uuid4())


    disease_name = random.choice(list(DISEASES.keys()))

 
    graph = build_patient_graph()

    sessions[session_id] = {
        "graph": graph,
        "patient_state": {
            "disease": disease_name,

          
            "questions_asked": 0,
            "symptoms_revealed": [],
            "ready_for_diagnosis": False,
            "last_answers": {},

          
            "stage": 0,
        }
    }

    return session_id


def get_session(session_id):
    return sessions.get(session_id)
