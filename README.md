# J.A.R.V.I.S AI TRADER

Sistema proprietário de apoio à decisão em Trading desenvolvido para Renan Godoy.

> Primeiro proteger a banca. Depois crescer a banca.  
> Não buscamos mais operações. Buscamos operações melhores.

## Sprint atual

**Sprint 8 — Asset Scanner Engine**

Esta Sprint cria o scanner de múltiplos ativos, retornando o Top 12 de oportunidades técnicas para observação.

## Funcionalidades atuais

- Backend em FastAPI
- Arquitetura modular
- Configuração centralizada
- Health check
- System info
- Market Reader Service
- Provider simulado de candles
- AI Decision Engine V1
- Risk Manager Foundation
- Provider Engine
- TradingView Webhook Receiver
- Signal Engine
- Execution Engine DEMO
- Asset Scanner Engine
- Models Pydantic
- Testes automatizados

## Tecnologias

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic Settings
- Pytest

## Como rodar

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Acesse:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/v1/health
http://127.0.0.1:8000/api/v1/market/snapshot
http://127.0.0.1:8000/api/v1/ai/decision
http://127.0.0.1:8000/api/v1/risk/check
http://127.0.0.1:8000/api/v1/providers
http://127.0.0.1:8000/api/v1/signal/analyze
http://127.0.0.1:8000/api/v1/execution/status
http://127.0.0.1:8000/api/v1/scanner/top-assets
```

## Como testar

```bash
python -m pytest
```

## Sprint 5 — Provider Engine

Novo endpoint para listar provedores:

```text
GET /api/v1/providers
```

Novo endpoint para receber alertas do TradingView:

```text
POST /api/v1/providers/tradingview/webhook
```

Payload de exemplo:

```json
{
  "symbol": "EURUSD-OTC",
  "timeframe": "M1",
  "signal": "BUY",
  "price": 1.17545,
  "strategy": "Jarvis v1"
}
```

Resposta esperada:

```json
{
  "received": true,
  "provider": "TradingView",
  "status": "queued"
}
```

## Aviso operacional

Os dados e alertas desta fase são usados apenas para desenvolvimento, validação de arquitetura e apoio à decisão. O sistema não promete lucro, não garante assertividade e não executa ordens automaticamente.


## Sprint 6 — Signal Engine

A Sprint 6 adiciona o primeiro motor técnico do J.A.R.V.I.S AI TRADER.

Entregas principais:

- EMA 9
- EMA 21
- RSI 14
- ATR 14
- Tendência técnica
- Momentum
- Volatilidade
- Força do sinal
- Endpoint `/api/v1/signal/analyze`

Como testar:

```bash
source .venv/bin/activate
python -m pytest
python -m uvicorn app.main:app --reload
```

Acesse:

```text
http://127.0.0.1:8000/docs
```


## Sprint 7 — Execution Engine DEMO

Novos endpoints:

```text
GET /api/v1/execution/status
POST /api/v1/execution/demo/run
```

A Sprint 7 prepara o J.A.R.V.I.S para execução em conta DEMO, mantendo conta real bloqueada durante o desenvolvimento.

Regra oficial: primeiro proteger a banca. Depois crescer a banca.


## Sprint 8 — Asset Scanner Engine

Novo endpoint:

```text
GET /api/v1/scanner/top-assets
```

A Sprint 8 adiciona o scanner que analisa múltiplos ativos, calcula leitura técnica com o Signal Engine, valida risco com o Risk Manager e retorna os melhores candidatos ranqueados.

Exemplo de uso:

```text
http://127.0.0.1:8000/api/v1/scanner/top-assets?timeframe=M1&top=12
```

Regra oficial: o scanner não executa ordens. Ele apenas encontra oportunidades para validação.

## Sprint 9 — Multi Provider Engine

A Sprint 9 adiciona o **Provider Manager**, uma camada central para escolher e abstrair a fonte de dados ativa do J.A.R.V.I.S AI TRADER.

### Objetivo

Remover o acoplamento direto entre Market Reader/Scanner e um provider específico, preparando o sistema para alternar entre:

- Simulated Provider
- TradingView Provider estrutural
- Quadcode/Polarium Provider estrutural em modo DEMO

### Novos endpoints

```text
GET /api/v1/providers/current
GET /api/v1/providers/list
```

### Como testar

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Abra:

```text
http://127.0.0.1:8000/docs
```

Depois execute:

```text
GET /api/v1/providers/current
GET /api/v1/providers/list
GET /api/v1/scanner/top-assets
```

### Testes

```bash
python -m pytest
```

Resultado esperado:

```text
37 passed
```


## Sprint 10 — Quadcode / Polarium DEMO Adapter

Esta Sprint adiciona uma camada segura para futura integração com a Polarium/Quadcode em conta DEMO.

### Novos endpoints

```text
GET  /api/v1/quadcode/status
POST /api/v1/quadcode/demo/connect
POST /api/v1/quadcode/demo/disconnect
GET  /api/v1/quadcode/symbols
POST /api/v1/quadcode/demo/order
```

### Regra de segurança

Nenhuma ordem real é enviada nesta Sprint. O adapter opera somente em `DEMO/DRY_RUN`.

### Como testar

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
python -m uvicorn app.main:app --reload
```

Resultado esperado dos testes:

```text
43 passed
```
