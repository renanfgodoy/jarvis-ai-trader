# Sprint 13.3 — Dashboard Trading Terminal Refactor

## Objetivo

Refatorar o dashboard do J.A.R.V.I.S AI TRADER para ficar mais próximo de uma mesa profissional de trading, com gráfico maior, scanner compacto e leitura operacional mais direta.

## Alterações principais

- Gráfico de preço ampliado.
- Candlestick sempre como padrão visual.
- Fallback visual de candles para evitar tela vazia quando o WebSocket ou REST ainda estiver carregando.
- Scanner Top 12 em formato de tabela compacta.
- Layout mais próximo da referência operacional apresentada.
- Melhor aproveitamento horizontal da tela.

## Como testar

Backend:

```bash
cd ~/Desktop/jarvis-ai-trader
source .venv/bin/activate
python -m uvicorn app.main:app --reload
```

Frontend:

```bash
cd ~/Desktop/jarvis-ai-trader/frontend
npm install
npm run dev
```

Abrir:

```text
http://localhost:5173
```

Testes:

```bash
cd ~/Desktop/jarvis-ai-trader
source .venv/bin/activate
python -m pytest
```

## Critérios de validação

- Dashboard abre sem erro.
- Gráfico aparece grande e com candles visíveis.
- Scanner Top 12 está compacto.
- Layout parece mais operacional e menos administrativo.
- Backend continua com todos os testes passando.
