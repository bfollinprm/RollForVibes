import os
from typing import List
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from . import crud, schemas
from .database import SessionLocal, init_db
from .google_docs import create_document

app = FastAPI(
    title="RollForVibes Google Doc Service",
    description="Creates and shares Google Docs for session recordings",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "ok", "database": "reachable"}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="database unreachable")


@app.post("/api/recordings", response_model=schemas.RecordingRead)
def create_recording(payload: schemas.RecordingCreate, db: Session = Depends(get_db)):
    try:
        doc_id, doc_url = create_document(payload.title, payload.summary)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return crud.create_recording(db, payload, doc_id, doc_url)


@app.get("/api/recordings", response_model=List[schemas.RecordingRead])
def list_recordings(db: Session = Depends(get_db)):
    return crud.get_recordings(db)


@app.get("/api/recordings/session/{session_id}", response_model=List[schemas.RecordingRead])
def list_session_recordings(session_id: UUID, db: Session = Depends(get_db)):
    return crud.get_recordings_for_session(db, session_id)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 9000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")

