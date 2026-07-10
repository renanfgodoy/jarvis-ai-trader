# V0.20.1 — Polarium OAuth PKCE Lab

## Objetivo

Criar uma base segura para testar o fluxo OAuth/PKCE próprio do J.A.R.V.I.S sem reutilizar credenciais, tokens ou sessão de terceiros.

## O que foi implementado

- Gerador de `code_verifier`.
- Gerador de `code_challenge` S256.
- Endpoints de laboratório OAuth:
  - `GET /api/v1/polarium/oauth/config`
  - `POST /api/v1/polarium/oauth/start`
  - `GET /api/v1/polarium/oauth/callback`
  - `POST /api/v1/polarium/oauth/exchange`
  - `GET /api/v1/polarium/oauth/session`
  - `POST /api/v1/polarium/oauth/logout`
- Painel visual `OAuth PKCE Lab` no Dashboard.
- Cache local seguro para state/verifier/token.
- Guardrails para não expor access token no frontend.

## Variáveis de ambiente

```env
POLARIUM_OAUTH_CLIENT_ID=
POLARIUM_OAUTH_AUTHORIZE_URL=
POLARIUM_OAUTH_TOKEN_URL=https://api.trade.polariumbroker.com/auth/oauth.v5/token
POLARIUM_OAUTH_REDIRECT_URI=http://127.0.0.1:8000/api/v1/polarium/oauth/callback
```

## Segurança

- Não reutilizar `client_id`, `redirect_uri`, `code_verifier`, `access_token` ou `refresh_token` de outro app.
- AutoTrade permanece bloqueado.
- O token bruto não é exposto pela API de status.
- O endpoint `/exchange` roda por padrão em `dry_run=true`.

## Como testar

1. Rodar backend.
2. Rodar frontend.
3. Abrir Dashboard.
4. Verificar painel `OAuth PKCE Lab`.
5. Clicar em `Gerar PKCE / URL`.
6. Se não houver credenciais próprias configuradas, o painel deve mostrar `SEM CONFIG`.
7. Testar endpoints pelo Swagger apenas como debug técnico.

## Critérios de validação

- `pytest` passando.
- `npm run build` passando.
- Dashboard abrindo sem quebrar.
- Painel OAuth aparecendo.
- Nenhum token sensível mostrado no frontend.
