from pathlib import Path

import pytest

from core.analytics.engine import AnalyticsEngine
from core.audit.engine import AuditEngine
from core.context.engine import ContextEngine
from core.decision.engine import DecisionEngine
from core.identity.engine import IdentityEngine
from core.learning.engine import LearningEngine
from core.memory.engine import MemoryEngine
from core.prompts.engine import PromptEngine
from core.providers.factory import ProviderFactory
from core.providers.mock import MockProvider
from core.providers.openai import OpenAIProvider
from core.providers.engine import ProviderEngine
from core.risk.engine import RiskEngine
from core.vision.engine import VisionEngine
from modules.automation.module import AutomationModule
from modules.crm.module import CrmModule
from modules.documents.module import DocumentsModule
from modules.finance.module import FinanceModule
from modules.marketing.module import MarketingModule
from modules.seo.module import SeoModule
from modules.sites.module import SitesModule
from modules.trading.module import TradingModule
from shared.contracts import PlatformRequest, ProviderRequest


def test_all_platform_engines_describe_their_boundaries() -> None:
    engines = [
        IdentityEngine(),
        PromptEngine(),
        VisionEngine(),
        MemoryEngine(),
        DecisionEngine(),
        RiskEngine(),
        ContextEngine(),
        LearningEngine(),
        AnalyticsEngine(),
        AuditEngine(),
        ProviderEngine(),
    ]

    names = {engine.descriptor.name for engine in engines}

    assert names == {
        "identity",
        "prompts",
        "vision",
        "memory",
        "decision",
        "risk",
        "context",
        "learning",
        "analytics",
        "audit",
        "providers",
    }
    assert all(engine.describe() for engine in engines)


def test_provider_factory_creates_registered_placeholders_only() -> None:
    factory = ProviderFactory()
    factory.register("mock", MockProvider)
    factory.register("openai", OpenAIProvider)

    assert factory.list() == ("mock", "openai")
    assert factory.create("mock").execute(ProviderRequest(provider="mock", operation="noop")).status == "placeholder"
    assert factory.create("openai").execute(ProviderRequest(provider="openai", operation="noop")).status == "not_configured"

    with pytest.raises(ValueError):
        factory.register("mock", MockProvider)
    with pytest.raises(KeyError):
        factory.create("missing")


def test_modules_are_placeholders_behind_platform_contracts() -> None:
    modules = [
        TradingModule(),
        FinanceModule(),
        MarketingModule(),
        SeoModule(),
        DocumentsModule(),
        AutomationModule(),
        SitesModule(),
        CrmModule(),
    ]
    request = PlatformRequest(request_id="req-1", module="test", intent="describe")

    responses = [module.handle(request) for module in modules]

    assert {response.status for response in responses} == {"placeholder"}
    assert {response.module for response in responses} == {
        "trading",
        "finance",
        "marketing",
        "seo",
        "documents",
        "automation",
        "sites",
        "crm",
    }


def test_modules_do_not_import_providers_directly() -> None:
    module_files = Path("modules").rglob("*.py")

    for module_file in module_files:
        source = module_file.read_text(encoding="utf-8")
        assert "core.providers" not in source
        assert "OpenAIProvider" not in source
        assert "MockProvider" not in source


def test_architecture_document_names_friday_ai_platform() -> None:
    architecture = Path("docs/FRIDAY_ARCHITECTURE.md").read_text(encoding="utf-8")

    assert "Friday AI Platform" in architecture
    assert "Module -> Provider  # forbidden" in architecture
