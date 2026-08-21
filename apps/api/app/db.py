"""SQLAlchemy engine and session helpers (SQLite for prototype; PG-portable)."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Declarative base for future ORM models. No domain tables in v0.1-skeleton."""


def _sqlite_connect_args(url: str) -> dict[str, object]:
    if url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def create_db_engine(database_url: str | None = None) -> Engine:
    settings = get_settings()
    url = database_url or settings.database_url
    return create_engine(
        url,
        connect_args=_sqlite_connect_args(url),
        future=True,
    )


engine = create_db_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database(db_engine: Engine | None = None) -> bool:
    """Return True when a simple connection/ping succeeds."""
    target = db_engine or engine
    try:
        with target.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
