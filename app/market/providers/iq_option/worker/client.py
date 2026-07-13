from __future__ import annotations

import subprocess
import threading
import uuid
from pathlib import Path
from queue import Empty, Queue
from typing import Any

from app.market.providers.iq_option.worker.errors import (
    IQOptionWorkerFailed,
    IQOptionWorkerInvalidJSON,
    IQOptionWorkerTimeout,
)
from app.market.providers.iq_option.worker.protocol import decode_response, encode_request

DEFAULT_WORKER_PYTHON = Path(".jarvis_cache/iq_option_probe_venv/bin/python")
DEFAULT_WORKER_MODULE = "app.market.providers.iq_option.worker.runner"
DEFAULT_PERSISTENT_WORKER_MODULE = "app.market.providers.iq_option.worker.persistent_runner"
DEFAULT_WORKER_TIMEOUT_SECONDS = 75


class IQOptionIsolatedWorkerClient:
    """Backend-side client for the isolated IQ Option worker subprocess."""

    def __init__(
        self,
        *,
        python_path: Path | str = DEFAULT_WORKER_PYTHON,
        module: str = DEFAULT_WORKER_MODULE,
        timeout_seconds: float = DEFAULT_WORKER_TIMEOUT_SECONDS,
        cwd: Path | str = Path("."),
    ) -> None:
        self.python_path = Path(python_path)
        self.module = module
        self.timeout_seconds = timeout_seconds
        self.cwd = Path(cwd)
        self._connected = False
        self._process: subprocess.Popen[str] | None = None
        self._reader_thread: threading.Thread | None = None
        self._responses: Queue[str] = Queue()
        self._lock = threading.Lock()

    def connect(self) -> tuple[bool, str | None]:
        data = self._command("connect")
        self._connected = True
        return bool(data.get("connected")), None

    def check_connect(self) -> bool:
        return self._connected

    def close(self) -> None:
        try:
            self._command("disconnect")
        finally:
            self._connected = False

    def get_all_open_time(self) -> dict[str, Any]:
        data = self._command("list_assets", {"market_type": "OTC"})
        assets = data.get("assets")
        if not isinstance(assets, list):
            return {"digital": {}, "turbo": {}, "binary": {}}
        return {"digital": {asset["symbol"]: {"open": bool(asset.get("is_open"))} for asset in assets if isinstance(asset, dict) and isinstance(asset.get("symbol"), str)}}

    def list_assets(self, market_type: str = "OTC") -> list[dict[str, Any]]:
        data = self._command("list_assets", {"market_type": market_type})
        assets = data.get("assets")
        return assets if isinstance(assets, list) else []

    def get_candles(self, symbol: str, raw_size: int, limit: int, _now: float | None = None) -> list[dict[str, Any]]:
        data = self._command("get_candles", {"symbol": symbol, "raw_size": raw_size, "limit": limit})
        candles = data.get("candles")
        return candles if isinstance(candles, list) else []

    def start_realtime_candles(self, symbol: str, raw_size: int, maxdict: int = 20) -> dict[str, Any]:
        return self._command("start_realtime_candles", {"symbol": symbol, "raw_size": raw_size, "maxdict": maxdict})

    def get_realtime_candles(self, symbol: str, raw_size: int) -> list[dict[str, Any]]:
        data = self._command("get_realtime_candles", {"symbol": symbol, "raw_size": raw_size})
        candles = data.get("candles")
        return candles if isinstance(candles, list) else []

    def stop_realtime_candles(self, symbol: str, raw_size: int) -> dict[str, Any]:
        return self._command("stop_realtime_candles", {"symbol": symbol, "raw_size": raw_size})

    def status(self) -> dict[str, Any]:
        return self._command("status")

    def _command(self, command: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._persistent_command(command, params)

    def _persistent_command(self, command: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        request = encode_request(command, params)
        request_id = uuid.uuid4().hex
        with self._lock:
            self._ensure_process()
            assert self._process is not None and self._process.stdin is not None
            try:
                self._process.stdin.write(_with_request_id(request, request_id) + "\n")
                self._process.stdin.flush()
                stdout = self._responses.get(timeout=self.timeout_seconds)
            except (BrokenPipeError, TimeoutError, Empty) as exc:
                self._stop_process()
                raise IQOptionWorkerTimeout("IQ_OPTION_WORKER_TIMEOUT") from exc
        response = decode_response(stdout)
        if not response.success:
            raise IQOptionWorkerFailed(response.error_code or "IQ_OPTION_WORKER_FAILED")
        return response.data

    def _one_shot_command(self, command: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        request = encode_request(command, params)
        try:
            result = subprocess.run(
                [str(self.python_path), "-m", self.module],
                input=request,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                cwd=self.cwd,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise IQOptionWorkerTimeout("IQ_OPTION_WORKER_TIMEOUT") from exc

        stdout = result.stdout.strip()
        if not stdout:
            raise IQOptionWorkerInvalidJSON("IQ_OPTION_WORKER_EMPTY_RESPONSE")
        response = decode_response(stdout)
        if not response.success:
            raise IQOptionWorkerFailed(response.error_code or "IQ_OPTION_WORKER_FAILED")
        return response.data

    def _ensure_process(self) -> None:
        if self._process is not None and self._process.poll() is None:
            return
        self._stop_process()
        self._process = subprocess.Popen(
            [str(self.python_path), "-m", DEFAULT_PERSISTENT_WORKER_MODULE],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=self.cwd,
            bufsize=1,
        )
        self._reader_thread = threading.Thread(target=self._read_stdout, name="iq-option-persistent-worker-reader", daemon=True)
        self._reader_thread.start()

    def _read_stdout(self) -> None:
        process = self._process
        if process is None or process.stdout is None:
            return
        for line in process.stdout:
            line = line.strip()
            if line:
                self._responses.put(line)

    def _stop_process(self) -> None:
        process = self._process
        self._process = None
        if process is None:
            return
        if process.poll() is None:
            try:
                if process.stdin:
                    process.stdin.write(_with_request_id(encode_request("stop"), uuid.uuid4().hex) + "\n")
                    process.stdin.flush()
                process.wait(timeout=2)
            except Exception:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except Exception:
                    process.kill()


def _with_request_id(request: str, request_id: str) -> str:
    import json

    payload = json.loads(request)
    payload["request_id"] = request_id
    return json.dumps(payload, separators=(",", ":"))
