# SPRINT V5.3C — POLARIUM LIVE SYMBOL SYNC AND HISTORY BOOTSTRAP

## Objetivo

Corrigir dois problemas críticos da integração visual Polarium:

1. o gráfico começa vazio/zerado;
2. ao trocar o ativo na Polarium, a Friday mantém o nome antigo.

A Sprint deve garantir sincronização real entre:

Polarium ativa
→ active_id
→ símbolo
→ série
→ gráfico
→ cabeçalho Friday

Não implementar scanner.
Não implementar estratégia.
Não fazer commit.
Não fazer push.

---

# PROBLEMA 1 — SÍMBOLO DESATUALIZADO

Sintoma confirmado:

Polarium:
USD/BRL

Friday:
EUR/USD OTC

Isso é proibido.

A Friday nunca deve exibir um símbolo antigo quando o active_id vivo mudou.

---

# PARTE 1 — FONTE DO SÍMBOLO

Auditar de onde vem hoje:

- latest_active_id;
- latest_symbol;
- iqSymbol;
- selected asset;
- label do dropdown;
- título do gráfico;
- contexto do Strategy Engine.

Mapear o fluxo completo:

market event
→ active_id
→ instrument metadata
→ symbol
→ runtime status
→ API
→ frontend

---

# PARTE 2 — MAPA ACTIVE_ID → SÍMBOLO

Criar ou reutilizar um mapa oficial da sessão Polarium:

```text
active_id
→ symbol
→ market_type
→ display_name