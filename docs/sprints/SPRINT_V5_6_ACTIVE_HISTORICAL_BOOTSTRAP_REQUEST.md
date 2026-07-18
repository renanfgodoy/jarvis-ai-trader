# SPRINT V5.6 — ACTIVE HISTORICAL BOOTSTRAP REQUEST

## Objetivo

Implementar o bootstrap histórico ativo da Friday.

Hoje:

- a Friday observa candles-generated;
- a Friday observa first-candles quando a página envia.

Agora:

a própria Friday deverá iniciar o bootstrap histórico sempre que um novo contexto visível for detectado.

Sem depender da interface da Polarium.

Sem scanner.

Sem estratégia.

Sem IA.

Sem execução de ordens.

Sem saldo.

Sem portfolio.

Sem alterar layout.

Sem commit.

Sem push.

---

# PROBLEMA

Hoje:

Troca de ativo

↓

A Friday espera

↓

Se a página enviar get-first-candles

↓

Recebe histórico

Caso contrário:

0/50 para sempre.

---

# NOVA ARQUITETURA

Implementar:

VISIBLE CONTEXT

↓

BOOTSTRAP MANAGER

↓

REQUEST FACTORY

↓

Runtime Guard

↓

Market WebSocket

↓

sendMessage

↓

get-first-candles

↓

first-candles

↓

Parser

↓

Store

↓

READY

---

# PARTE 1

Criar:

HistoricalBootstrapManager

Responsável por:

- detectar novo active_id;
- detectar novo raw_size;
- controlar bootstrap pendente;
- impedir bootstrap duplicado;
- controlar timeout;
- permitir retry.

---

# PARTE 2

Criar:

BootstrapRequestFactory

Responsável por gerar exatamente o mesmo envelope observado na sessão real.

Nunca inventar campos.

Nunca adicionar payload extra.

Comparar continuamente com PAGE_NATIVE.

---

# PARTE 3

Request

Ao detectar novo contexto:

active_id

+

raw_size

↓

enviar

sendMessage

↓

get-first-candles

Registrar:

request_id

active_id

raw_size

timestamp

socket

---

# PARTE 4

Guard

Permitir apenas:

sendMessage

↓

get-first-candles

Bloquear qualquer tentativa de:

buy

sell

order

portfolio

balance

account

payment

deposit

withdraw

change-balance

---

# PARTE 5

Timeout

Caso não exista resposta:

10 segundos

↓

BOOTSTRAP_TIMEOUT

↓

Retry único.

Nunca loop infinito.

---

# PARTE 6

Retry

Máximo:

1 retry.

Depois:

NO_HISTORY

Aguardar nova troca de ativo.

---

# PARTE 7

Correlação

Relacionar resposta por:

1. request_id

2. active_id

3. raw_size

Nunca misturar ativos.

---

# PARTE 8

Readiness

Somente:

first-candles

candles

incrementam histórico.

Realtime nunca incrementa.

---

# PARTE 9

Troca de ativo

Novo active_id

↓

cancelar bootstrap anterior

↓

novo request

↓

novo histórico

↓

novo READY.

---

# PARTE 10

Troca de timeframe

Mesmo active_id

↓

novo raw_size

↓

novo request

↓

novo bootstrap.

---

# PARTE 11

Logs DEV

Adicionar somente no modo DEV:

BOOTSTRAP_REQUEST_SENT

BOOTSTRAP_RESPONSE

BOOTSTRAP_TIMEOUT

BOOTSTRAP_RETRY

BOOTSTRAP_READY

BOOTSTRAP_FAILED

Sem payload bruto.

---

# PARTE 12

Testes

Adicionar testes para:

bootstrap automático

troca de ativo

troca timeframe

timeout

retry

cancelamento

duplicação

request_id

correlação

guard

socket correto

READY

NO_HISTORY

Executar:

pytest

build frontend

---

# PARTE 13

Teste real

Abrir Polarium.

Trocar:

EURUSD

↓

USDBRL

↓

GBPUSD

↓

EURJPY

Confirmar:

cada troca

↓

gera novo get-first-candles

↓

histórico

↓

READY

↓

realtime.

Nunca depender da página enviar bootstrap.

---

# ENTREGA

Responder obrigatoriamente:

1. Arquitetura.

2. Arquivos criados.

3. Arquivos modificados.

4. Bootstrap Manager.

5. Request Factory.

6. Envelope utilizado.

7. Runtime Guard.

8. Socket utilizado.

9. Request enviado.

10. Timeout.

11. Retry.

12. Correlação.

13. Readiness.

14. Testes.

15. Build.

16. Teste real.

17. git status.

18. git diff.

19. Riscos.

20. Próximos passos.

Não implementar scanner.

Não implementar estratégia.

Não alterar layout.

Não fazer commit.

Não fazer push.