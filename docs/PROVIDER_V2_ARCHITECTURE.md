# Provider V2 Architecture

## Objective

Friday AI Platform has a neutral provider foundation for future providers. This document only defines architecture. It does not connect Pocket, Polarium, or any runtime flow to the new contracts.

## Boundary

Functional modules must not know broker-specific classes directly. Future integration points should depend on:

- `MarketProvider`
- `ProviderRegistry`
- `ProviderFactory`
- normalized provider models

Provider-specific implementations remain isolated under their own folders.

## Base Package

The provider foundation lives in:

```text
app/market/providers/base/
  contracts.py
  factory.py
  models.py
  provider.py
  registry.py
```

## Contracts

Every future provider should implement `MarketProvider`:

- `provider_name()`
- `start()`
- `stop()`
- `status()`
- `get_context()`
- `get_assets()`
- `get_history()`
- `get_ticks()`
- `get_readiness()`
- `health()`

## Normalized Models

The shared models are broker-neutral:

- `ProviderContext`
- `ProviderHistory`
- `ProviderTick`
- `ProviderAssets`
- `ProviderAsset`
- `ProviderCandle`
- `ProviderReadiness`
- `ProviderHealth`

These models must not contain raw broker payloads, credentials, cookies, tokens, headers, or private account data.

## Registry

`ProviderRegistry` owns provider instances and exposes:

- `register()`
- `unregister()`
- `get()`
- `list()`
- `current()`
- `set_current()`
- `exists()`
- `clear()`

It does not import Pocket, Polarium, or any concrete broker.

## Factory

`ProviderFactory` owns provider builders and creates providers by name. It also remains broker-neutral and receives constructors through dependency injection. Builders receive a sanitized configuration mapping and return a `MarketProvider`.

The factory exposes:

- `register_builder()`
- `unregister_builder()`
- `list_builders()`
- `has_builder()`
- `create()`
- `clear()`

## Compatibility

The previous import path remains valid:

```python
from app.market.providers.base import MarketDataProvider
```

This keeps existing provider code compiling while the new V2 interface is adopted gradually.
