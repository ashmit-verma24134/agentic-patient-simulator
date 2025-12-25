from enum import Enum, auto


class QuestionType(Enum):
    GENERAL = auto()
    PAIN = auto()
    FEVER = auto()
    RESPIRATORY = auto()
    DURATION = auto()
    SENSITIVITY = auto()
    IRRELEVANT = auto()


def classify_question(message: str) -> QuestionType:
    text = message.lower()

    if any(w in text for w in ["how long", "duration", "days", "since"]):
        return QuestionType.DURATION

    if any(w in text for w in ["fever", "temperature", "chills"]):
        return QuestionType.FEVER

    if any(w in text for w in ["cough", "breath", "breathing", "chest"]):
        return QuestionType.RESPIRATORY

    if any(w in text for w in ["light", "bright", "lights", "sound", "noise"]):
        return QuestionType.SENSITIVITY

    if any(w in text for w in [
        "headache", "migraine", "head pain",
        "stomach", "abdominal", "belly", "ache", "hurt"
    ]):
        return QuestionType.PAIN

    if any(w in text for w in ["tired", "fatigue", "exhausted", "weak"]):
        return QuestionType.GENERAL

    if any(w in text for w in ["feel", "feeling", "health", "unwell"]):
        return QuestionType.GENERAL

    return QuestionType.IRRELEVANT
