from typing import Tuple
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import User, ApiKey
from backend.app.auth import get_user_and_api_key_by_header
from backend.app.services.request_logger import log_api_request
from backend.app.schemas import CalculatorResponse

router = APIRouter(prefix="/api/calculator", tags=["Calculator API"])


@router.get("/add", response_model=CalculatorResponse)
def add(
    a: float = Query(..., description="First number"),
    b: float = Query(..., description="Second number"),
    user_auth: Tuple[User, ApiKey] = Depends(get_user_and_api_key_by_header),
    db: Session = Depends(get_db)
):
    user, api_key = user_auth
    result = a + b
    log_api_request(
        db=db,
        user_id=user.id,
        api_key_id=api_key.id,
        endpoint="/api/calculator/add",
        method="GET",
        status_code=200
    )
    return {
        "operation": "addition",
        "a": a,
        "b": b,
        "result": result
    }


@router.get("/subtract", response_model=CalculatorResponse)
def subtract(
    a: float = Query(..., description="First number"),
    b: float = Query(..., description="Second number"),
    user_auth: Tuple[User, ApiKey] = Depends(get_user_and_api_key_by_header),
    db: Session = Depends(get_db)
):
    user, api_key = user_auth
    result = a - b
    log_api_request(
        db=db,
        user_id=user.id,
        api_key_id=api_key.id,
        endpoint="/api/calculator/subtract",
        method="GET",
        status_code=200
    )
    return {
        "operation": "subtraction",
        "a": a,
        "b": b,
        "result": result
    }


@router.get("/multiply", response_model=CalculatorResponse)
def multiply(
    a: float = Query(..., description="First number"),
    b: float = Query(..., description="Second number"),
    user_auth: Tuple[User, ApiKey] = Depends(get_user_and_api_key_by_header),
    db: Session = Depends(get_db)
):
    user, api_key = user_auth
    result = a * b
    log_api_request(
        db=db,
        user_id=user.id,
        api_key_id=api_key.id,
        endpoint="/api/calculator/multiply",
        method="GET",
        status_code=200
    )
    return {
        "operation": "multiplication",
        "a": a,
        "b": b,
        "result": result
    }


@router.get("/divide", response_model=CalculatorResponse)
def divide(
    a: float = Query(..., description="Numerator"),
    b: float = Query(..., description="Denominator"),
    user_auth: Tuple[User, ApiKey] = Depends(get_user_and_api_key_by_header),
    db: Session = Depends(get_db)
):
    user, api_key = user_auth
    if b == 0:
        log_api_request(
            db=db,
            user_id=user.id,
            api_key_id=api_key.id,
            endpoint="/api/calculator/divide",
            method="GET",
            status_code=400
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Division by zero is not allowed"
        )

    result = a / b
    log_api_request(
        db=db,
        user_id=user.id,
        api_key_id=api_key.id,
        endpoint="/api/calculator/divide",
        method="GET",
        status_code=200
    )
    return {
        "operation": "division",
        "a": a,
        "b": b,
        "result": result
    }
