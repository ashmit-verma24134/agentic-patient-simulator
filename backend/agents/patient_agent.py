from agents.question_classifier import classify_question, QuestionType
from data.diseases import DISEASES


class PatientAgent:
    def __init__(self, state: dict):
        self.state = state

        disease = state["disease"]
        disease_info = DISEASES[disease]

        self.required_symptoms = set(disease_info.get("required_symptoms", []))
        self.optional_symptoms = set(disease_info.get("optional_symptoms", []))
        self.all_symptoms = self.required_symptoms | self.optional_symptoms
        self.min_questions = disease_info.get("min_questions", 2)
        self.state.setdefault("symptoms_revealed", [])
        self.state.setdefault("questions_asked", 0)
        self.state.setdefault("ready_for_diagnosis", False)
        self.state.setdefault("next_action", None)
    def respond(self, user_message: str) -> str:
        self.state["questions_asked"] += 1
        qtype = classify_question(user_message)
        msg = user_message.lower()
        if any(w in msg for w in ["tired", "fatigue", "exhausted"]):
            reply = self._symptom("fatigue")
        elif qtype == QuestionType.FEVER:
            reply = self._symptom("fever")
        elif qtype == QuestionType.RESPIRATORY:
            reply = self._symptom("cough")
        elif qtype == QuestionType.SENSITIVITY:
            reply = self._symptom("light_sensitivity")
        elif qtype == QuestionType.GI:
            reply = self._gi_reply(msg)
        elif qtype == QuestionType.PAIN:
            reply = self._pain_reply(msg)
        elif qtype == QuestionType.DURATION:
            reply = (
                "It’s hard to say right now."
                if not self.state["ready_for_diagnosis"]
                else "The symptoms have been going on for a few days."
            )
        else:
            reply = "I’m just not feeling very well.Please help me !! "

        self._check_unlock()
        return reply
#helpers
    def _symptom(self, symptom: str) -> str:
        if symptom not in self.all_symptoms:
            return "No, I don’t think that’s been an issue."

        self._record(symptom)

        responses = {
            "headache": "Yes, I’ve been having headaches.",
            "nausea": "Yes, I’ve been feeling nauseous.",
            "vomiting": "Yes, I’ve been vomiting.",
            "diarrhea": "Yes, I’ve been having diarrhea.",
            "fever": "Yes, I’ve had a fever.",
            "cough": "Yes, I’ve been coughing.",
            "fatigue": "Yes, I’ve been feeling very tired.",
            "light_sensitivity": "Yes, bright light makes it worse.",
            "unilateral_headache": "Yes, it’s mostly on one side of my head.",
            "movement_worsens_headache": "Yes, movement makes it worse.",
            "relieved_by_darkness": "Yes, resting in a dark room helps.",
        }
        return responses.get(symptom, "Yes, I’ve been experiencing that.")
    def _pain_reply(self, msg: str) -> str:
        pain_map = {
            "unilateral_headache": ["one side", "one-sided"],
            "movement_worsens_headache": ["movement", "walking", "physical activity"],
            "relieved_by_darkness": ["dark room", "resting in dark"],
            "headache": ["headache", "migraine", "head pain"],
            "body pain": ["body pain", "ache", "hurt"],
            "stomach pain": ["stomach", "abdominal", "belly"],
        }
        for symptom, keys in pain_map.items():
            if any(k in msg for k in keys):
                return self._symptom(symptom)

        return "Could you be more specific about the pain?"
    def _gi_reply(self, msg: str) -> str:
        gi_map = {
            "nausea": ["nausea", "nauseous"],
            "vomiting": ["vomit", "vomiting"],
            "diarrhea": ["diarrhea", "loose motion"],
        }

        for symptom, keys in gi_map.items():
            if any(k in msg for k in keys):
                return self._symptom(symptom)

        return "Could you clarify the stomach-related symptom?"

    def _record(self, symptom: str):
        if symptom not in self.state["symptoms_revealed"]:
            self.state["symptoms_revealed"].append(symptom)

    def _check_unlock(self):
        revealed = set(self.state["symptoms_revealed"])

        if self.state["disease"] == "migraine":
            if (
                "headache" in revealed
                and len(revealed & self.optional_symptoms) >= 1
                and self.state["questions_asked"] >= self.min_questions
            ):
                self.state["ready_for_diagnosis"] = True
                self.state["next_action"] = "allow_diagnosis"
            return

        if (
            not self.state["ready_for_diagnosis"]
            and self.required_symptoms <= revealed
            and self.state["questions_asked"] >= self.min_questions
        ):
            self.state["ready_for_diagnosis"] = True
            self.state["next_action"] = "allow_diagnosis"
