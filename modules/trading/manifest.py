from sdk import ModuleManifest


TRADING_MANIFEST = ModuleManifest(
    name="trading",
    display_name="Trading Module",
    description="Read-only trading analysis module powered by the Friday Module SDK.",
    version="1.0",
    identity="jarvis.trading",
    provider="mock",
    language="pt-BR",
    permissions=("read:trading-context",),
    core_version="1.0",
    enabled=True,
)
