from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class UserBase(BaseModel):
    username: str
    email: str
    role: str = "CONSUMER"
    quota_limit: int = 1000


class UserResponse(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ApiKeyResponse(BaseModel):
    id: int
    api_key: str
    active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ApiInfoResponse(BaseModel):
    id: int
    name: str
    description: str
    base_url: str
    active: bool
    model_config = ConfigDict(from_attributes=True)


class ApiRequestLogResponse(BaseModel):
    id: int
    user_id: int
    endpoint: str
    method: str
    status_code: int
    timestamp: datetime
    username: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class CalculatorResponse(BaseModel):
    operation: str
    a: float
    b: float
    result: float


class ConsumerAnalytics(BaseModel):
    username: str
    quota_limit: int
    total_requests: int
    used: int
    remaining: int
    usage_percentage: float
    successful_requests: int
    failed_requests: int
    error_rate: float
    recent_logs: List[ApiRequestLogResponse] = []


class AdminConsumerCard(BaseModel):
    id: int
    username: str
    email: str
    api_key: str
    quota_limit: int
    requests_used: int
    remaining: int
    error_rate: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    active: bool
