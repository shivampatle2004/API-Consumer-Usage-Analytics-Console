import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base, get_db
from backend.app.models import User, UserRole, ApiKey, ApiInfo
from backend.app.auth import hash_password
from backend.app.main_admin import app as admin_app
from backend.app.main_calculator import app as calculator_app
from backend.app.main_consumer import app as consumer_app

# Use in-memory SQLite with StaticPool so all connections share the same memory instance
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


admin_app.dependency_overrides[get_db] = override_get_db
calculator_app.dependency_overrides[get_db] = override_get_db
consumer_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # Seed Super Admin
        admin_user = User(
            username="admin",
            email="admin@apiprovider.internal",
            hashed_password=hash_password("admin123"),
            role=UserRole.SUPER_ADMIN.value,
            quota_limit=10000
        )
        db.add(admin_user)

        # Seed Consumer Alice
        alice_user = User(
            username="alice",
            email="alice@developer.internal",
            hashed_password=hash_password("alice123"),
            role=UserRole.CONSUMER.value,
            quota_limit=1000
        )
        db.add(alice_user)
        db.commit()
        db.refresh(alice_user)

        alice_key = ApiKey(
            user_id=alice_user.id,
            api_key="ak_alice_1234567890abcdef",
            active=True
        )
        db.add(alice_key)

        # Seed Consumer Bob
        bob_user = User(
            username="bob",
            email="bob@developer.internal",
            hashed_password=hash_password("bob123"),
            role=UserRole.CONSUMER.value,
            quota_limit=500
        )
        db.add(bob_user)
        db.commit()
        db.refresh(bob_user)

        bob_key = ApiKey(
            user_id=bob_user.id,
            api_key="ak_bob_9876543210fedcba",
            active=True
        )
        db.add(bob_key)

        # Seed Calculator API info
        calc_api = ApiInfo(
            name="Calculator API",
            description="Basic calculator operations.",
            base_url="http://localhost:8101",
            active=True
        )
        db.add(calc_api)
        db.commit()
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def admin_client():
    return TestClient(admin_app)


@pytest.fixture
def calculator_client():
    return TestClient(calculator_app)


@pytest.fixture
def consumer_client():
    return TestClient(consumer_app)
