from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.database import get_db
from backend.app.models import User, UserRole, ApiInfo, ApiRequestLog, ApiKey
from backend.app.auth import verify_password, create_access_token, get_current_admin
from backend.app.schemas import (
    LoginRequest,
    Token,
    ApiInfoResponse,
    AdminConsumerCard,
    ApiRequestLogResponse
)
from backend.app.analytics import get_admin_consumers_summary

router = APIRouter(prefix="/api/admin", tags=["Super Admin"])


@router.post("/login", response_model=Token)
def admin_login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    if user.role != UserRole.SUPER_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Super Admin credentials required"
        )

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username
    }


@router.get("/apis", response_model=List[ApiInfoResponse])
def list_apis(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return db.query(ApiInfo).all()


@router.get("/consumers", response_model=List[AdminConsumerCard])
def list_consumers(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return get_admin_consumers_summary(db)


@router.get("/logs", response_model=List[ApiRequestLogResponse])
def list_all_logs(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    limit: int = 100
):
    logs = (
        db.query(ApiRequestLog)
        .order_by(desc(ApiRequestLog.timestamp))
        .limit(limit)
        .all()
    )
    result = []
    for log in logs:
        consumer = db.query(User).filter(User.id == log.user_id).first()
        result.append(
            ApiRequestLogResponse(
                id=log.id,
                user_id=log.user_id,
                endpoint=log.endpoint,
                method=log.method,
                status_code=log.status_code,
                timestamp=log.timestamp,
                username=consumer.username if consumer else "Unknown"
            )
        )
    return result
