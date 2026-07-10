import sys

from app.connector.polarium.session import connector as _connector

sys.modules[__name__] = _connector
