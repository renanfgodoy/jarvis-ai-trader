from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import parse_qs, urlparse

from app.models.polarium_session_inspector import (
    ClientStorageProbeRequest,
    ClientStorageProbeResponse,
    HarInspectRequest,
    HarInspectResponse,
    InspectorFinding,
)

SENSITIVE_KEYS = (
    "access_token",
    "refresh_token",
    "id_token",
    "token",
    "authorization",
    "cookie",
    "set-cookie",
    "password",
    "code",
    "code_verifier",
)

TOKEN_PATTERNS = (
    "access_token",
    "refresh_token",
    "Bearer ",
    "oauth.v5/token",
    "oauth.v5/authorize",
)

WS_HINTS = (
    "wss://",
    "websocket",
    "echo/websocket",
)


def _mask(value: Any) -> Any:
    if value is None:
        return None
    text = str(value)
    if len(text) <= 10:
        return "***"
    return f"{text[:4]}***{text[-4:]}"


def _maybe_redact_key(key: str, value: Any, redact: bool = True) -> Any:
    if not redact:
        return value
    if any(s in key.lower() for s in SENSITIVE_KEYS):
        return _mask(value)
    return value


def _safe_json(value: Any, limit: int = 900) -> str:
    try:
        text = json.dumps(value, ensure_ascii=False)
    except Exception:
        text = str(value)
    return text[:limit] + ("..." if len(text) > limit else "")


def _headers_to_dict(headers: list[dict[str, Any]] | None, redact: bool = True) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for item in headers or []:
        name = str(item.get("name", ""))
        value = item.get("value")
        out[name] = _maybe_redact_key(name, value, redact)
    return out


def _parse_post_data(post_data: dict[str, Any] | None) -> dict[str, Any]:
    if not post_data:
        return {}
    text = post_data.get("text")
    if not text:
        return {}
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
    try:
        return {k: v[0] if len(v) == 1 else v for k, v in parse_qs(text).items()}
    except Exception:
        return {"raw_preview": str(text)[:500]}


class PolariumSessionInspectorService:
    """Inspeciona HAR/armazenamento sem reutilizar tokens.

    Objetivo: descobrir evidências técnicas do fluxo real: authorize, token,
    WebSocket, headers, cookies e parâmetros do handshake. Não executa ordens,
    não reaproveita credenciais e mascara dados sensíveis por padrão.
    """

    def inspect_har(self, payload: HarInspectRequest) -> HarInspectResponse:
        log = payload.har.get("log", {}) if isinstance(payload.har, dict) else {}
        entries = log.get("entries", []) if isinstance(log, dict) else []
        findings: list[InspectorFinding] = []

        oauth_authorize = []
        oauth_token = []
        callbacks = []
        websockets = []
        bearer_headers = []
        cookie_auth = []
        code_verifiers = []
        client_ids = set()
        redirect_uris = set()
        scopes = set()
        ws_protocol_headers = []

        for index, entry in enumerate(entries):
            req = entry.get("request", {}) if isinstance(entry, dict) else {}
            res = entry.get("response", {}) if isinstance(entry, dict) else {}
            url = str(req.get("url", ""))
            method = str(req.get("method", ""))
            lower_url = url.lower()
            request_headers = req.get("headers", []) or []
            response_headers = res.get("headers", []) or []
            headers_dict_raw = {str(h.get("name", "")).lower(): str(h.get("value", "")) for h in request_headers if isinstance(h, dict)}
            post = _parse_post_data(req.get("postData"))

            if "oauth.v5/authorize" in lower_url:
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                oauth_authorize.append({
                    "index": index,
                    "method": method,
                    "url_base": f"{parsed.scheme}://{parsed.netloc}{parsed.path}",
                    "params": {k: _maybe_redact_key(k, v[0] if len(v) == 1 else v, payload.redact) for k, v in params.items()},
                })
                if "client_id" in params:
                    client_ids.add(params["client_id"][0])
                if "redirect_uri" in params:
                    redirect_uris.add(params["redirect_uri"][0])
                if "scope" in params:
                    scopes.add(params["scope"][0])

            if "callback" in lower_url and "code=" in lower_url:
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                callbacks.append({
                    "index": index,
                    "url_base": f"{parsed.scheme}://{parsed.netloc}{parsed.path}",
                    "has_code": "code" in params,
                    "has_state": "state" in params,
                })

            if "oauth.v5/token" in lower_url:
                token_post = {k: _maybe_redact_key(k, v, payload.redact) for k, v in post.items()}
                oauth_token.append({
                    "index": index,
                    "method": method,
                    "url": url,
                    "status": res.get("status"),
                    "post_keys": list(post.keys()),
                    "post_preview": token_post,
                })
                if "client_id" in post:
                    client_ids.add(str(post.get("client_id")))
                if "redirect_uri" in post:
                    redirect_uris.add(str(post.get("redirect_uri")))
                if "code_verifier" in post:
                    code_verifiers.append({"index": index, "present": True, "preview": _mask(post.get("code_verifier"))})

            if url.startswith("wss://") or "websocket" in lower_url:
                header_safe = _headers_to_dict(request_headers, redact=True)
                websockets.append({
                    "index": index,
                    "url": url,
                    "status": res.get("status"),
                    "headers": {k: header_safe.get(k) for k in header_safe if k.lower() in ["origin", "authorization", "cookie", "sec-websocket-protocol", "user-agent"]},
                })
                if "sec-websocket-protocol" in headers_dict_raw:
                    ws_protocol_headers.append({"index": index, "value": _mask(headers_dict_raw["sec-websocket-protocol"])})

            auth_header = headers_dict_raw.get("authorization")
            if auth_header:
                bearer_headers.append({"index": index, "url": url[:120], "authorization": _mask(auth_header)})
            cookie_header = headers_dict_raw.get("cookie")
            if cookie_header and any(word in cookie_header.lower() for word in ["auth", "token", "session", "ssid", "access"]):
                cookie_auth.append({"index": index, "url": url[:120], "cookie_preview": _mask(cookie_header)})

        findings.append(InspectorFinding(
            name="OAuth Authorize",
            status="OK" if oauth_authorize else "WARN",
            message="URL /authorize encontrada." if oauth_authorize else "Nenhuma URL /authorize encontrada no HAR.",
            detail={"count": len(oauth_authorize), "items": oauth_authorize[:3]},
        ))
        findings.append(InspectorFinding(
            name="OAuth Token Exchange",
            status="OK" if oauth_token else "WARN",
            message="POST /token encontrado." if oauth_token else "Nenhum POST /token encontrado no HAR.",
            detail={"count": len(oauth_token), "items": oauth_token[:3]},
        ))
        findings.append(InspectorFinding(
            name="Callback com code/state",
            status="OK" if callbacks else "WARN",
            message="Callback com code/state detectado." if callbacks else "Callback OAuth não encontrado.",
            detail={"count": len(callbacks), "items": callbacks[:5]},
        ))
        findings.append(InspectorFinding(
            name="Client/Redirect/Scope",
            status="OK" if client_ids or redirect_uris else "WARN",
            message="Parâmetros OAuth identificados." if client_ids or redirect_uris else "Parâmetros OAuth não identificados.",
            detail={
                "client_ids_masked": [_mask(x) for x in sorted(client_ids)],
                "redirect_uris": sorted(redirect_uris),
                "scopes": sorted(scopes),
                "code_verifier_detected": bool(code_verifiers),
            },
        ))
        findings.append(InspectorFinding(
            name="WebSocket Handshake",
            status="OK" if websockets else "WARN",
            message="WebSocket encontrado no HAR." if websockets else "Nenhum WebSocket encontrado no HAR.",
            detail={"count": len(websockets), "items": websockets[:3], "protocol_headers": ws_protocol_headers[:3]},
        ))
        findings.append(InspectorFinding(
            name="Authorization Header",
            status="OK" if bearer_headers else "WARN",
            message="Headers Authorization detectados." if bearer_headers else "Nenhum Authorization header detectado.",
            detail={"count": len(bearer_headers), "items": bearer_headers[:5]},
        ))
        findings.append(InspectorFinding(
            name="Cookie Session/Auth",
            status="OK" if cookie_auth else "WARN",
            message="Cookies com indícios de sessão/auth detectados." if cookie_auth else "Nenhum cookie de sessão/auth claramente detectado.",
            detail={"count": len(cookie_auth), "items": cookie_auth[:5]},
        ))

        status = "OK" if oauth_token and websockets else "WARN"
        next_action = "Se OAuth token e WebSocket apareceram, compare headers do WebSocket com o token OAuth para descobrir se usa Bearer, cookie ou mensagem de autenticação pós-conexão."
        if not oauth_token:
            next_action = "Capture o HAR começando antes de clicar em Conectar Polarium até voltar do callback, preservando logs."
        elif not websockets:
            next_action = "Capture a etapa dentro da traderoom/robô após login, aguardando abrir WebSocket."

        return HarInspectResponse(
            status=status,  # type: ignore[arg-type]
            total_entries=len(entries),
            oauth_authorize_found=bool(oauth_authorize),
            oauth_token_found=bool(oauth_token),
            websocket_found=bool(websockets),
            bearer_found=bool(bearer_headers),
            cookie_auth_found=bool(cookie_auth),
            findings=findings,
            next_action=next_action,
        )

    def probe_client_storage(self, payload: ClientStorageProbeRequest) -> ClientStorageProbeResponse:
        findings: list[InspectorFinding] = []
        token_like_local = [k for k in payload.local_storage_keys if re.search(r"token|auth|session|jwt|bearer|oauth", k, re.I)]
        token_like_session = [k for k in payload.session_storage_keys if re.search(r"token|auth|session|jwt|bearer|oauth", k, re.I)]
        token_like_cookie = [k for k in payload.cookie_names if re.search(r"token|auth|session|jwt|bearer|oauth|ssid", k, re.I)]
        findings.append(InspectorFinding(name="LocalStorage", status="OK" if token_like_local else "WARN", message="Chaves suspeitas encontradas." if token_like_local else "Nenhuma chave suspeita no origin atual.", detail={"origin": payload.origin, "suspect_keys": token_like_local, "total_keys": len(payload.local_storage_keys)}))
        findings.append(InspectorFinding(name="SessionStorage", status="OK" if token_like_session else "WARN", message="Chaves suspeitas encontradas." if token_like_session else "Nenhuma chave suspeita no origin atual.", detail={"origin": payload.origin, "suspect_keys": token_like_session, "total_keys": len(payload.session_storage_keys)}))
        findings.append(InspectorFinding(name="Cookies acessíveis por JS", status="OK" if token_like_cookie else "WARN", message="Cookies suspeitos acessíveis por JS." if token_like_cookie else "Nenhum cookie suspeito acessível por JS. Cookies HttpOnly não aparecem aqui.", detail={"origin": payload.origin, "suspect_names": token_like_cookie, "total_cookies": len(payload.cookie_names)}))
        return ClientStorageProbeResponse(
            status="OK" if any([token_like_local, token_like_session, token_like_cookie]) else "WARN",  # type: ignore[arg-type]
            findings=findings,
            next_action="Se nada aparecer aqui, é provável que a sessão crítica esteja em cookie HttpOnly ou no backend do app, não no JavaScript do dashboard.",
        )
