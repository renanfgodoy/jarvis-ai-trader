from __future__ import annotations

from app.connector.polarium.live_session.manager import PolariumLiveSessionManager

# Process-local live session foundation. The default source is intentionally
# unavailable until a safe authorized backend message source exists.
polarium_live_session_manager = PolariumLiveSessionManager()
