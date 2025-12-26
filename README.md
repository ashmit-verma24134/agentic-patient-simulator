Agentic Patient Simulator

An agent-based, multi-user medical interview simulator built using LangGraph, LangChain, Flask, and vanilla HTML/CSS/JavaScript.
The system simulates a patient that progressively reveals symptoms, maintains conversation memory, updates diagnostic confidence in real time, and finally accepts or rejects a prescribed treatment.

Features
Multi-Session Patient Simulation

Create and manage multiple patients simultaneously

Each patient maintains an independent conversation state

Sessions can be switched without losing memory or progress

Agentic Reasoning with LangGraph

Patient behavior is driven by a LangGraph state machine

The patient:

Reveals symptoms progressively

Responds only to medically relevant questions

Prevents premature diagnosis

Transitions through question → diagnosis → treatment → completion phases

Diagnostic Confidence Engine

Real-time confidence scores for:

Flu

Migraine

Food Poisoning

Confidence updates dynamically as new symptoms are revealed

Uses weighted symptom reasoning (required vs optional symptoms)

Patient Memory Panel

Displays confirmed symptoms discovered during the conversation

Updates live per session

Allows doctors to reason based on accumulated evidence

Realistic Chat Experience

Human-like typing delays

Typing indicator for patient responses

Clear role distinction between Doctor, Patient, and System messages

Architecture Overview
Frontend

Built using HTML, CSS, and JavaScript

Three-panel layout:

Session management panel

Central chat interface

Patient memory and diagnostic confidence panel

UI state is synchronized with backend responses

Backend

Flask REST API

LangGraph controls patient state transitions

Modular agents:

EvaluatorAgent for diagnosis validation

TreatmentAgent for treatment evaluation

State Management

Each patient session maintains a structured state:

patient_state = {
    "symptoms_revealed": [],
    "questions_asked": int,
    "ready_for_diagnosis": bool,
    "diagnosis_confirmed": bool,
    "treatment_accepted": bool
}


This state ensures consistent behavior across multiple interactions.

Diagnostic Confidence Logic

Diagnostic confidence is computed using a weighted evidence model:

Required symptoms contribute higher weight

Optional symptoms contribute lower weight

Partial evidence still increases confidence

Scores are normalized into percentages

This approach ensures:

Overlapping symptoms affect multiple diseases

Confidence evolves gradually instead of jumping abruptly

Example Interaction Flow

Doctor asks symptom-related questions

Patient reveals symptoms progressively

Memory panel updates with confirmed symptoms

Diagnostic confidence bars update dynamically

Diagnosis becomes available after sufficient evidence

Doctor prescribes treatment

Patient evaluates and accepts treatment

Session is marked as completed

Technology Stack

Python

Flask

LangChain

LangGraph

HTML

CSS

JavaScript

Why This Is an Agentic System

This project is not a simple chatbot. It exhibits agentic behavior by:

Using explicit state transitions

Separating responsibilities into specialized agents

Enforcing medical workflow constraints

Maintaining long-term session memory

Acting in a goal-directed and rule-constrained manner

Future Improvements

Additional diseases and symptom graphs

Treatment effectiveness feedback

Instructor or evaluator mode

Patient personality variations

Deployment on Vercel

Author

Ashmit Verma
IIIT Delhi
Agentic AI Internship Candidate