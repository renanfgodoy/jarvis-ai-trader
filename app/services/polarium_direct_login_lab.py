import sys

from app.connector.polarium.diagnostics import direct_login_lab as _direct_login_lab

sys.modules[__name__] = _direct_login_lab
