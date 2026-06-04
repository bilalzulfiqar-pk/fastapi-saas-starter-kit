from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db.session import get_session
from app.main import app
from app.modules.billing.models import Plan


@pytest.fixture
def session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.add_all(
            [
                Plan(name="Free", slug="free", price_monthly=0, price_yearly=0, features_json={}, limits_json={}),
                Plan(name="Pro", slug="pro", price_monthly=2900, price_yearly=29000, features_json={}, limits_json={}),
                Plan(name="Business", slug="business", price_monthly=9900, price_yearly=99000, features_json={}, limits_json={}),
            ]
        )
        session.commit()
        yield session


@pytest.fixture
def client(session: Session) -> Generator[TestClient, None, None]:
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def auth_headers(origin: str = "http://localhost:3000") -> dict[str, str]:
    return {"origin": origin}
