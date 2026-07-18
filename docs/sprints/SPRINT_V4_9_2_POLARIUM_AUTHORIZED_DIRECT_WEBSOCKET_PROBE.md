# SPRINT V4.9.2 — POLARIUM AUTHORIZED DIRECT WEBSOCKET PROBE

## Objetivo

Validar, em ambiente isolado e somente leitura, se a Friday consegue estabelecer uma sessão autenticada legítima com a infraestrutura da Polarium e abrir um WebSocket de mercado.

Esta Sprint é uma prova técnica.

Não é implementação de produção.

Não é automação.

Não é execução de ordens.

---

# REGRAS

É proibido:

- comprar;
- vender;
- consultar saldo;
- consultar portfolio;
- alterar conta;
- alterar configurações;
- copiar credenciais;
- exportar cookies;
- reutilizar HAR bruto;
- reutilizar tokens manualmente.

Todo material sensível deve permanecer somente em memória durante o teste.

---

# PARTE 1 — OAUTH

Auditar o fluxo existente.

Responder:

- callback funciona?
- PKCE está completo?
- token é obtido?
- tempo de expiração conhecido?
- refresh token existe?
- quais campos são recebidos?

Nunca registrar valores.

Somente estrutura.

---

# PARTE 2 — WEBSOCKET

Objetivo:

abrir conexão WebSocket utilizando apenas a sessão legítima criada pela Friday.

Responder:

- conexão abriu?
- HTTP Upgrade ocorreu?
- handshake aceito?
- authenticate enviado?
- authenticated recebido?

Registrar apenas nomes dos eventos.

---

# PARTE 3 — READ ONLY

Após autenticação:

escutar apenas:

- timeSync
- first-candles
- candle-generated

Não enviar subscribe de ordens.

Não enviar chamadas financeiras.

---

# PARTE 4 — GUARDA DE SEGURANÇA

Adicionar Runtime Guard temporário.

Bloquear automaticamente qualquer mensagem contendo:

- order
- buy
- sell
- position
- portfolio
- balance
- account
- payment

Registrar:

forbidden_calls=[]

A Sprint falha imediatamente se qualquer chamada proibida for detectada.

---

# PARTE 5 — RESULTADO

Responder:

Conexão:

SIM / NÃO

Authenticate:

SIM / NÃO

Authenticated:

SIM / NÃO

timeSync:

SIM / NÃO

first-candles:

SIM / NÃO

candle-generated:

SIM / NÃO

Explicar exatamente onde ocorreu a falha, caso exista.

---

# PARTE 6 — ARQUITETURA

Responder:

É possível evoluir para:

Friday

↓

Sessão própria

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

sem Browser Bridge?

Classificar:

SIM

PARCIALMENTE

NÃO

Justificar.

---

# TESTES

Executar somente os testes necessários para qualquer código criado.

Executar build apenas se houver alteração de frontend.

---

# ENTREGA

Entregar:

1. fluxo OAuth;
2. resultado do callback;
3. resultado do WebSocket;
4. authenticate;
5. authenticated;
6. eventos recebidos;
7. Runtime Guard;
8. forbidden_calls;
9. arquivos modificados;
10. testes;
11. build;
12. git status;
13. git diff;
14. riscos;
15. recomendação.

Não fazer commit.

Não fazer push.

Não alterar Browser Bridge.

Não alterar IQ Option.

Não alterar Strategy Engine.

Não transformar esta Sprint em implementação definitiva.