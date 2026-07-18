# SPRINT V5.4A — POLARIUM VISIBLE ACTIVE CONTEXT SYNC

## Objetivo

Corrigir a troca de ativo visível entre Polarium e Friday.

O `PolariumSessionContext` não pode usar simplesmente o último `candles-generated` recebido para definir o ativo atual, porque múltiplos ativos podem continuar inscritos simultaneamente.

A Sprint deve separar:

```text
visible_active_context
```

de:

```text
background_market_contexts
```

Não implementar scanner.
Não alterar Strategy Engine além do consumo do contexto correto.
Não fazer commit.
Não fazer push.

---

# PROBLEMA CONFIRMADO

Ao trocar o ativo na plataforma Polarium, a Friday continua mostrando o ativo anterior.

A arquitetura multiativos permite que o ativo anterior continue enviando candles em segundo plano.

Portanto:

```text
latest_market_event.active_id
```

não representa obrigatoriamente:

```text
active_id visível na plataforma
```

---

# NOVO MODELO

O contexto deve possuir explicitamente:

```text
visible_active_id
visible_symbol
visible_display_name
visible_market_type
visible_raw_size
visible_timeframe
```

E, separadamente:

```text
subscribed_contexts
```

ou estrutura equivalente interna.

O frontend operador deve usar somente o contexto visível.

Feed Quality e futuro scanner podem usar todos os contextos monitorados.

---

# PARTE 1 — AUDITORIA DA TROCA NATIVA

Observar passivamente a troca manual de ativo na Polarium.

Auditar a sequência exata:

```text
unsubscribeMessage
subscribeMessage
get-first-candles
first-candles
candles-generated
```

Identificar qual evento representa com maior confiabilidade a seleção visível.

Registrar somente:

- nome da mensagem;
- active_id;
- size;
- ordem temporal;
- request_id sanitizado.

Não registrar payload bruto ou dados sensíveis.

---

# PARTE 2 — REGRA DO ATIVO VISÍVEL

Prioridade sugerida, a ser comprovada:

1. `get-first-candles` emitido nativamente pela página após interação;
2. `subscribeMessage -> candle-generated` ou `candles-generated` da página;
3. metadata explícita de ativo selecionado;
4. `first-candles` correlacionado com request da troca.

Não usar `candles-generated` inbound isolado como prova de ativo visível.

---

# PARTE 3 — ORIGEM DA MENSAGEM

Somente mensagens:

```text
PAGE_NATIVE
```

podem alterar `visible_active_id`.

Mensagens:

```text
FRIDAY_PROBE
```

não podem alterar o ativo visível.

Mensagens:

```text
SERVER_INBOUND
```

alimentam candles, mas não alteram por si só o ativo visível.

---

# PARTE 4 — SESSION CONTEXT

Atualizar o `PolariumSessionContext` para distinguir:

```text
visible_active_id
visible_symbol
visible_display_name
visible_raw_size
```

de:

```text
latest_market_event_active_id
```

Não remover informações úteis de background, mas não expô-las como ativo principal.

---

# PARTE 5 — TROCA ATÔMICA

Quando a página selecionar novo ativo:

1. detectar `visible_active_id`;
2. resolver símbolo;
3. publicar contexto em estado `SYNCING`;
4. limpar gráfico anterior;
5. solicitar/aguardar histórico real;
6. selecionar a série do novo contexto;
7. publicar estado `READY`;
8. liberar Strategy Engine.

Durante `SYNCING`:

```text
SINCRONIZANDO ATIVO
```

e análise bloqueada.

---

# PARTE 6 — PROTEÇÃO CONTRA RETORNO AO ATIVO ANTIGO

Depois que o contexto visível mudar de A para B:

- eventos de A continuam permitidos no CandleStore;
- eventos de A não podem alterar o contexto visível;
- eventos de A não podem mudar título;
- eventos de A não podem mudar dropdown;
- eventos de A não podem mudar Strategy Engine.

Somente nova ação nativa de seleção pode mudar o contexto visível.

---

# PARTE 7 — TIMEFRAME VISÍVEL

Aplicar a mesma regra ao timeframe.

O tamanho visível deve vir da ação nativa da página:

```text
size 60
size 300
size 900
```

Candles multi-timeframe recebidos no plural não significam que todos estão selecionados visualmente.

Separar:

```text
visible_raw_size
```

de:

```text
available_raw_sizes
```

---

# PARTE 8 — TESTE REAL

Executar sequência:

1. abrir EUR/USD OTC M1;
2. confirmar Friday em EUR/USD M1;
3. trocar para USD/BRL OTC M1;
4. confirmar Friday em USD/BRL;
5. deixar EUR/USD ainda recebendo em background;
6. confirmar que a Friday não volta para EUR/USD;
7. trocar M1 → M5;
8. confirmar que a Friday muda apenas para M5;
9. continuar recebendo M1/M15 em background sem alterar contexto visível;
10. trocar novamente para outro ativo.

---

# PARTE 9 — TESTES AUTOMATIZADOS

Adicionar testes para:

1. inbound de ativo A não define contexto visível sozinho;
2. PAGE_NATIVE seleciona ativo A;
3. PAGE_NATIVE troca A para B;
4. evento posterior de A não retorna contexto para A;
5. FRIDAY_PROBE não muda contexto visível;
6. SERVER_INBOUND não muda contexto visível;
7. timeframe plural não muda timeframe selecionado;
8. PAGE_NATIVE muda M1 para M5;
9. gráfico limpa ao trocar ativo visível;
10. Strategy bloqueia durante sincronização;
11. Strategy libera após série B pronta;
12. símbolo antigo não reaparece;
13. ativo não identificado bloqueia análise.

Executar:

```bash
.venv/bin/python -m pytest -q tests/market/providers
.venv/bin/python -m pytest -q tests/frontend
.venv/bin/python -m pytest -q
```

Depois:

```bash
cd frontend
npm run build
cd ..
```

---

# ENTREGA ESPERADA

Entregar:

1. causa raiz;
2. sequência nativa observada na troca;
3. evento usado como fonte do ativo visível;
4. distinção visible versus background;
5. arquivos modificados;
6. modelo atualizado do SessionContext;
7. regra de troca atômica;
8. proteção contra retorno ao ativo antigo;
9. regra de timeframe visível;
10. teste EURUSD → USDBRL;
11. teste M1 → M5;
12. testes específicos;
13. suíte completa;
14. build;
15. git status;
16. git diff;
17. riscos;
18. sugestão de commit.

Não implementar scanner.
Não fazer commit.
Não fazer push.