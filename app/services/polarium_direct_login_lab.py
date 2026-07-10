import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from app.models.polarium_direct import (
    PolariumDirectConfig,
    PolariumDirectProbeResponse,
    PolariumDirectSessionState,
)

CACHE_DIR = Path(".jarvis_cache")
DIRECT_SESSION_FILE = CACHE_DIR / "polarium_direct_session.json"

DEFAULT_WS_URL = "wss://ws.trade.polariumbroker.com/echo/websocket"

SENSITIVE_KEYS = {"access_token", "refresh_token", "token", "id_token", "password", "authorization"}


def _mask(value: str | None, head: int = 8, tail: int = 4) -> str | None:
    if not value:
        return None
    if len(value) <= head + tail:
        return "***"
    return f"{value[:head]}...{value[-tail:]}"


def _safe_keys(payload: Any) -> list[str]:
    if isinstance(payload, dict):
        return sorted([str(key) for key in payload.keys()])
    return []


class PolariumDirectLoginLabService:
    """Laboratório de login direto da Polarium.

    Regras:
    - usa somente credenciais da conta do usuário em .env local;
    - não reutiliza tokens ou credenciais do TradeAutoPilot;
    - por padrão roda em dry_run;
    - AutoTrade deve permanecer bloqueado até DEMO + saldo + moeda reais serem confirmados.
    """

    def config(self) -> PolariumDirectConfig:
        login_url = os.getenv("POLARIUM_DIRECT_LOGIN_URL")
        email = os.getenv("POLARIUM_DIRECT_EMAIL")
        password = os.getenv("POLARIUM_DIRECT_PASSWORD")
        websocket_url = os.getenv("POLARIUM_DIRECT_WS_URL", DEFAULT_WS_URL)
        configured = bool(login_url and email and password)
        return PolariumDirectConfig(
            configured=configured,
            login_url_configured=bool(login_url),
            email_configured=bool(email),
            password_configured=bool(password),
            websocket_url_configured=bool(websocket_url),
            login_url=login_url,
            websocket_url=websocket_url,
            message=(
                "Direct Login Lab pronto para teste controlado."
                if configured
                else "Configure POLARIUM_DIRECT_LOGIN_URL, POLARIUM_DIRECT_EMAIL e POLARIUM_DIRECT_PASSWORD no .env local."
            ),
            safety_rules=[
                "Não comitar .env com senha.",
                "Não usar tokens ou credenciais do TradeAutoPilot.",
                "Testar apenas leitura de sessão/saldo DEMO.",
                "AutoTrade permanece bloqueado até conta DEMO ser confirmada.",
            ],
        )

    async def probe(self, dry_run: bool = True, force_demo: bool = True) -> PolariumDirectProbeResponse:
        cfg = self.config()
        if dry_run:
            return PolariumDirectProbeResponse(
                success=False,
                status="DRY_RUN" if cfg.configured else "MISSING_CONFIG",
                dry_run=True,
                message=(
                    "Dry run executado. Nenhum login real foi enviado. Desative dry_run apenas depois de configurar .env local."
                    if cfg.configured
                    else "Dry run: configuração incompleta."
                ),
                warnings=cfg.safety_rules,
            )

        if not cfg.configured:
            return PolariumDirectProbeResponse(
                success=False,
                status="MISSING_CONFIG",
                dry_run=False,
                message="Não é possível testar login direto: configuração incompleta no .env.",
                warnings=cfg.safety_rules,
            )

        payload = {
            "email": os.getenv("POLARIUM_DIRECT_EMAIL"),
            "password": os.getenv("POLARIUM_DIRECT_PASSWORD"),
        }
        headers = {
            "content-type": "application/json",
            "accept": "application/json",
            "user-agent": "JARVIS-AI-TRADER/0.20.2 direct-login-lab",
        }
        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=False) as client:
                response = await client.post(cfg.login_url or "", json=payload, headers=headers)
                content_type = response.headers.get("content-type", "")
                body: Any = response.json() if "json" in content_type else {"raw_preview": response.text[:200]}
        except Exception as exc:  # pragma: no cover - remote/network dependent
            return PolariumDirectProbeResponse(
                success=False,
                status="LOGIN_FAILED",
                dry_run=False,
                message=f"Falha de rede/login direto: {exc}",
                warnings=["Isso pode indicar endpoint incorreto, bloqueio por CORS/WAF ou necessidade de OAuth oficial."],
            )

        keys = _safe_keys(body)
        token_type = body.get("token_type") if isinstance(body, dict) else None
        token_present = isinstance(body, dict) and any(key in body for key in ("access_token", "token", "session", "refresh_token"))
        success = 200 <= response.status_code < 300 and token_present
        if success:
            self._write_session({
                "stored_at": datetime.now(timezone.utc).isoformat(),
                "http_status": response.status_code,
                "token_type": token_type,
                "response_keys": keys,
                # O token bruto fica somente no arquivo local do usuário; a API nunca expõe o valor.
                "raw": body,
                "force_demo": force_demo,
            })
            return PolariumDirectProbeResponse(
                success=True,
                status="SESSION_STORED",
                dry_run=False,
                token_stored=True,
                token_type=token_type,
                response_keys=keys,
                http_status=response.status_code,
                message="Sessão/tokens recebidos e armazenados localmente. Próximo passo: testar WebSocket autenticado e leitura de marginal-balance.",
                warnings=["Token bruto não é exposto no frontend.", "Validar DEMO antes de qualquer execução."],
            )

        status = "NOT_AUTHORIZED" if response.status_code in (401, 403) else "LOGIN_FAILED"
        return PolariumDirectProbeResponse(
            success=False,
            status=status,
            dry_run=False,
            token_stored=False,
            response_keys=keys,
            http_status=response.status_code,
            message=f"Login direto não retornou sessão utilizável. HTTP {response.status_code}.",
            warnings=[
                "Pode ser necessário usar OAuth/PKCE com client_id autorizado.",
                "Não tente usar credenciais de outro app.",
            ],
        )

    def session(self) -> PolariumDirectSessionState:
        session = self._read_session()
        if not session:
            cfg = self.config()
            return PolariumDirectSessionState(
                has_session=False,
                status="READY" if cfg.configured else "MISSING_CONFIG",
                message="Nenhuma sessão direta armazenada.",
                safety_rules=cfg.safety_rules,
            )
        return PolariumDirectSessionState(
            has_session=True,
            status="SESSION_STORED",
            token_type=session.get("token_type"),
            response_keys=session.get("response_keys", []),
            message="Sessão direta armazenada localmente. Token bruto não é exposto pela API.",
            safety_rules=["Validar DEMO antes de AutoTrade.", "Não exibir tokens no frontend."],
        )

    def logout(self) -> dict:
        if DIRECT_SESSION_FILE.exists():
            DIRECT_SESSION_FILE.unlink()
        return {"success": True, "message": "Sessão direta removida do cache local."}

    def _read_session(self) -> dict | None:
        if not DIRECT_SESSION_FILE.exists():
            return None
        try:
            return json.loads(DIRECT_SESSION_FILE.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _write_session(self, payload: dict) -> None:
        DIRECT_SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        DIRECT_SESSION_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
