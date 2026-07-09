# Sprint 8 — Asset Scanner Engine

## Objetivo

Criar o primeiro scanner de oportunidades do J.A.R.V.I.S AI TRADER.

Até a Sprint 7, o sistema analisava principalmente um ativo por vez. A Sprint 8 adiciona uma camada que varre múltiplos ativos, calcula indicadores para cada um, valida risco e retorna um ranking com os melhores candidatos.

## Entregas

- `app/models/scanner.py`
- `app/services/asset_scanner.py`
- `app/api/routes/scanner.py`
- `tests/test_asset_scanner.py`
- Endpoint `GET /api/v1/scanner/top-assets`

## Como funciona

O scanner executa o fluxo:

```text
Lista de ativos
↓
Signal Engine
↓
Risk Manager
↓
Score técnico
↓
Ranking
↓
Top 12 ativos
```

## Endpoint

```text
GET /api/v1/scanner/top-assets
```

Parâmetros:

- `timeframe`: padrão `M1`
- `candle_limit`: padrão `50`
- `top`: padrão `12`
- `bankroll`: padrão `200`
- `payout`: padrão `80`

## Como testar

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Abra:

```text
http://127.0.0.1:8000/docs
```

Teste:

```text
GET /api/v1/scanner/top-assets
```

Depois rode:

```bash
python -m pytest
```

Resultado esperado:

```text
32 passed
```

## Critérios de validação

- Swagger mostra a seção `Asset Scanner`.
- Endpoint retorna até 12 ativos ranqueados.
- Cada ativo possui `rank`, `symbol`, `signal`, `score`, `risk_level`, `status`, indicadores e motivos.
- Scores vêm ordenados do maior para o menor.
- Todos os testes passam.

## Regra oficial

O scanner não executa ordens. Ele apenas encontra candidatos para observação e validações futuras.

> Não buscamos mais operações. Buscamos operações melhores.
