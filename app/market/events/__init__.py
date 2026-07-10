"""Passive Market Event Engine.

This package normalizes already-decoded, sanitized market messages. It does not
open sockets, call providers, or integrate with runtime connector flows.
"""

from app.market.events.router import route_market_event

__all__ = ["route_market_event"]
