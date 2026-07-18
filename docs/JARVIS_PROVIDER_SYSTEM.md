# J.A.R.V.I.S Provider Plugin System

## Objetivo

O Provider Plugin System transforma o Provider Engine da Friday AI Platform em uma
camada extensível por plugins, sem permitir que módulos acessem providers
diretamente.

## Fluxo

```text
Module
  -> Module SDK
  -> Core Orchestrator
  -> Identity Engine
  -> Prompt Engine
  -> Provider Engine
  -> Provider Registry
  -> Selected Provider
  -> ProviderResponse
```

## Contratos

- `ProviderRequest`
- `ProviderResponse`
- `ProviderManifest`
- `ProviderMetadata`
- `ProviderHealth`
- `ProviderUsage`

## Plugin Base

Todo provider deve herdar de `BaseProvider` e implementar o ciclo:

- `initialize()`
- `shutdown()`
- `health()`
- `execute()`
- `invoke()`
- `metadata()`
- `manifest()`

Providers nunca conhecem módulos, SDK, Trading, Vision ou UI.

## Registry

`ProviderRegistry` é responsável por:

- registrar providers;
- remover providers;
- listar providers;
- resolver provider ativo;
- resolver provider default;
- consultar health dos providers.

## Loader

`ProviderLoader` é responsável por:

- descobrir builders registrados na factory;
- carregar provider individual;
- executar autoload controlado;
- popular o registry sem instanciar providers dentro do Engine.

## Mock Provider

`MockProvider` foi migrado para o formato de plugin e continua sendo o único
provider funcional nesta Sprint.

Ele permanece local, determinístico e não chama APIs externas.

## Fora do Escopo

Esta Sprint não implementa:

- OpenAI;
- Gemini;
- Anthropic;
- Ollama;
- LM Studio;
- Azure;
- Vision;
- Memory;
- Learning.

Placeholders existentes continuam placeholders e não executam chamadas externas.
