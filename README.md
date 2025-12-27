# Agentic Patient Simulator

An **agent-based, multi-user medical interview simulator** built using **LangGraph, LangChain, Flask**, and **vanilla HTML/CSS/JavaScript**.  
The system simulates a patient that progressively reveals symptoms, maintains conversation memory, updates diagnostic confidence in real time, and finally accepts or rejects a prescribed treatment.

---

## Features

### Multi-Session Patient Simulation
- Create and manage multiple patient sessions simultaneously
- Each patient maintains an **independent conversation state**
- Sessions can be switched without losing memory or progress

---

### Agentic Reasoning with LangGraph
Patient behavior is driven by a **LangGraph state machine**.

The patient:
- Reveals symptoms progressively
- Responds only to medically relevant questions
- Prevents premature diagnosis
- Transitions through structured phases:
  - **Questioning → Diagnosis → Treatment → Completion**

---

### Diagnostic Confidence Engine
Real-time confidence scores for:
- Flu
- Migraine
- Food Poisoning

Confidence updates dynamically as new symptoms are revealed using:
- Weighted symptom reasoning
- Required vs optional symptoms
- Partial evidence accumulation

---

### Patient Memory Panel
- Displays confirmed symptoms discovered during the conversation
- Updates live per session
- Helps doctors reason based on accumulated evidence

---

### Realistic Chat Experience
- Human-like typing delays
- Typing indicator for patient responses
- Clear role distinction:
  - Doctor
  - Patient
  - System

---

## Architecture Overview

### Frontend
Built using **HTML, CSS, and JavaScript**

**Three-panel layout:**
- Session management panel
- Central chat interface
- Patient memory & diagnostic confidence panel

UI state remains synchronized with backend responses.

---

### Backend
- Flask-based REST API
- LangGraph controls patient state transitions

**Modular Agents:**
- `EvaluatorAgent` – validates diagnoses
- `TreatmentAgent` – evaluates prescribed treatments

---

### State Management
Each patient session maintains a structured state:

```json
{
  "symptoms_revealed": [],
  "questions_asked": 0,
  "ready_for_diagnosis": false,
  "diagnosis_confirmed": false,
  "treatment_accepted": false
}
