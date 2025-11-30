from typing import Any, Iterable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas


def _value_type(value: Any) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if value is None:
        return "null"
    return "json"


def get_sessions(db: Session) -> Iterable[models.Session]:
    stmt = select(models.Session).order_by(models.Session.scheduled_at.desc())
    return db.scalars(stmt).all()


def create_session(db: Session, session_in: schemas.SessionCreate) -> models.Session:
    db_obj = models.Session(**session_in.dict(exclude_none=True))
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_session(db: Session, session_id: UUID) -> models.Session | None:
    return db.get(models.Session, session_id)


def get_session_attributes(db: Session, session_id: UUID) -> Iterable[models.SessionAttribute]:
    stmt = (
        select(models.SessionAttribute)
        .where(models.SessionAttribute.session_id == session_id)
        .order_by(models.SessionAttribute.key)
    )
    return db.scalars(stmt).all()


def upsert_session_attribute(
    db: Session, session_id: UUID, payload: schemas.SessionAttributeCreate
) -> models.SessionAttribute:
    stmt = (
        select(models.SessionAttribute)
        .where(
            models.SessionAttribute.session_id == session_id,
            models.SessionAttribute.key == payload.key,
        )
        .limit(1)
    )
    existing = db.scalars(stmt).first()
    value_type = _value_type(payload.value)
    if existing:
        existing.value = payload.value
        existing.value_type = value_type
        db.commit()
        db.refresh(existing)
        return existing

    db_obj = models.SessionAttribute(
        session_id=session_id,
        key=payload.key,
        value=payload.value,
        value_type=value_type,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

