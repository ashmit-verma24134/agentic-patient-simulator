from data.diseases import DISEASES


class EvaluatorAgent:

    def evaluate(self, patient_state: dict, doctor_diagnosis: str) -> dict:
        diagnosis = doctor_diagnosis.lower().strip()
        actual_disease = patient_state.get("disease")

        # 🚫 Rule 1: Unsupported diagnosis
        if diagnosis not in DISEASES:
            return {
                "verdict": "out_of_scope",
                "reason": "This diagnosis is not supported in the simulation."
            }

        # ❌ Rule 2: Wrong disease guessed
        if diagnosis != actual_disease:
            return {
                "verdict": "incorrect",
                "reason": f"The symptoms do not match {diagnosis}."
            }

        required_symptoms = set(
            DISEASES[diagnosis]["required_symptoms"]
        )
        revealed_symptoms = set(
            patient_state.get("symptoms_revealed", [])
        )

        # ⚠️ Rule 3: Missing required symptoms
        missing = required_symptoms - revealed_symptoms
        if missing:
            return {
                "verdict": "incorrect",
                "reason": f"Missing required symptoms: {', '.join(missing)}."
            }

        # ✅ Rule 4: Correct diagnosis
        return {
            "verdict": "correct",
            "reason": "All required symptoms are present and diagnosis matches."
        }
