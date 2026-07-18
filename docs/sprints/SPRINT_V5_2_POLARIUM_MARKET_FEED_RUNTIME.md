# SPRINT V5.2 — POLARIUM MARKET FEED RUNTIME

## Objetivo

Transformar toda a arquitetura validada durante as Sprints V5.1A → V5.1E em um Runtime oficial da Friday, capaz de consumir dados de mercado da Polarium em modo totalmente **READ-ONLY**, utilizando exclusivamente informações de mercado provenientes do canal `candles-generated`.

Esta Sprint NÃO implementa:

- Scanner
- Estratégia
- IA
- CALL
- PUT
- Entradas automáticas
- Ordens
- Compra
- Venda
- Portfolio
- Saldo
- Conta

O objetivo desta Sprint é exclusivamente criar a camada oficial de aquisição de Market Data.

---

# CONTEXTO

As Sprints anteriores comprovaram:

✅ Chrome dedicado sem extensão

✅ Sessão autenticada

✅ Identificação automática do WebSocket de mercado

✅ Runtime Guard funcional

✅ Canal `candles-generated`

✅ Multi-timeframe

✅ Ativo fora da tela continua recebendo dados

✅ Dois active_ids simultâneos

✅ Um único WebSocket alimentando múltiplos ativos

Essas provas permitem iniciar a arquitetura oficial do Provider Polarium.

---

# NOVA ARQUITETURA

A arquitetura passa a ser:

```
Chrome Dedicado

↓

Sessão autenticada

↓

Market WebSocket

↓

candles-generated

↓

Polarium Market Feed Runtime

↓

Market Router

↓

Candle Store

↓

Frontend
```

Nenhum outro componente poderá consumir diretamente o WebSocket.

Todo acesso passa obrigatoriamente pelo Runtime.

---

# RESPONSABILIDADES DO RUNTIME

O Runtime será responsável por:

## Descobrir

- Market WebSocket

## Validar

- authenticated

## Detectar

- reconnect

## Criar

- subscriptions

## Cancelar

- unsubscribe

## Receber

- candles-generated

## Normalizar

- active_id

- timestamp

- value

- bid

- ask

- candles

## Distribuir

- CandleStore

## Atualizar

- FeedQualityTracker

Nunca deverá conhecer:

- Estratégias

- Scanner

- IA

- CALL

- PUT

---

# ESTRUTURA DE PASTAS

Criar:

```
app/

market/

providers/

polarium/

runtime.py

market_feed.py

market_socket.py

market_subscription.py

market_router.py

market_store_adapter.py

runtime_guard.py

parser.py

models.py
```

Cada arquivo deverá possuir responsabilidade única.

---

# MARKET SOCKET

Responsável por:

- localizar automaticamente o WebSocket correto

- validar authenticated

- validar timeSync

- detectar reconnect

- detectar fechamento

- trocar automaticamente para novo socket de mercado

Não poderá interpretar candles.

---

# RUNTIME GUARD

Continuará obrigatório.

Permitir somente mensagens relacionadas ao mercado.

Outbound permitido:

- subscribeMessage → candles-generated

- unsubscribeMessage → candles-generated

- subscribeMessage → candle-generated

- unsubscribeMessage → candle-generated

- sendMessage → get-first-candles

Inbound permitido:

- authenticated

- timeSync

- first-candles

- candles

- candle-generated

- candles-generated

Todo o restante:

DROP

Não persistir payload.

Não imprimir payload.

Não armazenar payload.

Registrar apenas categoria sanitizada.

---

# PARSER

Criar parser dedicado.

Converter o evento recebido para um modelo interno.

Modelo:

```
MarketEvent

provider

active_id

timestamp

bid

ask

value

candles

60

300

900
```

Sem lógica de estratégia.

---

# MARKET ROUTER

Responsável apenas por distribuir.

Entrada:

```
active_id
```

Saída:

```
Store(active_id,60)

Store(active_id,300)

Store(active_id,900)
```

Sem alterar candles.

Sem recalcular candles.

---

# CANDLE STORE ADAPTER

Responsável apenas por atualizar o CandleStore existente.

Não modificar arquitetura atual.

Não criar Store paralela.

---

# FEED QUALITY

Atualizar o FeedQualityTracker.

Agora ele deverá medir:

- qualidade do ativo

- estabilidade

- p50

- p95

- gaps

utilizando apenas o fluxo plural.

---

# FRONTEND

Não alterar layout.

Não alterar MarketChart.

Não alterar Friday Strategy.

Não alterar Scanner.

Nenhuma mudança visual nesta Sprint.

---

# TESTES

Criar testes para:

## Runtime

- descoberta do socket

- reconnect

- authenticated

## Parser

- candles-generated

- candle-generated

## Router

- active_id

- M1

- M5

- M15

## Runtime Guard

- mensagens permitidas

- mensagens bloqueadas

## Feed

- dois ativos

- três timeframes

---

# BUILD

Executar:

```
pytest
```

Depois:

```
npm run build
```

Não prosseguir caso existam falhas.

---

# GIT

Não executar:

- git add

- commit

- push

---

# ENTREGA ESPERADA

O Forge deverá entregar obrigatoriamente:

1. Arquitetura criada

2. Arquivos criados

3. Arquivos modificados

4. Fluxo completo

5. Runtime Guard

6. Parser

7. Router

8. Feed

9. CandleStore Adapter

10. FeedQuality

11. Testes executados

12. Resultado dos testes

13. Build

14. Performance

15. CPU

16. Memória

17. git status

18. git diff

19. Riscos encontrados

20. Próximos passos

Não implementar Scanner.

Não implementar IA.

Não implementar Estratégia.

Não alterar Runtime IQ.

Não alterar MarketChart.

Não alterar Friday Strategy.

Não consultar saldo.

Não consultar ordens.

Não consultar portfolio.

Não consultar conta.

Não fazer commit.

Não fazer push.