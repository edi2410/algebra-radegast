import pytest
import os
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

# Set environment variables BEFORE any app imports
os.environ["SECRET_KEY"] = "testsecret"
os.environ["PROJECT_NAME"] = "TestApp"
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
os.environ["FIRST_SUPERUSER"] = "test@example.com"
os.environ["FIRST_SUPERUSER_PASSWORD"] = "testpass"
os.environ["POSTGRES_SERVER"] = "localhost"
os.environ["POSTGRES_USER"] = "test_user"
os.environ["POSTGRES_PASSWORD"] = "test_password"

# Now import app modules that depend on settings
from app.core.db import get_session
from app.main import app


@pytest.fixture(name="engine")
def engine_fixture():
    """Create a test database engine (SQLite in-memory)"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine):
    """Create a test database session"""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with dependency override"""

    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()