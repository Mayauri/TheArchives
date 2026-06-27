import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Archivist API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = Path(__file__).parent / "archivist.db"


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                role TEXT NOT NULL DEFAULT 'assistant',
                status TEXT NOT NULL DEFAULT 'inactive',
                instructions TEXT NOT NULL DEFAULT '',
                tags TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["tags"] = json.loads(d["tags"])
    return d


class AgentCreate(BaseModel):
    name: str
    description: str = ""
    role: str = "assistant"
    instructions: str = ""
    tags: list[str] = []


class AgentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    role: str | None = None
    status: str | None = None
    instructions: str | None = None
    tags: list[str] | None = None


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {"status": "ok", "service": "Archivist API"}


@app.get("/agents")
def list_agents():
    with get_db() as db:
        rows = db.execute("SELECT * FROM agents ORDER BY created_at DESC").fetchall()
    return [row_to_dict(r) for r in rows]


@app.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    with get_db() as db:
        row = db.execute("SELECT * FROM agents WHERE id = ?", (agent_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Agent not found")
    return row_to_dict(row)


@app.post("/agents", status_code=201)
def create_agent(agent: AgentCreate):
    agent_id = str(uuid4())
    now = datetime.now().isoformat()
    with get_db() as db:
        db.execute(
            """INSERT INTO agents (id, name, description, role, status, instructions, tags, created_at, updated_at)
               VALUES (?, ?, ?, ?, 'inactive', ?, ?, ?, ?)""",
            (agent_id, agent.name, agent.description, agent.role,
             agent.instructions, json.dumps(agent.tags), now, now),
        )
    return get_agent(agent_id)


@app.put("/agents/{agent_id}")
def update_agent(agent_id: str, update: AgentUpdate):
    existing = get_agent(agent_id)
    fields = {}
    if update.name is not None:
        fields["name"] = update.name
    if update.description is not None:
        fields["description"] = update.description
    if update.role is not None:
        fields["role"] = update.role
    if update.status is not None:
        fields["status"] = update.status
    if update.instructions is not None:
        fields["instructions"] = update.instructions
    if update.tags is not None:
        fields["tags"] = json.dumps(update.tags)
    if not fields:
        return existing
    fields["updated_at"] = datetime.now().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [agent_id]
    with get_db() as db:
        db.execute(f"UPDATE agents SET {set_clause} WHERE id = ?", values)
    return get_agent(agent_id)


@app.post("/agents/{agent_id}/toggle")
def toggle_agent(agent_id: str):
    agent = get_agent(agent_id)
    new_status = "active" if agent["status"] == "inactive" else "inactive"
    with get_db() as db:
        db.execute(
            "UPDATE agents SET status = ?, updated_at = ? WHERE id = ?",
            (new_status, datetime.now().isoformat(), agent_id),
        )
    return get_agent(agent_id)


@app.delete("/agents/{agent_id}")
def delete_agent(agent_id: str):
    agent = get_agent(agent_id)
    with get_db() as db:
        db.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
    return {"detail": f"Agent '{agent['name']}' deleted"}


@app.get("/health")
def health():
    with get_db() as db:
        total = db.execute("SELECT COUNT(*) FROM agents").fetchone()[0]
        active = db.execute("SELECT COUNT(*) FROM agents WHERE status = 'active'").fetchone()[0]
    return {"status": "healthy", "total_agents": total, "active_agents": active}
