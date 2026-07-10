# V0.22.0 — Polarium Connection Diagnostic Lab

## Objetivo

Parar de tentar conectar no escuro e criar uma camada de diagnóstico verificável para OAuth, WebSocket e Stream de eventos da Polarium.

## O que foi adicionado

- `GET /api/v1/polarium/diagnostics/summary`
- `GET /api/v1/polarium/diagnostics/oauth`
- `POST /api/v1/polarium/diagnostics/websocket`
- `POST /api/v1/polarium/diagnostics/stream`
- Painel React **Diagnostics Lab** no dashboard.

## Como testar

### Backend

```bash
cd ~/Desktop/jarvis-ai-trader
source .venv/bin/activate
python -m pytest
python -m uvicorn app.main:app --reload
```

### Frontend

```bash
cd ~/Desktop/jarvis-ai-trader/frontend
npm install
npm run dev
```

Abra:

```text
http://localhost:5173
```

## Validação no Dashboard

No painel **Diagnostics Lab**:

1. Clique em **OAuth**.
2. Confirme PKCE OK.
3. Confirme se Client ID está OK ou WARN.
4. Clique em **WS**.
5. Veja se o WebSocket abre, falha ou fica sem mensagem.
6. Clique em **Stream** com o payload exemplo.
7. Confirme se detecta:
   - `marginal-balance`
   - `candle-generated`
   - `digital-option-client-price-generated`

## Prints para enviar ao J.A.R.V.I.S

- Painel Diagnostics completo.
- Resultado OAuth.
- Resultado WebSocket.
- Resultado Stream.
- Console F12 se der erro.

## Commit somente depois de validar

```bash
git add .
git commit -m "feat(v0.22.0): polarium connection diagnostic lab"
git push origin main
```
