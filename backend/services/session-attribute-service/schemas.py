from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class SessionBase(BaseModel):
    title: str
    scheduled_at: Optional[datetime]
    summary: Optional[str] = None
    notes: Optional[str] = None
    recording_url: Optional[str] = None


class SessionCreate(SessionBase):
    pass


class SessionRead(SessionBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class SessionAttributeBase(BaseModel):
    key: str
    value: Any


class SessionAttributeCreate(SessionAttributeBase):
    pass


class SessionAttributeRead(SessionAttributeBase):
    id: UUID
    session_id: UUID
    value_type: str
    updated_at: datetime

    class Config:
        orm_mode = True

