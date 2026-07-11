# FRIDAY TRADE
# SPRINT V3.8C
# VERIFIED POLARIUM WEBSOCKET HANDSHAKE EVIDENCE

Status:
PLANNED

---

# Objetivo

Comprovar, usando somente evidências autorizadas e sanitizadas, a sequência real necessária para estabelecer uma sessão WebSocket autenticada da Polarium.

Esta Sprint é exclusivamente investigativa.

Ela NÃO deve criar runtime novo.

Ela NÃO deve abrir WebSocket novo.

Ela NÃO deve alterar Connector.

Ela NÃO deve alterar MarketPipeline.

Ela NÃO deve alterar CandleStore.

Ela NÃO deve alterar frontend.

Ela NÃO deve alterar OAuth.

Ela NÃO deve criar execução automática.

Ela NÃO deve criar AutoTrade.

Ela NÃO deve criar IA.

---

# Ambiente

Projeto:

/Users/renangodoy/Desktop/jarvis-ai-trader

Branch:

main

---

# Antes de começar

Executar:

```bash
pwd
git rev-parse --show-toplevel
git branch --show-current
git status --short

.venv/bin/python --version

.venv/bin/python -m pytest -q

cd frontend
npm run build
```

A Sprint só pode continuar se:

- apenas este Markdown estiver untracked;
- testes passarem;
- build passar.

---

# Fontes permitidas

Somente:

.jarvis_cache/evidence/trade.polariumbroker.com.har

docs/ws/POLARIUM_HAR_CANDLE_EVIDENCE_SANITIZED.md

docs/ws/POLARIUM_DIRECTED_CORRELATION.md

docs/REAL_MARKET_DATA_REPORT.md

---

# Segurança

É proibido imprimir:

- access_token
- refresh_token
- Authorization
- bearer
- cookie
- SSID
- client_secret
- code_verifier
- e-mail
- senha
- qualquer credencial

Qualquer valor sensível deve aparecer apenas como:

[REDACTED]

Nunca reconstruir valores mascarados.

Nunca mover o HAR para docs.

Nunca adicionar o HAR ao Git.

---

# Objetivos técnicos

Descobrir e documentar somente o que puder ser comprovado:

1.
URL WebSocket utilizada.

2.
Mensagem enviada imediatamente após abrir conexão.

3.
Resposta inicial do servidor.

4.
Evento que confirma autenticação.

5.
Primeiro timeSync.

6.
Primeiro subscribeMessage.

7.
Primeiro get-first-candles.

8.
Primeiro first-candles.

9.
Primeiro candle-generated.

10.
Mensagens de heartbeat.

11.
Mensagens de encerramento.

---

# Para cada etapa

Informar:

- direção

client → server

ou

server → client

- nome do evento

- campos estruturais

- campos removidos

- classificação:

CONFIRMADO

PARCIAL

NÃO CONFIRMADO

---

# Sequência esperada

Somente se realmente encontrada.

Exemplo:

WebSocket Open

↓

authenticate

↓

authenticated

↓

timeSync

↓

subscribeMessage

↓

get-first-candles

↓

first-candles

↓

candle-generated

↓

heartbeat

↓

close

Não inventar etapas ausentes.

---

# Arquitetura

Responder:

Existe hoje alguma abstração segura capaz de criar uma conexão autenticada sem expor token?

Se SIM:

explicar.

Se NÃO:

explicar exatamente por quê.

---

# Factory

Responder:

É possível criar uma

AuthenticatedWebSocketFactory

sem acessar token bruto?

Responder:

SIM

NÃO

PARCIAL

com justificativa.

---

# Message Source

Responder:

O AuthorizedPolariumMessageSource pode receber uma conexão já autenticada?

Ou obrigatoriamente precisa abrir conexão?

Responder somente baseado nas evidências.

---

# Atualizações permitidas

Pode atualizar:

docs/REAL_MARKET_DATA_REPORT.md

Pode criar:

docs/ws/POLARIUM_WEBSOCKET_HANDSHAKE_SANITIZED.md

Não criar código.

Não alterar runtime.

---

# Testes

Executar novamente:

```bash
.venv/bin/python -m pytest -q

cd frontend
npm run build
```

---

# Entrega obrigatória

1. Objetivo

2. Quantidade de frames analisados

3. URL encontrada

4. Handshake

5. Authenticate

6. Authenticated

7. timeSync

8. subscribeMessage

9. get-first-candles

10. first-candles

11. candle-generated

12. heartbeat

13. encerramento

14. sequência completa

15. campos confirmados

16. campos parciais

17. campos não confirmados

18. arquitetura recomendada

19. factory possível ou não

20. message source

21. arquivos criados

22. arquivos modificados

23. segurança

24. pytest

25. build

26. git status

27. git diff --stat

28. próxima Sprint recomendada

29. sugestão de commit

---

# Regra final

Se qualquer evidência depender de:

token

cookie

Authorization

bearer

SSID

ou qualquer segredo,

NÃO implementar.

Documentar apenas o bloqueio.

Não fazer commit.

Não fazer push.