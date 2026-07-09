from __future__ import annotations

from datetime import datetime, timedelta, timezone
import math
import random

from app.core.config import settings
from app.indicators.signal_engine import SignalEngineService
from app.models.candle import Candle, Timeframe
from app.models.live import LiveCandlesResponse, LiveMarketTick
from app.services.asset_scanner import AssetScannerService
from app.services.market_reader import MarketReaderService


class LiveMarketEngine:
    """Motor de candles vivos em modo DEMO.

    Esta Sprint não conecta conta real e não envia ordens. O objetivo é criar
    uma fonte de candles mais viva para o dashboard, mantendo o contrato pronto
    para WebSocket e providers reais nas próximas etapas.
    """

    def __init__(self) -> None:
        self.market_reader = MarketReaderService()
        self.signal_engine = SignalEngineService()
        self.scanner = AssetScannerService()

    def get_live_candles(self, symbol: str, timeframe: Timeframe = "M1", limit: int = 120) -> LiveCandlesResponse:
        clean_symbol = symbol.strip().upper() or settings.default_symbol
        candles = self._build_live_candles(symbol=clean_symbol, timeframe=timeframe, limit=limit)
        countdown = self._countdown_seconds(timeframe=timeframe)
        return LiveCandlesResponse(
            symbol=clean_symbol,
            timeframe=timeframe,
            provider="live-simulated",
            count=len(candles),
            countdown_seconds=countdown,
            candles=candles,
            last_price=candles[-1].close,
        )

    def get_tick(self, symbol: str, timeframe: Timeframe = "M1", limit: int = 120) -> LiveMarketTick:
        clean_symbol = symbol.strip().upper() or settings.default_symbol
        live = self.get_live_candles(symbol=clean_symbol, timeframe=timeframe, limit=limit)
        signal = self.signal_engine.analyze_candles(candles=live.candles, symbol=clean_symbol, timeframe=timeframe)
        scanner = self.scanner.scan(timeframe=timeframe, candle_limit=60, top=12)
        trend = getattr(signal, "trend", "NEUTRAL")
        strength = int(getattr(signal, "strength", 0) or 0)
        events = [
            f"Live Market Engine atualizou {clean_symbol}",
            f"Candlestick recalculado com {len(live.candles)} candles",
            f"Signal Engine: {trend} com força {strength}%",
            f"Próxima vela em {live.countdown_seconds}s",
        ]
        return LiveMarketTick(
            symbol=clean_symbol,
            timeframe=timeframe,
            provider=live.provider,
            server_time=datetime.now(timezone.utc),
            price=live.last_price,
            candle=live.candles[-1],
            candles=live.candles,
            countdown_seconds=live.countdown_seconds,
            signal=signal,
            top_assets=scanner.results,
            scanner_total=scanner.assets_scanned,
            events=events,
        )

    def _build_live_candles(self, symbol: str, timeframe: Timeframe, limit: int) -> list[Candle]:
        safe_limit = max(30, min(limit, 300))
        minutes = self._timeframe_to_minutes(timeframe)
        now = datetime.now(timezone.utc)
        current_bucket = now.replace(second=0, microsecond=0)
        if minutes > 1:
            minute_bucket = (current_bucket.minute // minutes) * minutes
            current_bucket = current_bucket.replace(minute=minute_bucket)
        start = current_bucket - timedelta(minutes=minutes * (safe_limit - 1))
        seed_symbol = sum(ord(ch) for ch in symbol)
        base = self._base_price(symbol)
        candles: list[Candle] = []
        last_close = base
        random.seed(f"live-{symbol}-{timeframe}-{current_bucket.isoformat()}")

        for index in range(safe_limit):
            timestamp = start + timedelta(minutes=minutes * index)
            phase = (index + seed_symbol % 17) / 5.0
            wave = math.sin(phase) * self._amplitude(symbol)
            drift = math.sin((index + seed_symbol) / 23.0) * self._amplitude(symbol) * 0.35
            noise = random.uniform(-self._amplitude(symbol), self._amplitude(symbol)) * 0.55
            open_price = last_close
            close_price = max(0.00001, base + wave + drift + noise)
            if index == safe_limit - 1:
                progress = self._candle_progress(timeframe)
                live_pulse = math.sin(now.timestamp() / 3.0) * self._amplitude(symbol) * 0.8
                close_price = max(0.00001, open_price + (close_price - open_price) * progress + live_pulse)
            high_price = max(open_price, close_price) + abs(random.uniform(0.2, 1.1)) * self._amplitude(symbol)
            low_price = max(0.00001, min(open_price, close_price) - abs(random.uniform(0.2, 1.1)) * self._amplitude(symbol))
            volume = 400 + abs(math.sin(index / 3.0 + seed_symbol)) * 620 + random.uniform(0, 180)
            if index == safe_limit - 1:
                volume *= 1 + self._candle_progress(timeframe)
            candle = Candle(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=timestamp,
                open=round(open_price, self._precision(symbol)),
                high=round(high_price, self._precision(symbol)),
                low=round(low_price, self._precision(symbol)),
                close=round(close_price, self._precision(symbol)),
                volume=round(volume, 2),
            )
            candles.append(candle)
            last_close = candle.close
        return candles

    @staticmethod
    def _timeframe_to_minutes(timeframe: Timeframe) -> int:
        return {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}[timeframe]

    def _countdown_seconds(self, timeframe: Timeframe) -> int:
        seconds = self._timeframe_to_minutes(timeframe) * 60
        now = datetime.now(timezone.utc)
        elapsed = int(now.timestamp()) % seconds
        remaining = seconds - elapsed
        return seconds if remaining == 0 else remaining

    def _candle_progress(self, timeframe: Timeframe) -> float:
        seconds = self._timeframe_to_minutes(timeframe) * 60
        now = datetime.now(timezone.utc)
        elapsed = int(now.timestamp()) % seconds
        return max(0.05, min(elapsed / seconds, 1.0))

    @staticmethod
    def _base_price(symbol: str) -> float:
        if "BTC" in symbol:
            return 65000.0
        if "ETH" in symbol:
            return 3500.0
        if "SOL" in symbol:
            return 150.0
        if "XAU" in symbol or "GOLD" in symbol:
            return 2300.0
        return 1.10 + (sum(ord(ch) for ch in symbol) % 80) / 10000

    @staticmethod
    def _amplitude(symbol: str) -> float:
        if "BTC" in symbol:
            return 120.0
        if "ETH" in symbol:
            return 9.0
        if "SOL" in symbol:
            return 0.7
        if "XAU" in symbol or "GOLD" in symbol:
            return 3.5
        return 0.00065

    @staticmethod
    def _precision(symbol: str) -> int:
        if any(asset in symbol for asset in ("BTC", "ETH", "SOL", "XAU", "GOLD")):
            return 2
        return 5
