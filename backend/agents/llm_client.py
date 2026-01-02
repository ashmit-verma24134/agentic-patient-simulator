#It is ONLY for turning an already-decided medical statement into natural language.

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv() #import env for api

client=Groq(api_key=os.getenv("GROQ_API_KEY"))  #used for all llm calls
modelname="llama-3.1-8b-instant"

#Hard coded responses never goes to llm
_HARD_RESPONSES={"I feel unwell.","I am not feeling well.","I have been feeling unwell.","I don't know, I just feel unwell."}

#Forbidden phrases which agent must avoid
_FORBIDDEN = [
    "glad",
    "relieved",
    "thankfully",
    "luckily",
    "happy",
    "no need to worry",
    "that's fine",
    "that’s fine",
    "not a problem",
    "reassuring",
]

def llm_speak(system_prompt:str,user_prompt:str)->str:
    if user_prompt in _HARD_RESPONSES:   #if in hardcoded then reply with that
        return user_prompt

    response= client.chat.completions.create(    #llm call
        model=modelname,
        messages=[
            {
                "role": "system",
                "content": (
                    "ROLE: Simulated Patient\n"
                    "TASK: Turn the medical statement into a natural patient reply.\n\n"
                    "ALLOWED:\n"
                    "- Mild elaboration (timing, intensity, frequency)\n"                    #strict rigid prompt to avoid hallucination of messages
                    "- Natural human phrasing\n\n"
                    "FORBIDDEN (CRITICAL):\n"
                    "- Do NOT add new symptoms\n"
                    "- Do NOT reassure or express relief\n"
                    "- Do NOT interpret results\n"
                    "- Do NOT diagnose\n"
                    "- Do NOT give advice\n"
                    "- First person only\n"
                    "- One or two sentences maximum\n"
                    "- Preserve exact medical meaning\n"
                ),
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.75,   #to control 
        max_tokens=70,      #Short output→less risk
    )
    text = response.choices[0].message.content.strip()

    #Safety filters:-
    if not text:
        return user_prompt

    lowered = text.lower()
    for phrase in _FORBIDDEN:
        if phrase in lowered:
            return user_prompt

    # Strip internal markers if any
    if text.startswith("__"):
        return user_prompt
    return text
    
#The LLM is strictly constrained to linguistic realization with multiple deterministic safety gates to prevent hallucination, emotional interpretation, or medical reasoning.