# FRIDAY AI TRADER

# SPRINT POCKET V1.2 — READ-ONLY LIVE FEED ARCHITECTURE

## Status

ARQUITETURA E IMPLEMENTAÇÃO CONTROLADA — SEM CONEXÃO REAL — SOMENTE LEITURA

---

## 1. Objetivo

Projetar e implementar a arquitetura do futuro feed ao vivo da Pocket Option em modo exclusivamente read-only, utilizando os schemas comprovados pela Sprint Pocket V1.1.

Esta Sprint deverá criar:

```text
Pocket Provider Contracts
→ Pocket Transport Interface
→ Pocket Session State
→ Pocket Event Pipeline
→ Pocket Read-Only Runtime
→ Pocket Store Adapter
→ Fake Pocket Transport
→ testes determinísticos
```

Não conectar à Pocket Option nesta Sprint.

Não reutilizar credenciais dos HARs.

Não abrir WebSocket real.

Não enviar mensagens.

---

## 2. Evidências comprovadas pela Pocket V1.1

A Sprint Pocket V1.1 confirmou:

```text
protocol: Socket.IO / Engine.IO
HAR compatibility: COMPATIBLE
candle schema: STABLE
tick schema: STABLE
asset schema: PARTIAL_STABLE
candles found: 901
candles accepted: 890
candles rejected: 11
ticks found: 419
ticks accepted: 419
ticks rejected: 0
```

Schema de candle comprovado:

```text
[timestamp, open, close, high, low, volume]
```

Schema de tick comprovado:

```text
[asset, timestamp, price]
```

Evento de troca de ativo/timeframe comprovado:

```text
changeSymbol
{
  "asset": "EURUSD_otc",
  "period": 300
}
```

Evento histórico comprovado:

```text
updateHistoryNewFast
```

Evento realtime comprovado:

```text
updateStream
```

Evento de catálogo de ativos comprovado:

```text
updateAssets
```

Buckets offline comprovados:

```text
POCKET:EURUSD_otc:60
POCKET:EURUSD_otc:300
POCKET:AUDUSD_otc:60
POCKET:AUDUSD_otc:900
POCKET:USDBRL_otc:60
POCKET:USDBRL_otc:300
POCKET:USDBRL_otc:900
```

---

## 3. Regra principal

Esta Sprint não terá conexão real.

É proibido:

```text
abrir WebSocket da Pocket
conectar ao host api-us-south.po.market
enviar auth
enviar changeSymbol
enviar saveCharts
enviar ping-server
reutilizar token
reutilizar cookie
reutilizar SSID
reutilizar Authorization
automatizar login
abrir navegador
usar Chrome CDP
usar Browser Bridge
usar Playwright
usar Selenium
executar CALL
executar PUT
consultar saldo
consultar conta
alterar a Polarium
alterar o frontend funcional
```

Toda execução deverá utilizar transporte falso, replay offline ou fixtures sanitizadas.

---

## 4. Resultado esperado

Ao final da Sprint deverá existir uma arquitetura capaz de executar:

```text
FakePocketTransport
→ PocketReadOnlyLiveSource
→ PocketEventRouter
→ PocketMarketRuntime
→ PocketCandleStoreAdapter
→ CandleStore isolado
→ Session Context Pocket
→ status e métricas
```

Sem rede externa.

---

## 5. Arquitetura alvo

Criar:

```text
app/market/providers/pocket/
```

Estrutura recomendada:

```text
app/market/providers/pocket/
├── __init__.py
├── models.py
├── config.py
├── contracts.py
├── transport.py
├── fake_transport.py
├── event_router.py
├── runtime.py
├── live_source.py
├── session_context.py
├── candle_store_adapter.py
├── readiness.py
├── runtime_guard.py
├── metrics.py
├── errors.py
└── diagnostics.py
```

Criar testes em:

```text
tests/market/providers/pocket/
```

Não copiar a arquitetura Polarium cegamente.

Reutilizar apenas abstrações comprovadamente genéricas.

---

## 6. Separação de responsabilidades

A arquitetura deverá separar claramente:

```text
Transport
Protocol Parsing
Domain Events
Runtime State
Candle Storage
Readiness
Session Context
Diagnostics
```

Nenhuma classe deverá acumular múltiplas responsabilidades.

---

## 7. Pocket Transport Contract

Criar uma interface abstrata:

```text
PocketTransport
```

Responsabilidades permitidas:

```text
start()
stop()
is_running()
next_event()
status()
```

A interface não deverá conhecer CandleStore, Readiness ou frontend.

Não incluir métodos de execução de operações.

Não incluir:

```text
buy()
call()
put()
order()
trade()
execute()
```

---

## 8. Fake Pocket Transport

Criar:

```text
FakePocketTransport
```

Ele deverá simular:

```text
Socket connected
auth/success
updateAssets
changeSymbol observed
updateHistoryNewFast
updateStream
disconnect
reconnect
invalid frame
unknown event
```

Os dados deverão vir de:

```text
fixtures sanitizadas
eventos normalizados da Pocket V1.1
replay offline
```

Não carregar payload auth bruto.

---

## 9. Pocket Read-Only Live Source

Criar:

```text
PocketReadOnlyLiveSource
```

Responsabilidades:

```text
iniciar transport
receber eventos
encaminhar ao event router
manter estado técnico
registrar erros controlados
parar transport
```

Não deverá:

```text
enviar changeSymbol
enviar auth real
abrir socket
escrever diretamente no CandleStore
calcular indicadores
atualizar frontend
executar ordens
```

---

## 10. Pocket Event Router

Criar roteamento explícito:

```text
updateHistoryNewFast → historical handler
updateStream         → realtime handler
updateAssets         → asset catalog handler
updateCharts         → chart metadata handler
auth/success         → session state handler
unknown event        → diagnostic handler
```

O router deverá receber somente eventos já normalizados pelo parser.

Não interpretar Socket.IO bruto dentro do runtime.

---

## 11. Pocket Market Runtime

Criar:

```text
PocketMarketRuntime
```

Responsabilidades:

```text
manter contexto de mercado
receber eventos de domínio
gravar histórico
gravar realtime
atualizar readiness
atualizar métricas
expor status sanitizado
```

O runtime deverá trabalhar com:

```text
asset
period
timeframe
history_count
realtime_count
readiness
last_price
last_update
```

---

## 12. Session Context Pocket

Criar modelo explícito:

```text
PocketSessionContext
```

Campos mínimos:

```text
provider
connection_state
session_state
asset
display_name
market_type
is_otc
period
timeframe
last_price
history_count
history_required
history_state
bootstrap_complete
last_update
analysis_blocked
analysis_block_reason
```

Valores esperados:

```text
provider = POCKET
```

Estados de conexão:

```text
STOPPED
STARTING
CONNECTING
ONLINE
RECONNECTING
OFFLINE
ERROR
```

Estados de histórico:

```text
EMPTY
BOOTSTRAPPING
LIMITED
READY
ERROR
```

---

## 13. Chave de série

Definir oficialmente:

```text
POCKET:<asset>:<period>
```

Exemplos:

```text
POCKET:EURUSD_otc:60
POCKET:EURUSD_otc:300
POCKET:AUDUSD_otc:900
POCKET:USDBRL_otc:300
```

Não usar IDs numéricos inventados.

Não converter o símbolo Pocket para `active_id` Polarium.

---

## 14. CandleStore Adapter

Criar:

```text
PocketCandleStoreAdapter
```

Ele deverá converter:

```text
PocketNormalizedCandle
```

para o formato genérico aceito pelo CandleStore.

Responsabilidades:

```text
resolver chave
adicionar candle
substituir candle do mesmo timestamp
deduplicar
listar série
obter quantidade
obter último candle
```

Não alterar o CandleStore interno sem necessidade comprovada.

---

## 15. Histórico

Ao receber:

```text
PocketHistoryBatch
```

O runtime deverá:

```text
validar asset
validar period
resolver bucket
ordenar candles
gravar candles
registrar history_count
atualizar readiness
```

Não assumir exatamente 20 candles em todo evento futuro.

Usar o tamanho real do lote.

---

## 16. Realtime

Ao receber:

```text
PocketRealtimeTick
```

O runtime deverá:

```text
validar asset
validar timestamp
validar price
atualizar last_price
atualizar last_update
encaminhar ao candle builder apropriado
```

Nesta Sprint, o candle builder poderá ser:

```text
PocketRealtimeCandleBuilder
```

Somente se a arquitetura genérica existente não puder ser reutilizada com segurança.

---

## 17. Construção realtime de candles

O builder deverá agregar ticks por:

```text
asset
period
bucket timestamp
```

Para cada bucket:

```text
open = primeiro tick
high = maior preço
low = menor preço
close = último tick
```

O volume deverá ser:

```text
quantidade de ticks
```

ou `None`, conforme contrato escolhido e documentado.

Cobrir:

```text
60 segundos
300 segundos
900 segundos
```

---

## 18. Candle histórico versus candle realtime

A arquitetura deverá distinguir:

```text
historical candle
realtime candle
```

Regras:

```text
histórico incrementa history_count
realtime não incrementa history_count histórico
realtime pode atualizar/substituir candle aberto
candle fechado deve ser preservado
```

Não misturar readiness histórico com quantidade de ticks realtime.

---

## 19. Readiness

Criar:

```text
PocketReadinessTracker
```

Configuração inicial recomendada:

```text
history_required = 50
```

Mas permitir configuração.

Estados:

```text
EMPTY
BOOTSTRAPPING
LIMITED
READY
ERROR
```

Regras:

```text
0 candles históricos → EMPTY
request/context iniciado → BOOTSTRAPPING
1 até history_required - 1 → LIMITED
history_count >= history_required → READY
erro irrecuperável → ERROR
```

O modo fake deverá testar todas as transições.

---

## 20. Runtime Guard

Criar:

```text
PocketRuntimeGuard
```

Nesta Sprint ele deverá bloquear qualquer ação que não seja read-only.

Ações permitidas:

```text
PROCESS_ASSET_CATALOG
PROCESS_HISTORY
PROCESS_REALTIME
PROCESS_CHART_METADATA
UPDATE_SESSION_STATE
```

Ações bloqueadas:

```text
AUTHENTICATE_REAL_SESSION
SEND_CHANGE_SYMBOL
SEND_ORDER
SEND_CALL
SEND_PUT
READ_BALANCE
READ_PERSONAL_DATA
```

Qualquer tentativa deverá gerar:

```text
POCKET_READ_ONLY_GUARD_BLOCKED
```

---

## 21. Asset Catalog

Criar modelo:

```text
PocketAssetCatalog
```

Usar apenas os campos comprovados:

```text
symbol
display_name
market_type
supported_periods
```

Preservar campos ainda desconhecidos como:

```text
unknown_numeric_fields
unknown_boolean_fields
```

Não usar payout ou disponibilidade como regra de negócio nesta Sprint.

---

## 22. Payout e disponibilidade

Payout e disponibilidade continuam fora de uso operacional.

A arquitetura poderá armazenar:

```text
candidate_payout
candidate_availability
```

Mas não deverá:

```text
filtrar ativo
bloquear ativo
ordenar ativo
decidir operação
mostrar payout como confirmado
```

---

## 23. Configuração

Criar configurações isoladas:

```text
pocket_provider_enabled = false
pocket_live_connection_enabled = false
pocket_read_only = true
pocket_history_required = 50
```

Defaults obrigatórios:

```text
false
false
true
50
```

Nenhuma configuração deverá iniciar conexão externa.

---

## 24. Estado padrão

Mesmo quando o provider estiver habilitado em testes, a conexão real deverá permanecer desabilitada:

```text
pocket_live_connection_enabled = false
```

Se alguém tentar iniciar conexão real nesta Sprint, retornar:

```text
POCKET_LIVE_CONNECTION_DISABLED
```

---

## 25. Diagnóstico

Criar relatório sanitizado:

```text
.jarvis_cache/diagnostics/pocket_runtime_architecture_report.json
.jarvis_cache/diagnostics/pocket_runtime_architecture_report.txt
```

Registrar:

```text
transport
running
connection_state
events_received
events_routed
history_batches
historical_candles
realtime_ticks
realtime_candles
buckets
current_context
history_count
readiness
unknown_events
parse_errors
guard_blocks
last_error
```

---

## 26. Métricas

Criar:

```text
PocketRuntimeMetrics
```

Campos mínimos:

```text
events_received
events_processed
events_rejected
history_batches
historical_candles_written
historical_candles_rejected
ticks_received
ticks_processed
ticks_rejected
realtime_candles_created
realtime_candles_updated
duplicate_candles
unknown_events
guard_blocks
```

---

## 27. Erros controlados

Criar códigos:

```text
POCKET_PROVIDER_DISABLED
POCKET_LIVE_CONNECTION_DISABLED
POCKET_TRANSPORT_NOT_RUNNING
POCKET_EVENT_INVALID
POCKET_ASSET_MISSING
POCKET_PERIOD_MISSING
POCKET_PERIOD_UNSUPPORTED
POCKET_HISTORY_INVALID
POCKET_TICK_INVALID
POCKET_STORE_WRITE_FAILED
POCKET_READ_ONLY_GUARD_BLOCKED
POCKET_UNKNOWN_EVENT
POCKET_RUNTIME_ERROR
```

Nenhuma exceção isolada deverá derrubar todo o runtime fake.

---

## 28. Replay como transport

Permitir que o parser offline da V1.1 alimente o runtime por meio de um adapter:

```text
PocketReplayTransport
```

Fluxo:

```text
HAR
→ PocketOfflineReplayEngine
→ PocketReplayTransport
→ PocketReadOnlyLiveSource
→ PocketMarketRuntime
```

Isso permitirá validar a arquitetura como se fosse um feed vivo, mas sem rede.

---

## 29. Isolamento de sessões

O replay deverá permitir:

```text
HAR 1
HAR 2
```

como sessões separadas.

O runtime deverá suportar:

```text
start
process session
stop
clear transient state
start new session
```

Não carregar contexto anterior silenciosamente.

---

## 30. Limpeza de estado

No `stop()`:

```text
parar transport
limpar tasks
limpar contexto transitório
limpar candle aberto realtime
limpar subscriptions internas
preservar ou limpar store conforme configuração explícita
```

Não deixar:

```text
locks
owners
pending requests
tasks
callbacks
```

residuais.

---

## 31. Integração com o runtime principal

Nesta Sprint, não registrar o provider Pocket no startup principal da Friday.

Não modificar:

```text
app/main.py
app/market/runtime.py
frontend/
```

A arquitetura deverá ser instanciada apenas pelos testes e pelo CLI de demonstração controlado.

---

## 32. CLI de demonstração

Criar:

```text
tools/pocket_runtime_demo/
```

ou um comando equivalente dentro do provider.

Executar:

```bash
.venv/bin/python -m tools.pocket_runtime_demo
```

O demo deverá:

```text
carregar HARs
alimentar PocketReplayTransport
iniciar runtime
processar eventos
exibir resumo sanitizado
parar runtime
```

Não exibir payload bruto.

---

## 33. Resultado esperado do demo

Exemplo:

```text
Pocket Read-Only Runtime Demo

transport: REPLAY
sessions: 2
events_received: 800+
history_batches: 9
historical_candles: 890
realtime_ticks: 419
buckets: 7
readiness:
  EURUSD_otc/60: READY
  EURUSD_otc/300: READY
  AUDUSD_otc/60: LIMITED ou READY conforme dados
runtime_guard: READ_ONLY
live_connection: DISABLED
```

Não exigir números artificiais.

Usar os dados reais processados.

---

## 34. Testes obrigatórios

Criar testes para:

### Transport

```text
start
stop
next_event
transport vazio
transport com erro
replay ordenado
```

### Live Source

```text
start
stop
evento roteado
evento desconhecido
erro por evento não fatal
conexão real bloqueada
```

### Runtime

```text
contexto inicial
history batch
realtime tick
asset catalog
chart metadata
erro controlado
stop/start
```

### Store Adapter

```text
bucket por asset/period
append
replace
deduplicação
ordenação
último candle
```

### Candle Builder

```text
M1
M5
M15
open
high
low
close
virada de bucket
tick duplicado
tick fora de ordem
```

### Readiness

```text
EMPTY
BOOTSTRAPPING
LIMITED
READY
ERROR
```

### Guard

```text
ações read-only permitidas
auth real bloqueado
changeSymbol enviado bloqueado
CALL bloqueado
PUT bloqueado
ordem bloqueada
saldo bloqueado
```

### Replay

```text
HAR 1
HAR 2
duas sessões
reset entre sessões
resultado determinístico
```

### Segurança

```text
sem token
sem cookie
sem authorization
sem SSID
sem payload auth
sem credenciais
```

---

## 35. Testes de integração offline

Utilizar os HARs privados somente quando presentes:

```text
.jarvis_private/pocket_hars/pocketoption.com.har
.jarvis_private/pocket_hars/pocketoption.com(1).har
```

Os testes deverão ser ignorados se os arquivos não existirem.

Com os HARs presentes, comprovar:

```text
7 buckets
histórico processado
ticks processados
readiness calculada
runtime encerra limpo
nenhuma conexão externa
```

---

## 36. Verificação de ausência de rede

Adicionar teste ou mecanismo para comprovar que:

```text
socket.socket
websockets.connect
aiohttp.ClientSession
requests
httpx
```

não são utilizados pelo provider Pocket nesta Sprint.

A execução deverá ser 100% local.

---

## 37. Validação automatizada

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

.venv/bin/python -m pytest tests/market/providers/pocket -v
.venv/bin/python -m pytest tests/tools/pocket_parser -v
.venv/bin/python -m pytest tests/tools/pocket_discovery -v
.venv/bin/python -m pytest -v
```

Executar demo:

```bash
.venv/bin/python -m tools.pocket_runtime_demo
```

Executar build:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run build
```

---

## 38. Critérios de aceitação

A Sprint será aceita quando:

```text
provider Pocket isolado existir
transport contract existir
fake/replay transport funcionar
live source read-only funcionar
runtime processar histórico
runtime processar ticks
store adapter criar buckets corretos
readiness funcionar
guard bloquear ações proibidas
stop/start não deixar resíduos
demo offline funcionar
nenhuma conexão externa ocorrer
todos os testes passarem
build passar
```

---

## 39. Critério para avançar à Pocket V1.3

Só recomendar:

```text
SPRINT POCKET V1.3 — LIVE READ-ONLY SESSION DISCOVERY
```

se:

```text
arquitetura estável
replay determinístico
schemas estáveis
readiness correto
guard read-only aprovado
nenhum vazamento sensível
nenhum acoplamento Polarium
nenhuma conexão externa nesta Sprint
```

A V1.3 deverá continuar sem execução de operações.

---

## 40. Fora de escopo

Não implementar:

```text
Pocket login
auth automático
WebSocket real
Socket.IO real
changeSymbol enviado
seleção de ativo pela Friday
payout operacional
saldo
conta
execução
CALL
PUT
AutoTrade
frontend Pocket
Chart API Pocket
IA Pocket
```

---

## 41. Git

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

Não apagar código da Polarium.

Não adicionar HARs.

Confirmar que permanecem ignorados:

```text
.jarvis_private/
*.har
.jarvis_cache/
```

---

## 42. Entrega obrigatória

Entregar:

1. objetivo;
2. arquitetura implementada;
3. contratos criados;
4. transport criado;
5. fake transport;
6. replay transport;
7. live source;
8. runtime;
9. session context;
10. store adapter;
11. candle builder;
12. readiness;
13. guard;
14. métricas;
15. erros controlados;
16. arquivos criados;
17. arquivos modificados;
18. histórico processado;
19. ticks processados;
20. candles realtime;
21. buckets criados;
22. readiness por bucket;
23. sessões processadas;
24. eventos desconhecidos;
25. guard blocks;
26. limpeza de estado;
27. prova de ausência de rede;
28. relatórios;
29. demo;
30. testes criados;
31. testes específicos;
32. testes Pocket parser;
33. testes Pocket discovery;
34. suíte completa;
35. build;
36. git status;
37. git diff;
38. riscos;
39. lacunas;
40. decisão sobre Pocket V1.3;
41. próximos passos;
42. sugestão de commit.

---

## 43. Sugestão de commit

```text
feat(pocket): add read-only market provider architecture
```