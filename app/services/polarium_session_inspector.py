import sys

from app.connector.polarium.diagnostics import session_inspector as _session_inspector

sys.modules[__name__] = _session_inspector
