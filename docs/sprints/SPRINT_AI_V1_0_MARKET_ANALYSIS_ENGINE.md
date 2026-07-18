# SPRINT AI V1.0 — MARKET ANALYSIS ENGINE

## Objetivo

Iniciar oficialmente a FASE 3 da Friday AI Trader.

Esta Sprint cria a arquitetura base do Market Analysis Engine, responsável por transformar dados normalizados dos Providers em análises estruturadas para a IA.

IMPORTANTE

Esta Sprint NÃO cria sinais de compra.

NÃO cria sinais de venda.

NÃO cria AutoTrade.

NÃO cria CALL/PUT.

NÃO cria estratégias.

NÃO altera Frontend.

NÃO altera Chart API.

NÃO altera Providers.

NÃO altera Runtime.

Apenas cria o núcleo da camada de inteligência.

---

# Arquitetura

Provider

↓

Provider Models

↓

Market Analysis Engine

↓

Market Analysis Result

↓

(Indicadores futuramente)

↓

(Padrões futuramente)

↓

(Probabilidade futuramente)

↓

(Decision Engine futuramente)

---

# Criar estrutura

app/

market/

analysis/

__init__.py

engine.py

models.py

context.py

statistics.py

normalizer.py

health.py

exceptions.py

README.md

---

# Objetivo do Engine

Receber:

ProviderContext

ProviderHistory

ProviderTicks

ProviderAssets

Retornar:

MarketAnalysis

---

# Criar modelos

MarketAnalysis

MarketStatistics

MarketSnapshot

MarketHealth

MarketMetadata

MarketState

AnalysisContext

---

# MarketAnalysis

Deverá conter:

provider

symbol

asset

market_type

timeframe

period

candles

ticks

statistics

metadata

health

created_at

analysis_version

---

# MarketStatistics

Campos iniciais:

total_candles

total_ticks

first_timestamp

last_timestamp

duration

average_price

highest_price

lowest_price

price_range

---

# MarketSnapshot

Campos:

current_price

last_open

last_close

last_high

last_low

last_volume

---

# MarketMetadata

Campos:

provider_name

provider_version

analysis_engine_version

generated_at

timezone

---

# MarketHealth

Campos:

status

warnings

errors

quality_score

history_ready

tick_ready

---

# MarketState

Estados:

EMPTY

BOOTSTRAPPING

LIMITED

READY

ERROR

---

# AnalysisContext

Responsável por manter:

ProviderContext

ProviderHistory

ProviderTicks

ProviderAssets

---

# Engine

Criar:

MarketAnalysisEngine

Métodos:

analyze()

build_snapshot()

build_statistics()

build_health()

build_metadata()

---

# Normalizer

Criar classe responsável por transformar Provider Models em estruturas internas.

Nenhuma lógica de indicador nesta Sprint.

---

# Statistics

Criar cálculos básicos:

contagem

máximo

mínimo

média

range

duração

---

# Health

Criar avaliação simples:

EMPTY

LIMITED

READY

ERROR

baseada apenas na disponibilidade dos dados.

---

# Exceptions

Criar:

AnalysisError

InvalidProviderData

AnalysisUnavailable

StatisticsError

---

# Compatibilidade

Não alterar:

ProviderFactory

ProviderRegistry

Pocket

Polarium

Replay

Parser

Discovery

Chart API

Frontend

Runtime Principal

Friday IA

---

# Testes

Criar cobertura para:

Engine

Models

Statistics

Snapshot

Metadata

Health

Normalizer

Exceptions

Context

Analysis vazio

Analysis completo

Provider inválido

History vazio

Ticks vazios

---

# Critérios

Todos os testes anteriores continuam verdes.

Nenhuma regressão.

Nenhuma dependência circular.

Nenhuma alteração funcional.

Apenas arquitetura.

---

# Fora do escopo

Indicadores

RSI

EMA

MACD

ATR

ADX

Bandas

Price Action

Pattern Engine

Probability Engine

Decision Engine

AutoTrade

Signals

---

# Resultado esperado

A Friday passa a possuir oficialmente sua primeira camada de Inteligência de Mercado.

Todas as futuras análises utilizarão esta arquitetura.
