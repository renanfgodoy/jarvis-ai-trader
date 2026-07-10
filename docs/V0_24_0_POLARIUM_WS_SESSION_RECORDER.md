# V0.24.0 — Polarium WS Session Recorder

## Objetivo

A V0.24.0 adiciona um laboratório para analisar mensagens reais copiadas da aba **Network → WebSocket → Messages/Frames** do Chrome.

A Sprint não tenta operar nem reutilizar tokens. Ela apenas classifica frames para descobrir:

- mensagens de autenticação/sessão;
- mensagens de saldo (`marginal-balance`, `balances`, `subscription-balance-changed`);
- candles (`candle-generated`);
- preços/payout (`digital-option-client-price-generated`);
- primeira sequência de subscribe/auth após o WebSocket abrir.

## Como testar

1. Abra backend e frontend.
2. Abra o TradeAutoPilot ou Polarium no Chrome.
3. DevTools → Network → Socket/WS.
4. Clique no WebSocket `101`.
5. Abra **Messages** ou **Frames**.
6. Copie as primeiras mensagens, principalmente logo após conectar.
7. Cole no painel **WS Session Recorder**.
8. Clique em **Analyze Frames**.

## Resultado esperado

- `Frames parseados`: OK quando reconhecer JSON.
- `Auth candidates`: OK se houver mensagens de autenticação/sessão.
- `Balance stream`: OK se houver saldo.
- `Candle stream`: OK se houver candles.
- `Price stream`: OK se houver preços/payout.

## Critério de aprovação

A sprint é aprovada quando o painel identifica pelo menos candles/preços/saldo ou aponta claramente que faltaram frames iniciais de auth/subscribe.
