
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.auth import User, get_current_user


# Separate in-memory database for tests
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def override_session():
    with Session(test_engine) as session:
        yield session


def override_user():
    return User(
        id=1,
        email="test@example.com",
        hashed_password="test-only",
    )


def setup_function():
    SQLModel.metadata.create_all(test_engine)

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_current_user] = override_user


def teardown_function():
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(test_engine)


def test_ticket_lifecycle():
    with TestClient(app) as client:
        response = client.post(
            "/tickets",
            json={
                "customer_email": "customer@example.com",
                "subject": "Where is my order?",
                "message": "My parcel has not arrived yet.",
            },
        )

        assert response.status_code == 201

        ticket_id = response.json()["id"]

        response = client.get(f"/tickets/{ticket_id}")

        assert response.status_code == 200
        assert response.json()["id"] == ticket_id


def test_invalid_ticket():
    with TestClient(app) as client:
        response = client.post(
            "/tickets",
            json={
                "customer_email": "x",
                "subject": "a",
                "message": "hi",
            },
        )

        assert response.status_code == 422
