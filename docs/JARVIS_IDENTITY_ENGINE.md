# J.A.R.V.I.S Identity Engine

## Objective

The J.A.R.V.I.S Identity Engine defines who should answer a request inside Friday AI
Platform. It produces a stable identity profile for the Prompt Engine to consume later.

It does not answer users, does not build prompt messages, does not call providers, and
does not access the network.

## Flow

```text
Module
  -> IdentityRequest
  -> IdentityEngine
  -> IdentityProfile
  -> PromptEngine
  -> PromptPackage
  -> Provider
```

## Contracts

- `IdentityProfile`: immutable identity definition with version, tone, style,
  principles, capabilities, limitations, metadata, timestamp, and fingerprint.
- `IdentityRequest`: module request for an identity.
- `IdentityResult`: resolved identity output with request id, metadata, timestamp, and
  deterministic fingerprint.

## Official Profiles

Only four official identities exist in V1.0:

- `jarvis.default@1.0`
- `jarvis.trading@1.0`
- `jarvis.marketing@1.0`
- `jarvis.finance@1.0`

No other identity is registered in this sprint.

## Registry

`IdentityRegistry` explicitly registers profiles, blocks duplicates, lists identities,
lists versions, and fails when an identity or version does not exist.

There is no auto-discovery in V1.0.

## Resolver

`IdentityResolver` receives an `IdentityRequest` and returns one `IdentityProfile`.

Rules:

- no requested identity: use `jarvis.default`;
- unknown requested identity: fail explicitly;
- no silent fallback for unknown identities;
- requested language may override profile language when supported.

## Builder

`IdentityBuilder` produces the final `IdentityResult`. It applies metadata, timestamp,
resolver version, and deterministic fingerprint.

It does not create `PromptMessage` objects.

## Versioning

All identities use explicit `identity_id + version`. The registry rejects duplicate
versions and resolves default versions predictably.

## Fingerprint

Identity fingerprints are deterministic and based on:

- identity id;
- version;
- language;
- tone;
- style;
- principles;
- capabilities;
- limitations;
- normalized metadata.

They exclude volatile values such as request id, timestamp, and created-at fields.

## Validation

`IdentityValidator` checks:

- required identity id;
- required version;
- supported language;
- non-empty tone;
- non-empty style;
- required principles;
- serializable capabilities;
- serializable limitations;
- serializable metadata.

## Limits

V1.0 does not implement:

- OpenAI;
- Vision;
- Memory;
- Learning;
- frontend;
- chat;
- streaming;
- embeddings;
- RAG;
- function calling;
- trading analysis.

## Roadmap

1. Let the Prompt Engine consume `IdentityProfile` metadata in a future sprint.
2. Add Identity Engine policy presets per module after module contracts stabilize.
3. Add Audit Engine integration for traceability.
4. Add Identity version migration rules.
