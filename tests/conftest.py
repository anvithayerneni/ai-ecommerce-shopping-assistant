import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import TEST_DATABASE_URL
from app.db.base import Base
from app.db.session import get_db
from app.main import app


@pytest.fixture
def test_db() -> Session:
    engine = create_engine(TEST_DATABASE_URL)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(test_db):
    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(
        app,
        raise_server_exceptions=False,
)   as test_client:
        yield test_client

    app.dependency_overrides.clear()