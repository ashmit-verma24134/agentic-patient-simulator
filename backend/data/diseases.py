DISEASES = {
    "flu": {
        "required_symptoms": [
            "fever",
            "cough"
        ],
        "optional_symptoms": [
            "fatigue",
            "body pain",
            "headache"
        ],
        "min_questions": 3
    },

    "migraine": {
        "required_symptoms": ["headache"],
        "optional_symptoms": [
            "light_sensitivity",
            "nausea",
            "movement_worsens_headache",
            "unilateral_headache",
            "relieved_by_darkness"
        ],
        "min_questions": 2
    },


    "food_poisoning": {
        "required_symptoms": [
            "nausea",
            "vomiting"
        ],
        "optional_symptoms": [
            "diarrhea",
            "stomach pain"
        ],
        "min_questions": 2
    }
}
