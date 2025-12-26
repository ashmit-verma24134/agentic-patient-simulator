class SupervisorAgent:
    def decide_next_action(self, patient_state: dict) -> str:
        questions = patient_state.get("questions_asked", 0)
        if questions >= 10:
            return "allow_diagnosis"
        if patient_state.get("ready_for_diagnosis"):
            return "allow_diagnosis"
        return "continue_questioning"
