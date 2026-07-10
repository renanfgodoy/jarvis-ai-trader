from app.services.polarium_live_parser import PolariumLiveBalanceParser
from app.services.polarium_connector import PolariumConnectorService


def test_parse_marginal_balance_usd_payload():
    payload = {
        'request_id': '10',
        'name': 'marginal-balance',
        'msg': {
            'id': 1241028586,
            'user_id': 191243694,
            'available': '16037.53',
            'cash': '16037.53',
            'equity': '16037.53',
            'equity_usd': '16037.53',
            'currency': 'USD',
            'type': 4,
        },
        'status': 2000,
    }
    parsed = PolariumLiveBalanceParser.parse(payload)
    assert parsed['sync_status'] == 'SYNCED'
    assert parsed['balance'] == 16037.53
    assert parsed['currency'] == 'USD'
    assert parsed['minimum_entry'] == 1.0
    assert parsed['can_autotrade'] is True


def test_parse_subscription_balance_changed_is_not_full_sync():
    payload = {'request_id': '19', 'name': 'subscription-balance-changed', 'msg': {'id': 1241028586}, 'status': 2000}
    parsed = PolariumLiveBalanceParser.parse(payload)
    assert parsed['sync_status'] == 'CACHE_ONLY'
    assert parsed['is_balance_synced'] is False
    assert parsed['account_id'] == 1241028586


def test_connector_ingest_payload_updates_state(tmp_path, monkeypatch):
    import app.services.polarium_connector as connector_module
    monkeypatch.setattr(connector_module, 'CACHE_DIR', tmp_path)
    monkeypatch.setattr(connector_module, 'SESSION_FILE', tmp_path / 'polarium_session.json')
    service = PolariumConnectorService()
    state = service.ingest_ws_message({
        'name': 'marginal-balance',
        'msg': {'id': 1, 'user_id': 2, 'available': '15000', 'cash': '15000', 'equity': '15000', 'currency': 'BRL'},
    })
    assert state.is_balance_synced is True
    assert state.currency == 'BRL'
    assert state.minimum_entry == 5.0
    assert service.status().balance == 15000
