# SPRINT V5.1D — CANDLES-GENERATED MULTI-ASSET PROOF

## Objetivo

Auditar e provar o canal WebSocket `candles-generated` da Polarium como possível fonte principal read-only para preços, candles multi-timeframe e futuro scanner multiativos da Friday.

Esta Sprint deve continuar isolada em `.jarvis_cache`.

Não integrar ao runtime principal.

Não implementar scanner de produção.

Não executar ordens.

---

# EVIDÊNCIA COMPROVADA

O HAR da Polarium contém subscription:

```json
{
  "name": "subscribeMessage",
  "request_id": "<id>",
  "msg": {
    "name": "candles-generated",
    "params": {
      "routingFilters": {
        "active_id": "<id>"
      }
    }
  }
}
```

O evento inbound contém:

```text
active_id
at
ask
bid
value
phase
candles
```

O objeto `candles` contém simultaneamente vários tamanhos, incluindo:

```text
60
300
900
```

Portanto, `candles-generated` não deve ser tratado como alias automático de `candle-generated`.

São contratos diferentes até prova contrária.

---

# PARTE 1 — DIFERENÇA ENTRE OS CANAIS

Auditar separadamente:

## `candle-generated`

Registrar sanitizadamente:

- envelope de subscribe;
- routingFilters;
- formato do inbound;
- presença de size;
- frequência;
- finalidade provável.

## `candles-generated`

Registrar sanitizadamente:

- envelope de subscribe;
- routingFilters;
- formato do inbound;
- presença de bid/ask/value;
- chaves de candles disponíveis;
- frequência;
- finalidade provável.

Entregar tabela comparativa.

---

# PARTE 2 — RUNTIME GUARD

Manter origens:

```text
PAGE_NATIVE
FRIDAY_PROBE
SERVER_INBOUND
```

Permitir à FRIDAY_PROBE somente:

```text
subscribeMessage -> candles-generated
unsubscribeMessage -> candles-generated
subscribeMessage -> candle-generated
unsubscribeMessage -> candle-generated
sendMessage -> get-first-candles
```

Qualquer outra mensagem da probe deve ser bloqueada.

PAGE_NATIVE continua somente observada e sanitizada.

---

# PARTE 3 — SELF-TESTS

Criar testes que comprovem:

1. subscription plural válida é permitida;
2. subscription plural aceita somente active_id válido;
3. evento plural inbound é reconhecido;
4. bid/ask/value são lidos apenas em memória;
5. candles 60/300/900 são roteados separadamente;
6. evento financeiro é descartado;
7. payload sensível não vai para relatório;
8. singular e plural não são misturados.

Resultado obrigatório:

```text
CANDLES_GENERATED_SELF_TEST_OK
```

---

# PARTE 4 — ACTIVE IDS

Usar somente os active_ids validados na sessão atual:

```text
1857
2267
```

Revalidá-los antes do envio.

Não usar IDs apenas do HAR antigo.

---

# PARTE 5 — DOIS ATIVOS

Enviar subscription plural para:

```text
Ativo A
Ativo B
```

Envelope:

```json
{
  "name": "subscribeMessage",
  "request_id": "friday_probe_candles_generated_<active_id>_<timestamp>",
  "msg": {
    "name": "candles-generated",
    "params": {
      "routingFilters": {
        "active_id": "<active_id>"
      }
    }
  }
}
```

Observar por 60 segundos.

Confirmar:

- eventos para A;
- eventos para B;
- eventos intercalados;
- um único WebSocket de mercado;
- A continua recebendo sem estar visível;
- zero forbidden calls da Friday.

---

# PARTE 6 — MULTITIMEFRAME

Para cada evento plural, extrair somente:

```text
candles["60"]
candles["300"]
candles["900"]
```

Manter stores independentes:

```text
Store[active_id, 60]
Store[active_id, 300]
Store[active_id, 900]
```

Confirmar:

- M1 atualiza;
- M5 atualiza;
- M15 atualiza;
- uma subscription por ativo alimenta os três timeframes;
- nenhuma mistura de séries.

---

# PARTE 7 — PREÇO EM TEMPO REAL

Medir:

- intervalo entre eventos;
- mudanças de `value`;
- mudanças de bid;
- mudanças de ask;
- p50;
- p95;
- maior gap;
- eventos por segundo.

Não inventar ticks.

Não interpolar preços.

Não suavizar dados.

---

# PARTE 8 — COMPARAÇÃO VISUAL

Comparar conceitualmente:

```text
candle-generated singular
```

versus:

```text
candles-generated plural
```

Responder qual oferece:

- maior frequência;
- melhor preço atual;
- melhor suporte multi-timeframe;
- menos subscriptions;
- melhor candidata para gráfico Friday;
- melhor candidata para scanner.

Não integrar ao gráfico ainda.

---

# PARTE 9 — UNSUBSCRIBE

Observar e usar somente o envelope plural comprovado:

```text
unsubscribeMessage -> candles-generated
```

Cancelar apenas o Ativo B.

Confirmar:

- B para;
- A continua;
- WebSocket permanece aberto;
- stores de A continuam.

Se envelope plural não for comprovado, fechar navegador para cleanup.

---

# PARTE 10 — MÉTRICAS

Por ativo:

- event_count;
- value_changes;
- bid_changes;
- ask_changes;
- first_event_latency;
- average interval;
- p50;
- p95;
- maximum gap;
- candles 60 encontrados;
- candles 300 encontrados;
- candles 900 encontrados;
- eventos após unsubscribe.

Global:

- WebSocket count;
- CPU;
- memória;
- mensagens por segundo;
- forbidden calls;
- discarded page native;
- discarded inbound;
- cleanup duration.

---

# ENTREGA ESPERADA

Entregar:

1. diferença singular versus plural;
2. envelope plural confirmado;
3. active_ids validados;
4. eventos do ativo A;
5. eventos do ativo B;
6. prova de intercalamento;
7. resultado do ativo não visível;
8. candles M1;
9. candles M5;
10. candles M15;
11. frequência de preço;
12. p50;
13. p95;
14. maior gap;
15. resultado do unsubscribe;
16. Runtime Guard;
17. forbidden calls;
18. CPU e memória;
19. arquivos temporários;
20. testes;
21. git status;
22. git diff;
23. recomendação para integração V5.2.

Não implementar scanner.

Não alterar runtime principal.

Não alterar MarketChart.

Não usar extensão.

Não fazer commit.

Não fazer push.