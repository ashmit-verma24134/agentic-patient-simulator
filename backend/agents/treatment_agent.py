from data.treatments import TREATMENTS


class TreatmentAgent:
    def __init__(self, patient_state: dict):
        self.state= patient_state
        self.state.setdefault("treatment_accepted", False)

    def evaluate(self, doctor_message: str) -> dict:

        disease = (self.state.get("disease") or "").lower().replace(" ", "_")
        text = doctor_message.lower().strip()

        # Wrong format -> semantic rejection
        if not text.startswith("treatment"):
            return {
                "verdict": "out_of_scope",
                "semantic_reply": "Treatment was not provided in the correct format."
            }

        suggested= (
            text.replace("treatment", "", 1)
                .replace(":", "")
                .strip()
        )

        allowed_treatments =TREATMENTS.get(disease, [])

        # Loose but safe matching
        for treatment in allowed_treatments:
            t =treatment.lower()
            if suggested in t or t in suggested:
                self.state["treatment_accepted"] = True
                return {
                    "verdict": "accepted",
                    "semantic_reply": "The proposed treatment is appropriate."
                }
        #Incorrect treatment
        return {
            "verdict": "rejected",
            "semantic_reply": "The proposed treatment does not fit my condition."
        }
