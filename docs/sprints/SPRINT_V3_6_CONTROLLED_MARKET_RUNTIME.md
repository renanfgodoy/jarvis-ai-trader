# FRIDAY TRADE V3.6

# CONTROLLED MARKET RUNTIME

Status

PLANNED

---

# Objetivo

Implementar o primeiro Runtime Controlado do Friday Trade.

Esta Sprint deverá permitir alimentar o Market Pipeline com mensagens sanitizadas durante o desenvolvimento.

O objetivo é validar todo o fluxo:

Mensagem
↓

Market Event Engine

↓

Market Pipeline

↓

Candle Store

↓

Chart Runtime API

↓

Frontend

↓

Real Candle Chart

Sem utilizar WebSocket real.

Sem utilizar Connector.

Sem utilizar credenciais.

Sem utilizar OAuth.

---

# IMPORTANTE

Não alterar:

Connector

Providers

Polarium

OAuth

Autenticação

Frontend do gráfico

Indicator Engine

---

# Criar

app/market/runtime_feed.py

Responsável por:

receber mensagens sanitizadas

executar:

MarketPipeline.process()

Nada mais.

---

# Criar

app/api/routes/runtime_feed.py

Endpoint DEV ONLY

POST

/api/v1/runtime/feed

Recebe:

uma mensagem sanitizada

Executa:

runtime_feed

Retorna:

PipelineResult

---

# Segurança

O endpoint deve existir somente para desenvolvimento.

Adicionar aviso claro:

Development Runtime Only

Nunca conectar à Polarium.

Nunca abrir WebSocket.

Nunca aceitar HAR bruto.

Nunca aceitar cookies.

Nunca aceitar Authorization.

Nunca aceitar Bearer.

Nunca aceitar credenciais.

---

# Frontend

Nenhuma alteração visual.

O gráfico deverá continuar usando:

GET

/api/v1/market/chart

A única diferença é que agora haverá dados reais no Candle Store.

---

# Testes

Criar:

tests/market/runtime/

Cobrir:

pipeline vazio

mensagem candle-generated

mensagem first-candles

duplicados

erro estruturado

store atualizado

chart api refletindo o store

duas chamadas consecutivas

---

# Como testar

Backend

pytest

Frontend

build

Rodar backend

Rodar frontend

POST

/api/v1/runtime/feed

Depois abrir:

/market-chart

Os candles deverão aparecer.

Sem refresh.

Sem snapshot.

Sem alterar código.

---

# Critérios

Nenhum WebSocket.

Nenhum Connector.

Nenhuma API externa.

Nenhuma credencial.

Somente mensagens sanitizadas.

---

# Entrega

Mesmo padrão das últimas Sprints.

Não fazer commit.

Não fazer push.