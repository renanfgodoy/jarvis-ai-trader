# V0.17.0 — Professional Trading Workspace

## Objetivo
Transformar o Dashboard em uma estação operacional: gráfico como protagonista, barra de comando fixa, painel lateral compacto e melhor aproveitamento de espaço.

## Mudanças
- Gráfico central maior.
- Painel lateral com IA, Risk, Execution e Gate.
- Barra operacional com ativo, timeframe, sinal, score, payout e status do AutoTrade.
- Trading Panel compacto.
- Log operacional compacto.
- Mantém Top 12 em carrossel horizontal.

## Como testar
1. Rodar backend com `python -m uvicorn app.main:app --reload`.
2. Rodar frontend com `npm run dev`.
3. Abrir `http://localhost:5173`.
4. Selecionar M1/M5/M15.
5. Clicar em cards do Top 12 e validar sincronização com gráfico e IA.
6. Validar que zoom/crosshair do gráfico continuam funcionando.
