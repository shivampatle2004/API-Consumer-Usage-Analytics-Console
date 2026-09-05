from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import User, UserRole, ApiInfo, ApiKey
from backend.app.auth import verify_password, create_access_token, get_current_consumer_user
from backend.app.schemas import (
    LoginRequest,
    Token,
    UserResponse,
    ApiKeyResponse,
    ApiInfoResponse,
    ConsumerAnalytics
)
from backend.app.analytics import calculate_consumer_analytics

router = APIRouter(prefix="/api/consumer", tags=["API Consumer"])


@router.post("/login", response_model=Token)
def consumer_login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    if user.role != UserRole.CONSUMER.value and user.role != UserRole.SUPER_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Consumer credentials required"
        )

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username
    }


@router.get("/profile", response_model=UserResponse)
def get_profile(
    current_user: User = Depends(get_current_consumer_user)
):
    return current_user


@router.get("/apis", response_model=List[ApiInfoResponse])
def get_available_apis(
    current_user: User = Depends(get_current_consumer_user),
    db: Session = Depends(get_db)
):
    return db.query(ApiInfo).filter(ApiInfo.active == True).all()


@router.get("/api-key", response_model=ApiKeyResponse)
def get_my_api_key(
    current_user: User = Depends(get_current_consumer_user),
    db: Session = Depends(get_db)
):
    api_key_obj = db.query(ApiKey).filter(ApiKey.user_id == current_user.id, ApiKey.active == True).first()
    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active API key found for this user"
        )
    return api_key_obj


@router.get("/analytics", response_model=ConsumerAnalytics)
def get_my_analytics(
    current_user: User = Depends(get_current_consumer_user),
    db: Session = Depends(get_db)
):
    """
    Returns strict isolated analytics for the authenticated consumer.
    """
    return calculate_consumer_analytics(db=db, user=current_user)
