# J.A.R.V.I.S AI TRADER

Sistema proprietário de apoio à decisão em Trading desenvolvido para Renan Godoy.

> Primeiro proteger a banca. Depois crescer a banca.  
> Não buscamos mais operações. Buscamos operações melhores.

## Sprint atual

**Sprint 2 — Market Reader Foundation**

Esta Sprint cria a fundação de leitura de mercado com candles OHLC normalizados e provider simulado para desenvolvimento seguro.

## Funcionalidades atuais

- Backend em FastAPI
- Arquitetura modular
- Configuração centralizada
- Health check
- System info
- Market Reader Service
- Provider simulado de candles
- Models Pydantic para Candle e MarketSnapshot
- Endpoints de candles e snapshot
- Testes automatizados

## Tecnologias

- Python
- FastAPI
- Uvicorn
- Pydantic Settings
- Pytest

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/v1/health
http://127.0.0.1:8000/api/v1/market/snapshot
http://127.0.0.1:8000/api/v1/market/candles?symbol=EURUSD-OTC&timeframe=M1&limit=20
```

## Como testar

```bash
pytest
```

## Aviso operacional

Os candles da Sprint 2 são simulados. Eles servem apenas para validar arquitetura e fluxo técnico. Não devem ser usados como sinal real de operação.


## Sprint 3 — AI Decision Engine V1

Esta Sprint adiciona o primeiro motor de decisão do sistema.

O J.A.R.V.I.S passa a analisar os candles do Market Reader e retornar uma decisão probabilística:

- BUY
- SELL
- WAIT
- score
- confiança
- tendência
- momentum
- volatilidade
- motivos técnicos
- alertas de risco

Novo endpoint:

```text
GET /api/v1/ai/decision
```

Como testar:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
python -m uvicorn app.main:app --reload
```

Acesse:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/v1/ai/decision
```

Status: Sprint 3 pronta para validação local.
