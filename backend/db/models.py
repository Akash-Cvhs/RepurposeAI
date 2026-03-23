from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    query: Mapped[str] = mapped_column(Text)
    molecule: Mapped[str | None] = mapped_column(String(120), nullable=True)
    indication: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="completed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    agent_responses = relationship("AgentResponse", back_populates="session", cascade="all, delete-orphan")
    report = relationship("Report", uselist=False, back_populates="session", cascade="all, delete-orphan")


class AgentResponse(Base):
    __tablename__ = "agent_responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("research_sessions.id"), index=True)
    agent_name: Mapped[str] = mapped_column(String(120), index=True)
    content: Mapped[str] = mapped_column(Text)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)

    session = relationship("ResearchSession", back_populates="agent_responses")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("research_sessions.id"), unique=True)
    report_path: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text)

    session = relationship("ResearchSession", back_populates="report")


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int | None] = mapped_column(ForeignKey("research_sessions.id"), nullable=True, index=True)
    filename: Mapped[str] = mapped_column(String(255))
    path: Mapped[str] = mapped_column(Text)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
