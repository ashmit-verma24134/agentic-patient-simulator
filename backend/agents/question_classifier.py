#This file converts a doctor's question (text) into a structured query
from enum import Enum, auto
class QuestionType(Enum):
    GENERAL = auto()    # VAGUE / GENERAL

    # PRECISE CATEGORIES
    DURATION= auto()       #DURATION → “How long?”
    FEVER= auto()          #FEVER → “Do you have fever?”
    RESPIRATORY= auto()    #RESPIRATORY → “Do you have cough?”
    GI= auto()             #GI → nausea, vomiting, diarrhea
    PAIN= auto()           #PAIN → headache, body pain
    SENSITIVITY= auto()    #SENSITIVITY → light/noise sensitivity (migraine)

    # NON-MEDICAL / NO SIGNAL
    IRRELEVANT = auto()     #“Do you like football?”


def classify_question(message: str)-> QuestionType:
    text = message.lower().strip()
    #Detection rules

    #Durations
    if any(w in text for w in ["how long","since when","since","days","hours","weeks"]):
        return QuestionType.DURATION

    #Fever
    if any(w in text for w in ["fever", "temperature", "chills", "high temperature"]):
        return QuestionType.FEVER

    #Respiratory
    if any(w in text for w in ["cough", "breath", "breathing", "shortness of breath", "chest pain"]):
        return QuestionType.RESPIRATORY

    #GI
    if any(w in text for w in ["nausea", "nauseous", "vomit", "vomiting","diarrhea", "loose motion", "stool"]):
        return QuestionType.GI

    #Sensitivity
    if any(w in text for w in ["bright light", "light hurts", "light bother","photophobia", "noise", "sound", "loud"]):
        return QuestionType.SENSITIVITY

    #Pain
    if any(w in text for w in [
        "headache", "migraine", "head pain",
        "stomach pain", "abdominal", "belly",
        "body pain", "ache", "hurt", "pain",
        "one side", "one-sided",
        "movement", "moving", "physical activity",
        "walk", "climb", "resting in dark", "dark room"
    ]):
        return QuestionType.PAIN

    #General (vague but relevant)
    if any(w in text for w in [
        "tired", "fatigue", "exhausted", "weak",
        "feel", "feeling", "health", "unwell"
    ]):
        return QuestionType.GENERAL

    #No medical signal
    return QuestionType.IRRELEVANT
