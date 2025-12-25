from data.treatments import TREATMENTS


class TreatmentAgent:
    def __init__(self, patient_state: dict):
        self.state = patient_state

        # defensive defaults
        self.state.setdefault("treatment_accepted", False)

    def evaluate(self, doctor_message: str) -> dict:
        """
        Expected format:
        treatment: <treatment description>
        """

        disease = self.state.get("disease")
        text = doctor_message.lower().strip()

        # -------- format validation --------
        if not text.startswith("treatment"):
            return {
                "verdict": "out_of_scope",
                "reply": "Treatment must be provided as: treatment: <description>"
            }

        suggested = text.replace("treatment", "", 1).replace(":", "").strip()

        allowed_treatments = TREATMENTS.get(disease, [])

        # -------- matching logic --------
        for treatment in allowed_treatments:
            if treatment in suggested:
                self.state["treatment_accepted"] = True
                return {
                    "verdict": "accepted",
                    "reply": "Okay doctor, I’ll follow this treatment."
                }

        # -------- rejected --------
        return {
            "verdict": "rejected",
            "reply": "I’m not sure this treatment makes sense for my condition."
        }
