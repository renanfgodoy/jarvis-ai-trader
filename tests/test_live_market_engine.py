from fastapi.testclient import TestClient

from app.main import app
from app.services.live_market import LiveMarketEngine

client = TestClient(app)


def test_live_candles_endpoint_returns_streaming_candles() -> None:
    response = client.get('/api/v1/live/candles', params={'symbol': 'GBPUSD-OTC', 'timeframe': 'M1', 'limit': 60})

    assert response.status_code == 200
    data = response.json()

    assert data['mode'] == 'LIVE_DEMO'
    assert data['symbol'] == 'GBPUSD-OTC'
    assert data['provider'] == 'live-simulated'
    assert data['count'] == 60
    assert len(data['candles']) == 60
    assert 0 <= data['countdown_seconds'] <= 60
    assert data['last_price'] == data['candles'][-1]['close']


def test_live_tick_endpoint_returns_signal_scanner_and_countdown() -> None:
    response = client.get('/api/v1/live/tick', params={'symbol': 'EURUSD-OTC', 'timeframe': 'M1', 'limit': 80})

    assert response.status_code == 200
    data = response.json()

    assert data['type'] == 'live_tick'
    assert data['symbol'] == 'EURUSD-OTC'
    assert data['demo_only'] is True
    assert len(data['candles']) == 80
    assert len(data['top_assets']) == 12
    assert 'signal' in data
    assert 'countdown_seconds' in data
    assert data['events']


def test_live_market_engine_generates_valid_ohlc() -> None:
    live = LiveMarketEngine().get_live_candles(symbol='BTCUSD-OTC', timeframe='M1', limit=30)

    assert len(live.candles) == 30
    for candle in live.candles:
        assert candle.high >= max(candle.open, candle.close)
        assert candle.low <= min(candle.open, candle.close)
        assert candle.volume is not None


def test_live_workspace_websocket_sends_tick() -> None:
    with client.websocket_connect('/api/v1/live/workspace/ws?symbol=EURUSD-OTC&timeframe=M1') as websocket:
        data = websocket.receive_json()

    assert data['type'] == 'live_tick'
    assert data['symbol'] == 'EURUSD-OTC'
    assert len(data['candles']) == 120
    assert data['countdown_seconds'] >= 0
