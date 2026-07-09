# Sprint 4 — Risk Manager Foundation

## Objetivo

Criar a primeira camada oficial de proteção de banca do J.A.R.V.I.S AI TRADER.

O Risk Manager valida uma operação antes de qualquer decisão operacional ser considerada. A ideia central é impedir overtrade, recuperação emocional, Gale agressivo e entradas acima da gestão oficial.

## Regras iniciais implementadas

- Banca base: R$200
- Entrada máxima: 5% da banca
- Stop win diário: 3 WINs
- Stop loss diário: 2 LOSSes
- Gale máximo permitido: 1
- Payout mínimo informativo: 75%
- Risk Score entre 0 e 100

## Arquivos criados

```text
app/models/risk.py
app/services/risk_manager.py
app/api/routes/risk.py
tests/test_risk_manager.py
docs/SPRINT_4_RISK_MANAGER.md
```

## Arquivos alterados

```text
app/api/router.py
app/core/config.py
app/main.py
.env.example
README.md
```

## Novo endpoint

```text
GET /api/v1/risk/check
```

## Exemplos

Operação dentro das regras:

```text
/api/v1/risk/check?bankroll=200&daily_wins=0&daily_losses=0&gale_used=0
```

Operação bloqueada por stop loss:

```text
/api/v1/risk/check?bankroll=200&daily_losses=2
```

Entrada acima de 5% da banca:

```text
/api/v1/risk/check?bankroll=200&entry_value=20
```

## Como testar no VS Code

Ativar ambiente:

```bash
source .venv/bin/activate
```

Instalar dependências:

```bash
python -m pip install -r requirements.txt
```

Subir API:

```bash
python -m uvicorn app.main:app --reload
```

Abrir Swagger:

```text
http://127.0.0.1:8000/docs
```

Rodar testes:

```bash
python -m pytest
```

Resultado esperado:

```text
14 passed
```

## Critérios de validação

- A tag `Risk Manager` aparece no Swagger.
- `/api/v1/risk/check` retorna `APPROVED` em cenário seguro.
- `/api/v1/risk/check?daily_losses=2` retorna `BLOCKED`.
- `/api/v1/risk/check?daily_wins=3` retorna `BLOCKED`.
- `/api/v1/risk/check?entry_value=20&bankroll=200` retorna `BLOCKED`.
- Todos os testes passam.

## Importante

Esta Sprint não executa operações reais e não recomenda entradas reais. É uma camada de simulação e proteção de risco para desenvolvimento.

## Próxima Sprint

Sprint 5 — Trade Journal.

O objetivo será registrar operações, resultados, score, horário, ativo, payout e status para alimentar estatísticas e aprendizado futuro.
