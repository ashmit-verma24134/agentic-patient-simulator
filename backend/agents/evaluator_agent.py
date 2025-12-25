from data.diseases import DISEASES


class EvaluatorAgent:
    def __init__(self, patient_state: dict):
        self.state = patient_state

    def evaluate(self, doctor_message: str) -> dict:
        # 🔒 hard backend gate
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

        diagnosis = text.replace("diagnosis", "", 1).replace(":", "").strip()
        actual = self.state["disease"]

        # 🚫 unsupported disease
        if diagnosis not in DISEASES:
            return {
                "verdict": "out_of_scope",
                "reason": "This diagnosis is not supported in the simulation."
            }

        # ❌ wrong diagnosis
        if diagnosis != actual:
            return {
                "verdict": "incorrect",
                "reason": f"The symptoms do not match {diagnosis}."
            }

        # ---------------- SYMPTOM VALIDATION ----------------

        revealed = set(self.state.get("symptoms_revealed", []))
        disease_info = DISEASES[diagnosis]

        required = set(disease_info.get("required_symptoms", []))
        optional = set(disease_info.get("optional_symptoms", []))

        # ❌ missing required symptoms
        if not required.issubset(revealed):
            return self._insufficient(
                f"Missing required symptoms: {', '.join(required - revealed)}."
            )

        # ❌ no disease-specific features explored
        if len(optional & revealed) == 0:
            return self._insufficient(
                "Disease-specific characteristics were not sufficiently explored."
            )

        # ✅ CORRECT diagnosis
        return self._correct()

    # ---------------- HELPERS ----------------

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
