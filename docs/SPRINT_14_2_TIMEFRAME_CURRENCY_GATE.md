# Sprint 14.2 — Timeframe Control + Currency Risk Gate

## Objetivo

Adicionar a trava operacional oficial antes de qualquer análise ou AutoTrade.

## Regras implementadas

1. Timeframes permitidos: M1, M5 e M15.
2. O robô não gera sinal antes de o operador selecionar o timeframe e ativar AutoTrade.
3. AutoTrade opera somente em conta DEMO nesta fase.
4. Entrada mínima por moeda:
   - BRL: R$5,00
   - USD: US$1,00
5. O AutoTrade Gate valida:
   - conta DEMO;
   - timeframe válido;
   - moeda detectada;
   - entrada mínima respeitada;
   - Risk Manager aprovado;
   - score mínimo;
   - ativo válido;
   - WebSocket online;
   - Execution Engine READY.

## Endpoint

```text
POST /api/v1/execution/autotrade/gate
```

## Exemplo

```json
{
  "symbol": "EURUSD-OTC",
  "timeframe": "M1",
  "account_type": "DEMO",
  "currency": "BRL",
  "balance": 200,
  "entry_value": 10,
  "score": 91,
  "minimum_score": 80,
  "risk_approved": true,
  "websocket_online": true,
  "execution_ready": true,
  "asset_valid": true,
  "autotrade_requested": true
}
```

## Como testar

```bash
source .venv/bin/activate
python -m pytest
python -m uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Critérios de validação

- Backend com todos os testes passando.
- Swagger mostrando `POST /api/v1/execution/autotrade/gate`.
- Dashboard exibindo seletor M1/M5/M15.
- AutoTrade bloqueado sem timeframe.
- AutoTrade bloqueado antes do clique.
- BRL abaixo de R$5 bloqueado.
- USD abaixo de US$1 bloqueado.
- Operação válida em DEMO liberada pelo Gate.
