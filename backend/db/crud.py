from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import AgentResponse, Report, ResearchSession, UploadedFile


def create_session(
    db: Session,
    request_id: str,
    query: str,
    molecule: str | None,
    indication: str | None,
    status: str = "completed",
) -> ResearchSession:
    session = ResearchSession(
        request_id=request_id,
        query=query,
        molecule=molecule,
        indication=indication,
        status=status,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def save_agent_response(db: Session, session_id: int, agent_name: str, content: str, latency_ms: float = 0.0) -> AgentResponse:
    item = AgentResponse(
        session_id=session_id,
        agent_name=agent_name,
        content=content,
        latency_ms=latency_ms,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def save_report(db: Session, session_id: int, report_path: str, summary: str) -> Report:
    item = Report(session_id=session_id, report_path=report_path, summary=summary)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def save_uploaded_file(db: Session, filename: str, path: str, session_id: int | None = None) -> UploadedFile:
    item = UploadedFile(session_id=session_id, filename=filename, path=path)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_archive(db: Session, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    stmt = (
        select(ResearchSession, Report)
        .join(Report, Report.session_id == ResearchSession.id, isouter=True)
        .order_by(ResearchSession.id.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = db.execute(stmt).all()
    out: list[dict[str, Any]] = []
    for session, report in rows:
        out.append(
            {
                "id": session.request_id,
                "query": session.query,
                "molecule": session.molecule,
                "indication": session.indication,
                "timestamp": session.created_at.isoformat() if session.created_at else None,
                "status": session.status,
                "report_path": report.report_path if report else None,
            }
        )
    return out
