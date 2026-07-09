from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_live_workspace_endpoint_returns_candles_signal_and_top_assets() -> None:
    response = client.get('/api/v1/live/workspace', params={'symbol': 'EURUSD-OTC', 'timeframe': 'M1', 'limit': 80})

    assert response.status_code == 200
    data = response.json()

    assert data['mode'] == 'LIVE_WORKSPACE_DEMO'
    assert data['symbol'] == 'EURUSD-OTC'
    assert data['timeframe'] == 'M1'
    assert len(data['candles']) == 80
    assert 'signal' in data
    assert len(data['top_assets']) == 12
    assert data['disclaimer']


def test_live_workspace_endpoint_uses_candlestick_data_shape() -> None:
    response = client.get('/api/v1/live/workspace')

    assert response.status_code == 200
    candle = response.json()['candles'][0]

    assert {'open', 'high', 'low', 'close', 'timestamp'}.issubset(candle.keys())
    assert candle['high'] >= max(candle['open'], candle['close'])
    assert candle['low'] <= min(candle['open'], candle['close'])
