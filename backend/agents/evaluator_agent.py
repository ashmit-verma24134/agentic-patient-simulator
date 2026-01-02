#EvaluatorAgent checks whether the doctor’s diagnosis is valid, timely, and supported by evidence.

from data.diseases import DISEASES


class EvaluatorAgent:
    def __init__(self, patient_state: dict):
        self.state = patient_state

    def evaluate(self, doctor_message: str) -> dict:
        # Gate:diagnosis only when allowed
        if not self.state.get("ready_for_diagnosis", False):
            return {
                "verdict": "blocked",
                "reason": "Diagnosis attempted before sufficient information was gathered."
            }

        text = doctor_message.lower().strip()
        if not text.startswith("diagnosis"):
            return {
                "verdict": "out_of_scope",
                "reason": "Diagnosis must be provided as: diagnosis: <disease>"
            }
        #Normalize diagnosis
        diagnosis = (
            text.replace("diagnosis", "", 1)
                .replace(":", "")
                .strip()
                .replace(" ", "_")
        )

        actual=(
            self.state.get("disease", "")
                .lower()
                .replace(" ", "_")
        )

        if diagnosis not in DISEASES:
            return {
                "verdict": "out_of_scope",
                "reason": "This diagnosis is not supported in the simulation."
            }

        if diagnosis !=actual:
            return {
                "verdict":"incorrect",
                "reason": f"The symptoms do not match {diagnosis}."
            }

        revealed =set(self.state.get("symptoms_revealed", []))
        disease_info =DISEASES[diagnosis]

        required = set(disease_info.get("required_symptoms", []))
        optional = set(disease_info.get("optional_symptoms", []))

        if not required.issubset(revealed):
            return self._insufficient(
                f"Missing required symptoms: {', '.join(required - revealed)}."
            )

        if len(optional & revealed) == 0:
            return self._insufficient(
                "Disease-specific characteristics were not sufficiently explored."
            )

        return self._correct()

    #helpers

    def _correct(self):
        return {
            "verdict": "correct",
            "reason": "Diagnosis matches and sufficient evidence was gathered."
        }

    def _insufficient(self, reason: str):
        return {
            "verdict": "incorrect",
            "reason": reason
        }
