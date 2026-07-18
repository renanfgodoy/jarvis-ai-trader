# SPRINT PROVIDER V2.1 — POCKET PROVIDER ADAPTER

## Objetivo

Implementar o primeiro Provider oficial compatível com a arquitetura Provider V2.

Este Provider será exclusivamente da Pocket utilizando toda a infraestrutura já desenvolvida nas Sprints Pocket V1.x.

IMPORTANTE:

Esta Sprint NÃO integra Pocket ao Runtime Principal.

NÃO altera Chart API.

NÃO altera Frontend.

NÃO altera Friday IA.

NÃO altera Polarium.

Apenas cria o adapter.

---

# Arquitetura

Pocket Runtime

↓

PocketProviderAdapter

↓

MarketProvider

↓

Provider Models

---

# Objetivo principal

Traduzir todos os objetos Pocket para os modelos neutros da Provider V2.

---

# Criar

PocketProviderAdapter

---

# O adapter deverá implementar

provider_name()

start()

stop()

status()

health()

get_context()

get_assets()

get_history()

get_ticks()

get_readiness()

---

# Conversões obrigatórias

PocketSessionContext

↓

ProviderContext

PocketRealtimeTick

↓

ProviderTick

PocketNormalizedCandle

↓

ProviderCandle

PocketAsset

↓

ProviderAsset

PocketAssetCatalog

↓

ProviderAssets

PocketReadiness

↓

ProviderReadiness

---

# ProviderContext

Deverá conter

provider

symbol

asset

market_type

timeframe

period

connection_state

history_state

history_count

last_price

timestamp

readiness

---

# ProviderHistory

Lista de ProviderCandle

Sem referências Pocket.

---

# ProviderTick

asset

timestamp

price

---

# ProviderAsset

symbol

display_name

market_type

supported_periods

---

# Readiness

Converter estados Pocket para

EMPTY

BOOTSTRAPPING

LIMITED

READY

ERROR

---

# Health

Converter RuntimeMetrics para

ProviderHealth

---

# Compatibilidade

Nenhuma alteração no Runtime Pocket.

Nenhuma alteração no Replay.

Nenhuma alteração no Parser.

Nenhuma alteração no Discovery.

---

# Factory

Ainda NÃO registrar automaticamente.

Criar apenas builder.

---

# Registry

Ainda NÃO registrar automaticamente.

---

# Fake

Criar FakePocketProviderAdapter.

---

# Replay

PocketReplayTransport deve continuar funcionando.

---

# Segurança

Não conectar Pocket.

Não abrir Chrome.

Não usar CDP.

Não enviar Socket.IO.

Não alterar login.

Não alterar credenciais.

---

# Testes

Criar testes para

ProviderContext

ProviderHistory

ProviderTick

ProviderAsset

ProviderHealth

Adapter

Fake Adapter

Replay Adapter

Conversões

Readiness

Health

Lifecycle

---

# Critérios

Todos os testes anteriores continuam verdes.

Pocket continua funcionando isoladamente.

Provider V2 passa a possuir um provider concreto.

---

# Fora do escopo

Chart API

Frontend

Runtime principal

Friday IA

Polarium

AutoTrade

---

# Resultado esperado

Pocket torna-se o primeiro Provider compatível com Provider V2.

Nenhuma integração funcional ainda será realizada.
