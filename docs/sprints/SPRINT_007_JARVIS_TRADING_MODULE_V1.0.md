# SPRINT 007

# J.A.R.V.I.S Trading Module V1.0

Friday AI Platform

Versão

1.0

Status

PLANNING

Tipo

Business Module

---

# OBJETIVO

Implementar o primeiro módulo oficial da Friday AI Platform utilizando exclusivamente o Module SDK.

O módulo deverá representar o domínio Trading e consumir toda a infraestrutura criada nas Sprints anteriores.

---

# MISSÃO

Transformar a Friday de um Core Framework para uma plataforma capaz de executar um domínio de negócio real.

---

# ARQUITETURA

Fluxo obrigatório

Frontend

↓

Developer Console

↓

Trading Module

↓

Module SDK

↓

Core Orchestrator

↓

Identity Engine

↓

Prompt Engine

↓

Provider Engine

↓

Mock Provider

↓

ExecutionResponse

↓

TradingResponse

↓

Frontend

---

# REGRA DE OURO

O Trading Module nunca poderá importar:

core.identity

core.prompt

core.provider

core.orchestrator

Todo acesso ao Core deverá ocorrer exclusivamente através do SDK.

---

# ESTRUTURA

modules/

trading/

__init__.py

module.py

manifest.py

contracts.py

models.py

metadata.py

validators.py

exceptions.py

services/

analyzer.py

decision_engine.py

scenario_builder.py

prompt_builder.py

strategies/

trend.py

price_action.py

support_resistance.py

smc.py

ict.py

prompts/

default.md

otc.md

forex.md

crypto.md

tests/

---

# TRADING MODULE

Criar

TradingModule

Herdando obrigatoriamente de:

BaseModule

Responsabilidades

receber TradingRequest

validar dados

executar SDK

transformar ExecutionResponse em TradingResponse

Nunca acessar Engines diretamente.

---

# TRADING REQUEST

Criar contrato

TradingRequest

Campos

market

symbol

timeframe

strategy

message

metadata

timestamp

---

# TRADING RESPONSE

Criar contrato

TradingResponse

Campos

status

trend

support

resistance

decision

confidence

risk

analysis

execution

metadata

timestamp

---

# ANALYZER

Criar

TradingAnalyzer

Responsabilidades

interpretar TradingRequest

selecionar Prompt

montar contexto

delegar execução ao SDK

---

# DECISION ENGINE

Criar

DecisionEngine

Responsabilidades

transformar ExecutionResponse em TradingResponse

normalizar resposta

gerar decisão

---

# SCENARIO BUILDER

Criar

ScenarioBuilder

Responsabilidades

montar cenário interno

market

symbol

timeframe

strategy

---

# PROMPT BUILDER

Criar

PromptBuilder

Responsabilidades

selecionar prompt

default

otc

forex

crypto

Nunca executar Providers.

---

# STRATEGIES

Criar estrutura

TrendStrategy

PriceActionStrategy

SupportResistanceStrategy

SMCStrategy

ICTStrategy

Nesta Sprint todas poderão utilizar comportamento Mock.---

# REGISTRY

Registrar automaticamente

TradingModule

no ModuleRegistry.

---

# LOADER

Permitir

registry.load("trading")

retornando

TradingModule

---

# DEVELOPER CONSOLE

Adicionar seleção

Module

Trading

Estratégia

Trend

Price Action

Support Resistance

SMC

ICT

Mercado

OTC

Forex

Crypto

Ativo

Timeframe

Mensagem

---

# MOCK INTELIGENTE

O Provider Mock deverá gerar respostas coerentes de acordo com

market

symbol

timeframe

strategy

Sem acessar internet.

Sem APIs.

Sem corretoras.

---

# EXEMPLOS

EURUSD OTC M1

↓

Trend

↓

Alta

BTCUSD M5

↓

Price Action

↓

Consolidação

XAUUSD M15

↓

Support Resistance

↓

Resistência próxima

---

# TESTES

Criar testes para

TradingModule

TradingRequest

TradingResponse

Analyzer

DecisionEngine

ScenarioBuilder

PromptBuilder

Registry

Loader

Integração

Garantir

✓ Trading Module utiliza SDK

✓ Nenhum acesso direto às Engines

✓ Nenhuma API externa

✓ Provider Mock

✓ Build aprovado

---

# DOCUMENTAÇÃO

Criar

docs/JARVIS_TRADING_MODULE.md

Atualizar

FRIDAY_ARCHITECTURE.md

Adicionar

Trading Module

Business Modules

---

# CRITÉRIOS DE ACEITAÇÃO

Trading Module criado

Registry funcionando

Loader funcionando

Developer Console atualizado

Mock inteligente

TradingResponse funcionando

Testes aprovados

Build aprovado

Nenhum acesso direto às Engines

Nenhuma API externa

Provider Mock

---

# FORA DO ESCOPO

Ordens reais

Corretoras

Trading automático

Streaming

Vision

Memory

Learning

Banco de dados

IA real

OpenAI

Anthropic

Gemini

---

# RELATÓRIO FINAL

Entregar

Resumo

Arquivos criados

Arquivos modificados

Trading Module

Registry

Loader

Developer Console

Testes

Build

Problemas

Decisões arquiteturais

Limitações

Próxima Sprint

Confirmar

✓ Nenhuma API externa utilizada

✓ Nenhum Provider real utilizado

✓ Todo fluxo passou pelo SDK

✓ Nenhum acesso direto às Engines

SPRINT_007_JARVIS_TRADING_MODULE_V1.0

Objetivo

Criar oficialmente o primeiro módulo de negócio da Friday AI Platform utilizando exclusivamente o Module SDK.

Antes de modificar qualquer arquivo

1. Ler toda a Sprint.
2. Revisar FRIDAY_ARCHITECTURE.md.
3. Revisar Module SDK.
4. Revisar Core Orchestrator.
5. Revisar Core Demo.

Implementar apenas

TradingModule

TradingRequest

TradingResponse

TradingAnalyzer

DecisionEngine

ScenarioBuilder

PromptBuilder

Manifest

Metadata

Validators

Exceptions

Atualizar

Developer Console

Module Registry

Module Loader

Executar

Testes específicos

Suíte completa

Build

Somente concluir quando todos os critérios de aceitação forem atendidos.