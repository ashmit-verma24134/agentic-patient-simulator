def generate_lab_report(state: dict) -> dict:
    disease = state.get("disease")

    #Baseline normal report

    report = {
        "CRP": "2 mg/L (Normal)",
        "Stool Test": "Normal",
        "Photophobia Test": "Negative",
        "Notes": []
    }


    # FLU

    if disease == "flu":
        report.update({
            "CRP": "14 mg/L (High)",
            "Stool Test": "Normal",
            "Photophobia Test": "Negative",
        })
        report["Notes"].append(
            "Elevated CRP indicates systemic inflammation."
        )

    # FOOD POISONING
    elif disease == "food_poisoning":
        report.update({
            "CRP": "18 mg/L (High)",
            "Stool Test": "Bacterial infection detected",
            "Photophobia Test": "Negative",
        })
        report["Notes"].append(
            "Stool findings indicate gastrointestinal infection."
        )

    # MIGRAINE
    elif disease == "migraine":
        report.update({
            "CRP": "1.5 mg/L (Normal)",
            "Stool Test": "Normal",
            "Photophobia Test": "Positive",
        })
        report["Notes"].append(
            "Normal inflammatory markers with photophobia present."
        )

    return report
