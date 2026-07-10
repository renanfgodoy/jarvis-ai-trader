import sys

from app.connector.polarium.parser import live_balance as _live_balance

sys.modules[__name__] = _live_balance
