# Friday Trade

# Sprint V4.2

## REAL CHART DATA SOURCE DISCOVERY

### Objetivo

Parar completamente a investigação focada em WebSocket, Fetch e XHR como fonte principal do histórico.

A partir desta Sprint, descobrir exclusivamente qual estrutura de dados a própria interface da Polarium utiliza para desenhar o gráfico.

---

## Contexto

Já foi comprovado que:

- first-candles não representa histórico de uma única série;
- candles-generated representa snapshots multi-timeframe;
- candle-generated é apenas atualização incremental.

Portanto o histórico exibido pela interface provavelmente já existe em memória da própria aplicação.

---

## Escopo

Investigar somente leitura.

Nunca modificar objetos.

Nunca alterar estado React.

Nunca alterar Redux.

Nunca alterar MobX.

Nunca alterar Zustand.

Nunca alterar caches.

Nunca alterar WebSocket.

Nunca alterar Fetch.

Nunca alterar XHR.

Nunca criar candles.

Nunca reproduzir requests.

Nunca automatizar a Polarium.

---

## Investigar

Procurar estruturas relacionadas ao gráfico como:

- objetos globais
- stores
- datafeeds
- chart engine
- TradingView
- Lightweight Charts
- Redux
- MobX
- Zustand
- Context
- React internals
- cache de candles
- cache de séries
- cache de histórico

---

## Procurar estruturas contendo

active_id

timeframe

candles

bars

history

series

ohlc

chart

price

dataset

---

## Para cada candidato registrar apenas

nome sanitizado

tipo

quantidade de candles

quantidade de timestamps

quantidade de séries

active_ids distintos

raw_sizes distintos

---

## Nunca registrar

OHLC

preços

payloads

token

cookies

Authorization

SSID

credenciais

---

## Critério de sucesso

Encontrar uma estrutura que contenha:

1 active_id

1 raw_size

vários timestamps

utilizada pela própria interface da Polarium.

---

## Não implementar

Nenhum parser.

Nenhuma integração.

Nenhuma leitura pelo Friday Trade.

Nenhuma alteração no Browser Bridge.

Nenhuma alteração no MarketPipeline.

Nenhuma alteração no CandleStore.

Nenhuma alteração no Chart API.

Somente descoberta arquitetural.

---

## Entrega

Responder obrigatoriamente:

1. Estruturas encontradas.
2. Framework identificado.
3. Origem do gráfico.
4. Onde os candles ficam armazenados.
5. Existe cache?
6. Existe histórico completo?
7. Quantidade aproximada.
8. Pode ser lido passivamente?
9. Riscos.
10. Próximo passo.

Não fazer commit.

Não fazer push.