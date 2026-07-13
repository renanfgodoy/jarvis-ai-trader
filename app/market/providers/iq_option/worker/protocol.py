from __future__ import annotations

import json
from typing import Any

from app.market.providers.iq_option.worker.errors import IQOptionWorkerInvalidJSON, IQOptionWorkerRejectedCommand
from app.market.providers.iq_option.worker.models import WorkerRequest, WorkerResponse

ALLOWED_COMMANDS = {
    "status",
    "connect",
    "list_assets",
    "list_otc_assets",
    "get_candles",
    "start_realtime_candles",
    "get_realtime_candles",
    "stop_realtime_candles",
    "disconnect",
    "stop",
}
ALLOWED_PARAMS = {"symbol", "raw_size", "limit", "market_type", "maxdict"}
REJECTED_KEYS = {
    "email",
    "password",
    "token",
    "cookie",
    "authorization",
    "bearer",
    "ssid",
    "order",
    "amount",
    "direction",
    "expiration",
}


def parse_request(raw: str) -> WorkerRequest:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise IQOptionWorkerInvalidJSON("INVALID_WORKER_REQUEST_JSON") from exc
    if not isinstance(payload, dict):
        raise IQOptionWorkerRejectedCommand("WORKER_REQUEST_MUST_BE_OBJECT")
    command = payload.get("command")
    params = payload.get("params") or {}
    if command not in ALLOWED_COMMANDS:
        raise IQOptionWorkerRejectedCommand("WORKER_COMMAND_NOT_ALLOWED")
    if not isinstance(params, dict):
        raise IQOptionWorkerRejectedCommand("WORKER_PARAMS_MUST_BE_OBJECT")
    lower_keys = {str(key).lower() for key in params}
    if lower_keys & REJECTED_KEYS:
        raise IQOptionWorkerRejectedCommand("WORKER_REJECTED_SENSITIVE_OR_TRADING_PARAM")
    if any(key not in ALLOWED_PARAMS for key in lower_keys):
        raise IQOptionWorkerRejectedCommand("WORKER_PARAM_NOT_ALLOWED")
    return WorkerRequest(command=command, params=params)


def encode_request(command: str, params: dict[str, Any] | None = None) -> str:
    request = parse_request(json.dumps({"command": command, "params": params or {}}))
    return json.dumps({"command": request.command, "params": request.params})


def encode_response(success: bool, data: dict[str, Any] | None = None, error_code: str | None = None) -> str:
    response = WorkerResponse(success=success, data=data or {}, error_code=error_code)
    return json.dumps({"success": response.success, "data": response.data, "error_code": response.error_code}, separators=(",", ":"))


def decode_response(raw: str) -> WorkerResponse:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise IQOptionWorkerInvalidJSON("INVALID_WORKER_RESPONSE_JSON") from exc
    if not isinstance(payload, dict):
        raise IQOptionWorkerInvalidJSON("WORKER_RESPONSE_MUST_BE_OBJECT")
    success = payload.get("success")
    data = payload.get("data")
    error_code = payload.get("error_code")
    if not isinstance(success, bool) or not isinstance(data, dict) or (error_code is not None and not isinstance(error_code, str)):
        raise IQOptionWorkerInvalidJSON("WORKER_RESPONSE_SCHEMA_INVALID")
    return WorkerResponse(success=success, data=data, error_code=error_code)
