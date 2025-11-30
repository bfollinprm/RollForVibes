from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class RecordingBase(BaseModel):
    session_id: UUID
    title: str
    summary: Optional[str] = None


class RecordingCreate(RecordingBase):
    pass


class RecordingRead(RecordingBase):
    id: UUID
    doc_id: str
    doc_url: HttpUrl
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

