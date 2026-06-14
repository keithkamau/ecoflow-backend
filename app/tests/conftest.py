import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.config import settings

SQLITE_URL = "sqlite:///./test_waste.db"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _make_token(user_id: str, role: str) -> str:
    from app.utils.security import create_access_token
    return create_access_token({"sub": user_id, "email": f"{role}@test.com", "role": role})


@pytest.fixture()
def seller_headers():
    token = _make_token("00000000-0000-0000-0000-000000000001", "seller")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def recycler_headers():
    token = _make_token("00000000-0000-0000-0000-000000000002", "recycler")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def recycler_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000002")


@pytest.fixture()
def transaction_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000099")
