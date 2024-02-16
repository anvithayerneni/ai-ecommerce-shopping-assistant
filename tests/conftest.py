import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import TEST_DATABASE_URL
from app.db.base import Base


@pytest.fixture
def test_db() -> Session:
    engine = create_engine(TEST_DATABASE_URL)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(bind=engine)
    engine.dispose()