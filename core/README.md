# Friday AI Platform Core

The J.A.R.V.I.S Core is the architectural center of Friday AI Platform.

It defines engines and provider boundaries only. It does not connect to external APIs,
does not execute trading actions, and does not add runtime behavior.

## Engines

- Identity Engine
- Prompt Engine
- Vision Engine
- Memory Engine
- Decision Engine
- Risk Engine
- Context Engine
- Learning Engine
- Analytics Engine
- Audit Engine
- Provider Engine

## Dependency Rule

Modules must depend on Core contracts. Modules must not depend directly on providers.

```text
Module
  -> J.A.R.V.I.S Core
  -> Provider
  -> J.A.R.V.I.S Core
  -> Module
```
