# SPRINT V5.0 — MULTI-ASSET WEBSOCKET CAPABILITY AUDIT

## Objetivo

Descobrir se a infraestrutura WebSocket observada da Polarium permite acompanhar múltiplos ativos simultaneamente através de subscriptions independentes.

Esta Sprint é exclusivamente investigativa.

Não executar ordens.

Não consultar saldo.

Não utilizar credenciais exportadas.

Não reutilizar cookies.

Não alterar runtime existente.

Não implementar scanner.

Não fazer engenharia reversa de código proprietário.

---

# CONTEXTO

Hoje a Friday trabalha praticamente em:

1 ativo

↓

1 stream

↓

1 gráfico

O TradeAutoPilot aparenta conseguir:

vários ativos

↓

ranking

↓

melhores oportunidades

Sem depender do ativo atualmente aberto.

O objetivo é descobrir se isso é possível pela arquitetura observada.

---

# PARTE 1 — SUBSCRIPTIONS

Auditar o protocolo observado.

Responder:

Existe subscribe por ativo?

Existe unsubscribe?

Existe subscribe múltiplo?

Existe limite conhecido?

Existe active_id por canal?

Existe size por canal?

---

# PARTE 2 — MÚLTIPLOS ATIVOS

Determinar conceitualmente:

Arquitetura A

1 WebSocket

↓

1 ativo

Arquitetura B

1 WebSocket

↓

N ativos

Arquitetura C

N WebSockets

↓

N ativos

Responder qual hipótese é mais consistente com as evidências observadas.

---

# PARTE 3 — MENSAGENS

Mapear apenas estrutura.

Responder:

first-candles:

possui active_id?

candle-generated:

possui active_id?

timeSync:

global?

Existe identificador suficiente para manter múltiplos CandleStores simultaneamente?

---

# PARTE 4 — CANDLESTORE

Determinar se uma arquitetura futura pode manter:

Store[
active_id,
size
]

independente para cada ativo.

Sem compartilhar estado.

---

# PARTE 5 — SCANNER

Responder conceitualmente:

É possível criar:

Feed Scanner

↓

ativos

↓

ranking

↓

Friday Strategy

sem trocar o gráfico principal?

Não implementar.

Somente justificar.

---

# PARTE 6 — LIMITAÇÕES

Responder:

Há evidência de limite de subscriptions?

Há evidência de limite de throughput?

Há evidência de fechamento automático?

Há evidência de canais exclusivos?

Não inventar respostas.

Usar apenas evidências observadas.

---

# PARTE 7 — CONCLUSÃO

Responder:

A Friday pode evoluir para um scanner multiativos?

SIM

PARCIALMENTE

NÃO

Justificar.

---

# ENTREGA

Entregar:

1. hipótese mais provável de arquitetura;

2. modelo de subscriptions;

3. modelo de CandleStore;

4. possibilidade de múltiplos ativos;

5. limitações encontradas;

6. riscos;

7. recomendação para V5.1;

8. arquivos modificados;

9. testes;

10. build;

11. git status;

12. git diff;

13. sugestão de commit.

Não implementar scanner.

Não modificar Browser Bridge.

Não modificar IQ Option.

Não fazer commit.

Não fazer push.