# J.A.R.V.I.S Core Orchestrator

## Objective

The J.A.R.V.I.S Core Orchestrator is the single coordination point for Friday AI
Platform Core execution.

It does not implement intelligence, business rules, Vision, Memory, Trading, storage,
or external APIs. It coordinates engines through a local execution pipeline.

## Flow

```text
Module
  -> CoreOrchestrator
  -> IdentityEngine
  -> PromptEngine
  -> ProviderEngine
  -> AIProvider
  -> ExecutionResponse
```

Modules must not call Identity, Prompt, Provider, Vision, or any engine directly.

## Pipeline

Initial V1 pipeline:

1. Validate Request
2. Resolve Identity
3. Build Prompt
4. Execute Provider
5. Normalize Response
6. Finalize Execution

Each stage implements:

- `name()`
- `version()`
- `validate(context)`
- `execute(context)`
- `rollback(context)`

## Context

`ExecutionContext` exists only during one execution. It carries:

- request;
- identity result;
- prompt result;
- provider result;
- execution metadata;
- response;
- status;
- pipeline stage;
- errors;
- internal events.

No persistence is implemented in V1.

## Contracts

- `ExecutionRequest`
- `ExecutionResponse`
- `ExecutionMetadata`
- `ExecutionContext`
- `ExecutionPipeline`
- `PipelineStage`

## Hooks

`ExecutionHooks` contains no-op extension points:

- before/after validation;
- before/after identity;
- before/after prompt;
- before/after provider;
- before/after finish.

No Event Bus or external side effect is implemented.

## Events

Internal events:

- ExecutionStarted
- IdentityResolved
- PromptBuilt
- ProviderSelected
- ProviderExecuted
- ResponseNormalized
- ExecutionFinished
- ExecutionFailed

Events remain inside the execution context in V1.

## Metadata

`ExecutionMetadata` records:

- execution id;
- request id;
- started/finished timestamps;
- duration;
- provider;
- provider version;
- identity;
- module;
- pipeline version;
- fingerprint;
- status.

It does not store full prompt content or sensitive payloads.

## Versioning

The default pipeline version is `1.0`.

## Roadmap

1. Add module-facing Core contracts.
2. Add Audit Engine integration for execution traces.
3. Add Vision Engine integration through Orchestrator only.
4. Add Memory Engine integration behind explicit policies.
5. Add real provider adapters only behind Provider Engine security controls.
