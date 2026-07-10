from __future__ import annotations

import json
import re
from typing import Any

from app.models.polarium_ws_recorder import (
    WsFrameInput,
    WsMessageSummary,
    WsRecorderConsoleSnippetResponse,
    WsRecorderFinding,
    WsRecordingResponse,
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
    "ssid",
    "session",
)

AUTH_HINTS = (
    "authenticate",
    "authorization",
    "auth",
    "token",
    "ssid",
    "profile",
    "user.get",
    "set-user",
    "login",
    "oauth",
)

BALANCE_HINTS = (
    "marginal-balance",
    "balances",
    "balance",
    "subscription-balance-changed",
    "portfolio",
)

CANDLE_HINTS = (
    "candle-generated",
    "candles",
    "candle",
)

PRICE_HINTS = (
    "digital-option-client-price-generated",
    "price-generated",
    "quote-generated",
    "price",
    "quote",
)


def _mask(value: Any) -> Any:
    if value is None:
        return None
    text = str(value)
    if len(text) <= 10:
        return "***"
    return f"{text[:4]}***{text[-4:]}"


def _redact(value: Any, redact: bool = True) -> Any:
    if not redact:
        return value
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if any(s in str(key).lower() for s in SENSITIVE_KEYS):
                out[str(key)] = _mask(item)
            else:
                out[str(key)] = _redact(item, redact)
        return out
    if isinstance(value, list):
        return [_redact(item, redact) for item in value[:20]]
    return value


def _safe_preview(data: Any, redact: bool = True) -> dict[str, Any]:
    if isinstance(data, dict):
        allowed = {k: data.get(k) for k in ["name", "request_id", "status", "microserviceName"] if k in data}
        msg = data.get("msg")
        if isinstance(msg, dict):
            allowed["msg_keys"] = list(msg.keys())[:20]
            nested_name = msg.get("name")
            if nested_name:
                allowed["msg_name"] = nested_name
            body = msg.get("body")
            if isinstance(body, dict):
                allowed["body_keys"] = list(body.keys())[:20]
        elif isinstance(msg, list):
            allowed["msg_list_len"] = len(msg)
            if msg and isinstance(msg[0], dict):
                allowed["first_msg_keys"] = list(msg[0].keys())[:20]
        return _redact(allowed, redact)
    return {"raw": str(data)[:300]}


def _text_of(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False).lower()
    except Exception:
        return str(value).lower()


def _extract_json_objects(raw: str) -> tuple[list[Any], int]:
    messages: list[Any] = []
    total_lines = 0
    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        total_lines += 1
        # DevTools sometimes includes direction arrows, timestamps or copied columns before JSON.
        json_start_candidates = [idx for idx in [line.find("{"), line.find("[")] if idx >= 0]
        if json_start_candidates:
            line = line[min(json_start_candidates):]
        # Remove trailing DevTools metadata after a JSON object in the same row.
        parsed = None
        for end in range(len(line), max(0, len(line) - 1200), -1):
            candidate = line[:end].strip()
            if not candidate:
                continue
            try:
                parsed = json.loads(candidate)
                break
            except Exception:
                continue
        if parsed is None:
            try:
                parsed = json.loads(line)
            except Exception:
                continue
        if isinstance(parsed, list):
            messages.extend(parsed)
        else:
            messages.append(parsed)
    return messages, total_lines


class PolariumWsRecorderService:
    """Analisa mensagens copiadas do WebSocket do DevTools.

    Não conecta em corretora, não reutiliza token e não executa ordens. O objetivo é
    mapear a sequência real de mensagens após o handshake: auth, subscriptions,
    balance, candles e prices.
    """

    def analyze_frames(self, payload: WsFrameInput) -> WsRecordingResponse:
        messages, total_lines = _extract_json_objects(payload.raw)
        summaries: list[WsMessageSummary] = []
        detected: dict[str, int] = {}

        for index, message in enumerate(messages):
            if not isinstance(message, dict):
                continue
            msg = message.get("msg")
            name = message.get("name")
            micro = message.get("microserviceName")
            request_id = message.get("request_id")
            active_id = None
            if isinstance(msg, dict):
                micro = micro or msg.get("microserviceName")
                body = msg.get("body")
                active_id = msg.get("active_id") if isinstance(msg.get("active_id"), int) else None
                if active_id is None and isinstance(body, dict) and isinstance(body.get("active_id"), int):
                    active_id = body.get("active_id")
            text = _text_of(message)
            for hint in [*(AUTH_HINTS), *(BALANCE_HINTS), *(CANDLE_HINTS), *(PRICE_HINTS)]:
                if hint in text:
                    detected[hint] = detected.get(hint, 0) + 1
            summary = WsMessageSummary(
                index=index,
                direction="CLIENT_OR_SERVER",
                name=str(name) if name is not None else None,
                microservice_name=str(micro) if micro is not None else None,
                request_id=str(request_id) if request_id is not None else None,
                active_id=active_id,
                has_balance=any(h in text for h in BALANCE_HINTS),
                has_candle=any(h in text for h in CANDLE_HINTS),
                has_price=any(h in text for h in PRICE_HINTS),
                has_auth_hint=any(h in text for h in AUTH_HINTS),
                preview=_safe_preview(message, payload.redact),
            )
            summaries.append(summary)

        auth = [item for item in summaries if item.has_auth_hint]
        balance = [item for item in summaries if item.has_balance]
        candle = [item for item in summaries if item.has_candle]
        price = [item for item in summaries if item.has_price]

        findings: list[WsRecorderFinding] = [
            WsRecorderFinding(
                name="Frames parseados",
                status="OK" if summaries else "WARN",
                message=f"{len(summaries)} mensagens JSON reconhecidas." if summaries else "Nenhuma mensagem JSON reconhecida. Copie as linhas da aba Messages/Frames.",
                detail={"total_lines": total_lines, "parsed_messages": len(summaries)},
            ),
            WsRecorderFinding(
                name="Auth candidates",
                status="OK" if auth else "WARN",
                message="Possíveis mensagens de autenticação/sessão detectadas." if auth else "Nenhuma mensagem com indício de autenticação detectada.",
                detail={"count": len(auth), "items": [item.model_dump() for item in auth[:5]]},
            ),
            WsRecorderFinding(
                name="Balance stream",
                status="OK" if balance else "WARN",
                message="Mensagens de saldo/portfolio detectadas." if balance else "Nenhuma mensagem de saldo detectada.",
                detail={"count": len(balance), "items": [item.model_dump() for item in balance[:5]]},
            ),
            WsRecorderFinding(
                name="Candle stream",
                status="OK" if candle else "WARN",
                message="Mensagens de candle detectadas." if candle else "Nenhuma mensagem de candle detectada.",
                detail={"count": len(candle), "items": [item.model_dump() for item in candle[:5]]},
            ),
            WsRecorderFinding(
                name="Price stream",
                status="OK" if price else "WARN",
                message="Mensagens de preço detectadas." if price else "Nenhuma mensagem de preço detectada.",
                detail={"count": len(price), "items": [item.model_dump() for item in price[:5]]},
            ),
        ]

        status = "OK" if balance and candle and price else "WARN"
        next_action = "Capture os primeiros 20 frames logo após abrir o WebSocket e cole aqui; precisamos ver a primeira mensagem de auth/subscribe."
        if auth and balance:
            next_action = "Compare os primeiros auth candidates com as mensagens de subscribe; próximo passo é criar adapter somente leitura baseado nessa sequência."
        elif not summaries:
            next_action = "No DevTools, clique no websocket 101 > Messages/Frames, selecione as linhas e copie como texto."

        return WsRecordingResponse(
            status=status,  # type: ignore[arg-type]
            total_lines=total_lines,
            parsed_messages=len(summaries),
            detected_events=detected,
            first_messages=summaries[:12],
            auth_candidates=auth[:10],
            balance_candidates=balance[:10],
            candle_candidates=candle[:10],
            price_candidates=price[:10],
            findings=findings,
            next_action=next_action,
        )

    def console_snippet(self) -> WsRecorderConsoleSnippetResponse:
        snippet = r'''(() => {
  if (window.__JARVIS_WS_RECORDER__) {
    console.log('JARVIS WS Recorder já está ativo. Use window.__JARVIS_WS_RECORDER__.dump()');
    return;
  }
  const OriginalWebSocket = window.WebSocket;
  const frames = [];
  function safePush(item) {
    frames.push({ ...item, at: new Date().toISOString() });
    if (frames.length > 500) frames.shift();
  }
  window.WebSocket = function(url, protocols) {
    const ws = protocols ? new OriginalWebSocket(url, protocols) : new OriginalWebSocket(url);
    safePush({ type: 'open-attempt', url: String(url), protocols: protocols || null });
    ws.addEventListener('open', () => safePush({ type: 'open', url: String(url) }));
    ws.addEventListener('close', (event) => safePush({ type: 'close', url: String(url), code: event.code, reason: event.reason }));
    ws.addEventListener('message', (event) => safePush({ type: 'incoming', url: String(url), data: String(event.data).slice(0, 4000) }));
    const originalSend = ws.send.bind(ws);
    ws.send = (data) => {
      safePush({ type: 'outgoing', url: String(url), data: String(data).slice(0, 4000) });
      return originalSend(data);
    };
    return ws;
  };
  window.WebSocket.prototype = OriginalWebSocket.prototype;
  window.__JARVIS_WS_RECORDER__ = {
    frames,
    dump() { console.log(JSON.stringify(frames, null, 2)); return frames; },
    clear() { frames.length = 0; console.log('JARVIS WS Recorder limpo.'); },
  };
  console.log('JARVIS WS Recorder ativo. Recarregue a página, faça login/conexão e depois rode: window.__JARVIS_WS_RECORDER__.dump()');
})();'''
        return WsRecorderConsoleSnippetResponse(
            title="J.A.R.V.I.S WS Session Recorder Snippet",
            warning="Use apenas na sua sessão. O snippet registra frames localmente no console; pode capturar tokens. Não compartilhe a saída sem revisar.",
            snippet=snippet,
        )
