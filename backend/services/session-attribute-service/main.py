import os
from typing import List
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from . import crud, schemas
from .database import SessionLocal, init_db

app = FastAPI(
    title="RollForVibes Session Attribute Store",
    description="Stores session metadata and per-session attribute key/value pairs in PostgreSQL",
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


@app.post("/api/sessions", response_model=schemas.SessionRead)
def create_session(session_in: schemas.SessionCreate, db: Session = Depends(get_db)):
    return crud.create_session(db, session_in)


@app.get("/api/sessions", response_model=List[schemas.SessionRead])
def list_sessions(db: Session = Depends(get_db)):
    return crud.get_sessions(db)


@app.get("/api/sessions/{session_id}", response_model=schemas.SessionRead)
def get_session(session_id: UUID, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.get("/api/sessions/{session_id}/attributes", response_model=List[schemas.SessionAttributeRead])
def list_session_attributes(session_id: UUID, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return crud.get_session_attributes(db, session_id)


@app.post("/api/sessions/{session_id}/attributes", response_model=schemas.SessionAttributeRead)
def upsert_session_attribute(
    session_id: UUID,
    payload: schemas.SessionAttributeCreate,
    db: Session = Depends(get_db),
):
    session = crud.get_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return crud.upsert_session_attribute(db, session_id, payload)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")

