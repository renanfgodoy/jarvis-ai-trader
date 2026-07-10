from __future__ import annotations

import asyncio
import json
from typing import Any

from app.core.config import settings
from app.models.polarium_diagnostics import (
    DiagnosticCheck,
    DiagnosticSummaryResponse,
    OAuthDiagnosticResponse,
    StreamDiagnosticResponse,
    WebSocketDiagnosticRequest,
    WebSocketDiagnosticResponse,
)
from app.services.polarium_oauth_lab import PolariumOAuthLabService, create_code_challenge, create_code_verifier

EVENT_KEYS = (
    "marginal-balance",
    "balances",
    "subscription-balance-changed",
    "candle-generated",
    "digital-option-client-price-generated",
    "portfolio.get-history-positions",
)


def _status_from_checks(checks: list[DiagnosticCheck]) -> str:
    if any(check.status == "FAIL" for check in checks):
        return "FAIL"
    if any(check.status == "WARN" for check in checks):
        return "WARN"
    return "OK"


def _safe_preview(value: Any, limit: int = 260) -> str:
    try:
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    except Exception:
        text = str(value)
    return text[:limit] + ("..." if len(text) > limit else "")


class PolariumDiagnosticService:
    """Laboratório de diagnóstico da integração Polarium.

    Esta camada não promete conectar nem operar. Ela coleta evidências técnicas
    para sabermos exatamente onde a integração trava: config OAuth, callback,
    token, WebSocket ou stream de eventos.
    """

    def oauth(self) -> OAuthDiagnosticResponse:
        oauth = PolariumOAuthLabService()
        config = oauth.config()
        session = oauth.session()
        verifier = create_code_verifier()
        challenge = create_code_challenge(verifier)
        checks: list[DiagnosticCheck] = [
            DiagnosticCheck(
                name="PKCE",
                status="OK" if verifier and challenge else "FAIL",
                message="code_verifier/code_challenge gerados localmente.",
                detail={"challenge_method": "S256", "challenge_preview": challenge[:16] + "..."},
            ),
            DiagnosticCheck(
                name="Authorize URL",
                status="OK" if config.authorize_url_configured else "FAIL",
                message="URL de autorização mapeada." if config.authorize_url_configured else "URL de autorização ausente.",
                detail={"authorize_url": config.authorize_url},
            ),
            DiagnosticCheck(
                name="Token URL",
                status="OK" if config.token_url else "FAIL",
                message="URL de token mapeada." if config.token_url else "URL de token ausente.",
                detail={"token_url": config.token_url},
            ),
            DiagnosticCheck(
                name="Client ID",
                status="OK" if config.client_id_configured else "WARN",
                message="Client ID configurado." if config.client_id_configured else "Sem client_id próprio/autorizado. OAuth real deve ficar em SEM CONFIG.",
                detail={"client_id_configured": config.client_id_configured},
            ),
            DiagnosticCheck(
                name="Token Store",
                status="OK" if session.has_token else "WARN",
                message="Token armazenado localmente." if session.has_token else "Nenhum token próprio armazenado ainda.",
                detail={"session_status": session.status, "scope": session.scope},
            ),
        ]
        status = _status_from_checks(checks)
        return OAuthDiagnosticResponse(
            status=status,  # type: ignore[arg-type]
            checks=checks,
            next_action=(
                "Configurar POLARIUM_OAUTH_CLIENT_ID próprio/autorizado e testar Gerar URL de Login."
                if not config.client_id_configured
                else "Gerar URL de Login, fazer callback e testar troca por token em dry_run=false somente com credenciais próprias."
            ),
        )

    async def websocket(self, payload: WebSocketDiagnosticRequest) -> WebSocketDiagnosticResponse:
        ws_url = payload.ws_url or settings.polarium_ws_url
        checks: list[DiagnosticCheck] = [
            DiagnosticCheck(name="WS URL", status="OK" if ws_url else "FAIL", message="WebSocket URL configurada." if ws_url else "WebSocket URL ausente.", detail={"ws_url": ws_url}),
        ]
        if not ws_url:
            return WebSocketDiagnosticResponse(status="FAIL", ws_url="", connected=False, checks=checks, next_action="Configure POLARIUM_WS_URL no .env.")

        headers = []
        if payload.bearer_token:
            headers.append(("Authorization", f"Bearer {payload.bearer_token}"))

        try:
            import websockets  # type: ignore
        except Exception as exc:
            checks.append(DiagnosticCheck(name="WebSocket Library", status="FAIL", message="Biblioteca websockets indisponível.", detail={"error": str(exc)}))
            return WebSocketDiagnosticResponse(status="FAIL", ws_url=ws_url, connected=False, checks=checks, next_action="Instalar dependências com uvicorn[standard] ou websockets.")

        first_message = None
        close_code = None
        close_reason = None
        try:
            async with websockets.connect(ws_url, extra_headers=headers or None, open_timeout=payload.timeout_seconds, close_timeout=1) as ws:  # type: ignore[attr-defined]
                checks.append(DiagnosticCheck(name="Handshake", status="OK", message="WebSocket abriu conexão.", detail={"authenticated_header_sent": bool(payload.bearer_token)}))
                if payload.send_probe:
                    await ws.send(json.dumps({"name": "timeSync"}))
                try:
                    first_message = await asyncio.wait_for(ws.recv(), timeout=payload.timeout_seconds)
                    checks.append(DiagnosticCheck(name="First Message", status="OK", message="Primeira mensagem recebida.", detail={"preview": _safe_preview(first_message)}))
                except asyncio.TimeoutError:
                    checks.append(DiagnosticCheck(name="First Message", status="WARN", message="Conectou, mas nenhuma mensagem chegou dentro do timeout.", detail={"timeout_seconds": payload.timeout_seconds}))
                await ws.close()
                return WebSocketDiagnosticResponse(
                    status=_status_from_checks(checks),  # type: ignore[arg-type]
                    ws_url=ws_url,
                    connected=True,
                    first_message_preview=_safe_preview(first_message) if first_message is not None else None,
                    checks=checks,
                    next_action="Se conectou sem mensagens, testar com token OAuth próprio ou capturar quais mensagens de subscribe o navegador envia.",
                )
        except Exception as exc:  # network/remote dependent
            close_code = getattr(exc, "code", None)
            close_reason = getattr(exc, "reason", None)
            checks.append(DiagnosticCheck(name="Handshake", status="FAIL", message="WebSocket não abriu conexão.", detail={"error": str(exc), "close_code": close_code, "close_reason": close_reason}))
            return WebSocketDiagnosticResponse(
                status="FAIL",
                ws_url=ws_url,
                connected=False,
                close_code=close_code,
                close_reason=close_reason,
                checks=checks,
                next_action="Se falhar sem token, o próximo teste é abrir com access_token OAuth próprio. Se falhar com token, revisar protocolo/headers.",
            )

    def stream(self, payloads: list[dict[str, Any]]) -> StreamDiagnosticResponse:
        counters = {key: 0 for key in EVENT_KEYS}
        checks: list[DiagnosticCheck] = []
        for item in payloads:
            text = _safe_preview(item, limit=2000)
            name = str(item.get("name") or item.get("event") or item.get("type") or "")
            for key in EVENT_KEYS:
                if key in name or key in text:
                    counters[key] += 1
        balance = any(counters[key] for key in ["marginal-balance", "balances", "subscription-balance-changed"])
        candle = counters["candle-generated"] > 0
        price = counters["digital-option-client-price-generated"] > 0
        checks.append(DiagnosticCheck(name="Payloads recebidos", status="OK" if payloads else "WARN", message=f"{len(payloads)} payload(s) analisado(s).", detail={"total": len(payloads)}))
        checks.append(DiagnosticCheck(name="Balance Stream", status="OK" if balance else "WARN", message="Evento de saldo detectado." if balance else "Nenhum evento de saldo detectado.", detail={"balance_events": {k: counters[k] for k in ["marginal-balance", "balances", "subscription-balance-changed"]}}))
        checks.append(DiagnosticCheck(name="Candle Stream", status="OK" if candle else "WARN", message="Evento de candle detectado." if candle else "Nenhum evento candle-generated detectado.", detail={"candle-generated": counters["candle-generated"]}))
        checks.append(DiagnosticCheck(name="Price Stream", status="OK" if price else "WARN", message="Evento de preço detectado." if price else "Nenhum evento digital-option-client-price-generated detectado.", detail={"digital-option-client-price-generated": counters["digital-option-client-price-generated"]}))
        return StreamDiagnosticResponse(
            status=_status_from_checks(checks),  # type: ignore[arg-type]
            events_detected=counters,
            balance_payload_detected=balance,
            candle_payload_detected=candle,
            price_payload_detected=price,
            checks=checks,
            next_action="Use este resultado para confirmar quais eventos reais chegam antes de construir o conector automático.",
        )

    def summary(self) -> DiagnosticSummaryResponse:
        oauth_report = self.oauth()
        checks = [
            DiagnosticCheck(name="OAuth", status=oauth_report.status, message="Diagnóstico OAuth pronto.", detail={"checks": len(oauth_report.checks)}),
            DiagnosticCheck(name="WebSocket", status="SKIPPED", message="Rode o teste WebSocket no painel para coletar evidência real.", detail={}),
            DiagnosticCheck(name="Stream", status="SKIPPED", message="Cole payloads capturados para validar eventos marginal-balance/candle/price.", detail={}),
        ]
        return DiagnosticSummaryResponse(
            version=settings.app_version,
            status=_status_from_checks(checks),  # type: ignore[arg-type]
            checks=checks,
            next_action="Rodar OAuth Diagnostic, WebSocket Diagnostic e Stream Diagnostic antes de tentar novo conector.",
        )
