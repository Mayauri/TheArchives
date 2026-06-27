from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4

app = FastAPI(title="Archivist API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

archives: dict[str, dict] = {}


class ArchiveEntry(BaseModel):
    title: str
    content: str
    tags: list[str] = []


class ArchiveUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None


@app.get("/")
def root():
    return {"status": "ok", "service": "Archivist API"}


@app.get("/archives")
def list_archives():
    return list(archives.values())


@app.get("/archives/{archive_id}")
def get_archive(archive_id: str):
    if archive_id not in archives:
        raise HTTPException(status_code=404, detail="Archive not found")
    return archives[archive_id]


@app.post("/archives", status_code=201)
def create_archive(entry: ArchiveEntry):
    archive_id = str(uuid4())
    record = {
        "id": archive_id,
        "title": entry.title,
        "content": entry.content,
        "tags": entry.tags,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    archives[archive_id] = record
    return record


@app.put("/archives/{archive_id}")
def update_archive(archive_id: str, entry: ArchiveUpdate):
    if archive_id not in archives:
        raise HTTPException(status_code=404, detail="Archive not found")
    record = archives[archive_id]
    if entry.title is not None:
        record["title"] = entry.title
    if entry.content is not None:
        record["content"] = entry.content
    if entry.tags is not None:
        record["tags"] = entry.tags
    record["updated_at"] = datetime.now().isoformat()
    return record


@app.delete("/archives/{archive_id}")
def delete_archive(archive_id: str):
    if archive_id not in archives:
        raise HTTPException(status_code=404, detail="Archive not found")
    del archives[archive_id]
    return {"detail": "Archive deleted"}


@app.get("/health")
def health():
    return {"status": "healthy", "archive_count": len(archives)}
