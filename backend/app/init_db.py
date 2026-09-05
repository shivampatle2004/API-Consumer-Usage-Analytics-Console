from sqlalchemy.orm import Session
from backend.app.database import engine, Base, SessionLocal
from backend.app.models import User, UserRole, ApiKey, ApiInfo
from backend.app.auth import hash_password
from backend.app.config import settings


def init_db():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # 1. Super Admin
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@apiprovider.internal",
                hashed_password=hash_password("admin123"),
                role=UserRole.SUPER_ADMIN.value,
                quota_limit=10000
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

        # 2. Consumer Alice
        alice_user = db.query(User).filter(User.username == "alice").first()
        if not alice_user:
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
            db.commit()

        # 3. Consumer Bob
        bob_user = db.query(User).filter(User.username == "bob").first()
        if not bob_user:
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
            db.commit()

        # 4. Calculator API Record
        calc_api = db.query(ApiInfo).filter(ApiInfo.name == "Calculator API").first()
        if not calc_api:
            calc_api = ApiInfo(
                name="Calculator API",
                description="Basic calculator operations (add, subtract, multiply, divide).",
                base_url=settings.CALCULATOR_BASE_URL,
                active=True
            )
            db.add(calc_api)
            db.commit()
        else:
            calc_api.base_url = settings.CALCULATOR_BASE_URL
            db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized with demo data.")
