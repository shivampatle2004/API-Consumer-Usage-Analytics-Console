from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.models import User, ApiRequestLog, ApiKey
from backend.app.schemas import ConsumerAnalytics, ApiRequestLogResponse, AdminConsumerCard


def calculate_consumer_analytics(db: Session, user: User, limit_logs: int = 50) -> ConsumerAnalytics:
    """
    Computes accurate analytics according to the specification:
    - total_requests = count of requests by consumer
    - used = total_requests
    - remaining = max(0, quota_limit - used)
    - usage_percentage = (used / quota_limit) * 100
    - failed_requests = count where status_code >= 400
    - successful_requests = total_requests - failed_requests
    - error_rate = (failed_requests / total_requests) * 100 (0% if 0 requests)
    """
    logs = (
        db.query(ApiRequestLog)
        .filter(ApiRequestLog.user_id == user.id)
        .order_by(desc(ApiRequestLog.timestamp))
        .all()
    )

    total_requests = len(logs)
    quota_limit = user.quota_limit if user.quota_limit is not None else 1000
    used = total_requests
    remaining = max(0, quota_limit - used)
    usage_percentage = round((used / quota_limit * 100), 2) if quota_limit > 0 else 0.0

    failed_requests = sum(1 for log in logs if log.status_code >= 400)
    successful_requests = total_requests - failed_requests
    error_rate = round((failed_requests / total_requests * 100), 2) if total_requests > 0 else 0.0

    recent_logs = [
        ApiRequestLogResponse(
            id=log.id,
            user_id=log.user_id,
            endpoint=log.endpoint,
            method=log.method,
            status_code=log.status_code,
            timestamp=log.timestamp,
            username=user.username
        )
        for log in logs[:limit_logs]
    ]

    return ConsumerAnalytics(
        username=user.username,
        quota_limit=quota_limit,
        total_requests=total_requests,
        used=used,
        remaining=remaining,
        usage_percentage=usage_percentage,
        successful_requests=successful_requests,
        failed_requests=failed_requests,
        error_rate=error_rate,
        recent_logs=recent_logs
    )


def get_admin_consumers_summary(db: Session) -> List[AdminConsumerCard]:
    """
    Returns summary analytics for all registered consumers for Super Admin.
    """
    consumers = db.query(User).filter(User.role == "CONSUMER").all()
    cards = []

    for consumer in consumers:
        api_key_obj = db.query(ApiKey).filter(ApiKey.user_id == consumer.id, ApiKey.active == True).first()
        api_key_str = api_key_obj.api_key if api_key_obj else "No active key"

        logs = db.query(ApiRequestLog).filter(ApiRequestLog.user_id == consumer.id).all()
        total_requests = len(logs)
        quota_limit = consumer.quota_limit if consumer.quota_limit is not None else 1000
        requests_used = total_requests
        remaining = max(0, quota_limit - requests_used)

        failed_requests = sum(1 for log in logs if log.status_code >= 400)
        successful_requests = total_requests - failed_requests
        error_rate = round((failed_requests / total_requests * 100), 2) if total_requests > 0 else 0.0

        cards.append(
            AdminConsumerCard(
                id=consumer.id,
                username=consumer.username,
                email=consumer.email,
                api_key=api_key_str,
                quota_limit=quota_limit,
                requests_used=requests_used,
                remaining=remaining,
                error_rate=error_rate,
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                active=True
            )
        )
    return cards
