# V0.20.3 — Polarium OAuth Authorize Flow

## Objetivo

Corrigir a V0.20.2 adicionando a URL de autorização OAuth mapeada:

- `https://api.trade.polariumbroker.com/auth/oauth.v5/authorize`
- `https://api.trade.polariumbroker.com/auth/oauth.v5/token`

O J.A.R.V.I.S agora gera `state`, `code_verifier`, `code_challenge`, `prompt=login` e `max_age=0`.

## Segurança

- Não reutilizar credenciais/tokens de terceiros.
- AutoTrade permanece bloqueado.
- Token bruto não é exibido no frontend.

## Como testar

1. Configure `.env` com `POLARIUM_OAUTH_CLIENT_ID` próprio/autorizado.
2. Inicie backend e frontend.
3. Clique em `Gerar URL de Login`.
4. Abra o link gerado.
5. Valide se a Polarium aceita ou retorna erro de client/redirect.
