# Polarium HAR Candle Evidence Sanitized

Sprint: V2.8 — HAR Candle Evidence Extraction

Fonte privada analisada: `.jarvis_cache/evidence/trade.polariumbroker.com.har`.

Este documento contém somente pequenos trechos sanitizados de dados de mercado. Material privado de sessão, autenticação, cabeçalhos e identificadores pessoais foi omitido.

## Resumo da captura

- Entradas HAR inspecionadas: 1
- Mensagens WebSocket encontradas: 3348
- Mensagens WebSocket com termos de mercado: 2713

## Eventos observados

- `get-first-candles`: CONFIRMADO (3 ocorrência(s) observada(s)).
- `first-candles`: CONFIRMADO (3 ocorrência(s) observada(s)).
- `candle-generated`: CONFIRMADO (209 ocorrência(s) observada(s)).
- `candles-generated`: CONFIRMADO (6 ocorrência(s) observada(s)).
- `digital-option-client-price-generated`: CONFIRMADO (193 ocorrência(s) observada(s)).
- `timeSync`: CONFIRMADO (214 ocorrência(s) observada(s)).
- `subscribeMessage`: CONFIRMADO (127 ocorrência(s) observada(s)).
- `unsubscribeMessage`: CONFIRMADO (53 ocorrência(s) observada(s)).

## Campos de mercado observados

- `active_id`: CONFIRMADO (5014 ocorrência(s)).
- `size`: CONFIRMADO (223 ocorrência(s)).
- `duration`: NÃO CONFIRMADO.
- `timeframe`: NÃO CONFIRMADO.
- `from`: CONFIRMADO (1035 ocorrência(s)).
- `to`: CONFIRMADO (1036 ocorrência(s)).
- `timestamp`: CONFIRMADO (1 ocorrência(s)).
- `time`: CONFIRMADO (2212 ocorrência(s)).
- `open`: CONFIRMADO (35806 ocorrência(s)).
- `high`: NÃO CONFIRMADO.
- `low`: NÃO CONFIRMADO.
- `close`: CONFIRMADO (35692 ocorrência(s)).
- `min`: CONFIRMADO (1530 ocorrência(s)).
- `max`: CONFIRMADO (1530 ocorrência(s)).
- `volume`: CONFIRMADO (1616 ocorrência(s)).
- `price`: NÃO CONFIRMADO.
- `instrument_id`: NÃO CONFIRMADO.
- `symbol`: CONFIRMADO (7168 ocorrência(s)).

## Estrutura real confirmada para candles

- `first-candles` retorna `candles_by_size` com chaves numéricas de tamanho/duração e candles contendo `from`, `to`, `open`, `close`, `min`, `max` e `volume`.
- `max` é o melhor candidato observado para `high`.
- `min` é o melhor candidato observado para `low`.

## Mapeamento de timeframe

- `60`: PARCIAL (120 ocorrência(s)); representa tamanho/duração observado, mas exige correlação visual para rotular M1/M5/M15.
- `300`: PARCIAL (109 ocorrência(s)); representa tamanho/duração observado, mas exige correlação visual para rotular M1/M5/M15.
- `1`: PARCIAL (3 ocorrência(s)); representa tamanho/duração observado, mas exige correlação visual para rotular M1/M5/M15.
- `10`: PARCIAL (3 ocorrência(s)); representa tamanho/duração observado, mas exige correlação visual para rotular M1/M5/M15.
- `120`: PARCIAL (3 ocorrência(s)); representa tamanho/duração observado, mas exige correlação visual para rotular M1/M5/M15.
- `14400`: PARCIAL (3 ocorrência(s)); representa tamanho/duração observado, mas exige correlação visual para rotular M1/M5/M15.
- `15`: PARCIAL (3 ocorrência(s)); representa tamanho/duração observado, mas exige correlação visual para rotular M1/M5/M15.
- `1800`: PARCIAL (3 ocorrência(s)); representa tamanho/duração observado, mas exige correlação visual para rotular M1/M5/M15.
- `2592000`: PARCIAL (3 ocorrência(s)); representa tamanho/duração observado, mas exige correlação visual para rotular M1/M5/M15.
- `28800`: PARCIAL (3 ocorrência(s)); representa tamanho/duração observado, mas exige correlação visual para rotular M1/M5/M15.
- `30`: PARCIAL (3 ocorrência(s)); representa tamanho/duração observado, mas exige correlação visual para rotular M1/M5/M15.
- `3600`: PARCIAL (3 ocorrência(s)); representa tamanho/duração observado, mas exige correlação visual para rotular M1/M5/M15.

## Mapeamento de ativo

- `active_id=76`: PARCIAL (229 ocorrência(s)); o HAR não comprova o símbolo visual correspondente.
- `active_id=2298`: PARCIAL (35 ocorrência(s)); o HAR não comprova o símbolo visual correspondente.
- `active_id=77`: PARCIAL (14 ocorrência(s)); o HAR não comprova o símbolo visual correspondente.
- `active_id=78`: PARCIAL (14 ocorrência(s)); o HAR não comprova o símbolo visual correspondente.
- `active_id=79`: PARCIAL (14 ocorrência(s)); o HAR não comprova o símbolo visual correspondente.
- `active_id=80`: PARCIAL (14 ocorrência(s)); o HAR não comprova o símbolo visual correspondente.
- `active_id=81`: PARCIAL (14 ocorrência(s)); o HAR não comprova o símbolo visual correspondente.
- `active_id=84`: PARCIAL (14 ocorrência(s)); o HAR não comprova o símbolo visual correspondente.
- `active_id=86`: PARCIAL (14 ocorrência(s)); o HAR não comprova o símbolo visual correspondente.
- `active_id=1380`: PARCIAL (14 ocorrência(s)); o HAR não comprova o símbolo visual correspondente.

## Subscription

- PARCIAL: `subscribeMessage` aparece 127 vez(es), mas a relação exata com candle/timeframe ainda exige validação dirigida.

## Amostras sanitizadas

### `get-first-candles`

- Direção: `send`
- Classificação: `CONFIRMADO`

```json
{
  "request_id": "80",
  "name": "sendMessage",
  "msg": {
    "name": "get-first-candles",
    "body": {
      "active_id": 76
    }
  }
}
```

### `first-candles`

- Direção: `receive`
- Classificação: `CONFIRMADO`

```json
{
  "request_id": "80",
  "name": "first-candles",
  "status": 2000,
  "msg": {
    "body": {
      "candles_by_size": {
        "60": {
          "from": 1778475660,
          "to": 1778475720,
          "open": 1.201705,
          "close": 1.201425,
          "min": 1.201405,
          "max": 1.201825,
          "volume": 0
        },
        "300": {
          "from": 1757739900,
          "to": 1757740200,
          "open": 1.138605,
          "close": 1.138015,
          "min": 1.137295,
          "max": 1.139265,
          "volume": 0
        },
        "900": {
          "from": 1705900500,
          "to": 1705901400,
          "open": 1.013755,
          "close": 1.014425,
          "min": 1.013465,
          "max": 1.015035,
          "volume": 0
        }
      }
    }
  }
}
```

### `candle-generated`

- Direção: `receive`
- Classificação: `CONFIRMADO`

```json
{
  "name": "candle-generated",
  "msg": {
    "body": {
      "active_id": 76,
      "size": 60,
      "from": 1783721940,
      "to": 1783722000,
      "open": 1.162275,
      "close": 1.162145,
      "min": 1.162145,
      "max": 1.162395,
      "volume": 0
    }
  }
}
```

### `candles-generated`

- Direção: `receive`
- Classificação: `CONFIRMADO`

```json
{
  "name": "candles-generated",
  "msg": {
    "body": {
      "active_id": 76,
      "value": 1.162715
    }
  }
}
```

### `digital-option-client-price-generated`

- Direção: `receive`
- Classificação: `CONFIRMADO`

```json
{
  "name": "digital-option-client-price-generated"
}
```

### `timeSync`

- Direção: `receive`
- Classificação: `CONFIRMADO`

```json
{
  "name": "timeSync"
}
```

### `subscribeMessage`

- Direção: `send`
- Classificação: `CONFIRMADO`

```json
{
  "request_id": "s_2",
  "name": "subscribeMessage",
  "msg": {
    "name": "profile-changed"
  }
}
```

### `unsubscribeMessage`

- Direção: `send`
- Classificação: `CONFIRMADO`

```json
{
  "request_id": "s_2",
  "name": "unsubscribeMessage",
  "msg": {
    "name": "profile-changed"
  }
}
```

## Limitações

- O HAR confirma eventos e campos, mas não comprova sozinho o vínculo visual entre `active_id` e nome do ativo.
- Os valores de tamanho/duração observados ainda precisam ser correlacionados com a seleção visual de timeframe.
- Nenhuma rotina runtime foi criada nesta Sprint.
- O adapter não foi alterado porque a Sprint pediu evidência documental e não integração funcional.
