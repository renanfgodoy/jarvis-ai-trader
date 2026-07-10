import base64
import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

import httpx

from app.core.config import settings

from app.models.polarium_oauth import (
    PolariumOAuthCallbackResponse,
    PolariumOAuthConfig,
    PolariumOAuthSessionState,
    PolariumOAuthTokenExchangeResponse,
    PolariumPkceStartResponse,
)

CACHE_DIR = Path(".jarvis_cache")
OAUTH_STATE_FILE = CACHE_DIR / "polarium_oauth_state.json"
OAUTH_TOKEN_FILE = CACHE_DIR / "polarium_oauth_token.json"

DEFAULT_AUTHORIZE_URL = "https://api.trade.polariumbroker.com/auth/oauth.v5/authorize"
DEFAULT_TOKEN_URL = "https://api.trade.polariumbroker.com/auth/oauth.v5/token"
DEFAULT_REDIRECT_URI = "http://127.0.0.1:8000/api/v1/polarium/oauth/callback"


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def create_code_verifier() -> str:
    return _b64url(secrets.token_bytes(64))


def create_code_challenge(verifier: str) -> str:
    return _b64url(hashlib.sha256(verifier.encode("ascii")).digest())


def _preview(value: str | None, head: int = 8, tail: int = 4) -> str | None:
    if not value:
        return None
    if len(value) <= head + tail:
        return value
    return f"{value[:head]}...{value[-tail:]}"


class PolariumOAuthLabService:
    """OAuth/PKCE Lab do J.A.R.V.I.S.

    Esta camada não reutiliza credenciais do TradeAutoPilot. Ela prepara o fluxo
    correto para credenciais próprias do J.A.R.V.I.S quando existirem.
    """

    def config(self) -> PolariumOAuthConfig:
        client_id = settings.polarium_oauth_client_id
        authorize_url = settings.polarium_oauth_authorize_url or DEFAULT_AUTHORIZE_URL
        token_url = settings.polarium_oauth_token_url or DEFAULT_TOKEN_URL
        redirect_uri = settings.polarium_oauth_redirect_uri or DEFAULT_REDIRECT_URI
        configured = bool(client_id and authorize_url and token_url and redirect_uri)
        return PolariumOAuthConfig(
            configured=configured,
            client_id_configured=bool(client_id),
            authorize_url_configured=bool(authorize_url),
            token_url_configured=bool(token_url),
            redirect_uri=redirect_uri,
            token_url=token_url,
            authorize_url=authorize_url,
            message=(
                "OAuth Session Engine configurado para iniciar conexão própria."
                if configured
                else "Configure POLARIUM_OAUTH_CLIENT_ID no .env. URLs authorize/token/redirect já possuem defaults mapeados."
            ),
        )

    def start(self, redirect_uri: str | None = None, scope: str = settings.polarium_oauth_scope, remember_verifier: bool = True) -> PolariumPkceStartResponse:
        verifier = create_code_verifier()
        challenge = create_code_challenge(verifier)
        state = secrets.token_urlsafe(24)
        cfg = self.config()
        final_redirect_uri = redirect_uri or cfg.redirect_uri
        client_id = settings.polarium_oauth_client_id
        authorize_url = cfg.authorize_url
        url = None
        warnings: list[str] = []

        if authorize_url and client_id:
            query = urlencode(
                {
                    "response_type": "code",
                    "client_id": client_id,
                    "redirect_uri": final_redirect_uri,
                    "scope": scope,
                    "state": state,
                    "code_challenge": challenge,
                    "max_age": "0",
                    "prompt": "login",
                    "code_challenge_method": "S256",
                }
            )
            separator = "&" if "?" in authorize_url else "?"
            url = f"{authorize_url}{separator}{query}"
            status = "READY"
            message = "URL OAuth/PKCE gerada. Abra no navegador para testar o fluxo próprio e receber callback local."
        else:
            status = "MISSING_CONFIG"
            message = "SEM CONFIG: falta POLARIUM_OAUTH_CLIENT_ID próprio/autorizado."
            warnings.append("Não reutilize client_id, redirect_uri, code_verifier ou tokens de outro app.")

        if remember_verifier:
            self._write_state({"state": state, "code_verifier": verifier, "redirect_uri": final_redirect_uri, "created_at": datetime.now(timezone.utc).isoformat()})

        return PolariumPkceStartResponse(
            ready=bool(url),
            status=status,
            state=state,
            code_verifier_preview=_preview(verifier) or "",
            code_challenge=challenge,
            redirect_uri=final_redirect_uri,
            authorize_url=url,
            message=message,
            warnings=warnings,
        )

    def callback(self, code: str | None, state: str | None, error: str | None = None) -> PolariumOAuthCallbackResponse:
        if error:
            return PolariumOAuthCallbackResponse(received=False, status="EXCHANGE_FAILED", state=state, message=f"OAuth retornou erro: {error}")
        if not code:
            return PolariumOAuthCallbackResponse(received=False, status="MISSING_CONFIG", state=state, message="Callback recebido sem code.")
        existing = self._read_state() or {}
        existing.update({"last_code_preview": _preview(code), "last_state": state, "callback_at": datetime.now(timezone.utc).isoformat()})
        self._write_state(existing)
        return PolariumOAuthCallbackResponse(
            received=True,
            status="CALLBACK_RECEIVED",
            code_preview=_preview(code),
            state=state,
            message="Code recebido. Use o painel OAuth Session para trocar o code por token com credenciais próprias.",
        )

    async def exchange(self, code: str, state: str | None, code_verifier: str | None, redirect_uri: str | None, dry_run: bool = True) -> PolariumOAuthTokenExchangeResponse:
        cfg = self.config()
        client_id = settings.polarium_oauth_client_id
        cached = self._read_state() or {}
        verifier = code_verifier or cached.get("code_verifier")
        final_redirect_uri = redirect_uri or cached.get("redirect_uri") or cfg.redirect_uri
        warnings: list[str] = []

        if dry_run:
            return PolariumOAuthTokenExchangeResponse(
                success=False,
                status="READY" if client_id and verifier else "MISSING_CONFIG",
                dry_run=True,
                message="Dry run: troca por token não executada. Desative dry_run somente com credenciais próprias configuradas.",
                warnings=["Modo seguro: nenhum token foi solicitado.", "Nunca use code/token de outro serviço."],
            )

        missing = []
        if not client_id:
            missing.append("POLARIUM_OAUTH_CLIENT_ID")
        if not cfg.token_url:
            missing.append("POLARIUM_OAUTH_TOKEN_URL")
        if not verifier:
            missing.append("code_verifier")
        if missing:
            return PolariumOAuthTokenExchangeResponse(
                success=False,
                status="MISSING_CONFIG",
                dry_run=False,
                message=f"Não foi possível trocar code por token. Faltando: {', '.join(missing)}.",
                warnings=["Configure credenciais próprias do J.A.R.V.I.S antes de tentar a troca real."],
            )

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": final_redirect_uri,
            "client_id": client_id,
            "code_verifier": verifier,
        }
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(cfg.token_url, json=payload)
                response.raise_for_status()
                token_payload = response.json()
        except Exception as exc:  # pragma: no cover - network/remote dependent
            return PolariumOAuthTokenExchangeResponse(
                success=False,
                status="EXCHANGE_FAILED",
                dry_run=False,
                message=f"Troca por token falhou: {exc}",
                warnings=["Isso pode indicar client_id não autorizado, redirect_uri diferente ou code expirado."],
            )

        self._write_token(token_payload)
        expires_in = token_payload.get("expires_in")
        return PolariumOAuthTokenExchangeResponse(
            success=True,
            status="TOKEN_STORED",
            dry_run=False,
            token_stored=True,
            token_type=token_payload.get("token_type"),
            expires_in=expires_in,
            scope=token_payload.get("scope"),
            message="Token recebido e armazenado localmente. Próximo passo: testar WebSocket autenticado.",
        )

    def session(self) -> PolariumOAuthSessionState:
        token = self._read_token()
        cfg = self.config()
        if not token:
            return PolariumOAuthSessionState(
                has_token=False,
                status="READY" if cfg.configured else "MISSING_CONFIG",
                message="Nenhum token próprio do J.A.R.V.I.S armazenado ainda.",
                safety_rules=["Não usar credenciais de outro app.", "Operação real bloqueada até conta DEMO ser confirmada."],
            )
        created_at = token.get("stored_at")
        expires_at = None
        if created_at and token.get("expires_in"):
            try:
                expires_at = datetime.fromisoformat(created_at) + timedelta(seconds=int(token["expires_in"]))
            except Exception:
                expires_at = None
        return PolariumOAuthSessionState(
            has_token=True,
            status="TOKEN_STORED",
            token_type=token.get("token_type"),
            expires_at=expires_at,
            scope=token.get("scope"),
            message="Token próprio armazenado. O token bruto não é exposto pela API.",
            safety_rules=["Validar DEMO antes de liberar AutoTrade.", "Nunca exibir ou logar access_token no frontend."],
        )

    def logout(self) -> dict:
        if OAUTH_TOKEN_FILE.exists():
            OAUTH_TOKEN_FILE.unlink()
        if OAUTH_STATE_FILE.exists():
            OAUTH_STATE_FILE.unlink()
        return {"success": True, "message": "OAuth Lab limpo: token/state removidos do cache local."}

    def _read_state(self) -> dict | None:
        return self._read_json(OAUTH_STATE_FILE)

    def _write_state(self, payload: dict) -> None:
        self._write_json(OAUTH_STATE_FILE, payload)

    def _read_token(self) -> dict | None:
        return self._read_json(OAUTH_TOKEN_FILE)

    def _write_token(self, payload: dict) -> None:
        safe_payload = dict(payload)
        safe_payload["stored_at"] = datetime.now(timezone.utc).isoformat()
        self._write_json(OAUTH_TOKEN_FILE, safe_payload)

    def _read_json(self, path: Path) -> dict | None:
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
