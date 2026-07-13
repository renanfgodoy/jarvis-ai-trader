__all__ = ["IQOptionMarketDataProvider", "IQOptionProviderRuntime"]


def __getattr__(name: str):
    if name == "IQOptionMarketDataProvider":
        from app.market.providers.iq_option.provider import IQOptionMarketDataProvider

        return IQOptionMarketDataProvider
    if name == "IQOptionProviderRuntime":
        from app.market.providers.iq_option.runtime import IQOptionProviderRuntime

        return IQOptionProviderRuntime
    raise AttributeError(name)
