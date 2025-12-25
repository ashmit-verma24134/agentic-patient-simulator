# Agentic AI Patient Simulator

This project is a multi-user agentic AI chatbot that simulates a patient
interacting with doctors. Each user interacts with a unique patient whose
symptoms evolve over time.

## Key Features
- One patient per user session
- LangGraph-based multi-agent orchestration
- Progressive symptom disclosure
- Treatment evaluation and acceptance
- Flask backend + web frontend

## Tech Stack
- LangChain
- LangGraph
- Flask
- HTML/CSS/JS

## Architecture
Each user session maps to a single LangGraph thread, ensuring isolated
memory and realistic patient behavior.
