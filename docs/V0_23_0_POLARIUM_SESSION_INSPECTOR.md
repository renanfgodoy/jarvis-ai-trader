# V0.23.0 — Polarium Session Inspector

## Objetivo

Adicionar uma camada de diagnóstico para analisar evidências reais do fluxo OAuth/WebSocket sem reutilizar tokens ou credenciais de terceiros.

## O que mudou

- Novo backend `Polarium Session Inspector`.
- Novo endpoint `POST /api/v1/polarium/session-inspector/har` para analisar arquivo HAR colado no dashboard.
- Novo endpoint `POST /api/v1/polarium/session-inspector/client-storage` para listar chaves suspeitas do origin atual.
- Novo painel React `Session Inspector` no dashboard.
- Mascaramento automático de dados sensíveis em respostas de diagnóstico.

## Como testar

1. Subir backend e frontend.
2. Abrir o dashboard.
3. No painel `Session Inspector`, clicar em `Storage`.
4. Colar um HAR salvo do fluxo TradeAutoPilot/Polarium em `Colar HAR com conteúdo`.
5. Clicar em `Inspect HAR`.
6. Validar se aparecem:
   - OAuth Authorize;
   - OAuth Token Exchange;
   - Callback;
   - Client/Redirect/Scope;
   - WebSocket Handshake;
   - Authorization Header;
   - Cookie Session/Auth.

## Resultado esperado

O sistema deve indicar onde há authorize, token, callback e websocket. Tokens/cookies devem aparecer mascarados.

## Critério de aprovação

A Sprint só deve ser comitada se backend, frontend e build passarem, e se o painel conseguir analisar um HAR sem quebrar o dashboard.
