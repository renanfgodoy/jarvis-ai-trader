# J.A.R.V.I.S Prompt Engine

## Objective

The J.A.R.V.I.S Prompt Engine centralizes prompt construction for Friday AI Platform.
Modules request prompt packages through typed contracts and never assemble provider
instructions directly.

## Architecture

```text
Module
  -> PromptRequest
  -> PromptEngine
  -> PromptPackage
  -> Core Provider Layer
```

The Prompt Engine does not call providers, does not call OpenAI, and does not perform
network IO.

## Responsibilities

- Validate prompt requests.
- Locate registered templates.
- Validate template versions.
- Sanitize text, context, and metadata.
- Build final prompt messages.
- Validate allowed roles.
- Estimate prompt size.
- Generate deterministic fingerprints.
- Produce immutable prompt packages for future provider layers.

## Contracts

- `PromptRequest`: module, template id, version, input, context, metadata, language,
  response format, and optional request id.
- `PromptMessage`: role, content, optional name, and metadata.
- `PromptPackage`: finalized prompt output with request id, module, template, messages,
  metadata, estimate, timestamp, and fingerprint.
- `PromptTemplate`: template contract implemented by all templates.

## Templates

Initial templates:

- `core.system@1.0`
- `core.generic_analysis@1.0`
- `core.structured_response@1.0`

These templates are generic and do not contain trading analysis, CALL/PUT logic,
Vision logic, OCR, RAG, memory persistence, or provider-specific behavior.

## Versioning

Every template has an explicit version. The registry rejects duplicate
`template_id + version` registrations and fails explicitly when a template or version
does not exist.

## Fingerprint

The fingerprint is deterministic and based on:

- module
- template id
- template version
- messages
- response format

It excludes volatile values such as `created_at` and generated `request_id`.

## Sanitization

The first version sanitizes only structure and text hygiene:

- removes null bytes;
- normalizes newline formats;
- normalizes excessive spaces per line;
- validates serializable mappings;
- enforces configured size limits.

It does not implement moderation, prompt-injection detection, content filtering, or
security classification.

## Size Estimation

The estimator reports:

- character count
- word count
- estimated tokens
- message count

Estimated tokens use a simple documented approximation:

```text
estimated_tokens = ceil(character_count / estimated_characters_per_token)
```

## Errors

Standard errors:

- `PromptEngineError`
- `InvalidPromptRequestError`
- `PromptTemplateNotFoundError`
- `PromptTemplateVersionNotFoundError`
- `DuplicatePromptTemplateError`
- `InvalidPromptMessageError`
- `PromptSizeLimitExceededError`
- `PromptBuildError`

## Integration Rule

Modules must not import or call providers directly.

```text
Module -> PromptRequest -> PromptEngine -> PromptPackage -> Core Provider Layer
```

## Example

```python
from core.prompts import PromptEngine, PromptRequest

engine = PromptEngine()
request = PromptRequest(
    module="trading",
    template_id="core.generic_analysis",
    user_input="Analise somente os dados fornecidos.",
    context={"source": "example"},
)

package = engine.build(request)
```

## V1 Limitations

- No external API calls.
- No OpenAI integration.
- No Vision, OCR, Chat, RAG, or memory persistence.
- No trading analysis or operational decisions.
- No JSON Schema enforcement.
- No streaming.

## Roadmap

1. Connect Prompt Engine to future provider orchestration through Core only.
2. Add Identity Engine integration for tone and personality.
3. Add structured output schemas in a dedicated sprint.
4. Add audit-safe prompt history through future Memory and Audit engines.
5. Add Vision-specific templates only after Vision contracts are stable.
