# Archivist

A lightweight tool for creating and managing AI agents. Built with a **FastAPI** backend and a **Streamlit** frontend.

Agents are stored in a local SQLite database so they persist across restarts — no external database required.

## Features

- Create agents with a name, role, description, instructions, and tags
- Activate / deactivate agents with one click
- Browse, edit, and delete agents from a web UI
- RESTful API for programmatic access
- Persistent storage via SQLite

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/mayauri/TheArchives.git
cd TheArchives

# 2. Create a virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Start the backend (Terminal 1)
uvicorn backend.main:app --reload --port 8000

# 4. Start the frontend (Terminal 2)
streamlit run frontend/app.py --server.port 8501
```

Open **http://localhost:8501** in your browser.

## Project Structure

```
TheArchives/
├── backend/
│   └── main.py          # FastAPI REST API
├── frontend/
│   └── app.py           # Streamlit web UI
├── requirements.txt
└── README.md
```

## API Endpoints

| Method | Path                        | Description              |
|--------|-----------------------------|--------------------------|
| GET    | `/`                         | Service info             |
| GET    | `/health`                   | Health check + stats     |
| GET    | `/agents`                   | List all agents          |
| GET    | `/agents/{id}`              | Get a single agent       |
| POST   | `/agents`                   | Create a new agent       |
| PUT    | `/agents/{id}`              | Update an agent          |
| POST   | `/agents/{id}/toggle`       | Toggle active / inactive |
| DELETE | `/agents/{id}`              | Delete an agent          |

## Tech Stack

- **Backend:** FastAPI + Uvicorn
- **Frontend:** Streamlit
- **Database:** SQLite (zero-config, file-based)
- **Language:** Python 3.10+
