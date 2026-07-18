# J.A.R.V.I.S Trading Module

## Objetivo

O Trading Module V1.0 é o primeiro módulo de negócio oficial da Friday AI Platform.
Ele utiliza exclusivamente o Module SDK para conversar com o Core Orchestrator.

## Fluxo

```text
TradingModule
  -> Module SDK
  -> CoreOrchestrator
  -> IdentityEngine
  -> PromptEngine
  -> ProviderEngine
  -> MockProvider
  -> ModuleResponse
  -> TradingResponse
```

## Contratos

- `TradingRequest`
- `TradingResponse`
- `TradingScenario`

## Serviços

- `TradingAnalyzer`
- `ScenarioBuilder`
- `PromptBuilder`
- `DecisionEngine`

## Estratégias

V1.0 cria estruturas mock para:

- Trend
- Price Action
- Support Resistance
- SMC
- ICT

## Segurança

O módulo não acessa corretoras, APIs externas, providers reais, streaming, Vision,
Memory ou Learning. Nenhum arquivo do módulo importa `core.orchestrator`,
`core.identity`, `core.prompts` ou `core.providers`.

## Developer Console

O Developer Console permite selecionar:

- Module: Trading
- Mercado: OTC, Forex, Crypto
- Estratégia: Trend, Price Action, Support Resistance, SMC, ICT
- Ativo
- Timeframe
- Mensagem

## Release Candidate 1

A Sprint 007.1 refinou a experiência visual sem alterar o módulo:

- `J.A.R.V.I.S Trading Report` renderiza o `TradingResponse` público;
- o pipeline visual finaliza com `Validation`, `Identity`, `Prompt`, `Provider`
  e `Response` em `SUCCESS`;
- o histórico local mantém as últimas cinco execuções sem banco;
- os status cards mostram a saúde visual de Core, SDK, Trading Module, Identity,
  Prompt, Provider e Pipeline;
- o indicador de latência classifica a execução em Excelente (<50ms), Boa
  (50-150ms), Moderada (150-500ms) ou Lenta (>500ms), sem chamar APIs externas.

## Roadmap

1. Adicionar estratégias reais em sprint própria.
2. Adicionar validação de contexto de mercado real.
3. Integrar análise visual somente via Vision Engine.
4. Manter execução operacional fora do escopo até revisão de risco.
