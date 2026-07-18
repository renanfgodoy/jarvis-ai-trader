# SPRINT V5.1E — CANDLES-GENERATED TWO-ASSET FINAL PROOF

## Objetivo

Concluir a prova final de que um único WebSocket autenticado da Polarium consegue receber `candles-generated` simultaneamente para dois ativos distintos.

Esta Sprint não implementa scanner e não altera o runtime principal.

---

# CONTEXTO COMPROVADO

A V5.1D confirmou para o active_id `1857`:

- canal `candles-generated`;
- preço real;
- candles M1, M5 e M15;
- cadência M1 próxima de 1 segundo;
- Runtime Guard sem violações.

Falta somente comprovar dois ativos simultâneos após a correção final do parser plural.

---

# PARTE 1 — INTERAÇÃO ASSISTIDA

A probe deve exibir instruções claras no terminal.

## Etapa A

Exibir:

```text
PASSO 1:
Abra o primeiro ativo OTC em M1.
Aguarde até aparecer ACTIVE_A_VALIDATED.
```

Após validar:

```text
ACTIVE_A_VALIDATED
active_id=<sanitizado>
```

## Etapa B

Exibir:

```text
PASSO 2:
Agora troque manualmente para outro ativo OTC em M1.
Não volte para o primeiro.
Aguarde até aparecer ACTIVE_B_VALIDATED.
```

Timeout mínimo por etapa:

```text
120 segundos
```

Não usar timeout curto.

Não prosseguir enquanto os dois active_ids não forem distintos e válidos na sessão atual.

---

# PARTE 2 — WEBSOCKET

Identificar um único MARKET_WEBSOCKET ativo.

Requisitos:

- authenticated;
- timeSync;
- candles-generated;
- socket aberto;
- nenhum socket ambíguo.

---

# PARTE 3 — SUBSCRIPTIONS

Após validar A e B:

Enviar:

```text
subscribeMessage -> candles-generated -> active_id A
subscribeMessage -> candles-generated -> active_id B
```

Usar request_ids exclusivos com prefixo:

```text
friday_probe_
```

Não usar size no routingFilter plural.

---

# PARTE 4 — OBSERVAÇÃO

Observar por 90 segundos.

Para cada ativo, processar:

```text
candles["60"]
candles["300"]
candles["900"]
```

Comprovar:

- eventos para A;
- eventos para B;
- pelo menos 45 segundos de sobreposição;
- eventos intercalados;
- A continua recebendo mesmo sem estar visível;
- B continua recebendo;
- um único WebSocket;
- zero forbidden calls.

---

# PARTE 5 — CRITÉRIO DE SUCESSO

## Dois ativos simultâneos

Sucesso somente se:

```text
A event_count > 10
B event_count > 10
overlap_seconds >= 45
interleaving_confirmed = true
friday_probe_forbidden_calls = []
```

## Ativo invisível

Sucesso se o ativo A continuar recebendo depois que a tela estiver no ativo B.

Resultado:

```text
NON_VISIBLE_ASSET_STREAMING = YES / NO / INCONCLUSIVE
```

---

# PARTE 6 — UNSUBSCRIBE

Se o envelope plural estiver comprovado, cancelar somente B.

Observar por mais 20 segundos.

Confirmar:

- B para;
- A continua;
- WebSocket permanece aberto.

---

# PARTE 7 — MÉTRICAS

Por ativo:

- active_id;
- event_count;
- value_changes;
- M1 events;
- M5 events;
- M15 events;
- first_event_latency;
- p50;
- p95;
- maximum_gap;
- overlap_seconds;
- events_after_unsubscribe.

Global:

- WebSocket count;
- CPU;
- memória;
- messages_per_second;
- Runtime Guard;
- cleanup.

---

# PARTE 8 — ENTREGA

Entregar:

1. active_id A;
2. active_id B;
3. confirmação de IDs distintos;
4. subscriptions enviadas;
5. eventos A;
6. eventos B;
7. overlap;
8. intercalamento;
9. ativo não visível;
10. M1/M5/M15 por ativo;
11. unsubscribe;
12. CPU/memória;
13. forbidden calls;
14. cleanup;
15. arquivos alterados;
16. testes;
17. git status;
18. git diff;
19. conclusão definitiva:
   - multiasset confirmado;
   - inconclusivo;
   - não suportado.
20. recomendação para V5.2.

Não implementar scanner.
Não alterar runtime principal.
Não alterar MarketChart.
Não fazer commit.
Não fazer push.