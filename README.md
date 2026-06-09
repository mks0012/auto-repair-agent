# Auto-Repair Agent

An intelligent, agentic workflow for autonomous code generation and iterative debugging. This system leverages **LangGraph** to orchestrate specialized agents that plan, generate, and critique code in a sandbox environment.

## 🚀 Key Features
* **Agentic Workflow**: Uses a defined graph structure to manage code generation state.
* **Iterative Debugging**: The 'Critic' agent reviews sandbox execution results and feeds errors back into the 'Generator' for self-correction.
* **State Management**: Robust hydration of conversation history and code state between the React frontend and FastAPI backend.

## 🛠 Tech Stack
* **Frontend**: Next.js (TypeScript), Tailwind CSS.
* **Backend**: FastAPI, Uvicorn.
* **AI Orchestration**: LangGraph, Groq API.

## ⚙️ Setup & Installation

### Prerequisites
* Python 3.12+
* Node.js 20+

### Backend
```bash
cd .. # Ensure you are in the root directory
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
Frontend
Bash
cd frontend
npm install
npm run dev


🧠 Architecture
graph/: Contains the LangGraph definition and state logic.

nodes/: Modular definitions for Planner, Generator, and Critic agents.

server.py: FastAPI entry point handling WebSocket streams for the frontend.

1.  **Professionalism**: It uses industry-standard headings.
2.  **Clarity**: It immediately tells them *what* you built and *why* it matters (the "Critic" agent is a great selling point).
3.  **Actionable**: It provides the exact commands they need to run the app. If they can't run it in 60 seconds, they will move on to the next candidate.


