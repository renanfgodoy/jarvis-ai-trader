# J.A.R.V.I.S Provider Configuration System

Sprint 008.5 adds the official provider configuration layer for Friday AI
Platform.

The layer is infrastructure-only. It does not implement OpenAI, Gemini,
Anthropic, Ollama, LM Studio, Azure, streaming, Vision, Memory, or any external
API connection.

## Flow

```text
Core Orchestrator
  -> Provider Engine
  -> Provider Resolver
  -> Provider Configuration
  -> Provider Registry
  -> Selected Provider
```

Modules still never access providers directly. The Provider Engine remains the
only layer that can resolve and invoke a provider.

## Configuration

`ProviderConfiguration` centralizes:

- default provider;
- enabled providers;
- provider priority;
- fallback policy;
- health check toggle;
- debug mode;
- environment metadata.

The operational default is `mock`.

## Feature Flags

`FeatureFlags` keeps every real provider disabled by default:

- `mock`: enabled;
- `openai`: disabled;
- `gemini`: disabled;
- `anthropic`: disabled;
- `ollama`: disabled;
- `lmstudio`: disabled;
- `azure`: disabled.

Future real providers must be enabled explicitly and still pass through the
Provider Engine, Provider Resolver, Provider Registry, and Provider contracts.

## Resolver

`ProviderResolver` selects the active provider by:

1. requested provider;
2. default provider;
3. configured priority;
4. fallback provider when enabled.

The resolver respects feature flags and registry availability. If a requested
provider is disabled, the resolver falls back to `mock` when fallback is enabled.

## Health

`ProviderHealthManager` tracks sanitized runtime health:

- status;
- uptime;
- last execution;
- last error;
- latency average;
- request count.

No prompt, response body, credentials, token, or external payload is stored in
the health state.

## Developer Console

The Developer Console now includes:

- Provider Configuration panel;
- Environment;
- Default Provider;
- Enabled Providers;
- Fallback;
- Feature Flags;
- Provider Health panel.

These panels consume only `ExecutionResponse.provider_response.metadata`.

## Safety

- No external API is called.
- No real provider is used.
- Mock remains the default provider.
- Feature flags block real providers by default.
- Fallback remains local and mock-first.
- Modules still cannot access providers directly.
