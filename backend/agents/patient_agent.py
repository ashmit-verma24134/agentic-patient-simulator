from utils.question_classifier import classify_question, QuestionType


class PatientAgent:
    def __init__(self, state: dict):
        self.state = state

    def respond(self, user_message: str) -> str:
        # classify intent
        qtype = classify_question(user_message)

        # update state
        self.state["questions_asked"] = self.state.get("questions_asked", 0) + 1

        # generic opening
        if qtype == QuestionType.GENERAL:
            return "I'm not feeling very well."

        # duration logic (gate-aware)
        if qtype == QuestionType.DURATION:
            if not self.state.get("ready_for_diagnosis", False):
                return "It's hard to say right now."
            return "The symptoms have been going on for a few days."

        # placeholder for now
        return "I'm not sure."
