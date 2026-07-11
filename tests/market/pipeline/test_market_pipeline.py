from copy import deepcopy

from app.market.pipeline import MarketPipeline


def candle_generated_payload() -> dict:
    return {
        "name": "candle-generated",
        "msg": {
            "body": {
                "active_id": 76,
                "size": 60,
                "from": 1783721940,
                "to": 1783722000,
                "open": 1.162275,
                "close": 1.162145,
                "min": 1.162145,
                "max": 1.162395,
                "volume": 0,
            }
        },
    }


def first_candles_payload() -> dict:
    return {
        "request_id": "80",
        "name": "first-candles",
        "status": 2000,
        "msg": {
            "body": {
                "active_id": 76,
                "candles_by_size": {
                    "60": {
                        "from": 1778475660,
                        "to": 1778475720,
                        "open": 1.201705,
                        "close": 1.201425,
                        "min": 1.201405,
                        "max": 1.201825,
                        "volume": 0,
                    },
                    "300": {
                        "from": 1757739900,
                        "to": 1757740200,
                        "open": 1.138605,
                        "close": 1.138015,
                        "min": 1.137295,
                        "max": 1.139265,
                        "volume": 0,
                    },
                },
            }
        },
    }


def test_pipeline_processes_valid_candle_generated() -> None:
    pipeline = MarketPipeline()

    result = pipeline.process(candle_generated_payload())

    assert result.success is True
    assert result.processed == 1
    assert result.stored == 1
    assert len(pipeline.candle_store.series(active_id=76, raw_size=60)) == 1


def test_pipeline_processes_valid_first_candles() -> None:
    pipeline = MarketPipeline()

    result = pipeline.process(first_candles_payload())

    assert result.success is True
    assert result.processed == 2
    assert result.stored == 2
    assert len(pipeline.candle_store.series(active_id=76, raw_size=60)) == 1
    assert len(pipeline.candle_store.series(active_id=76, raw_size=300)) == 1


def test_pipeline_preserves_partial_invalid_collection_errors() -> None:
    pipeline = MarketPipeline()
    payload = first_candles_payload()
    del payload["msg"]["body"]["candles_by_size"]["300"]["close"]

    result = pipeline.process(payload)

    assert result.success is False
    assert result.processed == 1
    assert result.stored == 1
    assert len(result.errors) == 1
    assert result.errors[0].code == "missing_field"


def test_pipeline_handles_unknown_event_without_storing() -> None:
    pipeline = MarketPipeline()

    result = pipeline.process({"name": "unknown-market-event", "msg": {"body": {}}})

    assert result.success is False
    assert result.unsupported == 1
    assert result.processed == 0
    assert pipeline.candle_store.series_keys() == ()


def test_pipeline_handles_event_without_name() -> None:
    pipeline = MarketPipeline()

    result = pipeline.process({"msg": {"body": {}}})

    assert result.success is False
    assert result.unsupported == 0
    assert result.errors[0].code == "missing_event_name"
    assert pipeline.candle_store.series_keys() == ()


def test_pipeline_ignores_duplicate_candle() -> None:
    pipeline = MarketPipeline()
    payload = candle_generated_payload()

    pipeline.process(payload)
    result = pipeline.process(payload)

    assert result.success is True
    assert result.ignored == 1
    assert result.stored == 0
    assert len(pipeline.candle_store.series(active_id=76, raw_size=60)) == 1


def test_pipeline_updates_existing_candle() -> None:
    pipeline = MarketPipeline()
    original = candle_generated_payload()
    updated = deepcopy(original)
    updated["msg"]["body"]["close"] = 1.1625

    pipeline.process(original)
    result = pipeline.process(updated)

    assert result.success is True
    assert result.updated == 1
    assert pipeline.candle_store.series(active_id=76, raw_size=60)[0].close == 1.1625


def test_pipeline_processes_multiple_candles_from_collection() -> None:
    pipeline = MarketPipeline()

    result = pipeline.process(first_candles_payload())

    assert result.processed == 2
    assert result.stored == 2
    assert len(pipeline.candle_store.series_keys()) == 2


def test_pipeline_empty_message_returns_invalid_result() -> None:
    pipeline = MarketPipeline()

    result = pipeline.process({})

    assert result.success is False
    assert result.processed == 0
    assert result.errors[0].code == "missing_event_name"


def test_pipeline_updates_store_correctly_across_events() -> None:
    pipeline = MarketPipeline()

    pipeline.process(first_candles_payload())
    pipeline.process(candle_generated_payload())

    size_60_series = pipeline.candle_store.series(active_id=76, raw_size=60)
    assert [candle.start_timestamp for candle in size_60_series] == [1778475660, 1783721940]
    assert all(candle.symbol is None for candle in size_60_series)
    assert all(candle.timeframe is None for candle in size_60_series)
    assert all(candle.mapping_verified is False for candle in size_60_series)
