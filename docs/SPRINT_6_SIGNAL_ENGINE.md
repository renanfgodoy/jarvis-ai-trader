# Sprint 6 — Signal Engine

## Objetivo

Criar o motor técnico do J.A.R.V.I.S AI TRADER para transformar candles OHLC em leitura analítica baseada em indicadores.

Esta Sprint não executa ordens e não promete lucro. Ela fornece uma leitura probabilística para apoio à decisão.

## Entregas

- Módulo `app/indicators/`
- Indicadores técnicos:
  - EMA 9
  - EMA 21
  - RSI 14
  - ATR 14
- Serviço `SignalEngineService`
- Modelo `SignalAnalysisResponse`
- Endpoint `GET /api/v1/signal/analyze`
- Testes automatizados
- Swagger atualizado

## Endpoint

```text
GET /api/v1/signal/analyze
```

Parâmetros:

- `symbol`: ativo analisado
- `timeframe`: timeframe dos candles
- `limit`: quantidade de candles, mínimo 22

## Exemplo de resposta

```json
{
  "symbol": "EURUSD-OTC",
  "timeframe": "M1",
  "candles_analyzed": 50,
  "ema9": 1.1002,
  "ema21": 1.0998,
  "rsi14": 58.4,
  "atr14": 0.00031,
  "trend": "BUY",
  "momentum": "BULLISH",
  "volatility": "NORMAL",
  "strength": 85,
  "reasons": [],
  "warnings": []
}
```

## Como testar

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
python -m uvicorn app.main:app --reload
```

Abrir:

```text
http://127.0.0.1:8000/docs
```

Testar:

```text
GET /api/v1/signal/analyze
```

## Critérios de validação

- Swagger mostra a seção `Signal Engine`.
- Endpoint `/api/v1/signal/analyze` responde 200.
- Resposta contém EMA9, EMA21, RSI14, ATR14, tendência, momentum, volatilidade e força.
- Todos os testes passam.

## Aviso operacional

Este módulo é apenas analítico. Antes de qualquer uso operacional real, será obrigatório passar por backtesting, validação em ambiente de demonstração e Risk Manager.
