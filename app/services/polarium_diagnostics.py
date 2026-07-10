import sys

from app.connector.polarium.diagnostics import service as _service

sys.modules[__name__] = _service
