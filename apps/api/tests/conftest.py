"""Shared pytest fixtures for the FastAPI foundation."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from app.config import get_settings
from app.db import Base
from app.main import create_app
from app.services.case_service import reset_platform_state


@pytest.fixture(autouse=True)
def _clear_settings_caches() -> Generator[None, None, None]:
    get_settings.cache_clear()
    try:
        from app.adapters.price.factory import get_live_price_adapter

        get_live_price_adapter.cache_clear()
    except Exception:
        pass
    yield
    get_settings.cache_clear()
    try:
        from app.adapters.price.factory import get_live_price_adapter

        get_live_price_adapter.cache_clear()
    except Exception:
        pass


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    db_path = tmp_path / "test.db"
    url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    get_settings.cache_clear()
    reset_platform_state()

    import app.db as db_module

    engine = create_engine(url, connect_args={"check_same_thread": False}, future=True)
    Base.metadata.create_all(bind=engine)
    db_module.engine = engine
    db_module.SessionLocal.configure(bind=engine)

    application = create_app()
    with TestClient(application) as test_client:
        yield test_client

    get_settings.cache_clear()
    reset_platform_state()
