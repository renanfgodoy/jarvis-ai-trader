# V0.17.1 — Chart Symbol Sync Fix

## Objetivo

Corrigir a sincronização entre o card selecionado no Top 12, o ativo/timeframe ativo e o gráfico candlestick.

## Correções

- Ao trocar de ativo ou timeframe, o WebSocket antigo é limpo.
- Dados antigos não são mais usados quando o símbolo/timeframe muda.
- O gráfico só consome candles do contexto atual.
- Fallback visual do gráfico agora muda por ativo/timeframe, evitando aparência de gráfico parado.
- Zoom é preservado durante updates do mesmo ativo/timeframe.
- Ao trocar ativo/timeframe, o gráfico carrega novo dataset e reposiciona a visualização.

## Como testar

1. Subir backend.
2. Subir frontend.
3. Clicar em diferentes cards do Top 12.
4. Confirmar que o título, candles, IA e Risk acompanham o ativo selecionado.
5. Trocar M1/M5/M15 e confirmar que o gráfico atualiza.
6. Dar zoom no gráfico e confirmar que ele não reseta durante updates do mesmo ativo.
