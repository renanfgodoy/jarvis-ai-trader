# Sprint 13.1 — Dashboard Refactor

## Objetivo

Refatorar o Live Trading Workspace para priorizar o gráfico de candlestick, deixando as velas maiores, mais visíveis e mais próximas de uma plataforma profissional de trading.

## Alterações principais

- O gráfico deixou de dividir espaço com o painel lateral de indicadores.
- O ChartCard agora usa largura total da área principal.
- O CandlestickChart foi ampliado para altura mínima de 640px.
- A quantidade de candles visíveis foi reduzida para aumentar a leitura visual.
- Candles, pavios, volume e médias móveis foram redesenhados com mais contraste.
- Adicionada EMA 200 visual.
- Indicadores foram movidos para cards abaixo do gráfico.
- Layout do dashboard agora usa scanner lateral + gráfico principal.

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

Testes:

```bash
cd ~/Desktop/jarvis-ai-trader
source .venv/bin/activate
python -m pytest
```

## Critérios de validação

- Dashboard abre em `http://localhost:5173`.
- Gráfico ocupa muito mais espaço horizontal e vertical.
- Velas candlestick ficam claramente visíveis.
- EMA 9, EMA 21, EMA 200 e volume aparecem no gráfico.
- Testes backend continuam passando.

## Commit sugerido

```bash
git add .
git commit -m "refactor(sprint-13): enlarge live candlestick workspace"
git push origin main
```
