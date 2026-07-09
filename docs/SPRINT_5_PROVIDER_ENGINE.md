# Sprint 5 — Provider Engine

## Objetivo

Criar a camada oficial de provedores do J.A.R.V.I.S AI TRADER, preparando o sistema para receber dados e alertas de fontes externas sem acoplar a IA diretamente a uma plataforma específica.

## O que foi implementado

- Provider Engine Service.
- Modelo de payload para webhook do TradingView.
- Provider de webhook do TradingView.
- Endpoint para listar providers disponíveis.
- Endpoint para receber alertas do TradingView.
- Testes automatizados do Provider Engine.

## Endpoints

```text
GET /api/v1/providers
POST /api/v1/providers/tradingview/webhook
```

## Payload de exemplo

```json
{
  "symbol": "EURUSD-OTC",
  "timeframe": "M1",
  "signal": "BUY",
  "price": 1.17545,
  "strategy": "Jarvis v1"
}
```

## Resposta esperada

```json
{
  "received": true,
  "provider": "TradingView",
  "status": "queued",
  "symbol": "EURUSD-OTC",
  "timeframe": "M1",
  "signal": "BUY",
  "price": 1.17545,
  "strategy": "Jarvis v1",
  "message": "TradingView webhook recebido e enfileirado para análise."
}
```

## Decisão técnica

O TradingView será usado via webhook/alertas, não como fonte raspada de dados. Isso mantém o projeto mais seguro, modular e alinhado a uma arquitetura profissional.

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

Testar no Swagger:

```text
GET /api/v1/providers
POST /api/v1/providers/tradingview/webhook
```

## Critérios de validação

- Swagger mostra a seção `Providers`.
- `GET /api/v1/providers` retorna `simulated` e `TradingView`.
- `POST /api/v1/providers/tradingview/webhook` retorna `received: true` e `status: queued`.
- Todos os testes passam.

## Aviso operacional

Este módulo não executa ordens. Ele apenas recebe alertas para análise futura pelo AI Decision Engine e pelo Risk Manager.
