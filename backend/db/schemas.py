from __future__ import annotations

from pydantic import BaseModel


class SessionCreate(BaseModel):
    request_id: str
    query: str
    molecule: str | None = None
    indication: str | None = None


class SessionRead(BaseModel):
    id: int
    request_id: str
    query: str
    molecule: str | None = None
    indication: str | None = None
    status: str


class ReportCreate(BaseModel):
    session_id: int
    report_path: str
    summary: str
