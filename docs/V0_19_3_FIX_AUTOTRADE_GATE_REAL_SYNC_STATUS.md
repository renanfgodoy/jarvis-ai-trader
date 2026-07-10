# V0.19.3 — Fix AutoTrade Gate + Real Sync Status

## Objetivo

Corrigir o spam de erro 422 no dashboard e deixar o fluxo de sincronização do saldo real da Polarium dentro da própria interface, sem depender do Swagger para o uso normal.

## Mudanças

- O AutoTrade Gate só é chamado quando existe payload completo: timeframe, ativo, conta DEMO, moeda, saldo, entrada, score e execução READY.
- Se o saldo/moeda ainda não foram sincronizados, o Gate fica bloqueado localmente e não gera requisições inválidas.
- Adicionado painel `Live payload parser` dentro do card Polarium para colar o JSON `marginal-balance` capturado no DevTools.
- Após aplicar o payload, o dashboard atualiza saldo, moeda, mínimo e fonte `DEVTOOLS_PAYLOAD`.
- Swagger permanece apenas como ferramenta técnica, não como fluxo normal de uso.

## Como testar

1. Subir backend e frontend.
2. Abrir o dashboard.
3. Confirmar que não aparecem chamadas repetidas 422 no Console.
4. Fazer login/cache da Polarium no painel.
5. Colar payload `marginal-balance` real no painel `Live payload parser`.
6. Confirmar que saldo, moeda e mínimo aparecem no dashboard.
7. Selecionar M1/M5/M15 e confirmar que o scanner recalcula sem acionar AutoTrade.
8. Ativar AutoTrade apenas depois do saldo/moeda sincronizados.
