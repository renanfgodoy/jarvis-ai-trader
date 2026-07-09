from fastapi.testclient import TestClient

from app.main import app
from app.providers.quadcode import QuadcodePolariumProvider

client = TestClient(app)


def test_quadcode_status_is_safe_demo_only():
    response = client.get('/api/v1/quadcode/status')
    assert response.status_code == 200
    data = response.json()
    assert data['provider'] == 'quadcode'
    assert data['broker'] == 'Polarium'
    assert data['dry_run'] is True
    assert data['canTrade'] is False
    assert data['accountType'] == 'DEMO_ONLY'


def test_quadcode_demo_connect_accepts_demo_only():
    response = client.post('/api/v1/quadcode/demo/connect', json={
        'mode': 'DEMO',
        'dry_run': True,
        'account_type': 'DEMO',
        'allow_real_orders': False,
    })
    assert response.status_code == 200
    data = response.json()
    assert data['connected'] is True
    assert data['status'] == 'CONNECTED'
    assert data['canTrade'] is False


def test_quadcode_demo_connect_blocks_real_orders():
    response = client.post('/api/v1/quadcode/demo/connect', json={
        'mode': 'DEMO',
        'dry_run': False,
        'account_type': 'REAL',
        'allow_real_orders': True,
    })
    assert response.status_code == 200
    data = response.json()
    assert data['connected'] is False
    assert data['status'] == 'BLOCKED'
    assert data['canTrade'] is False


def test_quadcode_symbols_returns_otc_catalog():
    response = client.get('/api/v1/quadcode/symbols')
    assert response.status_code == 200
    data = response.json()
    assert data['total'] >= 12
    symbols = [item['symbol'] for item in data['symbols']]
    assert 'EURUSD-OTC' in symbols
    assert 'BTCUSD-OTC' in symbols


def test_quadcode_dry_run_order_never_executes():
    response = client.post('/api/v1/quadcode/demo/order', json={
        'symbol': 'EURUSD-OTC',
        'signal': 'BUY',
        'entryValue': 10,
        'timeframe': 'M1',
        'expirationMinutes': 1,
        'dryRun': True,
    })
    assert response.status_code == 200
    data = response.json()
    assert data['accepted'] is True
    assert data['executed'] is False
    assert data['mode'] == 'DRY_RUN'


def test_quadcode_provider_get_symbols_has_multi_asset_universe():
    provider = QuadcodePolariumProvider()
    symbols = provider.get_symbols()
    assert len(symbols) >= 12
    assert all(symbol.endswith('-OTC') for symbol in symbols)
