# FRIDAY AI TRADER

# SPRINT POCKET V1.3 — LIVE READ-ONLY SESSION DISCOVERY

## Status

DESCOBERTA LIVE PASSIVA — CONTA DEMO — SEM ENVIO DE MENSAGENS — SEM AUTOMAÇÃO

---

## 1. Objetivo

Validar, em uma sessão real da Pocket aberta e autenticada manualmente pelo Renan, se os eventos comprovados offline nas Sprints Pocket V1.0, V1.1 e V1.2 podem ser observados passivamente e processados pela arquitetura read-only já criada.

Fluxo pretendido:

```text
Chrome dedicado
→ login manual Pocket Demo
→ observação passiva CDP do WebSocket
→ frames recebidos e enviados pelo navegador
→ sanitização imediata
→ parser Pocket V1.1
→ PocketReadOnlyLiveSource
→ PocketMarketRuntime
→ PocketCandleStoreAdapter
→ buckets POCKET:<asset>:<period>
→ diagnóstico local
```

Nesta Sprint, o sistema não deverá abrir uma conexão Socket.IO independente.

A sessão continuará pertencendo integralmente ao navegador.

---

## 2. Evidências comprovadas

### Pocket V1.0

```text
protocol: Socket.IO / Engine.IO
main host: api-us-south.po.market
viability: EXCELLENT
technical score: 9.5
```

Eventos comprovados:

```text
changeSymbol
updateHistoryNewFast
updateStream
updateAssets
updateCharts
auth/success
```

### Pocket V1.1

```text
candle schema: STABLE
tick schema: STABLE
asset schema: PARTIAL_STABLE
HAR compatibility: COMPATIBLE
candles accepted: 890
ticks accepted: 419
```

Schema histórico:

```text
[timestamp, open, close, high, low, volume]
```

Schema realtime:

```text
[asset, timestamp, price]
```

### Pocket V1.2

```text
history_batches: 9
historical_candles: 890
realtime_ticks: 419
buckets: 7
all buckets: READY
live connection: DISABLED
network usage: NONE
```

A arquitetura read-only já contém:

```text
PocketTransport
PocketReplayTransport
FakePocketTransport
PocketReadOnlyLiveSource
PocketEventRouter
PocketMarketRuntime
PocketCandleStoreAdapter
PocketRealtimeCandleBuilder
PocketReadinessTracker
PocketRuntimeGuard
PocketRuntimeMetrics
```

---

## 3. Regra principal

Esta Sprint será exclusivamente de observação passiva.

É proibido:

```text
automatizar login
preencher usuário ou senha
ler senha
copiar token
copiar cookie
copiar SSID
copiar Authorization
persistir frame auth
reutilizar credenciais
abrir Socket.IO independente
enviar auth
enviar changeSymbol
enviar saveCharts
enviar ping-server
enviar CALL
enviar PUT
enviar ordem
consultar saldo
consultar dados pessoais
alterar conta
automatizar clique de operação
usar Selenium
usar Playwright para interagir com a plataforma
interceptar ou modificar mensagens
modificar payloads
alterar a Polarium
integrar a Pocket ao frontend principal
registrar a Pocket no startup principal
```

A única ação permitida será observar eventos que o próprio navegador já está transmitindo e recebendo durante o uso manual.

---

## 4. Conta e ambiente permitidos

Usar exclusivamente:

```text
Pocket Option
conta DEMO
login manual pelo Renan
Chrome dedicado
ambiente local
```

Não utilizar conta real nesta Sprint.

Não realizar depósito.

Não aceitar bônus.

Não executar operações.

---

## 5. Arquitetura de observação

Criar um transporte passivo:

```text
PocketCDPObservationTransport
```

Ele deverá implementar o contrato já existente:

```text
PocketTransport
```

Métodos:

```text
start()
stop()
is_running()
next_event()
status()
```

O transporte deverá apenas observar frames CDP.

Não deverá possuir qualquer método de envio.

---

## 6. Modo de conexão

A arquitetura permitida é:

```text
Chrome dedicado
→ remote debugging local
→ target Pocket identificado
→ Network.enable
→ Network.webSocketCreated
→ Network.webSocketFrameReceived
→ Network.webSocketFrameSent
```

O transporte deverá observar somente o target principal da Pocket.

Não anexar:

```text
iframe de terceiros
service worker de analytics
worker desconhecido
aba Friday
extensão
target browser_ui
```

---

## 7. URL da Pocket

A URL oficial da Pocket deverá ser configurável.

Criar:

```text
pocket_trade_url
```

Não assumir domínio sem auditar a sessão real.

O target correto deverá ser selecionado por:

```text
type = page
URL pertencente ao domínio Pocket aberto manualmente
```

Não selecionar simplesmente a primeira aba `page`.

---

## 8. Chrome dedicado

Criar configuração isolada:

```text
pocket_cdp_enabled = false
pocket_cdp_debug_port = 9230
pocket_cdp_profile_dir = .jarvis_private/chrome-pocket-profile
pocket_cdp_open_browser = true
pocket_cdp_observation_only = true
pocket_live_connection_enabled = false
pocket_read_only = true
```

Defaults obrigatórios:

```text
pocket_cdp_enabled = false
pocket_live_connection_enabled = false
pocket_cdp_observation_only = true
pocket_read_only = true
```

Não reutilizar a porta `9227` da Polarium.

---

## 9. Ownership da sessão

A sessão pertence ao navegador.

A Friday não deverá:

```text
possuir token
possuir cookie
possuir credencial
renovar sessão
reautenticar
criar Socket.IO
reconectar Socket.IO diretamente
```

Se o navegador desconectar, o observer apenas reportará:

```text
POCKET_BROWSER_SESSION_OFFLINE
```

---

## 10. Identificação do WebSocket de mercado

O observer deverá catalogar os WebSockets do target Pocket e identificar o socket de mercado por evidência.

Evidência esperada:

```text
host semelhante a api-*.po.market
path contendo /socket.io/
EIO=4
transport=websocket
eventos updateStream
eventos updateHistoryNewFast
eventos updateAssets
```

Não escolher um socket apenas pelo host.

A classificação deverá considerar eventos reais observados.

Estados:

```text
UNKNOWN
CANDIDATE
MARKET_SOCKET
AUXILIARY_SOCKET
REJECTED
```

---

## 11. Sanitização imediata

Todo frame deverá ser sanitizado antes de entrar em qualquer fila, relatório ou log.

Eventos que devem ser descartados integralmente:

```text
auth
auth/success com dados de conta
profile
balance
account
personal data
```

Para frames sensíveis, registrar somente:

```text
event_name
direction
timestamp
discarded = true
reason = SENSITIVE_EVENT
```

Nunca armazenar o payload.

---

## 12. Eventos permitidos

Somente estes eventos poderão entrar no pipeline de mercado:

```text
changeSymbol
updateHistoryNewFast
updateStream
updateAssets
updateCharts
saveCharts
```

Eventos auxiliares poderão ser contabilizados, sem payload:

```text
ping
pong
ping-server
connect
disconnect
reconnect
```

Outros eventos:

```text
PocketUnknownObservedEvent
```

com payload descartado.

---

## 13. Eventos enviados pelo navegador

Frames enviados pelo navegador poderão ser observados exclusivamente para descobrir:

```text
changeSymbol
asset
period
saveCharts
heartbeat
subscription lifecycle
```

Não poderão ser reenviados.

O observer deverá produzir:

```text
PocketObservedOutboundEvent
```

Campos sanitizados:

```text
event_name
asset
period
timestamp
socket_request_id
```

Somente quando esses campos forem comprovadamente não sensíveis.

---

## 14. Eventos recebidos

Frames recebidos deverão ser encaminhados ao parser V1.1 somente quando pertencerem ao Market WebSocket comprovado.

Fluxo:

```text
CDP frame received
→ socket ownership check
→ sanitização
→ Engine.IO parser
→ Socket.IO parser
→ Pocket domain event
→ PocketMarketRuntime
```

Frames de outro socket não poderão alimentar o runtime.

---

## 15. PocketCDPObservationTransport

Criar em:

```text
app/market/providers/pocket/cdp_observation_transport.py
```

Responsabilidades:

```text
anexar ao target Pocket
habilitar Network CDP
catalogar sockets
identificar Market WebSocket
observar frames
sanitizar frames
converter em eventos Pocket
enfileirar eventos permitidos
expor status
parar de forma limpa
```

Não deverá conhecer CandleStore.

---

## 16. Pocket CDP Client

Criar uma abstração pequena:

```text
PocketCDPClient
```

Permitido:

```text
listar targets
anexar target
enviar comandos CDP de observação
receber eventos CDP
fechar conexão CDP
```

Comandos CDP permitidos:

```text
Network.enable
Runtime.enable, somente se tecnicamente necessário para leitura de metadados não sensíveis
Target.getTargets
```

Comandos proibidos:

```text
Runtime.evaluate para enviar WebSocket
Target.createTarget para abrir a Friday
Input.dispatchMouseEvent
Input.dispatchKeyEvent
Page.navigate após login
Storage.getCookies
Network.getAllCookies
Network.setCookie
Fetch.enable para interceptação
```

---

## 17. Estados do observer

Criar:

```text
STOPPED
STARTING_CHROME
WAITING_TARGET
TARGET_ATTACHED
WAITING_MARKET_SOCKET
OBSERVING
DEGRADED
ERROR
```

O status deverá informar:

```text
running
observer_state
target_found
target_url_sanitized
sockets_observed
market_socket_found
market_events_received
market_events_processed
sensitive_events_discarded
unknown_events
last_error_code
last_update
```

---

## 18. Target Manager

Criar um target manager Pocket independente da Polarium.

Ele deverá:

```text
localizar a aba Pocket
ignorar aba Friday
ignorar Polarium
ignorar workers
ignorar iframes
ignorar service workers
revalidar target após reload
detectar target fechado
```

Não reutilizar estado global do target manager Polarium.

---

## 19. Socket ownership

Cada frame deverá preservar internamente:

```text
cdp_request_id
target_id
socket_url_sanitized
direction
timestamp
```

Antes de rotear, verificar:

```text
target_id == pocket_target_id
cdp_request_id == confirmed_market_socket_request_id
```

Caso contrário:

```text
POCKET_NON_MARKET_SOCKET_FRAME_IGNORED
```

---

## 20. Troca manual de ativo

Quando o Renan trocar manualmente:

```text
EURUSD OTC
→ AUDUSD OTC
→ USDBRL OTC
```

O observer deverá identificar:

```text
changeSymbol
asset
period
```

E atualizar o contexto somente depois de validar:

```text
asset presente
period suportado
frame pertencente ao Market WebSocket
```

A Friday não enviará a troca.

---

## 21. Troca manual de timeframe

Validar manualmente:

```text
M1
M5
M15
```

Mapeamento:

```text
60  → M1
300 → M5
900 → M15
```

O observer deverá atualizar o Session Context Pocket com o par completo:

```text
asset + period
```

Não publicar contexto parcial.

---

## 22. Contexto atômico

Nunca publicar:

```text
asset sem period
period sem asset
bucket incompleto
```

Só atualizar quando houver:

```text
asset válido
period válido
timeframe resolvido
```

Caso o evento esteja incompleto:

```text
POCKET_PARTIAL_CONTEXT_IGNORED
```

---

## 23. Histórico live observado

Ao receber:

```text
updateHistoryNewFast
```

O runtime deverá:

```text
validar Market WebSocket
validar asset
validar period
usar parser V1.1
normalizar candles
resolver bucket POCKET:<asset>:<period>
gravar histórico
incrementar history_count
atualizar readiness
```

Não exigir exatamente 20 candles.

---

## 24. Realtime live observado

Ao receber:

```text
updateStream
```

O runtime deverá:

```text
usar parser V1.1
gerar PocketRealtimeTick
atualizar last_price
agregar candle realtime
não incrementar history_count histórico
```

---

## 25. Catálogo de ativos

Ao receber:

```text
updateAssets
```

O runtime poderá atualizar catálogo read-only com:

```text
symbol
display_name
market_type
supported_periods
candidate fields
```

Payout e disponibilidade continuam sem uso operacional.

---

## 26. Readiness live

O readiness deverá seguir as regras V1.2:

```text
0 históricos      → EMPTY ou BOOTSTRAPPING
1 até 49          → LIMITED
50 ou mais        → READY
erro irrecuperável → ERROR
```

Configuração:

```text
pocket_history_required = 50
```

Se a plataforma entregar apenas 20 candles inicialmente, registrar `LIMITED` sem inventar dados.

---

## 27. Modo análise

Mesmo com Pocket READY:

```text
analysis_allowed = true
```

apenas para futuras Sprints.

Nesta Sprint, não integrar Strategy Engine ou IA.

O status poderá informar:

```text
analysis_blocked
analysis_block_reason
```

---

## 28. Guard read-only

O `PocketRuntimeGuard` deverá continuar bloqueando:

```text
AUTHENTICATE_REAL_SESSION
OPEN_SOCKET_DIRECTLY
SEND_CHANGE_SYMBOL
SEND_MESSAGE
SEND_ORDER
SEND_CALL
SEND_PUT
READ_BALANCE
READ_PERSONAL_DATA
```

Adicionar:

```text
MODIFY_CDP_FRAME
INTERCEPT_REQUEST
REPLAY_LIVE_CREDENTIAL
```

Todas retornam:

```text
POCKET_READ_ONLY_GUARD_BLOCKED
```

---

## 29. Diagnóstico live

Criar:

```text
.jarvis_cache/diagnostics/pocket_live_observation_report.json
.jarvis_cache/diagnostics/pocket_live_observation_report.txt
```

Campos:

```text
observer_started
target_found
target_url_sanitized
sockets_observed
socket_candidates
market_socket_found
market_socket_reason
frames_sent_observed
frames_received_observed
events_parsed
change_symbol_events
history_batches
historical_candles
stream_events
ticks
asset_catalog_events
contexts_published
buckets_created
readiness
sensitive_events_discarded
non_market_frames_ignored
unknown_events
errors
observer_stopped_cleanly
```

---

## 30. Relatório de sockets

Criar:

```text
.jarvis_cache/diagnostics/pocket_socket_observation_report.json
.jarvis_cache/diagnostics/pocket_socket_observation_report.txt
```

Para cada socket:

```text
sanitized_host
sanitized_path
target_id_masked
request_id_masked
frames_sent_count
frames_received_count
event_names
classification
classification_reason
```

Nunca incluir query string completa.

---

## 31. Relatório de contexto

Criar:

```text
.jarvis_cache/diagnostics/pocket_live_context_report.json
.jarvis_cache/diagnostics/pocket_live_context_report.txt
```

Registrar:

```text
old_asset
new_asset
old_period
new_period
timeframe
origin
reason
bucket_key
bucket_exists
history_count
readiness
timestamp
```

---

## 32. Logs sanitizados

Adicionar logs técnicos:

```text
POCKET_CDP_START
POCKET_TARGET_FOUND
POCKET_TARGET_WAIT
POCKET_SOCKET_CREATED
POCKET_MARKET_SOCKET_CANDIDATE
POCKET_MARKET_SOCKET_CONFIRMED
POCKET_FRAME_ALLOWED
POCKET_FRAME_DISCARDED
POCKET_CONTEXT_UPDATED
POCKET_HISTORY_WRITTEN
POCKET_REALTIME_PROCESSED
POCKET_OBSERVER_STOPPED
```

Não imprimir payload bruto.

---

## 33. Configuração

Criar configurações:

```text
pocket_cdp_enabled = false
pocket_cdp_debug_port = 9230
pocket_cdp_profile_dir = .jarvis_private/chrome-pocket-profile
pocket_cdp_observation_only = true
pocket_trade_url = URL configurável
pocket_history_required = 50
pocket_read_only = true
pocket_live_connection_enabled = false
```

Defaults seguros obrigatórios.

---

## 34. Isolamento do startup principal

Não registrar o provider Pocket automaticamente em:

```text
app/main.py
app/market/runtime.py
```

Criar um CLI controlado:

```text
tools/pocket_live_observation/
```

Executar:

```bash
.venv/bin/python -m tools.pocket_live_observation
```

O CLI poderá iniciar o Chrome dedicado e o observer, mas não poderá preencher login.

---

## 35. Comportamento do CLI

Fluxo esperado:

```text
1. Iniciar Chrome dedicado na URL Pocket.
2. Exibir: "Faça login manualmente na conta DEMO."
3. Aguardar target.
4. Observar sockets.
5. Confirmar Market WebSocket.
6. Processar apenas eventos de mercado.
7. Gerar relatórios.
8. Encerrar com Control + C.
9. Limpar tarefas e conexões CDP.
```

Não pedir credenciais no Terminal.

---

## 36. Validação manual planejada

Sequência:

```text
1. Abrir Pocket Demo.
2. Fazer login manual.
3. Aguardar gráfico.
4. Selecionar EURUSD OTC M1.
5. Aguardar 15 segundos.
6. Trocar para EURUSD OTC M5.
7. Aguardar 15 segundos.
8. Trocar para AUDUSD OTC M15.
9. Aguardar 15 segundos.
10. Trocar para USDBRL OTC M5.
11. Aguardar 15 segundos.
12. Encerrar observer.
```

---

## 37. Critério real por ativo

Para cada combinação observada, confirmar:

```text
contexto asset/period correto
bucket POCKET:<asset>:<period>
histórico recebido
ticks recebidos
realtime atualizado
sem mistura entre ativos
sem mistura entre timeframes
```

---

## 38. Ausência de envio

Adicionar prova técnica de que nenhuma chamada de envio existe no transporte.

Proibir no código:

```text
Runtime.evaluate com socket.send
websocket.send
socket.emit
sio.emit
sendMessage
changeSymbol outbound programático
```

O observer poderá registrar frames enviados pelo navegador, mas nunca originá-los.

---

## 39. Testes automatizados

Criar testes com fake CDP para:

### Target

```text
target Pocket correto
aba Friday ignorada
Polarium ignorada
iframe ignorado
worker ignorado
target fechado
reload
```

### Sockets

```text
socket candidato
Market WebSocket confirmado por eventos
socket auxiliar rejeitado
frame de socket errado ignorado
```

### Sanitização

```text
auth descartado
token descartado
cookie descartado
SSID descartado
saldo descartado
dados pessoais descartados
```

### Contexto

```text
EURUSD_otc/60
EURUSD_otc/300
AUDUSD_otc/900
USDBRL_otc/300
contexto parcial ignorado
contexto atômico publicado
```

### Histórico

```text
updateHistoryNewFast processado
bucket correto
history_count
readiness
```

### Realtime

```text
updateStream processado
tick aceito
candle atualizado
history_count não alterado
```

### Lifecycle

```text
start
stop
target reload
socket reconnect
evento inválido não fatal
Control + C
cleanup completo
```

### Guard

```text
send bloqueado
auth bloqueado
changeSymbol bloqueado
ordem bloqueada
interceptação bloqueada
```

---

## 40. Testes sem rede real

Os testes automatizados devem utilizar:

```text
FakePocketCDPClient
fixtures sanitizadas
frames dos HARs sem credenciais
```

Não conectar ao domínio Pocket durante pytest.

Adicionar proteção que falhe o teste caso haja tentativa de rede externa.

---

## 41. Validação automatizada

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

.venv/bin/python -m pytest tests/market/providers/pocket -v
.venv/bin/python -m pytest tests/tools/pocket_parser -v
.venv/bin/python -m pytest tests/tools/pocket_discovery -v
.venv/bin/python -m pytest -v
```

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run build
```

---

## 42. Validação real obrigatória

A Sprint não poderá ser considerada validada em ambiente real antes de o Renan executar o CLI na conta demo.

Comando futuro:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

POCKET_CDP_ENABLED=true \
POCKET_CDP_OBSERVATION_ONLY=true \
POCKET_READ_ONLY=true \
POCKET_LIVE_CONNECTION_ENABLED=false \
.venv/bin/python -m tools.pocket_live_observation
```

O Forge não deverá executar esse teste sem autorização expressa e sem o Renan estar presente para fazer login manual.

---

## 43. Critério de aceitação automatizado

A parte automatizada será aprovada quando:

```text
transport CDP passivo existir
target correto for selecionado
Market WebSocket for confirmado por eventos
frames sensíveis forem descartados
changeSymbol observado for processado
histórico observado for processado
realtime observado for processado
buckets corretos forem criados
nenhum envio existir
guard estiver ativo
cleanup for aprovado
todos os testes passarem
build passar
```

---

## 44. Critério de aceitação real

A Sprint somente poderá ser declarada validada em sessão real quando:

```text
conta DEMO autenticada manualmente
Market WebSocket identificado
EURUSD M1 observado
EURUSD M5 observado
AUDUSD M15 observado
USDBRL M5 observado
histórico recebido
ticks recebidos
buckets corretos criados
nenhum payload sensível salvo
nenhuma mensagem enviada pela Friday
observer encerrado limpo
```

---

## 45. Critério para avançar à Pocket V1.4

Somente recomendar:

```text
SPRINT POCKET V1.4 — READ-ONLY CHART API INTEGRATION
```

se a validação real comprovar:

```text
target estável
Market WebSocket estável
schema live igual ao HAR
contexto atômico
histórico utilizável
realtime utilizável
buckets corretos
readiness confiável
zero envio
zero vazamento sensível
cleanup aprovado
```

Ainda sem automação de operações.

---

## 46. Fora de escopo

Não implementar:

```text
login automático
captura de credencial
Socket.IO independente
seleção de ativo pela Friday
changeSymbol enviado
payout operacional
saldo
conta
CALL
PUT
AutoTrade
Strategy Engine
IA
frontend Pocket
Chart API Pocket
```

---

## 47. Git

Não executar:

```text
git add
git commit
git push
git reset
git checkout
git restore
git clean
git stash
```

Não apagar a Polarium.

Não adicionar perfil do Chrome.

Confirmar ignorados:

```text
.jarvis_private/
*.har
.jarvis_cache/
```

Adicionar também, se necessário:

```text
*chrome-pocket-profile*
```

---

## 48. Entrega obrigatória

Entregar:

1. objetivo;
2. arquitetura implementada;
3. transporte CDP;
4. cliente CDP;
5. target manager;
6. identificação do socket;
7. sanitização;
8. eventos permitidos;
9. eventos descartados;
10. contexto Pocket;
11. histórico;
12. realtime;
13. catálogo de ativos;
14. readiness;
15. guard;
16. configurações;
17. CLI;
18. arquivos criados;
19. arquivos modificados;
20. testes de target;
21. testes de socket;
22. testes de sanitização;
23. testes de contexto;
24. testes de histórico;
25. testes de realtime;
26. testes de lifecycle;
27. testes de guard;
28. prova de ausência de envio;
29. prova de ausência de rede em pytest;
30. relatórios gerados;
31. resultado dos testes Pocket;
32. resultado do parser;
33. resultado do discovery;
34. resultado da suíte completa;
35. resultado do build;
36. procedimento de validação real;
37. critérios reais;
38. git status;
39. git diff;
40. riscos;
41. lacunas;
42. decisão sobre Pocket V1.4;
43. próximos passos;
44. sugestão de commit.

---

## 49. Sugestão de commit

```text
feat(pocket): add passive live session observation architecture
```