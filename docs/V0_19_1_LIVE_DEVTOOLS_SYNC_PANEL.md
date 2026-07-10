# V0.19.1 — Live DevTools Sync Panel

## Objetivo
Permitir testar no Dashboard o payload real `marginal-balance` capturado no WebSocket da Polarium.

## Segurança
- Não conecta automaticamente na Polarium.
- Não salva senha.
- Não envia ordens.
- AutoTrade continua condicionado ao Gate.

## Como testar
1. Faça login/cache no painel Polarium.
2. No DevTools da Polarium, copie uma mensagem `marginal-balance`.
3. Cole no campo Live Sync DevTools.
4. Clique em Aplicar Payload Real.
5. Confira saldo, moeda, mínimo e gate.
