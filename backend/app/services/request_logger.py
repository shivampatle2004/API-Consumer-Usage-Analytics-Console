from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models import ApiRequestLog


def log_api_request(
    db: Session,
    user_id: int,
    endpoint: str,
    method: str,
    status_code: int,
    api_key_id: Optional[int] = None
) -> ApiRequestLog:
    """
    Persists a request log entry into the SQLite database.
    """
    log_entry = ApiRequestLog(
        user_id=user_id,
        api_key_id=api_key_id,
        endpoint=endpoint,
        method=method.upper(),
        status_code=status_code,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
