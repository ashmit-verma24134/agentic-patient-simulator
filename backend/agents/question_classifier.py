from enum import Enum, auto


class QuestionType(Enum):
    GENERAL = auto()
    PAIN = auto()           # headache / body / stomach pain
    GI = auto()             # nausea / vomiting / diarrhea
    FEVER = auto()
    RESPIRATORY = auto()
    SENSITIVITY = auto()    # light / sound
    DURATION = auto()
    IRRELEVANT = auto()


def classify_question(message: str) -> QuestionType:
    text = message.lower()

    # ⏳ duration FIRST
    if any(w in text for w in ["how long", "duration", "days", "since"]):
        return QuestionType.DURATION

    # 🌡 fever
    if any(w in text for w in ["fever", "temperature", "chills"]):
        return QuestionType.FEVER

    # 🫁 respiratory
    if any(w in text for w in ["cough", "breath", "breathing", "chest"]):
        return QuestionType.RESPIRATORY

    # 🧠 MIGRAINE-SPECIFIC FEATURES (treat as PAIN)
    if any(w in text for w in [
        "dark room",
        "darkness",
        "resting in dark",
        "lights off",
        "movement",
        "moving",
        "physical activity",
        "walk",
        "climb",
        "one side",
        "one-sided"
    ]):
        return QuestionType.PAIN

    # 🌟 sensory sensitivity (explicit)
    if any(w in text for w in [
        "bright light",
        "light bother",
        "light hurts",
        "photophobia",
        "noise",
        "sound",
        "loud"
    ]):
        return QuestionType.SENSITIVITY

    # 🤢 GI symptoms (STRICT)
    if any(w in text for w in [
        "nausea", "nauseous",
        "vomit", "vomiting",
        "diarrhea", "loose motion"
    ]):
        return QuestionType.GI

    # 🧠 pain (general + stomach)
    if any(w in text for w in [
        "headache", "migraine", "head pain",
        "stomach", "abdominal", "belly",
        "body pain", "ache", "hurt", "pain"
    ]):
        return QuestionType.PAIN

    # 😴 fatigue / weakness
    if any(w in text for w in ["tired", "fatigue", "exhausted", "weak"]):
        return QuestionType.GENERAL

    # 🧍 general feelings LAST
    if any(w in text for w in ["feel", "feeling", "health", "unwell"]):
        return QuestionType.GENERAL

    return QuestionType.IRRELEVANT
