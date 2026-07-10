# V0.18.1 — Real Balance Sync Guard

## Objetivo

Corrigir o painel da Polarium para nunca exibir saldo simulado como se fosse saldo real da conta DEMO.

## Mudanças

- Removido saldo mock de R$10.000.
- Adicionado `data_source` ao estado da conta.
- Adicionado `sync_status` ao estado da conta.
- Adicionado `is_balance_synced`.
- Adicionado `last_sync_error`.
- Novo endpoint `POST /api/v1/polarium/sync`.
- Botão **Sincronizar Conta** no frontend.
- Quando não houver integração real autorizada, o saldo aparece como **Não sincronizado**.
- AutoTrade deve permanecer bloqueado se o saldo/moeda não estiverem sincronizados por sessão real.

## Regra de Segurança

O J.A.R.V.I.S nunca deve inventar saldo da Polarium.

Estados válidos:

- `REAL_SESSION`: dados vieram de uma sessão real/autorizada.
- `UNAVAILABLE`: dados reais ainda não disponíveis.
- `SIMULATED`: dados simulados claramente marcados como simulação.
- `CACHE`: dados vindos de cache local, mas não necessariamente sincronizados.

## Como testar

1. Fazer login no painel da Polarium.
2. Confirmar que o saldo não aparece como R$10.000.
3. Verificar que aparece **Não sincronizado**.
4. Clicar em **Sincronizar Conta**.
5. Confirmar que o sistema retorna falha segura enquanto o adapter real não estiver configurado.
6. Rodar `python -m pytest`.
