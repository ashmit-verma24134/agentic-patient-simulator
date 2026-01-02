# It decides:

# What the patient knows

# Which symptoms to reveal

# When diagnosis becomes allowed

# How the internal patient state updates

# How replies are phrased (via LLM, safely)

from agents.question_classifier import classify_question,QuestionType
from data.diseases import DISEASES
from agents.llm_client import llm_speak


class PatientAgent:
    def __init__(self, state:dict):
        self.state= state             #dictionary stored in session_store

        disease= state["disease"]
        disease_info= DISEASES[disease]

        self.required_symptoms= set(disease_info.get("required_symptoms", []))
        self.optional_symptoms= set(disease_info.get("optional_symptoms", []))
        self.all_symptoms= self.required_symptoms | self.optional_symptoms
        self.min_questions= disease_info.get("min_questions", 2)

        self.state.setdefault("symptoms_revealed", [])
        self.state.setdefault("questions_asked", 0)
        self.state.setdefault("ready_for_diagnosis", False)
        self.state.setdefault("next_action", None)
        self.state.setdefault("reasoning_trace", [])

    # MAIN ENTRY
    def respond(self, user_message: str) -> str:
        msg = user_message.lower().strip()

        #Greeting
        if msg in {"hi", "hello", "hey"}:
            return "I have been feeling unwell."
        self.state["questions_asked"] += 1

        #Lab report trigger
        if any(k in msg for k in ("lab report", "test report", "investigation")):   #here the tool will come
            self.state["next_action"] = "show_lab_report"
            return "Already shown above."

        # Severity follow-up (only if a symptom exists)
        resolved= self._resolve_reference(msg)
        if resolved and "severe" in msg:
            self.state["reasoning_trace"].append(f"Severity clarified for symptom '{resolved}'")
            return self._speak(f"My {resolved} feels quite severe.")

        # Fatigue shortcut
        if any(w in msg for w in ("tired", "fatigue", "exhausted")):
            return self._symptom("fatigue")

        qtype = classify_question(user_message)   #System knows what type of medical ques is this

        # Vague
        if qtype in {QuestionType.GENERAL, QuestionType.IRRELEVANT}:
            return "I don't know, I just feel unwell."

        # Precise questions
        if qtype == QuestionType.FEVER:
            return self._symptom("fever")

        if qtype == QuestionType.RESPIRATORY:
            return self._symptom("cough")

        if qtype == QuestionType.SENSITIVITY:
            return self._symptom("light_sensitivity")

        if qtype == QuestionType.GI:
            return self._gi_reply(msg)

        if qtype == QuestionType.PAIN:
            return self._pain_reply(msg)

        if qtype == QuestionType.DURATION:
            self.state["reasoning_trace"].append("Duration asked")
            return (
                "The symptoms have been present for a few days."
                if self.state["ready_for_diagnosis"]
                else "I am not sure how long it has been."
            )
        return "I don't know, I just feel unwell."


    # SYMPTOMS
    def _symptom(self, symptom: str) -> str:
        if symptom not in self.all_symptoms:
            return f"I do not have {symptom}."

        self._record(symptom)    #add to symptom revealed and check for diagnosis

        # Disease-aware phrasing for PRESENCE
        if symptom == "nausea":
            return self._speak("I feel quite nauseous")

        return self._speak(f"I have {symptom}.")

    def _pain_reply(self, msg: str) -> str:
        pain_map = {
            "unilateral_headache": ["one side", "one-sided"],
            "movement_worsens_headache": ["movement", "walking", "activity"],
            "relieved_by_darkness": ["dark room", "resting in dark"],
            "headache": ["headache", "migraine", "head pain"],
            "body pain": ["body pain", "ache", "hurt"],
            "stomach pain": ["stomach", "abdominal", "belly"],
        }

        for symptom, keys in pain_map.items():
            if any(k in msg for k in keys):
                return self._symptom(symptom)

        return self._speak("I am experiencing some pain.")

    def _gi_reply(self, msg: str) -> str:
        gi_map = {
            "nausea": ["nausea", "nauseous"],
            "vomiting": ["vomit", "vomiting"],
            "diarrhea": ["diarrhea", "loose motion"],
        }

        for symptom, keys in gi_map.items():
            if any(k in msg for k in keys):
                return self._symptom(symptom)

        return self._speak("I have some stomach discomfort.")

    # STATE MANAGEMENT
    def _record(self, symptom: str):
        if symptom not in self.state["symptoms_revealed"]:   #avoid duplicates
            self.state["symptoms_revealed"].append(symptom)
            self.state["reasoning_trace"].append(f"Symptom '{symptom}' confirmed")
        self._check_unlock()




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
                self.state["reasoning_trace"].append(
                    "Migraine diagnostic criteria satisfied"
                )
            return

        if (
            not self.state["ready_for_diagnosis"]
            and self.required_symptoms <= revealed
            and self.state["questions_asked"] >= self.min_questions
        ):
            self.state["ready_for_diagnosis"] = True
            self.state["next_action"] = "allow_diagnosis"      #All required symptoms are present
            self.state["reasoning_trace"].append(
                f"Required symptoms {list(self.required_symptoms)} satisfied"
            )

    
    # Reference resolution

    def _resolve_reference(self, message: str):
        refs = ("that symptom", "that issue", "it", "this symptom")
        if any(ref in message for ref in refs):
            if self.state["symptoms_revealed"]:
                return self.state["symptoms_revealed"][-1]
        return None

    #LLM SPEAK FX
    def _speak(self, semantic_text: str) -> str:
        return llm_speak(
            system_prompt=(
                "ROLE: Patient\n"
                "TASK: Rephrase the medical statement naturally.\n\n"
                "RULES:\n"
                "- First person only\n"
                "- One sentence only\n"
                "- Neutral human tone\n"
                "- Do NOT add symptoms\n"
                "- Do NOT reassure or react emotionally\n"
                "- Do NOT diagnose\n"
                "- Preserve exact meaning\n"
            ),
            user_prompt=semantic_text,
        )
