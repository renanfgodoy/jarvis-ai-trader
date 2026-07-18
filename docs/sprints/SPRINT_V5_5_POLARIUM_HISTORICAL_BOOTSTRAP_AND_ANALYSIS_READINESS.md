# SPRINT V5.5 — POLARIUM HISTORICAL BOOTSTRAP AND ANALYSIS READINESS

## Objetivo

Preparar a Friday para analisar ativos reais da Polarium.

Hoje o gráfico consegue espelhar o mercado.

Agora precisamos garantir:

- histórico real;
- bootstrap;
- continuidade com candles-generated;
- readiness por ativo;
- readiness por timeframe.

Sem scanner.

Sem IA.

Sem CALL.

Sem PUT.

Sem estratégia operacional.

Sem ordens.

---

# PROBLEMA

Hoje:

seleciona ativo

↓

começa receber candles-generated

↓

gráfico aparece

Mas:

não existe histórico suficiente.

Logo:

não existe análise consistente.

---

# NOVA ARQUITETURA

Todo ativo deverá passar obrigatoriamente por:

ATIVO

↓

BOOTSTRAP

↓

HISTÓRICO

↓

REALTIME

↓

READY

↓

ANÁLISE

Nunca:

ATIVO

↓

REALTIME

↓

ANÁLISE

---

# PARTE 1

Implementar Historical Bootstrap oficial.

Quando surgir novo:

active_id

+

raw_size

executar:

sendMessage

↓

get-first-candles

↓

first-candles

↓

candles

↓

CandleStore

↓

candles-generated

---

# PARTE 2

Criar estado oficial:

BOOTSTRAPPING

Enquanto:

first-candles

não terminar

mostrar:

Carregando histórico...

Não liberar análise.

---

# PARTE 3

Readiness

Criar estados:

NO_HISTORY

BOOTSTRAPPING

LIMITED

READY

STALE

Cada ativo/timeframe terá readiness próprio.

---

# PARTE 4

Quantidade mínima

Implementar configuração.

Exemplo inicial:

20 candles

↓

LIMITED

50 candles

↓

READY

Não fixar números no código.

Permitir configuração futura.

---

# PARTE 5

Regras

Somente:

first-candles

candles

podem preencher histórico.

candles-generated

somente atualiza:

vela aberta

ou

nova vela.

Nunca criar histórico.

---

# PARTE 6

Reconciliação

Quando terminar bootstrap:

última vela histórica

↓

primeira vela realtime

não pode:

duplicar

nem

pular timestamp.

---

# PARTE 7

Troca de ativo

Ao trocar ativo:

limpar readiness anterior

↓

BOOTSTRAPPING

↓

novo histórico

↓

READY

Não reutilizar histórico de outro ativo.

---

# PARTE 8

Troca de timeframe

Mesmo active_id.

Novo raw_size.

Novo bootstrap.

Readiness independente.

---

# PARTE 9

Strategy Engine

Ainda não analisar.

Somente mostrar:

HISTÓRICO INSUFICIENTE

↓

CARREGANDO HISTÓRICO

↓

PRONTO PARA ANÁLISE

Nenhuma decisão operacional.

---

# PARTE 10

Frontend

Mostrar discretamente:

Histórico

0/50

15/50

37/50

50/50

READY

---

# PARTE 11

Persistência

Guardar bootstrap somente por:

provider

active_id

raw_size

Nunca compartilhar entre ativos.

---

# PARTE 12

Performance

Bootstrap:

uma única vez.

Depois:

somente realtime.

Nunca solicitar bootstrap repetidamente enquanto o contexto permanecer válido.

---

# PARTE 13

Testes

Adicionar testes para:

bootstrap iniciado

bootstrap concluído

histórico preenchido

reconciliação

duplicação

troca ativo

troca timeframe

readiness

strategy bloqueada

READY

persistência

sem candles sintéticos

sem gaps

Executar:

pytest

npm run build

---

# ENTREGA

Informar:

1. arquitetura

2. arquivos

3. bootstrap

4. parser

5. reconciliação

6. readiness

7. frontend

8. testes

9. build

10. performance

11. CPU

12. memória

13. git status

14. git diff

15. riscos

16. próximos passos

Não implementar scanner.

Não implementar IA.

Não implementar estratégia.

Não fazer commit.

Não fazer push.