import uuid   #unique ids
import random
from data.diseases import DISEASES

#importing graph for each unique patient which acts differently for each patient
from graph.patient_graph import build_patient_graph    

_sessions= {}  #to store diff sessions

def create_session():
    session_id  = str(uuid.uuid4())    #creates uniqe session id
    disease_name = random.choice(list(DISEASES.keys()))

    graph = build_patient_graph()    #langgraph state machine

    _sessions[session_id] = {  #storing each session's data also the starting state of a patient
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
    return _sessions.get(session_id)
