# FRIDAY TRADE V3.1

# CANDLE STORE FOUNDATION

Status

PLANNED

---

## Objetivo

Criar a primeira implementação do Candle Store do Friday Trade.

O Candle Store será responsável por armazenar em memória candles normalizados produzidos pelo Market Event Engine.

Não conectar ao WebSocket real.

Não alterar frontend.

Não alterar Connector.

Não alterar APIs.

Não criar indicadores.

Não criar IA.

Não criar Probability Engine.

Não criar sinais.

---

## Arquitetura

Criar:

app/market/store/

    __init__.py

    candle_store.py

    repository.py

    types.py

Criar testes:

tests/market/store/

---

## Responsabilidades

O Candle Store deve:

- armazenar candles por active_id

- armazenar por raw_size

- ordenar por timestamp inicial

- impedir duplicação

- atualizar candle existente quando necessário

- limitar quantidade máxima por série

- permitir consulta dos últimos N candles

- manter estrutura pronta para indicadores

---

## Não fazer

Não abrir WebSocket.

Não integrar Connector.

Não criar runtime.

Não alterar frontend.

Não criar EMA.

Não criar RSI.

Não criar MACD.

Não criar IA.

---

## Regras

symbol continua None

timeframe continua None

mapping_verified continua False

---

## Testes obrigatórios

Adicionar candle.

Atualizar candle existente.

Ignorar duplicado.

Ordenação correta.

Limite máximo.

Consulta últimos N.

Separação por active_id.

Separação por raw_size.

Coleção vazia.

Persistência somente em memória.

---

## Critérios

100% passivo.

100% testável.

Sem runtime.

Sem frontend.

Sem APIs.

Sem Connector.

Sem WebSocket.

---

## Entrega

Mesmo padrão das Sprints anteriores.

Não fazer commit.

Não fazer push.