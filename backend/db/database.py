from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.config import DATABASE_URL

DEFAULT_DB_URL = "sqlite:///./backend/archives/research.db"

engine = create_engine(DATABASE_URL or DEFAULT_DB_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()
