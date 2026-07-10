# V0.20.2 — Polarium Direct Login Lab

## Objetivo

Testar uma camada própria do J.A.R.V.I.S para login direto usando apenas credenciais da conta Polarium do usuário em `.env` local.

## Regras de segurança

- Não usar tokens ou credenciais do TradeAutoPilot.
- Não salvar senha no código.
- Não commitar `.env` real.
- Primeiro teste é somente leitura/sessão.
- AutoTrade fica bloqueado até conta DEMO, moeda e saldo real serem confirmados.

## Endpoints

- `GET /api/v1/polarium/direct/config`
- `POST /api/v1/polarium/direct/probe`
- `GET /api/v1/polarium/direct/session`
- `POST /api/v1/polarium/direct/logout`

## Como testar

1. Copie `.env.example` para `.env`.
2. Configure `POLARIUM_DIRECT_LOGIN_URL`, `POLARIUM_DIRECT_EMAIL` e `POLARIUM_DIRECT_PASSWORD`.
3. Rode o backend e o frontend.
4. No dashboard, use o painel `Direct Login Lab`.
5. Comece com `dry_run` ligado.
6. Só desligue `dry_run` depois de confirmar que o endpoint de login está correto.

## Resultado esperado

- Sem configuração: status `MISSING_CONFIG`.
- Dry run com configuração: status `DRY_RUN`.
- Login real bem-sucedido: status `SESSION_STORED`.
- Login rejeitado: status `NOT_AUTHORIZED` ou `LOGIN_FAILED`.
