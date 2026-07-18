# Pocket Provider V2 Adapter

## Objective

`PocketProviderAdapter` is the first concrete implementation of the Provider V2 interface. It wraps the existing isolated Pocket runtime and does not register itself in the main runtime.

## Scope

This adapter only converts Pocket runtime objects into neutral Provider V2 models:

- `PocketSessionContext` to `ProviderContext`
- `PocketRealtimeTick` to `ProviderTick`
- `PocketNormalizedCandle` to `ProviderCandle`
- `PocketAssetCatalog` to `ProviderAssets`
- Pocket readiness state to `ProviderReadiness`
- `PocketRuntimeMetrics` to `ProviderHealth`

## Isolation

The adapter does not:

- connect Pocket to the main Friday runtime;
- alter Chart API;
- alter frontend;
- alter Polarium;
- alter Pocket parser, discovery, or replay;
- auto-register in `ProviderRegistry`.

Future integration must explicitly inject it through `ProviderFactory` or `ProviderRegistry`.

## Builders

The official builders are:

- `PocketProviderBuilder`
- `FakePocketProviderBuilder`

They are compatible with `ProviderFactory` and do not register themselves automatically.
