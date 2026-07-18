# FRIDAY AI TRADER

# SPRINT POCKET V1.4C — MULTI-ASSET / TIMEFRAME BUCKET VALIDATION

## Status

VALIDAÇÃO LIVE ASSISTIDA — MULTIATIVO — MULTITIMEFRAME — ZERO OUTBOUND

---

## 1. Objetivo

Comprovar em sessão Pocket DEMO real que o provider read-only:

```text
detecta ativo e período;
recebe histórico;
recebe realtime;
cria o bucket correto;
mantém isolamento entre ativos e timeframes;
atinge readiness confiável;
não mistura candles;
não envia mensagens.
```

A validação deverá abranger obrigatoriamente:

```text
EURUSD_otc / 60
EURUSD_otc / 300
AUDUSD_otc / 900
USDBRL_otc / 300
```

Esta Sprint não deve integrar a Pocket ao frontend ou à Chart API.

---

## 2. Evidências já comprovadas

A Sprint Pocket V1.4B comprovou em sessão real:

```text
observation_mode = REAL_PASSIVE_CDP
target_found = true
market_socket_found = true
period source = changeSymbol
history event = updateHistoryNewFast
historical_candles = 99
ticks = 112
bucket = POCKET:SOL-USD_otc:300
readiness = READY
outbound_messages_originated_by_friday = 0
observer_stopped_cleanly = true
```

Também confirmou:

```text
updateCharts = não histórico
chafor = MARKET_CONTROL_ONLY
HTTP history = não observado
changeSymbol = fonte confiável de asset + period
```

---

## 3. Regra principal

Esta Sprint será exclusivamente read-only.

É proibido:

```text
enviar auth
enviar changeSymbol
enviar chafor
enviar saveCharts
enviar qualquer frame
usar Runtime.evaluate
usar WebSocket.send
usar socket.emit
usar sio.emit
usar sendMessage
automatizar login
automatizar cliques
executar CALL
executar PUT
consultar saldo
consultar payout operacional
ler cookies
ler tokens
ler SSID
ler Authorization
integrar Pocket ao frontend
integrar Pocket à Chart API
alterar Polarium
alterar IA
alterar Strategy Engine
```

---

## 4. Escopo permitido

Alterar somente o mínimo necessário em:

```text
app/market/providers/pocket/
tools/pocket_live_observation/
tests/market/providers/pocket/
```

É permitido criar:

```text
app/market/providers/pocket/multi_context_validation.py
tests/market/providers/pocket/test_pocket_multi_context_validation.py
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

## 5. Sequência real obrigatória

Com o observer iniciado antes do login, executar exatamente:

```text
1. Login manual na Pocket DEMO.
2. Aguardar terminal carregar completamente.

3. Selecionar EURUSD OTC M1.
4. Aguardar no mínimo 25 segundos.

5. Trocar para EURUSD OTC M5.
6. Aguardar no mínimo 25 segundos.

7. Trocar para AUDUSD OTC M15.
8. Aguardar no mínimo 25 segundos.

9. Trocar para USDBRL OTC M5.
10. Aguardar no mínimo 25 segundos.

11. Voltar para EURUSD OTC M1.
12. Aguardar no mínimo 20 segundos.

13. Encerrar com Control + C.
```

Não realizar operações.

---

## 6. Contextos obrigatórios

Validar:

```text
EURUSD_otc / 60 / M1
EURUSD_otc / 300 / M5
AUDUSD_otc / 900 / M15
USDBRL_otc / 300 / M5
```

Para cada contexto registrar:

```text
asset
period
timeframe
changeSymbol observed
history event observed
history batch count
historical candles
stream event count
ticks
realtime candles
bucket key
bucket count
history count
readiness
first timestamp
last timestamp
last price
context published
```

---

## 7. Chaves esperadas

Criar ou validar exclusivamente:

```text
POCKET:EURUSD_otc:60
POCKET:EURUSD_otc:300
POCKET:AUDUSD_otc:900
POCKET:USDBRL_otc:300
```

A volta ao primeiro contexto deverá reutilizar:

```text
POCKET:EURUSD_otc:60
```

sem criar bucket duplicado.

---

## 8. Isolamento de buckets

Comprovar:

```text
candles de EURUSD_otc:60 não entram em EURUSD_otc:300;
candles de EURUSD não entram em AUDUSD;
candles de AUDUSD não entram em USDBRL;
ticks de contexto antigo não alteram o contexto atual;
history_count é independente por bucket;
readiness é independente por bucket.
```

Categorias de falha:

```text
ASSET_BUCKET_MIX
TIMEFRAME_BUCKET_MIX
STALE_CONTEXT_WRITE
WRONG_BUCKET_RESOLUTION
CROSS_CONTEXT_HISTORY_COUNT
CROSS_CONTEXT_REALTIME_WRITE
```

---

## 9. Contexto atômico

Somente publicar contexto depois de confirmar:

```text
asset válido
period válido
timeframe resolvido
changeSymbol pertencente ao Market WebSocket
```

Não publicar estado parcial.

Categorias:

```text
ATOMIC_CONTEXT_CONFIRMED
PARTIAL_CONTEXT_IGNORED
STALE_CONTEXT_IGNORED
CONTEXT_SOURCE_CONFLICT
```

---

## 10. Correlação por transição

Para cada troca registrar a linha do tempo:

```text
context_previous
change_symbol_timestamp
context_published_timestamp
history_event_timestamp
first_stream_timestamp
first_tick_timestamp
bucket_created_timestamp
readiness_ready_timestamp
```

Calcular:

```text
context_publish_latency_ms
history_latency_ms
first_tick_latency_ms
ready_latency_ms
```

Não definir limites artificiais como falha sem evidência.

---

## 11. Histórico por contexto

Para cada contexto:

```text
updateHistoryNewFast deve corresponder ao asset e period atuais;
histórico deve ser escrito apenas no bucket correspondente;
history_count deve considerar somente timestamps históricos únicos;
duplicatas devem ser filtradas;
realtime não deve incrementar history_count.
```

Se não houver histórico:

```text
HISTORY_NOT_OBSERVED_FOR_CONTEXT
```

---

## 12. Realtime por contexto

Para cada contexto:

```text
updateStream deve fornecer tick do ativo atual;
tick deve atualizar last_price;
candle realtime deve usar o period atual;
realtime deve escrever apenas no bucket atual;
tick do ativo anterior deve ser ignorado ou roteado ao bucket correspondente sem alterar contexto visível.
```

Categorias:

```text
REALTIME_CONTEXT_MATCH
REALTIME_BACKGROUND_ASSET
REALTIME_WRONG_PERIOD
REALTIME_STALE_CONTEXT
```

---

## 13. Readiness

Para cada bucket:

```text
0 históricos → EMPTY ou BOOTSTRAPPING
1 a 49 → LIMITED
50 ou mais → READY
```

Não usar candles realtime para alcançar READY.

Registrar:

```text
history_count
history_required
history_state
bootstrap_complete
analysis_blocked
analysis_block_reason
```

---

## 14. Revisita de contexto

Quando voltar para:

```text
EURUSD_otc / 60
```

comprovar:

```text
mesma chave reutilizada
histórico anterior preservado
nenhuma duplicação massiva
realtime continua atualizando
readiness permanece coerente
contexto não volta para M5
```

Categorias:

```text
BUCKET_REUSED
BUCKET_DUPLICATED
STALE_PERIOD_RESTORED
CONTEXT_REVISIT_OK
```

---

## 15. Diagnóstico obrigatório

Criar:

```text
PocketMultiContextValidation
```

Relatórios:

```text
.jarvis_cache/diagnostics/pocket_multi_context_validation.json
.jarvis_cache/diagnostics/pocket_multi_context_validation.txt
```

Também criar:

```text
.jarvis_cache/diagnostics/pocket_bucket_isolation_report.json
.jarvis_cache/diagnostics/pocket_bucket_isolation_report.txt
```

---

## 16. Conteúdo do relatório principal

Registrar:

```text
observation_mode
target_found
market_socket_found
contexts_expected
contexts_observed
context_sequence
context_transitions
history_batches_by_context
historical_candles_by_context
stream_events_by_context
ticks_by_context
realtime_candles_by_context
buckets
bucket_counts
history_counts
readiness_by_bucket
context_latencies
failure_categories
outbound_messages_originated_by_friday
observer_stopped_cleanly
```

---

## 17. Relatório de isolamento

Para cada bucket:

```text
bucket_key
asset
period
timeframe
historical_count
realtime_count
first_timestamp
last_timestamp
foreign_asset_count
foreign_period_count
duplicate_count
stale_write_count
isolation_status
```

Status:

```text
ISOLATED
MIXED_ASSET
MIXED_PERIOD
STALE_WRITE
UNKNOWN
```

---

## 18. Integridade dos candles

Validar por bucket:

```text
timestamp ordenável
OHLC válido
high >= low
high >= open
high >= close
low <= open
low <= close
preço positivo
asset correto
period correto
```

Não registrar payload bruto.

---

## 19. Eventos de background

Se `updateStream` entregar múltiplos ativos simultaneamente:

```text
preservar asset do tick;
rotear somente para bucket conhecido do ativo/período;
não alterar contexto visível;
não misturar com ativo atual.
```

Se o period do ativo em background não puder ser comprovado:

```text
BACKGROUND_PERIOD_UNKNOWN
```

e não gravar candle.

---

## 20. Critério por contexto

Cada contexto será classificado:

```text
PASS
PARTIAL
FAIL
NOT_OBSERVED
```

PASS exige:

```text
changeSymbol correto
contexto atômico
histórico > 0
ticks > 0
bucket correto
zero mistura
readiness coerente
```

---

## 21. Critério global

A Sprint será aprovada apenas se:

```text
os 4 contextos forem observados;
os 4 buckets forem criados;
histórico e ticks existirem por contexto;
nenhuma mistura de ativo ou timeframe ocorrer;
a revisita EURUSD M1 reutilizar o bucket;
zero outbound;
cleanup limpo.
```

Caso algum contexto falhe, não integrar Chart API ainda.

---

## 22. Patch permitido

Somente após evidência, corrigir minimamente:

```text
resolução de bucket
isolamento de contexto
deduplicação
roteamento de realtime
revisita de contexto
period source
```

Não alterar:

```text
Chart API
frontend
CandleStore global
Polarium
IA
Strategy Engine
```

---

## 23. Testes obrigatórios

### Contextos

```text
EURUSD 60
EURUSD 300
AUDUSD 900
USDBRL 300
revisita EURUSD 60
```

### Buckets

```text
criação
reutilização
isolamento por asset
isolamento por period
ausência de duplicação
```

### Histórico

```text
histórico correto por contexto
duplicata filtrada
history_count independente
realtime não altera history_count
```

### Realtime

```text
tick do contexto atual
tick de background
tick stale
period desconhecido
roteamento correto
```

### Readiness

```text
READY independente por bucket
LIMITED em um bucket não altera outro
```

### Integridade

```text
asset correto
period correto
OHLC válido
timestamps ordenados
```

### Lifecycle

```text
start
trocas sucessivas
revisita
stop
cleanup
```

### Segurança

```text
zero outbound
sem Runtime.evaluate
sem WebSocket.send
sem socket.emit
sem sio.emit
sem sendMessage
sem dados sensíveis
```

---

## 24. Regressões obrigatórias

Confirmar:

```text
Pocket V1.1 parser continua verde;
Pocket V1.2 replay continua determinístico;
Pocket V1.4A updateStream continua gerando ticks;
Pocket V1.4B history/period continuam comprovados.
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

Executar integralmente a sequência da Seção 5.

---

## 27. Critério para avançar à Pocket V1.5

Somente recomendar:

```text
SPRINT POCKET V1.5 — READ-ONLY CHART API PROVIDER INTEGRATION
```

quando:

```text
4 contextos reais aprovados;
4 buckets isolados;
histórico real por bucket;
ticks reais por bucket;
M1/M5/M15 comprovados;
revisita de contexto aprovada;
readiness confiável;
zero outbound;
cleanup limpo.
```

---

## 28. Fora de escopo

Não implementar:

```text
Chart API Pocket
frontend Pocket
provider principal
seleção pela Friday
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
3. arquitetura;
4. sequência real executada;
5. contextos esperados;
6. contextos observados;
7. transições;
8. EURUSD M1;
9. EURUSD M5;
10. AUDUSD M15;
11. USDBRL M5;
12. revisita EURUSD M1;
13. buckets criados;
14. isolamento;
15. históricos por bucket;
16. ticks por bucket;
17. candles realtime por bucket;
18. history count;
19. readiness;
20. latências;
21. duplicatas;
22. stale writes;
23. background events;
24. integridade OHLC;
25. categorias de falha;
26. patch mínimo;
27. arquivos criados;
28. arquivos modificados;
29. relatórios;
30. testes contextos;
31. testes buckets;
32. testes histórico;
33. testes realtime;
34. testes readiness;
35. testes integridade;
36. testes lifecycle;
37. testes segurança;
38. regressões;
39. testes Pocket;
40. parser;
41. discovery;
42. suíte completa;
43. build;
44. validação real;
45. zero outbound;
46. cleanup;
47. git status;
48. git diff;
49. riscos;
50. lacunas;
51. decisão sobre V1.5;
52. próximos passos;
53. sugestão de commit.

---

## 31. Sugestão de commit

```text
test(pocket): validate live multi-asset timeframe bucket isolation
```