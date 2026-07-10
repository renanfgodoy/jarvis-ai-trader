# V0.16.2 — Instant Timeframe Scanner

## Objetivo

Separar análise de execução. O operador não precisa ativar AutoTrade para o J.A.R.V.I.S analisar os melhores ativos.

## Regra operacional

1. O operador seleciona M1, M5 ou M15.
2. O Scanner recalcula automaticamente o Top 12 para o timeframe selecionado.
3. O gráfico, IA e Market Intelligence acompanham o timeframe.
4. O AutoTrade fica responsável apenas pela execução DEMO quando o gate aprovar.
5. Ao trocar o timeframe, o modo AutoTrade é pausado por segurança.

## Como testar

- Abrir o dashboard.
- Clicar em M1, M5 e M15 sem ativar AutoTrade.
- Confirmar que os cards do Top 12 e a IA atualizam automaticamente.
- Confirmar que o AutoTrade continua como modo de execução, não como gatilho de análise.
