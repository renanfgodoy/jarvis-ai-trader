from __future__ import annotations

from app.connector.polarium.live_session.manager import PolariumLiveSessionManager
from app.connector.polarium.live_session.sources.authorized_source import AuthorizedPolariumMessageSource

# Process-local live session foundation. The default source is intentionally
# blocked until the real WebSocket authentication sequence is proven.
polarium_live_session_manager = PolariumLiveSessionManager(message_source=AuthorizedPolariumMessageSource())
