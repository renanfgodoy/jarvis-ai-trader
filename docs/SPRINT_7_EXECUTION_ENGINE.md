# Sprint 7 — Execution Engine DEMO

## Objetivo

Criar a primeira camada de execução do J.A.R.V.I.S AI TRADER em modo seguro, preparada para conta DEMO.

Esta Sprint **não envia ordens reais**. Ela cria a arquitetura base do Executor para que futuras integrações com Polarium/Quadcode sejam feitas com segurança.

## Entregas

- `app/models/execution.py`
- `app/execution/demo_executor.py`
- `app/api/routes/execution.py`
- `tests/test_execution_engine.py`
- Atualização do router da API
- Versão do projeto `0.7.0`

## Endpoints

### Status do Execution Engine

```text
GET /api/v1/execution/status
```

### Simulação de execução em conta DEMO

```text
POST /api/v1/execution/demo/run
```

Payload:

```json
{
  "symbol": "EURUSD-OTC",
  "timeframe": "M1",
  "signal": "BUY",
  "bankroll": 200,
  "entry_value": 10,
  "daily_wins": 0,
  "daily_losses": 0,
  "gale_used": 0,
  "payout": 80,
  "expiration_minutes": 1,
  "mode": "DEMO"
}
```

Resposta esperada:

```json
{
  "status": "SIMULATED",
  "allowed": true,
  "mode": "DEMO",
  "provider": "Polarium Demo Adapter",
  "account_type": "DEMO",
  "action": "SIMULATED_BUY_ORDER",
  "result": "PENDING_DEMO_RESULT"
}
```

## Regras de segurança

- Conta real bloqueada durante desenvolvimento.
- Somente DEMO ou DRY_RUN são permitidos nesta fase.
- Nenhuma ordem real é enviada pela Sprint 7.
- Toda execução passa pelo Risk Manager.
- Stop diário e limite de entrada continuam obrigatórios.

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

Validar:

- `GET /api/v1/execution/status`
- `POST /api/v1/execution/demo/run`

## Critérios de validação

- Swagger mostra a seção `Execution Engine`.
- Status retorna `demo_only=true`.
- Execução aprovada retorna `SIMULATED`.
- Stop loss ou entrada acima de 5% bloqueia a execução.
- Todos os testes passam.
