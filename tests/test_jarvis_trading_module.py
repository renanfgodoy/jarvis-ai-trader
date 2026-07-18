from pathlib import Path

import pytest

from modules.trading import TradingModule, TradingRequest, TradingResponse
from modules.trading.exceptions import TradingValidationException
from modules.trading.services import DecisionEngine, PromptBuilder, ScenarioBuilder, TradingAnalyzer
from modules.trading.validators import TradingValidator
from sdk import create_default_module_loader


def _request(**overrides) -> TradingRequest:
    data = {
        "market": "OTC",
        "symbol": "EURUSD",
        "timeframe": "M1",
        "strategy": "Trend",
        "message": "Avalie o cenário sem corretora.",
        "metadata": {"test": True},
    }
    data.update(overrides)
    return TradingRequest(**data)


def test_trading_request_and_validator_contracts() -> None:
    validator = TradingValidator()
    validator.validate_request(_request())

    with pytest.raises(TradingValidationException):
        validator.validate_request(_request(symbol=""))
    with pytest.raises(TradingValidationException):
        validator.validate_request(_request(timeframe="M30"))


def test_scenario_builder_uses_market_symbol_timeframe_and_strategy() -> None:
    scenario = ScenarioBuilder().build(_request(symbol="XAUUSD", timeframe="M15", strategy="Support Resistance"))

    assert scenario.market == "OTC"
    assert scenario.symbol == "XAUUSD"
    assert scenario.timeframe == "M15"
    assert scenario.strategy == "Support Resistance"
    assert scenario.bias == "near resistance"
    assert scenario.risk == "LOW"


def test_prompt_builder_selects_market_specific_prompt() -> None:
    builder = PromptBuilder()
    scenario = ScenarioBuilder().build(_request(market="Crypto", symbol="BTCUSD", strategy="Price Action"))
    prompt = builder.build(_request(market="Crypto", symbol="BTCUSD", strategy="Price Action"), scenario)

    assert "crypto.md" in prompt
    assert "BTCUSD" in prompt
    assert "Price Action" in prompt


def test_trading_module_executes_through_sdk_and_returns_trading_response() -> None:
    response = TradingModule().execute(_request())

    assert isinstance(response, TradingResponse)
    assert response.status == "SUCCESS"
    assert response.decision == "OBSERVE"
    assert response.confidence == 72
    assert response.execution.module == "trading"
    assert response.execution.provider == "mock"
    assert response.execution.execution.provider_response.metadata["module_sdk"] is True
    assert response.execution.execution.provider_response.metadata["external_api_called"] is False
    assert response.metadata["intelligent_mock"] is True


def test_decision_engine_generates_distinct_mock_outputs() -> None:
    module = TradingModule()
    crypto = module.execute(_request(market="Crypto", symbol="BTCUSD", strategy="Price Action", timeframe="M5"))
    gold = module.execute(_request(symbol="XAUUSD", strategy="Support Resistance", timeframe="M15"))

    assert crypto.decision == "DO_NOT_TRADE"
    assert crypto.trend == "CHOPPY"
    assert gold.decision == "WAIT"
    assert gold.resistance == "Resistência próxima"


def test_trading_analyzer_composes_services() -> None:
    analyzer = TradingAnalyzer(
        scenario_builder=ScenarioBuilder(),
        prompt_builder=PromptBuilder(),
        decision_engine=DecisionEngine(),
    )
    response = analyzer.analyze(TradingModule(analyzer=analyzer), _request(strategy="ICT"))

    assert response.decision == "WAIT"
    assert "liquidity" in response.metadata["scenario_bias"]


def test_default_module_loader_registers_trading_module() -> None:
    loader = create_default_module_loader()

    assert loader.list_builders() == ("trading",)
    module = loader.registry.get("trading")
    assert isinstance(module, TradingModule)
    assert module.initialized is True


def test_trading_module_architecture_has_no_direct_engine_or_provider_access() -> None:
    source = "\n".join(path.read_text(encoding="utf-8") for path in Path("modules/trading").rglob("*.py"))
    forbidden_terms = [
        "core.orchestrator",
        "core.identity",
        "core.prompts",
        "core.providers",
        "CoreOrchestrator",
        "IdentityEngine",
        "PromptEngine",
        "ProviderEngine",
        "OpenAIProvider",
        "MockProvider",
    ]
    for term in forbidden_terms:
        assert term not in source


def test_trading_module_documentation_exists() -> None:
    docs = Path("docs/JARVIS_TRADING_MODULE.md").read_text(encoding="utf-8")

    assert "J.A.R.V.I.S Trading Module" in docs
    assert "TradingResponse" in docs
    assert "Module SDK" in docs
