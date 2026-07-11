# FRIDAY TRADE V3.8A
# AUTHORIZED SESSION RUNTIME FOUNDATION

Status

PLANNED

---

# Objetivo

Criar a fundação segura para manter uma única sessão Polarium autorizada no backend, com lifecycle controlado e capacidade de distribuir mensagens decodificadas para listeners internos somente leitura.

Esta Sprint NÃO encaminha candles ao MarketPipeline.

Esta Sprint NÃO altera o gráfico.

Esta Sprint NÃO cria indicadores.

Esta Sprint NÃO envia ordens.

Esta Sprint NÃO aceita credenciais, tokens, cookies, bearer, Authorization, SSID ou HAR por endpoint.

O objetivo é criar somente a infraestrutura de sessão autorizada que permitirá uma futura integração real.

---

# Problema atual

O projeto possui:

- OAuth Lab;
- diagnósticos WebSocket;
- WS Recorder;
- Connector de sessão;
- MarketPipeline;
- CandleStore;
- Chart API.

Mas não existe:

```text
sessão autorizada persistente no processo
→ WebSocket único
→ stream contínuo decodificado
→ listeners internos read-only
```

Sem essa fronteira, a integração live exigiria soluções inseguras ou paralelas.

---

# Regras obrigatórias

Não:

- aceitar token no body;
- aceitar cookie no body;
- aceitar bearer;
- aceitar Authorization;
- aceitar SSID;
- aceitar HAR;
- copiar credenciais;
- reconstruir autenticação por hipótese;
- abrir múltiplos WebSockets concorrentes;
- enviar ordens;
- alterar execução;
- alterar AutoTrade;
- alterar frontend;
- alterar MarketPipeline;
- alterar CandleStore;
- criar IA;
- criar indicadores.

Não fazer commit.

Não fazer push.

---

# Antes de começar

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

pwd
git rev-parse --show-toplevel
git branch --show-current
git status --short
.venv/bin/python --version

.venv/bin/python -m pytest -q

cd frontend
npm run build
```

O Markdown desta Sprint pode estar não rastreado e, sozinho, não bloqueia a execução.

Qualquer outra alteração pendente deve bloquear.

---

# Análise inicial obrigatória

Antes de implementar, mapear:

1. Como o OAuth autorizado atual persiste o estado.
2. Onde o token fica armazenado.
3. Se o backend consegue obter uma sessão válida sem expor o token.
4. Se já existe factory ou client reutilizável.
5. Como o Connector atual trata login, logout e expiração.
6. Como o WebSocket Diagnostic abre conexão.
7. Quais partes podem ser reutilizadas sem transformar laboratório em runtime.
8. Quais partes precisam ser extraídas para uma camada segura e neutra.

Se não houver meio seguro de obter autenticação sem leitura direta de segredo bruto, interromper e relatar.

---

# Arquitetura alvo

Criar, se tecnicamente seguro:

```text
app/connector/polarium/live_session/
    __init__.py
    manager.py
    models.py
    status.py
    event_bus.py
    errors.py
```

---

# Session Manager

Responsável por:

- existir uma única instância por processo;
- iniciar sessão somente com autenticação previamente autorizada;
- impedir start duplicado;
- parar sessão de forma limpa;
- controlar reconnect de forma limitada;
- expor status sanitizado;
- nunca retornar token;
- nunca logar payload sensível;
- não enviar ordens;
- não aceitar credenciais por endpoint.

Estados sugeridos:

```text
STOPPED
STARTING
CONNECTED
RECONNECTING
ERROR
STOPPING
```

---

# Event Bus interno

Criar um mecanismo interno read-only para listeners.

Responsabilidades:

- registrar listener;
- remover listener;
- publicar mensagens já decodificadas;
- isolar erro de um listener;
- não guardar payloads indefinidamente;
- não expor mensagens por endpoint;
- não imprimir conteúdo bruto;
- permitir futura conexão do Market Live Runtime.

Não utilizar broker externo.

Não adicionar dependências.

---

# Mensagens

Nesta Sprint, apenas distribuir mensagens decodificadas internamente.

Não filtrar candles ainda.

Não encaminhar ao MarketPipeline ainda.

Não interpretar ordens.

Não persistir frames.

Metadados sanitizados permitidos:

```text
event_name
received_at
message_sequence
connection_state
```

---

# Status sanitizado

Criar modelo de status com:

```text
state
authorized
connected
started_at
last_message_at
last_event_name
message_count
reconnect_count
last_error_code
```

Nunca incluir:

```text
token
cookie
authorization
ssid
email
headers
url privada
payload bruto
```

---

# Endpoints

Criar somente se necessários:

```text
POST /api/v1/polarium/live-session/start
POST /api/v1/polarium/live-session/stop
GET  /api/v1/polarium/live-session/status
```

Regras:

- nenhum endpoint aceita credencial;
- start usa somente autenticação previamente autorizada;
- sem autorização válida, retornar erro estruturado;
- status totalmente sanitizado;
- proteção explícita por ambiente, se necessária;
- nenhuma mensagem de mercado exposta diretamente.

---

# Integração com autenticação

Reutilizar somente mecanismo seguro já existente.

Não:

- ler arquivo de token manualmente sem abstração;
- copiar token para novo módulo;
- duplicar cache;
- criar segundo OAuth;
- aceitar token vindo do frontend.

Preferir injeção por serviço de sessão/autorização existente.

---

# WebSocket

Criar apenas se houver protocolo e autenticação já comprovados pelo código atual.

Requisitos:

- uma conexão por processo;
- lifecycle explícito;
- timeout;
- cancelamento limpo;
- reconnect limitado;
- heartbeat somente se comprovado;
- nenhuma subscription de ordem;
- nenhuma execução;
- sem payload bruto em logs.

Se a sequência necessária de autenticação WebSocket ainda não estiver comprovada, criar somente contratos/manager passivo e bloquear o start real com motivo explícito.

---

# Testes obrigatórios

Criar testes para:

- estado inicial STOPPED;
- start sem autorização;
- start idempotente;
- stop idempotente;
- uma única conexão;
- status sanitizado;
- token ausente da resposta;
- cookie ausente da resposta;
- Authorization ausente da resposta;
- erro do listener isolado;
- registro e remoção de listener;
- publicação interna de mensagem;
- reconnect limitado;
- stop limpa recursos;
- nenhuma ordem enviada;
- nenhuma dependência do MarketPipeline;
- nenhuma dependência do CandleStore.

Usar fakes/mocks. Não acessar Polarium nos testes.

---

# Fora do escopo

Não conectar ao MarketPipeline.

Não alimentar CandleStore.

Não atualizar gráfico.

Não criar parser novo.

Não criar indicadores.

Não criar IA.

Não criar sinais.

Não criar ordens.

Não criar AutoTrade.

Não criar captura HAR.

---

# Critérios de aprovação

- Lifecycle de sessão definido.
- Instância única por processo.
- Event Bus interno testável.
- Status sanitizado.
- Nenhum segredo exposto.
- Nenhuma credencial aceita por endpoint.
- Nenhuma ordem possível.
- Sem integração prematura com MarketPipeline.
- Testes passando.
- Build passando.

---

# Entrega obrigatória

1. Objetivo.
2. Diagnóstico da autenticação existente.
3. Ponto seguro encontrado ou bloqueio.
4. Arquitetura implementada.
5. Arquivos criados.
6. Arquivos modificados.
7. Lifecycle da sessão.
8. Event Bus.
9. Status sanitizado.
10. Endpoints criados.
11. Política de segredo.
12. Política de reconnect.
13. Testes criados.
14. Resultado dos testes específicos.
15. Resultado da suíte completa.
16. Resultado do build.
17. Como testar.
18. Riscos conhecidos.
19. Débitos técnicos.
20. `git status --short`.
21. `git diff --stat`.
22. Próxima Sprint recomendada.
23. Sugestão de commit.

Mensagem sugerida:

```text
feat(connector): add authorized live session runtime foundation
```

---

# Regra final

Não fazer commit.

Não fazer push.

Se a autenticação segura não puder ser reutilizada sem tocar diretamente em token, cookie, bearer ou SSID, interromper e relatar exatamente o bloqueio.

Não criar atalhos inseguros para fazer o runtime funcionar.
