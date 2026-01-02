# from agents.question_classifier import classify_question

# def classify_node(state):
#     state["question_type"] = classify_question(state["last_user_message"])
#     return state

# def respond_node(state):
#     qtype = state["question_type"]
#     disease = state["disease"]
#     symptom_map = {
#         "flu": {"fever": "fever","respiratory": "cough"},
#         "migraine": {
#             "pain": "headache",
#             "light": "light_sensitivity"},
#         "food_poisoning": {"pain": "stomach pain","nausea": "nausea"}
#     }

#     reply = "I’m not sure that’s related."

#     for symptom in state["required_symptoms"] + state["optional_symptoms"]:
#         if symptom not in state["symptoms_revealed"]:
#             state["symptoms_revealed"].append(symptom)
#             reply = symptom_sentence(symptom)
#             break
#     state["questions_asked"] += 1
#     state["last_reply"] = reply
#     return state
# def diagnosis_gate_node(state):
#     if state["questions_asked"] >= 3:
#         state["ready_for_diagnosis"] = True
#     return state


#Another approach  where patient behavior was decomposed into multiple LangGraph nodes but then we made patient agent for this