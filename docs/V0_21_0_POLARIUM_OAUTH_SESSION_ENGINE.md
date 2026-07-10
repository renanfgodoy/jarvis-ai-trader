# V0.21.0 — Polarium OAuth Session Engine

## Objetivo
Remover o fluxo Direct Login com e-mail/senha e estabilizar a base OAuth/PKCE.

## Mudanças
- `Settings` agora aceita variáveis OAuth da Polarium sem quebrar o backend.
- `.env.example` atualizado para OAuth/PKCE.
- `extra="ignore"` evita crash se sobrarem variáveis antigas no `.env`.
- Dashboard não exibe mais o painel Direct Login Lab.
- Fluxo normal: gerar URL, abrir login, receber callback, trocar code por token quando houver `client_id` autorizado.

## Como testar
1. Limpe o `.env` antigo ou mantenha só variáveis `POLARIUM_OAUTH_*`.
2. Rode backend e frontend.
3. Abra o dashboard.
4. Clique em Gerar URL de Login.
5. Sem `POLARIUM_OAUTH_CLIENT_ID`, deve mostrar SEM CONFIG.
6. Com client_id autorizado, deve gerar URL de login.

## Segurança
- Não armazenar senha da Polarium no código.
- Não usar tokens de terceiros.
- AutoTrade continua bloqueado até validar DEMO, saldo e moeda.
