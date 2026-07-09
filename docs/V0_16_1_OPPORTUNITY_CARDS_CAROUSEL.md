# V0.16.1 — Opportunity Cards Carousel + Chart Below

## Objetivo

Refatorar o scanner Top 12 para um formato visual mais operacional, usando cards de oportunidades em carrossel horizontal, exibindo 3 oportunidades por página em desktop.

## Mudanças principais

- Top 12 deixou de ser uma tabela lateral.
- Oportunidades agora aparecem como cards premium no topo do workspace.
- Cards mostram ativo, timeframe, sinal, score, payout, risco, status e qualidade do dado.
- Clique no card sincroniza símbolo selecionado com gráfico e painéis da IA.
- Gráfico foi movido para baixo dos cards, com área operacional maior.
- Layout segue a ideia de vitrine de oportunidades + chart workspace.

## Como testar

1. Subir backend:

```bash
cd ~/Desktop/jarvis-ai-trader
source .venv/bin/activate
python -m pytest
python -m uvicorn app.main:app --reload
```

2. Subir frontend:

```bash
cd ~/Desktop/jarvis-ai-trader/frontend
npm install
npm run dev
```

3. Abrir:

```text
http://localhost:5173
```

## Critérios de validação

- Top 12 aparece em cards horizontais.
- Em desktop aparecem 3 cards por vez.
- Scroll horizontal funciona.
- Clicar em um card troca o ativo do gráfico.
- Gráfico fica abaixo do carrossel e continua em candlestick.
- Timeframe M1/M5/M15 continua controlando análise e AutoTrade Gate.
- Testes backend continuam passando.
