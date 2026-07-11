from __future__ import annotations

from app.connector.polarium.live_session.models import LiveSessionStatus


def to_sanitized_status(status: LiveSessionStatus) -> dict:
    return status.sanitized()
