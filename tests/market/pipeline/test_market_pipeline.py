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


def first_candles_list_payload(count: int = 100, *, active_id: int = 76, raw_size: int = 60, start: int = 1_783_720_000) -> dict:
    return {
        "name": "first-candles",
        "msg": {
            "body": {
                "candles": [
                    {
                        "active_id": active_id,
                        "size": raw_size,
                        "from": start + index * raw_size,
                        "to": start + (index + 1) * raw_size,
                        "open": 1.1 + index / 10000,
                        "close": 1.2 + index / 10000,
                        "min": 1.0 + index / 10000,
                        "max": 1.3 + index / 10000,
                        "volume": 0,
                    }
                    for index in range(count)
                ]
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


def test_pipeline_bootstraps_100_historical_candles_from_first_candles_list() -> None:
    pipeline = MarketPipeline()

    result = pipeline.process(first_candles_list_payload(100))

    series = pipeline.candle_store.series(active_id=76, raw_size=60)
    assert result.success is True
    assert result.processed == 100
    assert result.stored == 100
    assert len(series) == 100
    assert series[0].start_timestamp == 1_783_720_000
    assert series[-1].start_timestamp == 1_783_725_940


def test_pipeline_bootstraps_200_historical_candles_from_first_candles_list() -> None:
    pipeline = MarketPipeline()

    result = pipeline.process(first_candles_list_payload(200))

    series = pipeline.candle_store.series(active_id=76, raw_size=60)
    assert result.success is True
    assert len(series) == 200
    assert series[-1].start_timestamp == 1_783_731_940


def test_historical_bootstrap_deduplicates_by_timestamp_and_updates_duplicate() -> None:
    pipeline = MarketPipeline()
    payload = first_candles_list_payload(2)
    duplicate = dict(payload["msg"]["body"]["candles"][1])
    duplicate["close"] = 9.9
    payload["msg"]["body"]["candles"].append(duplicate)

    result = pipeline.process(payload)

    series = pipeline.candle_store.series(active_id=76, raw_size=60)
    assert result.stored == 2
    assert result.updated == 1
    assert len(series) == 2
    assert series[-1].close == 9.9


def test_historical_bootstrap_separates_active_id_and_raw_size() -> None:
    pipeline = MarketPipeline()

    pipeline.process(first_candles_list_payload(2, active_id=76, raw_size=60, start=1000))
    pipeline.process(first_candles_list_payload(3, active_id=2298, raw_size=60, start=2000))
    pipeline.process(first_candles_list_payload(4, active_id=76, raw_size=300, start=3000))

    assert len(pipeline.candle_store.series(active_id=76, raw_size=60)) == 2
    assert len(pipeline.candle_store.series(active_id=2298, raw_size=60)) == 3
    assert len(pipeline.candle_store.series(active_id=76, raw_size=300)) == 4


def test_realtime_candle_updates_last_bootstrap_candle_without_reducing_history() -> None:
    pipeline = MarketPipeline()
    pipeline.process(first_candles_list_payload(100))
    realtime = candle_generated_payload()
    realtime["msg"]["body"]["from"] = 1_783_725_940
    realtime["msg"]["body"]["to"] = 1_783_726_000
    realtime["msg"]["body"]["close"] = 1.999

    result = pipeline.process(realtime)

    series = pipeline.candle_store.series(active_id=76, raw_size=60)
    assert result.updated == 1
    assert len(series) == 100
    assert series[-1].close == 1.999


def test_realtime_candle_appends_after_bootstrap_without_reducing_history() -> None:
    pipeline = MarketPipeline()
    pipeline.process(first_candles_list_payload(100))
    realtime = candle_generated_payload()
    realtime["msg"]["body"]["from"] = 1_783_726_000
    realtime["msg"]["body"]["to"] = 1_783_726_060

    result = pipeline.process(realtime)

    series = pipeline.candle_store.series(active_id=76, raw_size=60)
    assert result.stored == 1
    assert len(series) == 101
    assert series[-1].start_timestamp == 1_783_726_000
