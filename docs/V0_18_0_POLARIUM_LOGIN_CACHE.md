# V0.18.0 — Polarium Login Panel + Session Cache

## Objetivo
Criar a base visual e técnica para o operador conectar a conta Polarium usando o login real, mas mantendo o sistema em modo seguro de desenvolvimento.

## Regras de segurança
- A senha nunca é salva no cache.
- A sessão cacheada guarda apenas dados não sensíveis: e-mail mascarado, modo DEMO, moeda, saldo demo e status.
- Conta REAL continua bloqueada nesta fase.
- A integração real Polarium/Quadcode será plugada no adapter quando houver endpoint autorizado.

## Endpoints
- `GET /api/v1/polarium/status`
- `POST /api/v1/polarium/login`
- `POST /api/v1/polarium/logout`

## Como testar
1. Abrir o dashboard.
2. Preencher e-mail e senha no painel Polarium.
3. Clicar em conectar.
4. Confirmar que o painel mostra DEMO, saldo, moeda e sessão cacheada.
5. Recarregar a página e confirmar que a sessão permanece.
6. Clicar em sair e confirmar que o cache foi removido.
