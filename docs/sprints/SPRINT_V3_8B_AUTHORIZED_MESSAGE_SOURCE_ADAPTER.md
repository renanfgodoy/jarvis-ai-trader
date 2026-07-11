# FRIDAY TRADE V3.8B
# AUTHORIZED POLARIUM MESSAGE SOURCE ADAPTER

## Status

PLANNED

---

# Objetivo

Criar uma fonte autorizada segura que implemente o contrato esperado pelo `PolariumLiveSessionManager`.

A fonte deve:

- reutilizar a autenticação previamente autorizada;
- ocultar completamente tokens, cookies, bearer, Authorization e SSID;
- entregar mensagens já decodificadas ao Session Manager;
- manter uma única conexão por processo;
- operar somente em leitura;
- nunca enviar ordens;
- nunca aceitar credenciais por endpoint.

Esta Sprint ainda NÃO conecta mensagens ao MarketPipeline.

Esta Sprint ainda NÃO alimenta o CandleStore.

Esta Sprint ainda NÃO altera o gráfico.

---

# Estado atual

A Sprint V3.8A criou:

```text
PolariumLiveSessionManager
PolariumLiveSessionEventBus
status sanitizado
lifecycle único
endpoints start/stop/status
```

O start real permanece bloqueado porque não existe uma implementação segura de `PolariumLiveMessageSource`.

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

O Markdown da Sprint atual pode permanecer não rastreado.

Qualquer outra alteração pendente deve bloquear.

---

# Diagnóstico obrigatório antes da implementação

Mapear detalhadamente:

1. Como o OAuth Lab armazena autorização.
2. Qual abstração gerencia o segredo persistido.
3. Se existe método seguro que devolva um client/sessão pronta sem expor o token ao novo módulo.
4. Como o diagnóstico WebSocket autentica.
5. Qual URL WebSocket foi realmente comprovada.
6. Qual sequência de autenticação foi confirmada pelas evidências.
7. Como o logout invalida a autorização.
8. Como detectar token expirado sem imprimi-lo.
9. Como impedir duas conexões simultâneas.
10. Como o manager deve receber mensagens decodificadas.

Se qualquer ponto exigir copiar segredo bruto para o novo adapter, interromper.

---

# Arquitetura alvo

Criar, somente se seguro:

```text
app/connector/polarium/live_session/sources/
    __init__.py
    base.py
    authorized_source.py
    models.py
    errors.py
```

---

# Contrato da fonte

Criar um protocolo semelhante a:

```text
start(on_message, on_state_change)
stop()
is_authorized()
is_connected()
```

A fonte deve entregar ao manager somente:

```text
mensagem decodificada
nome do evento
timestamp de recebimento
sequência interna
```

Nunca entregar metadados de autenticação aos listeners.

---

# Authorized Source

A implementação concreta deve:

- receber dependências por injeção;
- não ler arquivos de token diretamente;
- não duplicar cache OAuth;
- não aceitar segredo no construtor público;
- não aceitar segredo vindo de endpoint;
- não expor segredo em propriedades;
- não serializar segredo;
- não logar segredo;
- não persistir frames;
- não enviar ordens;
- não criar subscriptions de execução.

---

# WebSocket

Somente abrir conexão real se todos estes itens estiverem comprovados:

- URL real confirmada;
- autenticação real confirmada;
- sequência de handshake confirmada;
- método seguro de obter sessão autorizada;
- cancelamento limpo;
- timeout;
- uma única conexão;
- nenhuma credencial exposta.

Caso contrário:

- implementar apenas o contrato e o adapter bloqueado;
- retornar código estruturado `AUTHORIZED_SOURCE_UNAVAILABLE`;
- documentar exatamente o que falta.

Não inventar protocolo.

---

# Segurança

Proibido:

```text
token em endpoint
cookie em endpoint
Authorization em endpoint
bearer em endpoint
SSID em endpoint
HAR em endpoint
e-mail ou senha
token em logs
payload de autenticação em resposta
URL privada completa em status
```

Logs permitidos:

```text
connection_state
event_name
message_sequence
received_at
error_code sanitizado
```

---

# Integração com Session Manager

O `PolariumLiveSessionManager` deve receber a fonte por injeção.

O manager continua responsável por:

- lifecycle;
- status;
- Event Bus;
- start/stop;
- contadores;
- tratamento de erros.

A fonte é responsável somente por:

- autorização;
- conexão;
- recebimento;
- decodificação básica;
- encerramento.

Não duplicar responsabilidades.

---

# Endpoints

Não criar endpoint novo para segredos.

Os endpoints existentes devem continuar:

```text
POST /api/v1/polarium/live-session/start
POST /api/v1/polarium/live-session/stop
GET  /api/v1/polarium/live-session/status
```

Depois do adapter:

- `start` tenta usar apenas autorização previamente existente;
- sem autorização segura, retorna erro estruturado;
- não aceita body;
- não devolve segredo.

---

# Testes obrigatórios

Criar testes para:

- fonte não autorizada;
- fonte autorizada fake;
- start usando fonte injetada;
- uma única conexão;
- segunda chamada start idempotente;
- stop limpo;
- mensagem recebida publicada no Event Bus;
- erro de conexão convertido em código sanitizado;
- segredo ausente do status;
- segredo ausente de exceptions serializadas;
- listener não recebe dados de autenticação;
- logout/invalidação bloqueia novo start;
- fonte não depende de MarketPipeline;
- fonte não depende de CandleStore;
- nenhuma ordem enviada;
- nenhum payload de autenticação logado.

Usar fakes/mocks nos testes.

Não acessar Polarium real nos testes automatizados.

---

# Fora do escopo

Não conectar Event Bus ao MarketPipeline.

Não filtrar candle.

Não alimentar CandleStore.

Não atualizar gráfico.

Não criar indicadores.

Não criar IA.

Não criar sinais.

Não criar execução.

Não criar AutoTrade.

---

# Critérios de aprovação

- contrato da fonte criado;
- adapter seguro criado ou bloqueio técnico preciso documentado;
- manager usa injeção;
- nenhuma credencial aceita ou exposta;
- lifecycle preservado;
- Event Bus recebe mensagens do fake autorizado;
- uma única conexão garantida;
- testes passando;
- build passando.

---

# Entrega obrigatória

1. Objetivo.
2. Diagnóstico da autenticação.
3. Abstração segura encontrada ou bloqueio.
4. Arquitetura implementada.
5. Arquivos criados.
6. Arquivos modificados.
7. Contrato da fonte.
8. Implementação concreta ou motivo do bloqueio.
9. Integração com Session Manager.
10. Política de segredos.
11. Política de conexão única.
12. Política de stop/reconnect.
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
feat(connector): add authorized Polarium message source adapter
```

---

# Regra final

Não fazer commit.

Não fazer push.

Se a implementação exigir manipular segredo bruto diretamente no novo adapter, interromper.

Se o protocolo real de autenticação WebSocket não estiver comprovado, não abrir conexão baseada em hipótese.