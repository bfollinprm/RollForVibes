from typing import Iterable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas


def create_recording(
    db: Session,
    payload: schemas.RecordingCreate,
    doc_id: str,
    doc_url: str,
) -> models.SessionRecording:
    db_obj = models.SessionRecording(
        session_id=payload.session_id,
        title=payload.title,
        summary=payload.summary,
        doc_id=doc_id,
        doc_url=doc_url,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_recordings(db: Session) -> Iterable[models.SessionRecording]:
    stmt = select(models.SessionRecording).order_by(models.SessionRecording.created_at.desc())
    return db.scalars(stmt).all()


def get_recordings_for_session(db: Session, session_id: UUID) -> Iterable[models.SessionRecording]:
    stmt = (
        select(models.SessionRecording)
        .where(models.SessionRecording.session_id == session_id)
        .order_by(models.SessionRecording.created_at.desc())
    )
    return db.scalars(stmt).all()

