import sys

from app.connector.polarium.websocket import recorder as _recorder

sys.modules[__name__] = _recorder
