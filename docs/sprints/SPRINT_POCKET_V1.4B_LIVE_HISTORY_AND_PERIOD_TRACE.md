# FRIDAY AI TRADER

# SPRINT POCKET V1.4B — LIVE HISTORY AND PERIOD TRACE

## Status

AUDITORIA LIVE PASSIVA — HISTÓRICO E TIMEFRAME — ZERO OUTBOUND

---

## 1. Objetivo

Comprovar como a sessão live da Pocket fornece:

```text
histórico de candles
ativo atual
período/timeframe atual
```

durante observação passiva via CDP.

A Sprint Pocket V1.4A já comprovou com sessão real:

```text
observation_mode = REAL_PASSIVE_CDP
target_found = true
market_socket_found = true
stream_events = 99
ticks = 99
realtime_candles = 4
outbound_messages_originated_by_friday = 0
observer_stopped_cleanly = true
```

Porém:

```text
history_batches = 0
historical_candles = 0
updateHistoryNewFast não observado
```

Esta Sprint deve descobrir se:

1. o histórico ocorreu antes do attach CDP;
2. o histórico usa outro evento;
3. o histórico usa outro socket;
4. o histórico chega via HTTP;
5. o histórico está embutido em `updateCharts`;
6. o histórico depende de `changeSymbol`;
7. o período live pode ser extraído de `changeSymbol`, `chafor`, `updateCharts` ou outro evento;
8. o terminal não solicitou histórico durante a janela observada.

Não criar pedido de histórico.

Não enviar nenhuma mensagem.

---

## 2. Evidências comprovadas

### Realtime live

Schema live de `updateStream`:

```text
[[asset, timestamp, price]]
```

Classificação HAR versus live:

```text
IDENTICAL
```

Resultado real:

```text
stream_events = 99
ticks = 99
candles = 4
```

### Histórico

Nenhum evento:

```text
updateHistoryNewFast
```

foi observado.

Classificação atual:

```text
HISTORY_EVENT_NOT_OBSERVED
```

### Controle de mercado

Evento:

```text
chafor
```

classificado como:

```text
MARKET_CONTROL
```

Ainda não utilizado como fonte de contexto.

---

## 3. Regra principal

Esta Sprint será exclusivamente passiva e read-only.

É proibido:

```text
enviar auth
enviar changeSymbol
enviar chafor
enviar saveCharts
enviar ping-server
enviar qualquer frame
usar Runtime.evaluate
usar WebSocket.send
usar socket.emit
usar sio.emit
usar sendMessage
interceptar requests
modificar frames
automatizar login
automatizar clique
executar CALL
executar PUT
consultar saldo
ler cookies
ler tokens
ler SSID
ler Authorization
integrar Pocket ao frontend
integrar Pocket à Chart API
alterar Polarium
alterar Strategy Engine
alterar IA
```

---

## 4. Escopo permitido

Alterar somente o mínimo necessário em:

```text
app/market/providers/pocket/
tools/pocket_live_observation/
tests/market/providers/pocket/
tests/tools/pocket_parser/
```

É permitido criar:

```text
app/market/providers/pocket/live_history_trace.py
app/market/providers/pocket/live_period_trace.py
tests/market/providers/pocket/test_pocket_live_history_trace.py
tests/market/providers/pocket/test_pocket_live_period_trace.py
```

Não modificar:

```text
app/main.py
app/market/runtime.py
app/api/routes/market_chart.py
frontend/
app/market/providers/polarium/
```

---

## 5. Diagnósticos obrigatórios

Criar:

```text
.jarvis_cache/diagnostics/pocket_live_history_trace.json
.jarvis_cache/diagnostics/pocket_live_history_trace.txt
.jarvis_cache/diagnostics/pocket_live_period_trace.json
.jarvis_cache/diagnostics/pocket_live_period_trace.txt
.jarvis_cache/diagnostics/pocket_live_http_history_trace.json
.jarvis_cache/diagnostics/pocket_live_http_history_trace.txt
```

Atualizar também:

```text
pocket_real_validation.json
pocket_real_validation.txt
```

---

## 6. Auditoria de timing

Registrar:

```text
observer_started_at
chrome_started_at
target_found_at
target_attached_at
network_enabled_at
market_socket_created_at
market_socket_confirmed_at
first_change_symbol_at
first_history_event_at
first_update_charts_at
first_update_stream_at
first_tick_at
```

Classificar:

```text
ATTACHED_BEFORE_TERMINAL_LOAD
ATTACHED_DURING_TERMINAL_LOAD
ATTACHED_AFTER_TERMINAL_LOAD
TIMING_UNKNOWN
```

Se `updateStream` começar antes de qualquer histórico e o attach ocorrer após o carregamento do terminal:

```text
HISTORY_EVENT_MISSED_BEFORE_ATTACH
```

---

## 7. Estratégia de attach precoce

No modo real, o observer deverá:

```text
iniciar Chrome dedicado
anexar ao target Pocket o mais cedo possível
habilitar Network imediatamente
observar reload e navegação
revalidar target após login
continuar observando sem reiniciar o processo
```

Não navegar programaticamente após startup.

Não recarregar a página automaticamente.

O Renan poderá fazer reload manual quando solicitado.

---

## 8. Cenários de validação real

Executar três cenários separados.

### Cenário A — observer antes do login

```text
1. Iniciar observer.
2. Chrome abre.
3. Observer anexa à aba.
4. Renan faz login manual.
5. Aguardar terminal carregar.
6. Não trocar ativo por 30 segundos.
```

Objetivo:

```text
capturar histórico inicial desde o começo da sessão
```

### Cenário B — reload manual

```text
1. Observer ativo.
2. Pocket autenticada em Demo.
3. Renan recarrega manualmente a página.
4. Aguardar terminal reconstruir.
5. Não interagir por 30 segundos.
```

Objetivo:

```text
capturar histórico durante reconstrução completa do terminal
```

### Cenário C — trocas manuais

```text
EURUSD OTC M1
aguardar 20 segundos

EURUSD OTC M5
aguardar 20 segundos

AUDUSD OTC M15
aguardar 20 segundos

USDBRL OTC M5
aguardar 20 segundos
```

Objetivo:

```text
capturar evento de período e eventual histórico por troca
```

---

## 9. Eventos históricos candidatos

Auditar passivamente:

```text
updateHistoryNewFast
updateHistory
updateHistoryNew
updateCharts
loadHistory
history
candles
chart
bars
quotes
```

Não assumir nomes não observados.

Registrar todos os eventos que possuam estruturas candidatas:

```text
listas grandes
timestamps ordenáveis
valores OHLC
asset
period
timeframe
```

---

## 10. Detecção estrutural de histórico

Criar detector passivo que identifique payload candidato por shape.

Critérios permitidos:

```text
lista com 10 ou mais registros
timestamps ordenáveis
valores numéricos compatíveis com OHLC
asset identificável
period identificável ou inferível
```

Não transformar automaticamente em histórico.

Classificar:

```text
CONFIRMED_HISTORY_EVENT
CANDIDATE_HISTORY_EVENT
NON_HISTORY_EVENT
AMBIGUOUS_HISTORY_EVENT
```

---

## 11. Auditoria de updateCharts

Auditar `updateCharts` em sessão real.

Registrar somente shape sanitizado:

```text
payload root type
key paths
list lengths
numeric value types
candidate timestamp paths
candidate OHLC paths
candidate asset paths
candidate period paths
```

Responder:

```text
updateCharts contém histórico?
updateCharts contém somente layout?
updateCharts contém estado gráfico?
updateCharts contém ativo e period?
```

Não promovê-lo a histórico sem prova.

---

## 12. Auditoria HTTP

Observar passivamente eventos CDP HTTP:

```text
Network.requestWillBeSent
Network.responseReceived
Network.loadingFinished
```

Somente para endpoints candidatos relacionados a:

```text
history
candles
chart
quotes
bars
series
```

Não baixar corpo por:

```text
Network.getResponseBody
```

a menos que seja comprovadamente necessário, sanitizado e autorizado pela Sprint.

Preferência:

```text
catalogar endpoint, método, status e content-type sem corpo
```

Registrar:

```text
sanitized_host
sanitized_path
method
status
content_type
initiator_type
timestamp
candidate_reason
```

Nunca registrar query string sensível ou headers.

---

## 13. Histórico em outro socket

Catalogar todos os sockets observados.

Para cada socket registrar:

```text
event_names
frames_received
frames_sent
candidate_history_shapes
candidate_market_events
classification
```

Se o histórico aparecer em socket diferente:

```text
HISTORY_EVENT_OTHER_SOCKET
```

Não alimentar o runtime antes de confirmar ownership e segurança.

---

## 14. Contexto de período

Descobrir a fonte live oficial de:

```text
period
timeframe
```

Candidatos:

```text
changeSymbol
chafor
updateCharts
saveCharts
updateAssets
outro evento observado
```

Para cada fonte candidata registrar:

```text
event_name
direction
asset_path
period_path
value_type
observed_values
timing
socket ownership
confidence
```

---

## 15. changeSymbol live

Auditar se o navegador envia:

```text
changeSymbol
```

em todas as trocas de ativo e timeframe.

Formato esperado:

```json
{
  "asset": "EURUSD_otc",
  "period": 300
}
```

Confirmar:

```text
M1 = 60
M5 = 300
M15 = 900
```

Se observado consistentemente:

```text
PERIOD_SOURCE_CONFIRMED_CHANGE_SYMBOL
```

---

## 16. chafor live

Auditar se `chafor` contém:

```text
asset
period
timeframe
subscription
chart identifier
```

Classificar:

```text
PERIOD_SOURCE
ASSET_SOURCE
MARKET_CONTROL_ONLY
SUBSCRIPTION_CONTROL
UNKNOWN
```

Não usar como contexto sem consistência comprovada.

---

## 17. Contexto atômico

O runtime só poderá publicar:

```text
asset + period
```

quando ambos forem comprovados.

Não publicar contexto usando:

```text
ativo do tick + period antigo
ativo novo + period ausente
period novo + ativo antigo
```

Categorias:

```text
ATOMIC_CONTEXT_CONFIRMED
PARTIAL_CONTEXT_IGNORED
STALE_PERIOD_IGNORED
STALE_ASSET_IGNORED
CONTEXT_SOURCE_CONFLICT
```

---

## 18. Correlação de eventos

Criar linha do tempo por troca:

```text
user action timestamp aproximado
changeSymbol observed
chafor observed
updateCharts observed
history candidate observed
first updateStream of new asset
context published
bucket key
```

Usar tolerância temporal configurável.

Não exigir timestamp exato da ação manual.

---

## 19. Histórico e bucket

Somente se histórico live for confirmado:

```text
normalizar com parser V1.1
resolver POCKET:<asset>:<period>
gravar em store isolado
incrementar history_count
atualizar readiness
```

Não integrar ao CandleStore global.

---

## 20. Fallback proibido

Não é permitido declarar READY usando apenas candles realtime.

Enquanto histórico não existir:

```text
history_count = 0
history_state = EMPTY ou BOOTSTRAPPING
analysis_blocked = true
analysis_block_reason = POCKET_HISTORY_NOT_READY
```

Mesmo que existam candles realtime.

---

## 21. Possível histórico reconstruído

Não reconstruir 50 candles retroativos usando apenas ticks live nesta Sprint.

É permitido apenas registrar que:

```text
realtime candle accumulation exists
```

Mas isso não substitui histórico.

---

## 22. Categorias finais de ausência

Ao final, classificar uma única causa principal:

```text
HISTORY_EVENT_CONFIRMED
HISTORY_EVENT_MISSED_BEFORE_ATTACH
HISTORY_EVENT_OTHER_SOCKET
HISTORY_EVENT_DIFFERENT_NAME
HISTORY_EVENT_HTTP_ONLY
HISTORY_EVENT_NOT_TRIGGERED
HISTORY_EVENT_SCHEMA_AMBIGUOUS
HISTORY_EVENT_UNKNOWN
```

Com evidência.

---

## 23. Correção permitida

Somente após comprovação, aplicar patch mínimo para:

```text
attach mais precoce
revalidação após reload
reconhecimento de evento histórico com nome diferente
contexto de period comprovado
roteamento de socket histórico confirmado
```

Não criar request de histórico.

Não enviar mensagens.

---

## 24. Testes obrigatórios

### Timing

```text
attach antes do load
attach depois do load
history antes do attach
history depois do attach
reload manual
```

### Eventos históricos

```text
updateHistoryNewFast
evento histórico com nome alternativo
updateCharts não histórico
shape ambíguo
```

### HTTP

```text
endpoint candidato
endpoint irrelevante
sanitização de URL
sem headers
sem corpo sensível
```

### Socket ownership

```text
histórico no market socket
histórico em socket auxiliar
socket desconhecido
```

### Period

```text
changeSymbol 60
changeSymbol 300
changeSymbol 900
chafor candidato
period ausente
period inválido
conflito entre fontes
```

### Contexto

```text
asset + period atômico
asset sem period
period sem asset
stale asset
stale period
```

### Segurança

```text
zero outbound
sem Runtime.evaluate
sem getResponseBody por padrão
sem cookie
sem token
sem Authorization
```

### Regressão

```text
ticks live continuam processando
schema updateStream permanece IDENTICAL
parser offline continua passando
replay continua determinístico
```

---

## 25. Validação automatizada

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

.venv/bin/python -m pytest tests/market/providers/pocket -v
.venv/bin/python -m pytest tests/tools/pocket_parser -v
.venv/bin/python -m pytest tests/tools/pocket_discovery -v
.venv/bin/python -m pytest -v
```

Build:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run build
```

---

## 26. Validação real assistida

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

POCKET_CDP_ENABLED=true \
POCKET_CDP_OBSERVATION_ONLY=true \
POCKET_READ_ONLY=true \
POCKET_LIVE_CONNECTION_ENABLED=false \
POCKET_REAL_OBSERVATION_AUTHORIZED=true \
.venv/bin/python -m tools.pocket_live_observation
```

Realizar os cenários A, B e C descritos nesta Sprint.

Não realizar operações.

---

## 27. Critério de aceitação

A Sprint será aprovada quando:

```text
observation_mode = REAL_PASSIVE_CDP
market_socket_found = true
period source classified
M1/M5/M15 comprovados
contexto atômico publicado
stream_events > 0
ticks > 0
zero outbound
cleanup limpo
histórico confirmado ou ausência classificada com evidência
```

Para avançar à Chart API, adicionalmente exigir:

```text
historical_candles > 0
history_count confiável
bucket asset/period correto
```

---

## 28. Fora de escopo

Não implementar:

```text
Chart API Pocket
frontend Pocket
provider principal
seleção de ativo pela Friday
histórico programático
Socket.IO próprio
login automático
saldo
payout
CALL
PUT
AutoTrade
IA
Strategy Engine
```

---

## 29. Git

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

Não apagar Polarium.

Não versionar perfil Chrome, HARs ou relatórios.

---

## 30. Entrega obrigatória

Entregar:

1. objetivo;
2. evidência inicial;
3. arquitetura auditada;
4. timing do attach;
5. cenário A;
6. cenário B;
7. cenário C;
8. eventos históricos candidatos;
9. análise updateCharts;
10. análise HTTP;
11. análise de outros sockets;
12. fonte de period;
13. changeSymbol live;
14. chafor live;
15. contexto atômico;
16. correlação de eventos;
17. causa do histórico ausente;
18. categoria final;
19. patch mínimo;
20. arquivos criados;
21. arquivos modificados;
22. relatórios;
23. testes timing;
24. testes histórico;
25. testes HTTP;
26. testes socket;
27. testes period;
28. testes contexto;
29. segurança;
30. regressões;
31. testes Pocket;
32. parser;
33. discovery;
34. suíte completa;
35. build;
36. validação real;
37. ativos/timeframes comprovados;
38. historical candles;
39. ticks;
40. buckets;
41. zero outbound;
42. cleanup;
43. git status;
44. git diff;
45. riscos;
46. lacunas;
47. decisão sobre V1.4C ou V1.5;
48. próximos passos;
49. sugestão de commit.

---

## 31. Sugestão de commit

```text
chore(pocket): trace live history and timeframe ownership
```