# SPRINT V5.1B — CDP MESSAGE ORIGIN GUARD AND MULTI-ASSET RETRY

## Objetivo

Corrigir exclusivamente a classificação de origem das mensagens observadas pela probe CDP e repetir o teste read-only com dois ativos.

A V5.1A comprovou:

- Chrome dedicado sem extensão;
- login manual legítimo;
- um WebSocket Polarium;
- estado authenticated;
- timeSync;
- ausência de exportação de cookie/token.

A prova multiativos foi interrompida porque o Runtime Guard tratou uma mensagem nativa da página como se tivesse sido criada pela Friday.

Esta Sprint deve separar:

```text
PAGE_NATIVE
FRIDAY_PROBE
SERVER_INBOUND
```

Não implementar scanner.

Não integrar ao runtime principal.

---

# PARTE 1 — CLASSIFICAÇÃO DE ORIGEM

## 1. PAGE_NATIVE

Mensagem enviada originalmente pelo JavaScript da página Polarium.

Regras:

- não bloquear a página;
- não reproduzir a mensagem;
- não encaminhar ao backend Friday;
- não persistir payload;
- não extrair conteúdo financeiro;
- registrar apenas nome sanitizado e contagem;
- descartar domínios não relacionados a candles.

Exemplo de registro permitido:

```json
{
  "origin": "PAGE_NATIVE",
  "name": "subscribeMessage",
  "domain": "discarded_non_market",
  "count": 1
}
```

Não registrar:

- saldo;
- valor;
- usuário;
- conta;
- posição;
- ordem;
- token;
- cookie;
- SSID;
- payload completo.

---

## 2. FRIDAY_PROBE

Mensagem construída explicitamente pela probe.

Apenas estas mensagens são permitidas:

```text
subscribeMessage → candle-generated
unsubscribeMessage → candle-generated
sendMessage → get-first-candles
```

A validação deve considerar:

- origin;
- name externo;
- msg.name;
- routingFilters;
- active_id;
- size.

Qualquer mensagem criada pela Friday fora dessa allowlist deve:

1. não ser enviada;
2. adicionar item em `forbidden_calls`;
3. abortar imediatamente a probe.

---

## 3. SERVER_INBOUND

Mensagem recebida do servidor.

Processar somente:

```text
authenticated
timeSync
first-candles
candles
candle-generated
```

Outras mensagens:

- descartar;
- não persistir;
- registrar somente contagem sanitizada por categoria;
- não expor conteúdo.

---

# PARTE 2 — PROVA DE ORIGEM

Antes da execução real, criar self-tests que comprovem:

1. mensagem nativa proibida da página não vira `forbidden_call` da Friday;
2. mensagem proibida criada pela probe é bloqueada;
3. subscription Friday para `candle-generated` é permitida;
4. active_id e size inválidos são bloqueados;
5. payload financeiro inbound é descartado;
6. nenhuma informação sensível aparece no relatório.

Resultado obrigatório:

```text
ORIGIN_GUARD_SELF_TEST_OK
```

---

# PARTE 3 — ACTIVE IDS

Validar na sessão atual que os IDs utilizados continuam existentes.

Contextos candidatos da evidência anterior:

```text
79:60
2289:60
```

Não enviar subscription se o active_id não estiver presente em evento, lista ou estrutura sanitizada da sessão atual.

Registrar somente:

```text
active_id
symbol, se disponível sem dado sensível
size
```

---

# PARTE 4 — TESTE COM DOIS ATIVOS

Após self-test e validação dos IDs:

1. manter uma única sessão;
2. manter um único WebSocket;
3. enviar duas subscriptions Friday;
4. usar dois active_ids distintos;
5. usar `size=60`;
6. observar por no mínimo 60 segundos.

Comprovar:

- eventos para ativo A;
- eventos para ativo B;
- eventos intercalados;
- pelo menos 30 segundos de sobreposição;
- séries isoladas por `active_id + size`;
- zero mensagens proibidas originadas pela Friday.

---

# PARTE 5 — ATIVO NÃO VISÍVEL

Durante a medição:

- deixar apenas um ativo visível na interface Polarium;
- comprovar se o outro active_id continua recebendo candles;
- não trocar a interface apenas para forçar eventos.

Resultado:

```text
VISIBLE_ASSET_ONLY_REQUIRED:
YES / NO / INCONCLUSIVE
```

---

# PARTE 6 — M1 E M5

Somente após sucesso com dois ativos:

```text
Ativo A + size 60
Ativo A + size 300
```

Confirmar:

- eventos para os dois tamanhos;
- stores separados;
- nenhuma mistura;
- mesmo WebSocket;
- zero forbidden calls da Friday.

---

# PARTE 7 — UNSUBSCRIBE

Usar somente envelope de unsubscribe comprovado por observação ou HAR.

Não inventar contrato.

Cancelar somente:

```text
Ativo B + size 60
```

Confirmar:

- B para de receber;
- A continua;
- outro timeframe continua;
- WebSocket permanece aberto.

Se o envelope não estiver comprovado:

```text
UNSUBSCRIBE: INCONCLUSIVE
```

e realizar cleanup encerrando o navegador.

---

# PARTE 8 — RELATÓRIO DE SEGURANÇA

Separar claramente:

```json
{
  "friday_probe_forbidden_calls": [],
  "page_native_discarded_count": 0,
  "server_inbound_discarded_count": 0
}
```

Nunca usar uma lista única que misture origens.

Não armazenar payloads descartados.

---

# PARTE 9 — MÉTRICAS

Registrar por `active_id + size`:

- subscription_at;
- first_event_at;
- event_count;
- OHLC changes;
- identical events;
- average interval;
- p50;
- p95;
- maximum gap;
- last_event_at;
- events after unsubscribe.

Registrar globalmente:

- WebSocket count;
- CPU;
- memória;
- processos Chrome;
- mensagens por segundo;
- tempo de cleanup.

---

# PARTE 10 — ARQUIVOS

Modificar somente a probe ignorada:

```text
.jarvis_cache/polarium_cdp_probe/
```

Não alterar arquivos rastreados sem necessidade comprovada.

Não alterar:

- MarketChart;
- Browser Bridge;
- IQ Option;
- Strategy Engine;
- runtime principal;
- frontend.

---

# PARTE 11 — ENTREGA ESPERADA

Entregar:

1. causa do falso positivo da V5.1A;
2. regra PAGE_NATIVE;
3. regra FRIDAY_PROBE;
4. regra SERVER_INBOUND;
5. resultado dos self-tests;
6. active_ids validados;
7. quantidade de WebSockets;
8. resultado com dois ativos;
9. eventos por ativo;
10. prova de intercalamento;
11. ativo não visível;
12. resultado M1 + M5;
13. resultado do unsubscribe;
14. CPU e memória;
15. cleanup;
16. `friday_probe_forbidden_calls`;
17. `page_native_discarded_count`;
18. `server_inbound_discarded_count`;
19. arquivos modificados;
20. testes;
21. git status;
22. git diff;
23. riscos;
24. recomendação para V5.2.

Não implementar scanner.

Não executar ordens.

Não consultar saldo, posições, portfolio ou conta.

Não fazer commit.

Não fazer push.