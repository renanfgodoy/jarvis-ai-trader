# V0.19.0 — Live Account Sync Bridge

## Objetivo
Consolidar o parser do payload real `marginal-balance` observado no WebSocket da Polarium e alimentar o estado de conta do J.A.R.V.I.S sem inventar saldo.

## O que entra
- Parser seguro para `marginal-balance`, `balances` e `subscription-balance-changed`.
- Endpoint `POST /api/v1/polarium/debug/ws-message` para colar payload real do DevTools.
- Endpoint `GET /api/v1/polarium/account/state` para ler o estado atual.
- Dashboard passa a aceitar `DEVTOOLS_PAYLOAD` como fonte sincronizada para testes.
- BRL mínimo R$5 e USD mínimo US$1.

## Segurança
Esta Sprint **não** conecta automaticamente na Polarium, **não** replica autenticação externa e **não** envia ordens. Ela apenas interpreta payloads fornecidos pelo operador para validar a integração.
