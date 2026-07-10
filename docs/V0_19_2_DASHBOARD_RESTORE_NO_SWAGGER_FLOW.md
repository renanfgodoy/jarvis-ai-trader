# V0.19.2 — Dashboard Restore + No Swagger Flow

## Objetivo

Corrigir o fluxo de uso da V0.19.x para que o J.A.R.V.I.S AI TRADER não dependa do Swagger no uso normal.

## Entregas

- Dashboard restaurado.
- Painel Polarium mais limpo.
- Removido o bloco de colar payload manual do painel principal.
- Swagger permanece apenas como ferramenta de debug técnico.
- AutoTrade continua bloqueado sem conta DEMO, moeda, saldo e mínimo sincronizados.

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

Abrir:

```text
http://localhost:5173
```

## Critérios de validação

- Dashboard abre sem tela branca.
- Gráfico candlestick continua funcionando.
- Cards Top 12 continuam clicáveis.
- M1/M5/M15 continuam recalculando o scanner.
- Painel Polarium não exige Swagger para o fluxo normal.
- Não aparece saldo fake.
- AutoTrade segue bloqueado sem saldo real sincronizado.
