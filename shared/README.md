# Friday AI Platform Shared Contracts

This package contains small, stable contracts shared by Core, Modules, and Providers.

The contracts are intentionally generic:

- `PlatformRequest`
- `PlatformResponse`
- `ProviderRequest`
- `ProviderResponse`

No sensitive data, provider payload, image, broker credential, API key, token, cookie,
or raw external response belongs in shared contracts.
