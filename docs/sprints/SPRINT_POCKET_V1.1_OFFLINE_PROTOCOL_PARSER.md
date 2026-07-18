# FRIDAY AI TRADER

# SPRINT POCKET V1.1 — OFFLINE PROTOCOL PARSER

## Status

IMPLEMENTAÇÃO OFFLINE — SEM CONEXÃO COM A POCKET — SEM AUTOMAÇÃO

---

## 1. Objetivo

Implementar um parser offline, determinístico, testável e sanitizado para os eventos de mercado da Pocket Option já comprovados nos dois arquivos HAR da Sprint Pocket V1.0.

O parser deverá transformar frames Socket.IO capturados nos HARs em eventos de domínio normalizados da Friday.

Fluxo esperado:

```text
HAR sanitizado
→ frame Engine.IO / Socket.IO
→ parser Pocket
→ evento de domínio
→ candle normalizado
→ tick normalizado
→ catálogo de ativos normalizado
→ CandleStore isolado de teste
→ relatório offline
```

Esta Sprint não deve criar conexão ao vivo com a Pocket.

---

## 2. Evidências comprovadas pela Sprint Pocket V1.0

Foram analisados integralmente:

```text
.jarvis_private/pocket_hars/pocketoption.com.har
.jarvis_private/pocket_hars/pocketoption.com(1).har
```

Resultado da descoberta:

```text
requests_total: 541
websocket_count: 14
main_socket: wss://api-us-south.po.market/socket.io/?EIO=4&transport=websocket
protocol: Socket.IO / Engine.IO
viability: EXCELLENT
technical_score: 9.5
```

Eventos enviados comprovados:

```text
auth
changeSymbol
saveCharts
ping-server
subfor
unsubfor
signals/stats
signals/subscribe
```

Eventos recebidos comprovados:

```text
auth/success
updateAssets
updateCharts
updateHistoryNewFast
updateStream
updateOpenedDeals
updateClosedDeals
signals/update
```

Formato comprovado de troca de ativo/timeframe:

```text
changeSymbol → {"asset":"EURUSD_otc","period":300}
```

Ativos e períodos observados:

```text
EURUSD_otc / 60
EURUSD_otc / 300
AUDUSD_otc / 60
AUDUSD_otc / 900
USDBRL_otc / 60
USDBRL_otc / 300
USDBRL_otc / 900
```

Histórico comprovado:

```text
updateHistoryNewFast
```

Tempo real comprovado:

```text
updateStream
```

Catálogo de ativos comprovado:

```text
updateAssets
```

---

## 3. Regra principal

Esta Sprint é exclusivamente offline.

É proibido:

```text
conectar à Pocket
abrir WebSocket real
reutilizar token
reutilizar cookie
reutilizar SSID
reutilizar Authorization
automatizar login
enviar changeSymbol
enviar auth
enviar qualquer frame
executar CALL
executar PUT
consultar saldo real
alterar conta
criar Browser Bridge
criar extensão
usar Playwright
usar Selenium
automatizar navegador
alterar a integração Polarium
alterar a Friday funcional
```

Os HARs devem ser tratados somente como arquivos locais de entrada.

---

## 4. Resultado esperado

Ao final da Sprint, o projeto deverá ser capaz de executar:

```bash
.venv/bin/python -m tools.pocket_parser \
  --har ".jarvis_private/pocket_hars/pocketoption.com.har" \
  --har ".jarvis_private/pocket_hars/pocketoption.com(1).har"
```

E gerar eventos normalizados semelhantes a:

```text
PocketAssetChanged
PocketHistoryBatch
PocketRealtimeTick
PocketAssetCatalog
PocketChartUpdate
```

Sem conexão externa.

---

## 5. Arquitetura

Criar um módulo novo e isolado:

```text
tools/pocket_parser/
```

Estrutura recomendada:

```text
tools/pocket_parser/
├── __init__.py
├── __main__.py
├── models.py
├── frame_reader.py
├── engineio_parser.py
├── socketio_parser.py
├── event_router.py
├── asset_parser.py
├── history_parser.py
├── stream_parser.py
├── chart_parser.py
├── candle_normalizer.py
├── tick_normalizer.py
├── asset_normalizer.py
├── replay_engine.py
├── offline_store.py
├── validator.py
├── sanitizer.py
└── report_generator.py
```

Criar testes em:

```text
tests/tools/pocket_parser/
```

Não acoplar o novo parser diretamente ao runtime principal da Friday nesta Sprint.

---

## 6. Reutilização obrigatória

Auditar antes de criar código duplicado:

```text
tools/pocket_discovery/
```

Reutilizar, quando seguro:

```text
parser Engine.IO existente
parser Socket.IO existente
sanitização existente
modelos existentes
loader de HAR
catálogo de eventos
```

Não duplicar código apenas para manter os módulos separados.

Se uma função da V1.0 puder ser promovida para código compartilhado sem alterar comportamento, documentar a mudança.

Não realizar refatoração ampla.

---

## 7. Modelos de domínio

Criar modelos explícitos e tipados.

### 7.1 PocketSocketEvent

Campos mínimos:

```text
event_name
direction
timestamp
payload
source_har
socket_host
socket_path
frame_index
```

O payload armazenado no modelo interno deve ser sanitizado.

---

### 7.2 PocketAssetChanged

Campos mínimos:

```text
asset
display_name
market_type
is_otc
period
timeframe
timestamp
```

Conversões obrigatórias:

```text
60  → M1
300 → M5
900 → M15
```

Não aceitar período não suportado silenciosamente.

---

### 7.3 PocketHistoryBatch

Campos mínimos:

```text
asset
period
timeframe
candles
history_count
first_timestamp
last_timestamp
source_event
```

---

### 7.4 PocketRealtimeTick

Campos mínimos:

```text
asset
price
timestamp
source_event
sequence
```

Campos adicionais só podem ser criados quando comprovados pelos HARs.

---

### 7.5 PocketAssetInfo

Campos mínimos quando comprovados:

```text
symbol
display_name
is_otc
market_type
is_available
payout
supported_periods
raw_fields_detected
```

Campos cuja semântica ainda não esteja comprovada devem permanecer como:

```text
unknown_numeric_fields
unknown_boolean_fields
```

Não inventar nomes como payout ou disponibilidade sem evidência suficiente.

---

### 7.6 PocketNormalizedCandle

Campos obrigatórios:

```text
provider
symbol
period
timeframe
timestamp
open
high
low
close
volume
is_closed
source_event
```

Valor obrigatório:

```text
provider = POCKET
```

Volume poderá ser `None` somente se não existir no protocolo.

---

## 8. Parser Engine.IO

Interpretar passivamente frames como:

```text
0
2
3
40
41
42[...]
```

Classificar:

```text
ENGINE_OPEN
PING
PONG
SOCKET_CONNECT
SOCKET_DISCONNECT
SOCKET_EVENT
UNKNOWN_ENGINE_FRAME
```

O parser não poderá lançar exceção fatal por frame inválido.

Frames inválidos devem gerar resultado controlado:

```text
PARSE_ERROR
```

Com:

```text
frame_index
reason
sanitized_preview
```

---

## 9. Parser Socket.IO

Para frames:

```text
42["eventName", {...}]
```

Extrair:

```text
event_name
payload
payload_type
payload_keys
direction
timestamp
```

Cobrir:

```text
payload dict
payload list
payload string
payload number
payload null
evento sem payload
JSON inválido
frame incompleto
```

Não executar conteúdo do payload.

---

## 10. Event Router

Criar roteamento explícito:

```text
changeSymbol         → asset_parser
updateHistoryNewFast → history_parser
updateStream         → stream_parser
updateAssets         → asset_parser
updateCharts         → chart_parser
```

Eventos conhecidos, mas fora do escopo de mercado:

```text
updateOpenedDeals
updateClosedDeals
signals/update
auth
auth/success
```

Devem ser catalogados, porém não transformados em candles ou ticks.

Eventos desconhecidos devem ser preservados como:

```text
PocketUnknownEvent
```

Sem derrubar o replay.

---

## 11. Parser de changeSymbol

Validar o formato comprovado:

```json
{
  "asset": "EURUSD_otc",
  "period": 300
}
```

Normalizar:

```text
asset = EURUSD_otc
display_name = EURUSD OTC
market_type = OTC
is_otc = true
period = 300
timeframe = M5
```

Cobrir:

```text
ativo OTC
ativo não OTC
period 60
period 300
period 900
ativo ausente
period ausente
period inválido
payload inválido
```

Não enviar `changeSymbol`. Apenas interpretar frames já capturados.

---

## 12. Parser de updateHistoryNewFast

Mapear o evento real observado nos HARs.

Campos comprovados:

```text
asset
period
history
candles
```

O parser deverá:

1. identificar o ativo;
2. identificar o período;
3. identificar o lote de candles;
4. distinguir `history` de `candles`;
5. descobrir o formato semântico dos arrays;
6. converter os itens para `PocketNormalizedCandle`;
7. ordenar por timestamp;
8. remover duplicatas exatas;
9. validar OHLC;
10. registrar itens rejeitados.

Não assumir a ordem dos campos numéricos sem validar diretamente contra os dois HARs.

---

## 13. Prova semântica do candle

Antes de declarar o formato final, o Forge deverá comparar os arrays de candles dos dois HARs e comprovar:

```text
posição do timestamp
posição do open
posição do high
posição do low
posição do close
posição do volume, se existir
```

Validações mínimas:

```text
high >= open
high >= close
low <= open
low <= close
high >= low
timestamp crescente ou ordenável
preços positivos
```

Se houver mais de uma interpretação possível, não escolher arbitrariamente.

Nesse caso:

```text
classificação = CANDLE_SCHEMA_AMBIGUOUS
```

E documentar quais posições ainda precisam de confirmação.

---

## 14. Parser de updateStream

Mapear o realtime comprovado.

O parser deverá:

1. identificar todos os ativos presentes;
2. identificar preço;
3. identificar timestamp;
4. suportar múltiplos ticks em um frame;
5. gerar um `PocketRealtimeTick` para cada tick;
6. preservar ordem temporal;
7. detectar duplicatas;
8. rejeitar preço inválido;
9. rejeitar timestamp inválido;
10. registrar eventos não interpretados.

Ativos obrigatórios nos testes:

```text
EURUSD_otc
AUDUSD_otc
USDBRL_otc
```

---

## 15. Parser de updateAssets

O parser deverá catalogar os 20 ativos observados por sessão.

Extrair apenas campos comprovados.

Campos possivelmente relacionados a payout, disponibilidade ou períodos devem ser classificados inicialmente como:

```text
candidate_payout
candidate_availability
candidate_periods
unknown_numeric_fields
unknown_boolean_fields
```

Somente promover para:

```text
payout
is_available
supported_periods
```

quando a semântica for comprovada por consistência entre os dois HARs.

Gerar um relatório específico:

```text
.jarvis_cache/diagnostics/pocket_asset_schema_report.json
.jarvis_cache/diagnostics/pocket_asset_schema_report.txt
```

---

## 16. Parser de updateCharts

Auditar o papel de:

```text
updateCharts
saveCharts
```

Responder:

```text
updateCharts contém candles?
updateCharts contém estado visual?
updateCharts contém ativo e período?
updateCharts complementa updateHistoryNewFast?
saveCharts é apenas persistência de layout?
```

Não transformar `updateCharts` em histórico sem evidência.

---

## 17. Candle Normalizer

Criar uma camada única para normalizar candles.

Entrada:

```text
Pocket raw candle
```

Saída:

```text
PocketNormalizedCandle
```

Validações:

```text
timestamp válido
OHLC numérico
high >= low
high >= open
high >= close
low <= open
low <= close
ativo presente
period suportado
sem NaN
sem infinito
```

Rejeições devem possuir códigos:

```text
MISSING_TIMESTAMP
INVALID_TIMESTAMP
MISSING_PRICE
INVALID_PRICE
INVALID_OHLC
UNSUPPORTED_PERIOD
MISSING_ASSET
DUPLICATE_CANDLE
UNKNOWN_CANDLE_SCHEMA
```

---

## 18. Tick Normalizer

Validar:

```text
asset
price
timestamp
```

Códigos de rejeição:

```text
MISSING_ASSET
MISSING_PRICE
INVALID_PRICE
MISSING_TIMESTAMP
INVALID_TIMESTAMP
DUPLICATE_TICK
UNKNOWN_TICK_SCHEMA
```

---

## 19. Offline Store

Criar um store isolado da Friday principal:

```text
PocketOfflineStore
```

Chave recomendada:

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

O store deverá:

```text
adicionar candles
ordenar por timestamp
deduplicar
substituir candle do mesmo timestamp
listar buckets
contar candles
retornar primeiro/último candle
retornar últimos N candles
```

Não reutilizar o CandleStore principal ainda.

---

## 20. Replay Engine

Criar:

```text
PocketOfflineReplayEngine
```

Ele deverá processar os frames na ordem temporal original dos HARs.

Fluxo:

```text
carregar HAR
→ extrair frames
→ ordenar por timestamp
→ interpretar Engine.IO
→ interpretar Socket.IO
→ rotear evento
→ normalizar
→ gravar no Offline Store
→ gerar métricas
```

Suportar os dois HARs em uma única execução.

Não misturar sessões silenciosamente.

Cada evento deve preservar:

```text
source_har
session_index
frame_index
```

---

## 21. Session Isolation

Os dois HARs representam sessões distintas.

O replay deverá:

```text
processar sessão 1 isoladamente
processar sessão 2 isoladamente
comparar resultados
gerar visão combinada apenas no relatório
```

Não juntar candles de sessões diferentes sem marcar a origem.

Detectar:

```text
mesmo ativo/período
candles repetidos entre sessões
diferenças de schema
diferenças de protocolo
diferenças de timestamps
```

---

## 22. Relatórios obrigatórios

Gerar:

```text
.jarvis_cache/diagnostics/pocket_parser_report.json
.jarvis_cache/diagnostics/pocket_parser_report.txt
.jarvis_cache/diagnostics/pocket_candle_schema_report.json
.jarvis_cache/diagnostics/pocket_candle_schema_report.txt
.jarvis_cache/diagnostics/pocket_tick_schema_report.json
.jarvis_cache/diagnostics/pocket_tick_schema_report.txt
.jarvis_cache/diagnostics/pocket_asset_schema_report.json
.jarvis_cache/diagnostics/pocket_asset_schema_report.txt
.jarvis_cache/diagnostics/pocket_offline_store_report.json
.jarvis_cache/diagnostics/pocket_offline_store_report.txt
```

Todos dentro de `.jarvis_cache`.

---

## 23. Conteúdo do relatório principal

O relatório deve apresentar:

```text
HARs processados
sessões processadas
frames totais
frames válidos
frames inválidos
eventos Socket.IO
changeSymbol encontrados
updateHistoryNewFast encontrados
updateStream encontrados
updateAssets encontrados
updateCharts encontrados
candles encontrados
candles aceitos
candles rejeitados
ticks encontrados
ticks aceitos
ticks rejeitados
ativos encontrados
períodos encontrados
buckets criados
duplicatas
primeiro timestamp
último timestamp
schema do candle
schema do tick
schema dos ativos
lacunas
classificação
```

---

## 24. Critério de sucesso do parser

A Sprint será considerada aprovada quando conseguir, offline:

```text
interpretar changeSymbol
interpretar updateHistoryNewFast
interpretar updateStream
interpretar updateAssets
normalizar candles
normalizar ticks
criar buckets separados por ativo/período
processar os dois HARs
gerar resultados determinísticos
não expor credenciais
```

---

## 25. Critério quantitativo

O parser deverá conseguir criar buckets para os pares comprovados:

```text
POCKET:EURUSD_otc:60
POCKET:EURUSD_otc:300
POCKET:AUDUSD_otc:60
POCKET:AUDUSD_otc:900
POCKET:USDBRL_otc:60
POCKET:USDBRL_otc:300
POCKET:USDBRL_otc:900
```

Cada bucket histórico deverá conter os candles válidos encontrados nos HARs.

Não exigir artificialmente mais candles do que o HAR contém.

---

## 26. Comparação entre os HARs

Gerar uma comparação:

```text
schema de changeSymbol
schema de updateHistoryNewFast
schema de updateStream
schema de updateAssets
schema de updateCharts
eventos presentes
eventos ausentes
ativos presentes
períodos presentes
quantidade de candles
quantidade de ticks
frequência do stream
campos divergentes
```

Classificar compatibilidade:

```text
IDENTICAL
COMPATIBLE
PARTIALLY_COMPATIBLE
INCOMPATIBLE
```

---

## 27. Segurança

Nunca incluir nos relatórios:

```text
token
cookie
authorization
bearer
ssid
password
e-mail
user id real
account id real
saldo
dados da conta
payload auth bruto
```

Também não incluir:

```text
query string sensível do WebSocket
headers completos
cookies do HAR
request headers
response headers
```

Adicionar verificação automática nos relatórios.

Se algum termo sensível for encontrado, o teste deverá falhar.

---

## 28. Integração com a Friday

Não integrar ao runtime principal nesta Sprint.

Não modificar:

```text
app/market/runtime.py
app/market/providers/polarium/
app/api/routes/market_chart.py
frontend/
```

A única exceção é ajuste estritamente necessário em `.gitignore`.

Não criar rota HTTP Pocket.

Não criar provider Pocket em `app/market/providers/` ainda.

---

## 29. Testes obrigatórios

Criar testes para:

### Engine.IO

```text
open
ping
pong
connect
disconnect
evento
frame inválido
```

### Socket.IO

```text
evento com dict
evento com list
evento com null
evento sem payload
JSON inválido
frame incompleto
```

### changeSymbol

```text
EURUSD_otc/60
EURUSD_otc/300
AUDUSD_otc/900
USDBRL_otc/300
ativo ausente
period ausente
period inválido
```

### Histórico

```text
parse de lote
20 candles
ordenação
deduplicação
OHLC válido
OHLC inválido
timestamp inválido
schema desconhecido
```

### Stream

```text
um tick
múltiplos ticks
ativos diferentes
duplicatas
preço inválido
timestamp inválido
```

### Ativos

```text
lista de ativos
OTC
campos desconhecidos preservados
payout não inventado
disponibilidade não inventada
```

### Offline Store

```text
bucket por ativo/período
append
replace
deduplicação
ordenação
últimos N candles
isolamento de sessões
```

### Replay

```text
HAR 1
HAR 2
dois HARs
ordem temporal
resultado determinístico
evento desconhecido
frame inválido não fatal
```

### Segurança

```text
token removido
cookie removido
authorization removido
SSID removido
payload auth bruto ausente
relatórios sanitizados
```

---

## 30. Testes com dados reais dos HARs

Além de fixtures sintéticas, criar testes de integração offline utilizando os dois HARs privados.

Esses testes devem:

```text
ser ignorados quando os HARs não existirem
não imprimir payload bruto
não copiar os HARs
não adicionar os HARs ao Git
não salvar credenciais
```

Devem comprovar:

```text
changeSymbol real encontrado
updateHistoryNewFast real encontrado
updateStream real encontrado
updateAssets real encontrado
buckets reais criados
```

---

## 31. Comando de execução

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

.venv/bin/python -m tools.pocket_parser \
  --har ".jarvis_private/pocket_hars/pocketoption.com.har" \
  --har ".jarvis_private/pocket_hars/pocketoption.com(1).har"
```

O CLI deve também aceitar execução padrão:

```bash
.venv/bin/python -m tools.pocket_parser
```

Com os caminhos locais padrão:

```text
.jarvis_private/pocket_hars/pocketoption.com.har
.jarvis_private/pocket_hars/pocketoption.com(1).har
```

---

## 32. Validação automatizada

Executar testes específicos:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

.venv/bin/python -m pytest tests/tools/pocket_parser -v
```

Executar também os testes do laboratório anterior:

```bash
.venv/bin/python -m pytest tests/tools/pocket_discovery -v
```

Executar suíte completa:

```bash
.venv/bin/python -m pytest -v
```

Executar build:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run build
```

---

## 33. Critério para avançar à Pocket V1.2

Só recomendar:

```text
SPRINT POCKET V1.2 — READ-ONLY LIVE FEED ARCHITECTURE
```

se forem comprovados:

```text
candle schema estável
tick schema estável
asset schema suficientemente compreendido
dois HARs compatíveis
parser determinístico
buckets corretos
sem dados sensíveis
```

A V1.2 ainda deverá começar com desenho arquitetural e não conexão imediata.

---

## 34. Fora de escopo

Não implementar:

```text
login Pocket
WebSocket ao vivo
reconexão ao vivo
autenticação automática
envio de auth
envio de changeSymbol
execução de operação
CALL
PUT
saldo
payout operacional
conta real
conta demo automatizada
frontend Pocket
Chart API Pocket
AI Pocket
```

---

## 35. Git

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

Não apagar arquivos da Polarium.

Não adicionar HARs ao Git.

Confirmar:

```text
.jarvis_private/
*.har
.jarvis_cache/
```

ignorados.

---

## 36. Entrega obrigatória

Entregar:

1. objetivo;
2. arquitetura implementada;
3. código reutilizado da V1.0;
4. arquivos criados;
5. arquivos modificados;
6. eventos processados;
7. schema de changeSymbol;
8. schema de histórico;
9. schema do candle;
10. schema do realtime;
11. schema do tick;
12. schema dos ativos;
13. campos comprovados;
14. campos ainda desconhecidos;
15. candles encontrados;
16. candles aceitos;
17. candles rejeitados;
18. ticks encontrados;
19. ticks aceitos;
20. ticks rejeitados;
21. buckets criados;
22. ativos processados;
23. períodos processados;
24. comparação entre os HARs;
25. compatibilidade;
26. relatórios gerados;
27. segurança;
28. testes criados;
29. resultado dos testes específicos;
30. resultado da suíte completa;
31. resultado do build;
32. `git status --short`;
33. `git diff --stat`;
34. riscos;
35. lacunas;
36. decisão sobre Pocket V1.2;
37. próximos passos;
38. sugestão de commit.

---

## 37. Sugestão de commit

```text
feat(pocket): add deterministic offline market protocol parser
```