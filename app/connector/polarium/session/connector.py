import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

from app.models.polarium import (
    PolariumAccountState,
    PolariumLoginRequest,
    PolariumLoginResponse,
    PolariumLogoutResponse,
    PolariumSyncResponse,
)
from app.connector.polarium.parser.live_balance import PolariumLiveBalanceParser

CACHE_DIR = Path(".jarvis_cache")
SESSION_FILE = CACHE_DIR / "polarium_session.json"


def _mask_email(email: str) -> str:
    name, _, domain = email.partition("@")
    if not domain:
        return "***"
    visible = name[:2] if len(name) > 2 else name[:1]
    return f"{visible}***@{domain}"


def _minimum_entry_for_currency(currency: str | None) -> float | None:
    if currency == "BRL":
        return 5.0
    if currency == "USD":
        return 1.0
    return None


def _currency_symbol(currency: str | None) -> str | None:
    if currency == "BRL":
        return "R$"
    if currency == "USD":
        return "US$"
    return None


class PolariumConnectorService:
    """Connector seguro da Polarium.

    V0.18.1 remove qualquer saldo inventado. A sessão pode ficar cacheada, mas
    saldo/moeda só aparecem como sincronizados quando vierem de uma sessão real.
    Enquanto a integração autorizada não estiver plugada, a UI deve exibir
    "Não sincronizado" em vez de um saldo fake.
    """

    def status(self) -> PolariumAccountState:
        cached = self._read_cache()
        if cached is None:
            return self._disconnected_state()
        return cached

    def login(self, request: PolariumLoginRequest) -> PolariumLoginResponse:
        account = PolariumAccountState(
            connected=True,
            status="CONNECTED",
            account_mode="DEMO",
            currency=None,
            currency_symbol=None,
            balance=None,
            minimum_entry=None,
            demo_only=True,
            email_masked=_mask_email(request.email),
            session_cached=request.remember_session,
            session_id=f"jarvis-demo-{secrets.token_hex(8)}",
            provider="POLARIUM_DEMO_CONNECTOR",
            data_source="UNAVAILABLE",
            sync_status="NOT_SYNCED",
            is_balance_synced=False,
            last_sync=None,
            last_sync_error="Sessão cacheada, mas saldo real da Polarium ainda não foi sincronizado.",
            warnings=[
                "Saldo não sincronizado: nenhum valor será inventado.",
                "Integração em modo seguro: somente conta DEMO.",
                "Senha não foi salva no cache.",
                "Execução real continua bloqueada até validação futura.",
            ],
            safety_rules=[
                "Conta REAL bloqueada durante desenvolvimento.",
                "BRL exige entrada mínima de R$5 quando a moeda for sincronizada.",
                "USD exige entrada mínima de US$1 quando a moeda for sincronizada.",
                "AutoTrade depende de saldo/moeda reais, Risk Manager e Execution Engine READY.",
            ],
        )
        if request.remember_session:
            self._write_cache(account)
        return PolariumLoginResponse(
            success=True,
            message="Sessão DEMO cacheada com segurança. Clique em Sincronizar Conta para buscar saldo/moeda reais quando o adapter autorizado estiver disponível.",
            account=account,
        )

    def sync_account(self) -> PolariumSyncResponse:
        account = self.status()
        if not account.connected:
            return PolariumSyncResponse(
                success=False,
                message="Polarium não conectada. Faça login antes de sincronizar.",
                account=account,
            )

        # Guardrail: this version does not have an authorized live Polarium API adapter yet.
        # Never return simulated balance as if it were real.
        account.data_source = "UNAVAILABLE"
        account.sync_status = "FAILED"
        account.is_balance_synced = False
        account.balance = None
        account.currency = None
        account.currency_symbol = None
        account.minimum_entry = None
        account.last_sync = datetime.now(timezone.utc)
        account.last_sync_error = (
            "Adapter real da Polarium/Quadcode ainda não configurado. "
            "Saldo, moeda e mínimo de entrada não foram sincronizados."
        )
        account.warnings = [
            "Não foi possível ler saldo real da Polarium nesta versão.",
            "O valor de 10k foi removido para evitar informação falsa.",
            "AutoTrade deve permanecer bloqueado até a sincronização real da conta DEMO.",
        ]
        account.safety_rules = [
            "Nunca exibir saldo simulado como saldo da Polarium.",
            "Só liberar operação com data_source=REAL_SESSION e account_mode=DEMO.",
            "BRL mínimo R$5; USD mínimo US$1 após moeda sincronizada.",
        ]
        self._write_cache(account)
        return PolariumSyncResponse(
            success=False,
            message="Conta não sincronizada: integração real ainda não disponível neste adapter.",
            account=account,
        )


    def ingest_ws_message(self, payload: dict, *, force_demo: bool = True) -> PolariumAccountState:
        parsed = PolariumLiveBalanceParser.parse(payload, force_demo=force_demo)
        current = self.status()
        base = current.model_dump(mode="json") if current.connected else self._disconnected_state().model_dump(mode="json")
        base.update(parsed)
        account = PolariumAccountState.model_validate(base)
        account.last_sync = datetime.now(timezone.utc)
        if account.is_balance_synced:
            account.last_sync_error = None
        self._write_cache(account)
        return account

    def logout(self) -> PolariumLogoutResponse:
        if SESSION_FILE.exists():
            SESSION_FILE.unlink()
        return PolariumLogoutResponse(success=True, message="Sessão Polarium removida do cache local.")

    def _disconnected_state(self) -> PolariumAccountState:
        return PolariumAccountState(
            connected=False,
            status="DISCONNECTED",
            account_mode="DEMO",
            currency=None,
            currency_symbol=None,
            balance=None,
            minimum_entry=None,
            demo_only=True,
            session_cached=False,
            data_source="UNAVAILABLE",
            sync_status="NOT_SYNCED",
            is_balance_synced=False,
            warnings=["Polarium ainda não conectada."],
            safety_rules=["Conecte a conta DEMO antes de sincronizar saldo/moeda."],
        )

    def _read_cache(self) -> PolariumAccountState | None:
        if not SESSION_FILE.exists():
            return None
        try:
            payload = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
            # Backward compatibility: invalidate old fake balance cache from V0.18.0.
            if payload.get("data_source") is None and payload.get("balance") == 10000.0:
                payload["balance"] = None
                payload["currency"] = None
                payload["currency_symbol"] = None
                payload["minimum_entry"] = None
                payload["data_source"] = "UNAVAILABLE"
                payload["sync_status"] = "NOT_SYNCED"
                payload["is_balance_synced"] = False
                payload["last_sync_error"] = "Cache antigo com saldo simulado foi invalidado. Sincronize a conta novamente."
            return PolariumAccountState.model_validate(payload)
        except Exception:
            return None

    def _write_cache(self, account: PolariumAccountState) -> None:
        SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        payload = account.model_dump(mode="json")
        # Defensive: never persist password-like keys even if model changes later.
        payload.pop("password", None)
        SESSION_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
