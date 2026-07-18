# SPRINT PROVIDER V2 ARCHITECTURE

## Objetivo

Criar a arquitetura definitiva de Providers da Friday AI Trader.

A partir desta Sprint, nenhuma parte da IA, Chart API, Frontend, CandleStore ou Runtime Principal poderá conhecer detalhes específicos de qualquer corretora.

Todo acesso deverá ocorrer através da interface única MarketProvider.

---

# Objetivos da Sprint

Esta Sprint NÃO implementa funcionalidades novas.

Ela reorganiza a arquitetura para suportar múltiplos providers.

Exemplos:

- Pocket
- Polarium
- Quotex
- Avalon
- futuros providers

---

# Arquitetura desejada

Friday

↓

MarketProvider Interface

↓

PocketProvider
PolariumProvider
QuotexProvider

↓

Market Runtime

↓

Chart API

↓

Frontend

---

# Interface obrigatória

Todo provider deverá implementar exatamente os seguintes contratos.

start()

stop()

status()

get_context()

get_assets()

get_history()

get_ticks()

get_readiness()

health()

provider_name()

---

# Regras

Nenhum provider poderá acessar diretamente:

- Frontend
- React
- Chart API
- Runtime Principal
- Friday IA

Toda comunicação deverá passar pela interface.

---

# Pocket

Pocket passa a ser o Provider piloto.

Tudo que já foi desenvolvido permanece isolado.

Nenhum código funcional deverá ser perdido.

---

# Polarium

Polarium continua existindo.

Nenhuma alteração funcional.

Apenas adaptar futuramente para implementar a interface.

---

# Chart API

Chart API deixa de conhecer Pocket ou Polarium.

Ela conhece apenas:

MarketProvider

---

# CandleStore

Nenhuma alteração funcional.

Apenas receberá dados do Provider ativo.

---

# Runtime

Runtime passa a trabalhar somente com:

ProviderContext

ProviderHistory

ProviderTicks

ProviderAssets

---

# IA

A IA nunca saberá qual corretora está sendo utilizada.

Ela receberá apenas:

Candles

Ticks

Readiness

Context

Indicators

Statistics

---

# ProviderContext

Criar estrutura única contendo:

provider

asset

symbol

timeframe

period

connection_state

history_state

readiness

last_price

history_count

timestamp

---

# ProviderHistory

Lista normalizada de candles.

Sem formato específico da corretora.

---

# ProviderTick

Tick normalizado.

timestamp

price

asset

---

# ProviderAssets

Lista normalizada.

symbol

display_name

market_type

supported_periods

---

# Estrutura de diretórios

app/

market/

providers/

base/

contracts.py

provider.py

models.py

registry.py

Pocket/

Polarium/

Quotex/

Avalon/

---

# Registry

Criar ProviderRegistry.

Responsável por:

register()

unregister()

get()

list()

current()

set_current()

---

# Provider Factory

Criar ProviderFactory.

Recebe configuração.

Retorna provider correto.

---

# Dependency Injection

Nenhuma classe poderá instanciar diretamente Pocket ou Polarium.

Sempre utilizar Factory ou Registry.

---

# Segurança

Nenhuma alteração em:

Autotrade

Operações

Saldo

Ordens

Login

Credenciais

Cookies

Tokens

---

# Testes

Adicionar cobertura para:

registro

factory

injeção

provider fake

provider mock

troca de provider

isolamento

contratos

---

# Critérios

Todos os providers existentes continuam compilando.

Nenhum teste anterior quebra.

Nenhum endpoint muda.

Nenhuma tela muda.

Nenhuma funcionalidade muda.

Apenas arquitetura.

---

# Fora do escopo

Não integrar Pocket.

Não integrar Polarium.

Não alterar Frontend.

Não alterar Chart API.

Não alterar IA.

Não alterar Runtime funcional.

---

# Resultado esperado

A Friday passa a possuir arquitetura desacoplada de corretoras.

Qualquer novo provider poderá ser conectado implementando apenas a interface MarketProvider.
