# Sprint 3 — AI Decision Engine V1

## Objetivo

Criar a primeira versão do motor de decisão do J.A.R.V.I.S AI TRADER.

Nesta Sprint, o sistema deixa de apenas ler candles e passa a interpretar o mercado de forma probabilística, retornando:

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

## Importante

Esta versão é baseada em regras simples e auditáveis. Ela ainda não usa machine learning e não deve ser usada como recomendação financeira ou sinal real sem backtesting e validação em ambiente de demonstração.

## Arquivos criados

```text
app/models/decision.py
app/services/ai_decision.py
app/api/routes/ai.py
tests/test_ai_decision.py
docs/SPRINT_3_AI_DECISION.md
```

## Arquivos alterados

```text
app/api/router.py
app/core/config.py
app/models/__init__.py
app/services/__init__.py
README.md
```

## Novo endpoint

```text
GET /api/v1/ai/decision
```

## Como testar

Ative o ambiente virtual:

```bash
source .venv/bin/activate
```

Instale dependências:

```bash
python -m pip install -r requirements.txt
```

Suba a API:

```bash
python -m uvicorn app.main:app --reload
```

Abra:

```text
http://127.0.0.1:8000/docs
```

Teste o endpoint:

```text
GET /api/v1/ai/decision
```

Rode os testes:

```bash
python -m pytest
```

Resultado esperado:

```text
9 passed
```

## Critérios de validação

- Swagger abre normalmente.
- A tag `AI Decision Engine` aparece no Swagger.
- O endpoint `/api/v1/ai/decision` retorna `BUY`, `SELL` ou `WAIT`.
- A resposta inclui motivos e alertas.
- Todos os testes passam.

## Próxima Sprint

Sprint 4 — Risk Manager.

O objetivo será calcular entrada recomendada, risco, limites diários, proteção de banca e bloqueio operacional após metas ou perdas.
