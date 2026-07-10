# SPRINT 6 — MARKET WORKSPACE

## Status

Planned

---

# Objetivo

Criar o Workspace de Mercado do Friday Trade.

Esta Sprint tem como objetivo separar definitivamente o ambiente de análise de mercado da área operacional.

O operador deve analisar o mercado em uma tela dedicada e operar em outra.

Não alterar Backend.

Não alterar APIs.

Não alterar Connector.

Não alterar Providers.

Não alterar AI.

Não alterar Risk.

Não alterar Execution.

Não instalar novas dependências.

Não alterar package.json.

---

# Contexto

Hoje o Dashboard ainda concentra elementos relacionados à análise de mercado.

O Friday Trade deve seguir uma arquitetura modular.

Cada domínio deve possuir sua própria área.

---

# Nova Página

Criar:

/markets

Adicionar na Sidebar:

📈 Markets

Posicionar entre:

Operation

Connections

Diagnostics

---

# Objetivo da Página

Concentrar tudo relacionado à leitura do mercado.

Não executar ordens.

Não conectar broker.

Não alterar conta.

Não abrir configurações.

---

# Estrutura da Página

## Cabeçalho

Mostrar:

Friday Trade

Markets

Última atualização

Timeframe selecionado

Mercado atual

Broker conectado

Ambiente

---

## Área 1

Scanner

Reutilizar Scanner existente.

Caso ainda esteja acoplado ao Dashboard:

Extrair para Widget.

Criar:

MarketScannerWidget

---

## Área 2

Watchlist

Criar lista de ativos favoritos.

Inicialmente:

EUR/USD

GBP/USD

USD/JPY

BTC/USD

EUR/JPY

Os dados podem utilizar os serviços atuais.

Não criar backend novo.

---

## Área 3

Market Status

Criar cards mostrando:

Mercado

Aberto

Fechado

OTC

Conectividade

Latência

Última sincronização

Utilizar somente informações existentes.

Quando não houver dado:

Mostrar:

Não disponível

Nunca inventar status.

---

## Área 4

Timeframe

Criar seletor visual.

M1

M5

M15

H1

Ainda não alterar operação.

Apenas interface.

O objetivo é preparar futuras integrações.

---

## Área 5

Market Overview

Criar painel resumido.

Mostrar:

Quantidade de ativos

Quantidade OTC

Mercado sincronizado

Scanner ativo

Última atualização

---

# Componentização

Criar:

MarketScannerWidget

MarketOverviewWidget

MarketStatusWidget

WatchlistWidget

TimeframeSelector

Todos independentes.

Evitar componentes gigantes.

---

# Hooks

Criar somente quando necessário.

Exemplos:

useMarketStatus

useWatchlist

useMarketOverview

Não criar hooks vazios.

---

# Reutilização

Sempre reutilizar:

Card

Section

StatusBadge

Loading

EmptyState

PageContainer

PageTitle

Widgets existentes

Hooks existentes

Tipos existentes

---

# Sidebar

Adicionar:

📈 Markets

Entre:

Operation

Connections

Sem quebrar navegação existente.

---

# Operation

Remover da tela de operação tudo que pertence exclusivamente à análise de mercado.

A tela Operation deve permanecer focada em:

Saldo

Conta

AI

Risk

Orders

Logs

AutoTrade

Execução

---

# Segurança

Não exibir:

Tokens

Cookies

Headers

HAR

Authorization

Credenciais

---

# Não Fazer

Não alterar Backend.

Não alterar Connector.

Não alterar APIs.

Não alterar AI.

Não alterar Risk.

Não alterar AutoTrade.

Não alterar Providers.

Não alterar package-lock.json.

Não instalar dependências.

---

# Testes

Executar:

Frontend

npm run build

Backend

.venv/bin/python -m pytest -q

---

# COMO TESTAR

Explicar passo a passo para o Renan.

1.

Subir Backend.

2.

Subir Frontend.

3.

Abrir:

/markets

4.

Validar:

Sidebar

Header

Scanner

Watchlist

Market Status

Overview

Timeframe

Console

5.

Abrir:

/operation

Confirmar que a tela ficou mais limpa.

6.

Enviar prints:

Markets

Operation

Sidebar

Console

Build

Pytest

---

# Critérios de Aceitação

Página Markets criada.

Sidebar atualizada.

Scanner separado.

Watchlist criada.

Overview criado.

Status criado.

Timeframe criado.

Build passando.

Backend sem alteração.

Nenhuma regressão.

---

# Entrega Obrigatória

1. Objetivo

2. Plano executado

3. Arquitetura implementada

4. Componentes criados

5. Componentes reutilizados

6. Hooks criados

7. Arquivos modificados

8. Build executado

9. Resultado do Build

10. Testes executados

11. Resultado dos testes

12. Como testar

13. Critérios de aprovação

14. Riscos conhecidos

15. Débitos técnicos

16. git status --short

17. Sugestão de commit

Mensagem sugerida:

feat(frontend): introduce Market Workspace and separate market analysis from operations

---

# Regra Final

Não faça commit.

Não faça push.

Pare após entregar o relatório completo e aguarde a revisão do J.A.R.V.I.S e do Renan Godoy.
