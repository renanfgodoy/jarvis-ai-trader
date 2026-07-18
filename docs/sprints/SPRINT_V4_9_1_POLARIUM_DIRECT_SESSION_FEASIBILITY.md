# SPRINT V4.9.1 — POLARIUM DIRECT SESSION FEASIBILITY AUDIT

## Objetivo

Determinar se a Friday pode consumir os dados da Polarium diretamente pela sessão autenticada do usuário, eliminando a necessidade do Browser Bridge como arquitetura principal.

Esta Sprint é exclusivamente de auditoria técnica.

Não implementar login automático.

Não automatizar operações.

Não executar ordens.

Não fazer engenharia reversa de código proprietário.

Não contornar autenticação.

---

# CONTEXTO

As análises anteriores mostraram que:

- Polarium utiliza um WebSocket principal.
- Eventos observados:
  - first-candles
  - candles
  - candle-generated
  - timeSync
- O TradeAutoPilot aparenta utilizar esse mesmo ecossistema de eventos.

O objetivo agora é descobrir se a Friday pode estabelecer sua própria sessão autenticada utilizando mecanismos legítimos da plataforma, sem Browser Bridge.

---

# PARTE 1 — AUTENTICAÇÃO

Auditar:

- fluxo de login observado;
- endpoints públicos envolvidos;
- criação da sessão;
- cookies utilizados;
- tokens de autenticação;
- tempo de vida da sessão.

Não registrar valores sensíveis.

Documentar apenas a estrutura.

---

# PARTE 2 — WEBSOCKET

Responder:

Existe apenas um WebSocket?

Quais headers são enviados?

Quais cookies acompanham a conexão?

Existe autenticação via token?

Existe autenticação apenas por cookie?

O WebSocket aceita reconexão independente?

---

# PARTE 3 — SUBSCRIPTIONS

Mapear somente a estrutura.

Identificar:

- first-candles
- candles
- candle-generated
- timeSync

Responder:

Como o ativo é informado?

Como o timeframe é informado?

Como ocorre a troca de ativo?

Como ocorre a troca de timeframe?

---

# PARTE 4 — SESSÃO

Determinar se uma aplicação externa pode:

- autenticar;
- abrir o WebSocket;
- receber eventos;
- permanecer sincronizada.

Sem reutilizar cookies exportados manualmente.

Sem copiar credenciais.

Sem acessar contas de terceiros.

---

# PARTE 5 — COMPARAÇÃO

Comparar conceitualmente:

Arquitetura atual:

Polarium
↓

Browser Bridge

↓

Backend

↓

Frontend

↓

Gráfico

Arquitetura candidata:

Friday

↓

Sessão autenticada

↓

WebSocket

↓

Parser

↓

CandleStore

↓

Frontend

↓

Gráfico

Listar vantagens e limitações.

---

# PARTE 6 — RISCOS

Responder:

Há bloqueios técnicos?

Há dependência do navegador?

Há limitação de CORS?

Há necessidade de contexto da página?

A autenticação depende exclusivamente da sessão do navegador?

---

# PARTE 7 — RESULTADO

Responder claramente:

A Friday pode substituir o Browser Bridge?

SIM

NÃO

PARCIALMENTE

Justificar tecnicamente.

---

# TESTES

Executar apenas testes necessários caso algum código seja criado.

Se não houver alteração de código:

Não criar testes artificiais.

---

# ENTREGA

Entregar:

1. arquitetura observada;
2. fluxo de autenticação;
3. fluxo do WebSocket;
4. mecanismo de subscriptions;
5. viabilidade técnica;
6. riscos;
7. limitações;
8. recomendação;
9. necessidade ou não do Browser Bridge;
10. arquivos modificados (se houver);
11. testes executados;
12. build (se houver);
13. git status;
14. git diff;
15. sugestão de commit.

Não fazer commit.

Não fazer push.

Não alterar arquitetura nesta Sprint.