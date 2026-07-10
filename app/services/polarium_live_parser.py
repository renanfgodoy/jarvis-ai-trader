from __future__ import annotations

from typing import Any


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(str(value).replace(',', '.'))
    except (TypeError, ValueError):
        return None


def currency_symbol(currency: str | None) -> str | None:
    if not currency:
        return None
    if currency.upper() == 'BRL':
        return 'R$'
    if currency.upper() == 'USD':
        return 'US$'
    return None


def minimum_entry(currency: str | None) -> float | None:
    if not currency:
        return None
    if currency.upper() == 'BRL':
        return 5.0
    if currency.upper() == 'USD':
        return 1.0
    return None


class PolariumLiveBalanceParser:
    """Interpreta mensagens reais observadas no WebSocket da Polarium.

    Não autentica, não conecta, não automatiza navegador e não envia ordens.
    O objetivo da V0.19.0 é consolidar o formato do payload real para preparar
    uma integração autorizada/compatível no futuro.
    """

    @staticmethod
    def parse(payload: dict[str, Any], *, force_demo: bool = True) -> dict[str, Any]:
        event_name = payload.get('name')
        msg = payload.get('msg')

        if event_name == 'subscription-balance-changed':
            account_id = msg.get('id') if isinstance(msg, dict) else None
            return {
                'connected': True,
                'status': 'CONNECTED',
                'account_mode': 'DEMO' if force_demo else 'REAL',
                'data_source': 'DEVTOOLS_PAYLOAD',
                'sync_status': 'CACHE_ONLY',
                'is_balance_synced': False,
                'account_id': account_id,
                'last_event_name': event_name,
                'autotrade_block_reason': 'Saldo alterado; aguardando payload completo marginal-balance ou balances.',
                'warnings': ['Evento de mudança recebido, mas ainda sem saldo/moeda completos.'],
                'safety_rules': ['AutoTrade bloqueado até saldo/moeda completos.'],
                'raw_summary': {'event': event_name, 'payload_keys': list(payload.keys())},
            }

        candidates: list[dict[str, Any]] = []
        if isinstance(msg, dict):
            candidates = [msg]
        elif isinstance(msg, list):
            candidates = [item for item in msg if isinstance(item, dict)]

        if not candidates:
            return {
                'connected': True,
                'status': 'CONNECTED',
                'account_mode': 'DEMO' if force_demo else 'REAL',
                'data_source': 'DEVTOOLS_PAYLOAD',
                'sync_status': 'FAILED',
                'is_balance_synced': False,
                'last_event_name': event_name,
                'last_sync_error': 'Payload não contém msg válida.',
                'autotrade_block_reason': 'Payload sem saldo/moeda.',
                'warnings': ['Não foi possível interpretar a mensagem enviada.'],
                'raw_summary': {'event': event_name, 'payload_keys': list(payload.keys())},
            }

        selected = max(candidates, key=lambda item: len(set(item.keys()) & {'available', 'cash', 'equity', 'currency'}))
        currency = str(selected.get('currency')).upper() if selected.get('currency') else None
        available = to_float(selected.get('available'))
        cash = to_float(selected.get('cash'))
        equity = to_float(selected.get('equity'))
        balance = available if available is not None else cash if cash is not None else equity
        minimum = minimum_entry(currency)
        symbol = currency_symbol(currency)
        account_mode = 'DEMO' if force_demo else 'REAL'
        is_synced = balance is not None and currency in {'BRL', 'USD'} and minimum is not None
        can_autotrade = bool(is_synced and account_mode == 'DEMO' and balance >= minimum)

        return {
            'connected': True,
            'status': 'CONNECTED',
            'account_mode': account_mode,
            'currency': currency,
            'currency_symbol': symbol,
            'balance': balance,
            'available': available,
            'equity': equity,
            'minimum_entry': minimum,
            'demo_only': True,
            'session_cached': True,
            'provider': 'POLARIUM_LIVE_BALANCE_PARSER',
            'data_source': 'DEVTOOLS_PAYLOAD',
            'sync_status': 'SYNCED' if is_synced else 'FAILED',
            'is_balance_synced': is_synced,
            'account_id': selected.get('id'),
            'user_id': selected.get('user_id'),
            'can_autotrade': can_autotrade,
            'last_event_name': event_name,
            'autotrade_block_reason': 'AutoTrade Gate aprovado em DEMO.' if can_autotrade else 'AutoTrade bloqueado: saldo/moeda/modo ainda não aprovados.',
            'warnings': [
                'Dados lidos de payload real copiado do DevTools; ainda não é conexão automática.',
                'Conta REAL permanece bloqueada durante desenvolvimento.',
            ],
            'safety_rules': [
                'Somente DEMO pode liberar AutoTrade.',
                'BRL mínimo R$5; USD mínimo US$1.',
                'Não executar ordens nesta sprint.',
            ],
            'raw_summary': {
                'event': event_name,
                'account_type_code': selected.get('type'),
                'msg_keys': list(selected.keys()),
            },
        }
