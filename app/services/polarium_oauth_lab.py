import sys

from app.connector.polarium.oauth import lab as _lab

sys.modules[__name__] = _lab
