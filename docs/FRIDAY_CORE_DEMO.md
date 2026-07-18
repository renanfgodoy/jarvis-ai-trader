# Friday Core Demo

## Objetivo

A Friday Core Demo é o primeiro Developer Console funcional da Friday AI Platform.
Ela prova a integração entre Frontend, Demo Module, Core Orchestrator, Identity Engine,
Prompt Engine, Provider Engine e Mock Provider sem qualquer chamada externa.

## Arquitetura

```text
Frontend
  -> DemoService
  -> Friday API interna
  -> CoreOrchestrator
  -> IdentityEngine
  -> PromptEngine
  -> ProviderEngine
  -> MockProvider
  -> ExecutionResponse
  -> Frontend
```

## Tela

A tela oficial é `/developer/core-demo`.

Ela contém:

- seleção de identity;
- provider mock bloqueado;
- seleção de idioma;
- mensagem;
- botão Execute Friday;
- J.A.R.V.I.S Trading Report;
- pipeline final com Response em `SUCCESS`;
- status cards para Core, SDK, Trading Module, Identity Engine, Prompt Engine,
  Provider Engine e Pipeline;
- histórico em memória das últimas cinco execuções;
- contador de execuções desde a abertura da página;
- indicador de latência;
- debug;
- erro sanitizado.

## Componentes

- `CoreDemo`
- `ExecutionForm`
- `ExecutionPanel`
- `PipelineViewer`
- `DebugPanel`
- `ResponseCard`
- `StatusBadge`
- `SystemStatusCards`
- `ExecutionStatsCards`
- `ExecutionHistory`
- `ExecutionError`

## Pipeline

O pipeline visual representa:

1. Validation
2. Identity
3. Prompt
4. Provider
5. Response

Na RC1, quando uma resposta pública termina com sucesso, todos os passos são
marcados como `SUCCESS`, incluindo `Response`.

## Release Candidate 1

A Sprint 007.1 estabiliza a experiência de validação do Developer Console:

- `Execution Report` substitui o card simples de resposta;
- o relatório mostra mercado, ativo, timeframe, estratégia, leitura, decisão,
  identidade, provider, latência, timestamp, execution id, request id e fingerprint;
- `Execution History` mantém somente as últimas cinco execuções em memória;
- `Execution Counter` calcula execuções, tempo médio e última execução desde a
  abertura da página;
- `Latency Indicator` classifica a execução como Excelente (<50ms), Boa
  (50-150ms), Moderada (150-500ms) ou Lenta (>500ms);
- `Status Cards` exibem Core, SDK, Trading Module, Identity Engine,
  Prompt Engine, Provider Engine e Pipeline como READY, ONLINE, SUCCESS ou ERROR.

## Debug

O DebugPanel consome apenas `ExecutionResponse`. Ele não exibe `ExecutionContext`,
`IdentityResult`, `PromptResult` ou outros objetos internos.

## Roadmap

1. Adicionar módulos reais por contrato.
2. Adicionar auditoria persistente em sprint própria.
3. Adicionar provider real somente por Provider Engine e configuração explícita.
