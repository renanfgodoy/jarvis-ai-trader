# J.A.R.V.I.S Provider Engine

## Objective

The J.A.R.V.I.S Provider Engine is the only Friday AI Platform layer authorized to
communicate with future AI providers.

In V1.0 it defines contracts, registries, policies, health, capabilities, and
placeholder providers only. It does not connect to any external API.

## Flow

```text
Module
  -> Identity Engine
  -> Prompt Engine
  -> Provider Engine
  -> AI Provider
  -> Response
```

Modules, Identity Engine, Prompt Engine, Vision, and Trading must not call providers
directly.

## Contracts

- `BaseProvider`
- `ProviderRequest`
- `ProviderInvocation`
- `ProviderResponse`
- `ProviderManifest`
- `ProviderMetadata`
- `ProviderConfig`
- `ProviderUsage`
- `ProviderHealth`

All providers implement:

- `initialize()`
- `shutdown()`
- `health()`
- `execute()`
- `metadata()`
- `manifest()`
- `capabilities()`
- `invoke()`
- `close()`

The legacy `execute()` method remains only for compatibility with the initial
foundation tests.

## Placeholder Providers

V1.0 registers placeholders for:

- `openai`
- `anthropic`
- `google`
- `groq`
- `ollama`
- `lmstudio`
- `mock`

These placeholders never call external APIs and never require API keys.

## Capabilities

`ProviderCapabilityRegistry` stores explicit provider capabilities. Capabilities are
never inferred.

Examples:

- OpenAI: chat, vision, json, streaming, tool_calling, embeddings
- Anthropic: chat, vision, streaming, tool_use
- Google: chat, vision, json, streaming, embeddings
- Groq: chat, streaming
- Ollama: chat, local, embeddings
- LM Studio: chat, local

## Health

`ProviderHealth` supports:

- ONLINE
- OFFLINE
- DEGRADED
- LIMITED
- RATE_LIMITED
- UNKNOWN

V1.0 placeholders return local placeholder health only.

## Retry

`RetryPolicy` defines:

- enabled/disabled;
- maximum attempts;
- interval placeholder;
- recoverable error types.

Retries are bounded. Infinite retry is not allowed.

## Fallback

`FallbackPolicy` optionally points to a secondary provider. The fallback provider is
used only when enabled and distinct from the primary provider.

## Observability

`ProviderResponse` records:

- provider;
- provider version;
- request id;
- normalized response;
- usage;
- latency;
- metadata;
- status;
- fingerprint;
- timestamp.

No raw external API response is exposed.

## Provider Plugin System

Sprint 008 moves provider creation behind `ProviderLoader` and `ProviderRegistry`.
The `ProviderEngine` no longer needs to instantiate provider plugins directly.

The Mock Provider is migrated to plugin shape while preserving behavior. Future
providers must be loaded through the registry/loader path and must return
`ProviderResponse`.

## Provider Configuration System

Sprint 008.5 adds `ProviderConfiguration`, `ProviderResolver`, `FeatureFlags`,
`ProviderSettings`, `ProviderEnvironment`, and `ProviderHealthManager`.

The default operational provider is `mock`. Real providers remain placeholders and
are disabled by feature flag unless a future sprint explicitly enables them.

The Provider Engine now resolves providers through:

```text
ProviderEngine
  -> ProviderResolver
  -> ProviderConfiguration
  -> ProviderRegistry
```

The Developer Console displays configuration and health panels using sanitized
metadata from `ProviderResponse`.

## Roadmap

1. Add secure provider-specific configuration loading.
2. Add real provider adapters behind explicit feature flags.
3. Add audit-safe provider invocation logs.
4. Add streaming as a separate contract.
5. Add tool calling and structured output only after contract hardening.
