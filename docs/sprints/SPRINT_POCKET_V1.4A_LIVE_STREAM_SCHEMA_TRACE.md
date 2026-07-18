# FRIDAY AI TRADER

# SPRINT POCKET V1.4A — LIVE STREAM SCHEMA TRACE

## Status

AUDITORIA LIVE SANITIZADA — SOMENTE LEITURA — SEM INTEGRAÇÃO COM A FRIDAY

---

## 1. Objetivo

Descobrir e comprovar o schema real dos eventos live:

```text
updateStream
chafor
```

observados durante a sessão Pocket Demo via CDP passivo.

A validação real da Sprint Pocket V1.4 comprovou:

```text
observation_mode = REAL_PASSIVE_CDP
target_found = true
market_socket_found = true
stream_events = 178
outbound_messages_originated_by_friday = 0
```

Porém:

```text
ticks = 0
history_batches = 0
historical_candles = 0
```

Esta Sprint deverá responder por que os eventos live `updateStream` não foram convertidos em `PocketRealtimeTick`.

Não integrar a Pocket ao frontend, Chart API ou runtime principal nesta Sprint.

---

## 2. Evidência real

Melhor tentativa real da V1.4:

```text
market_socket_found = true
events_found = updateStream, chafor
stream_events = 178
history_batches = 0
historical_candles = 0
ticks = 0
observer_stopped_cleanly = true
outbound_messages_originated_by_friday = 0
```

Conclusão comprovada:

```text
o observer CDP recebe frames live;
o Market WebSocket foi identificado;
o evento updateStream existe;
o parser V1.1 não reconheceu o payload live como tick.
```

A causa exata ainda não foi comprovada.

---

## 3. Hipóteses permitidas

Auditar, sem assumir conclusão:

1. O payload live de `updateStream` possui nesting diferente do HAR.
2. O evento live contém objeto em vez de lista.
3. O payload contém múltiplos ativos ou ticks agrupados.
4. O frame Socket.IO possui namespace, ack ID ou prefixo adicional.
5. O evento está comprimido ou serializado em formato diferente.
6. O timestamp está em posição diferente.
7. O preço está em campo ou índice diferente.
8. O parser removeu dados necessários durante a sanitização.
9. `chafor` altera o contexto ou precede o stream.
10. O socket confirmado não é exatamente o mesmo fluxo usado nos HARs.
11. O payload live contém wrappers adicionais antes de `[asset, timestamp, price]`.
12. O terminal ainda não enviou histórico durante a janela observada.

Não transformar hipótese em causa raiz sem relatório real.

---

## 4. Regra principal

Esta Sprint é exclusivamente de auditoria e parser sanitizado.

É proibido:

```text
enviar mensagens
enviar auth
enviar changeSymbol
usar WebSocket.send
usar socket.emit
usar sio.emit
usar Runtime.evaluate
interceptar requests
modificar frames
automatizar login
automatizar cliques
executar CALL
executar PUT
consultar saldo
ler cookies
ler tokens
ler SSID
ler Authorization
integrar Pocket à Chart API
integrar Pocket ao frontend
alterar Polarium
alterar Strategy Engine
alterar IA
```

---

## 5. Arquivos permitidos

Alterar somente o mínimo necessário em:

```text
app/market/providers/pocket/
tools/pocket_live_observation/
tests/market/providers/pocket/
tests/tools/pocket_parser/
```

É permitido criar:

```text
app/market/providers/pocket/live_schema_trace.py
tests/market/providers/pocket/test_pocket_live_schema_trace.py
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

## 6. Diagnóstico sanitizado

Criar:

```text
PocketLiveSchemaTrace
```

Relatórios:

```text
.jarvis_cache/diagnostics/pocket_live_stream_schema.json
.jarvis_cache/diagnostics/pocket_live_stream_schema.txt
```

Também criar:

```text
.jarvis_cache/diagnostics/pocket_chafor_schema.json
.jarvis_cache/diagnostics/pocket_chafor_schema.txt
```

---

## 7. Dados permitidos no relatório

Para cada evento `updateStream`, registrar somente:

```text
timestamp_observed
event_name
direction
socket_classification
frame_prefix
engineio_type
socketio_type
namespace_present
ack_id_present
payload_root_type
payload_depth
payload_length
top_level_key_names
nested_key_paths
value_types
list_lengths
string_patterns
numeric_ranges
candidate_asset_paths
candidate_timestamp_paths
candidate_price_paths
parser_result
rejection_code
```

Não registrar payload bruto.

---

## 8. Shape sanitizado

Criar representação estrutural semelhante a:

```text
dict
├── data: list[3]
│   ├── [0]: str
│   ├── [1]: int
│   └── [2]: float
└── source: str
```

ou:

```text
list[2]
├── [0]: str
└── [1]: list[3]
    ├── [0]: str
    ├── [1]: int
    └── [2]: float
```

Os valores reais devem ser substituídos por tipos ou amostras não sensíveis.

Ativos públicos de mercado como:

```text
EURUSD_otc
AUDUSD_otc
USDBRL_otc
```

podem ser registrados.

Nunca registrar dados de conta.

---

## 9. Comparação HAR versus live

Comparar obrigatoriamente:

```text
updateStream HAR V1.1
versus
updateStream live V1.4A
```

Para cada versão informar:

```text
frame prefix
event name
payload root type
payload nesting
asset path
timestamp path
price path
multiple ticks
namespace
ack id
array positions
key names
```

Classificar:

```text
IDENTICAL
WRAPPED_COMPATIBLE
SCHEMA_VARIANT
INCOMPATIBLE
INSUFFICIENT_EVIDENCE
```

---

## 10. Captura de amostras estruturais

Capturar no máximo:

```text
20 shapes únicos de updateStream
20 shapes únicos de chafor
```

Deduplicar por assinatura estrutural.

Assinatura sugerida:

```text
event_name
payload_root_type
key_paths
list_lengths
value_types
```

Não armazenar centenas de eventos repetidos.

---

## 11. Auditoria da sanitização

Comprovar se a sanitização atual:

```text
preserva asset
preserva timestamp
preserva price
remove somente campos sensíveis
não altera nesting necessário
não converte lista em string
não descarta números de mercado
```

Se a sanitização estiver destruindo o schema, corrigir somente o sanitizador Pocket.

Não reduzir a proteção de credenciais.

---

## 12. Auditoria do parser Socket.IO

Verificar suporte a frames como:

```text
42["updateStream", ...]
42/namespace,["updateStream", ...]
42<number>["updateStream", ...]
42/namespace,<ack_id>["updateStream", ...]
```

Cobrir:

```text
namespace
ack ID
evento com lista
evento com dict
evento com múltiplos argumentos
evento nested
payload vazio
frame incompleto
```

Não alterar parsing de eventos já estáveis sem testes de regressão.

---

## 13. Parser live de updateStream

Somente depois de comprovar o schema, criar suporte mínimo para a variante live.

O parser deverá aceitar:

```text
schema HAR comprovado
schema live comprovado
```

Ambos devem produzir:

```text
PocketRealtimeTick
```

Campos:

```text
asset
timestamp
price
source_event
sequence
schema_variant
```

Não criar fallback amplo que aceite qualquer array numérico.

---

## 14. Validação do tick

Regras:

```text
asset não vazio
asset compatível com símbolo de mercado
timestamp numérico e plausível
price numérico positivo
sem NaN
sem infinito
```

Códigos de rejeição:

```text
LIVE_STREAM_SCHEMA_UNKNOWN
LIVE_STREAM_ASSET_MISSING
LIVE_STREAM_TIMESTAMP_MISSING
LIVE_STREAM_TIMESTAMP_INVALID
LIVE_STREAM_PRICE_MISSING
LIVE_STREAM_PRICE_INVALID
LIVE_STREAM_NESTING_UNSUPPORTED
LIVE_STREAM_SANITIZATION_DROPPED_FIELD
```

---

## 15. Evento chafor

Auditar `chafor` separadamente.

Responder:

```text
é evento de mercado?
é catálogo?
é confirmação de assinatura?
é controle de gráfico?
contém ativo?
contém timeframe?
contém histórico?
precede updateStream?
```

Não enviar `chafor`.

Não usar `chafor` como fonte de contexto sem evidência.

Classificar:

```text
MARKET_CONTROL
MARKET_DATA
SUBSCRIPTION_CONTROL
CHART_CONTROL
UNKNOWN
```

---

## 16. Histórico ausente

A Sprint também deverá registrar por que nenhum `updateHistoryNewFast` foi observado.

Auditar passivamente:

```text
evento de histórico com outro nome
histórico enviado antes do attach CDP
histórico enviado em outro socket
histórico enviado por HTTP
histórico não solicitado durante a sessão
histórico em updateCharts
histórico comprimido
```

Não reproduzir request de histórico.

Criar categoria:

```text
HISTORY_EVENT_NOT_OBSERVED
HISTORY_EVENT_MISSED_BEFORE_ATTACH
HISTORY_EVENT_OTHER_SOCKET
HISTORY_EVENT_DIFFERENT_NAME
HISTORY_EVENT_HTTP_ONLY
HISTORY_EVENT_UNKNOWN
```

---

## 17. Attach precoce

Auditar se o observer anexa antes ou depois do carregamento do terminal.

Registrar:

```text
observer_started_at
target_attached_at
market_socket_confirmed_at
first_stream_event_at
first_history_event_at
page_load_state
```

Se o histórico tiver ocorrido antes do attach:

```text
HISTORY_EVENT_MISSED_BEFORE_ATTACH
```

Não criar correção funcional nesta Sprint além de instrumentação de timing.

---

## 18. Socket ownership

Confirmar para cada `updateStream`:

```text
target_id correto
request_id do Market WebSocket
host sanitizado
path sanitizado
classificação MARKET_SOCKET
```

Comparar com sockets auxiliares.

Não aceitar `updateStream` de socket não confirmado.

---

## 19. Resultado esperado

Ao final, o relatório deverá responder objetivamente:

```text
Qual é o shape live real de updateStream?
Por que o parser V1.1 rejeitou os eventos?
Qual caminho contém asset?
Qual caminho contém timestamp?
Qual caminho contém price?
O schema live é compatível com o HAR?
A sanitização preservou os campos?
O evento chafor tem função de mercado?
Por que histórico não foi observado?
```

---

## 20. Correção permitida

Somente se o schema live estiver comprovado, aplicar correção mínima em:

```text
stream_parser
socketio_parser
sanitizer
event router
```

Não alterar:

```text
runtime
CandleStore
readiness
Chart API
frontend
```

---

## 21. Testes obrigatórios

### Schema trace

```text
shape de dict
shape de list
shape nested
deduplicação de assinatura
limite de amostras
ausência de payload bruto
```

### Socket.IO

```text
frame simples
frame com namespace
frame com ack ID
frame com namespace e ack ID
payload list
payload dict
múltiplos argumentos
```

### Stream parser

```text
schema HAR
schema live comprovado
múltiplos ticks
asset ausente
timestamp ausente
price ausente
nesting desconhecido
```

### Sanitização

```text
asset preservado
timestamp preservado
price preservado
token removido
cookie removido
Authorization removido
dados de conta removidos
```

### chafor

```text
shape catalogado
payload sanitizado
não roteado como tick sem evidência
```

### Histórico

```text
histórico não observado
histórico anterior ao attach
histórico em socket diferente
categoria correta
```

### Regressão

```text
19 testes do parser V1.1 continuam passando
35 testes Pocket atuais continuam passando
replay V1.2 continua com 419 ticks
```

---

## 22. Teste real assistido

Depois dos testes automatizados, executar novamente:

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

No Chrome dedicado:

```text
1. Login manual na conta DEMO.
2. Aguardar terminal carregar.
3. Selecionar EURUSD OTC M1.
4. Aguardar 20 segundos.
5. Trocar para EURUSD OTC M5.
6. Aguardar 20 segundos.
7. Trocar para AUDUSD OTC M15.
8. Aguardar 20 segundos.
9. Trocar para USDBRL OTC M5.
10. Aguardar 20 segundos.
11. Encerrar com Control + C.
```

Não realizar operações.

---

## 23. Critério de sucesso

A Sprint será aprovada quando:

```text
observation_mode = REAL_PASSIVE_CDP
market_socket_found = true
updateStream events > 0
live stream schema classified
candidate asset path comprovado
candidate timestamp path comprovado
candidate price path comprovado
ticks > 0
outbound_messages_originated_by_friday = 0
observer_stopped_cleanly = true
```

Histórico poderá continuar pendente, desde que sua ausência seja classificada com evidência.

---

## 24. Relatórios obrigatórios

Gerar:

```text
.jarvis_cache/diagnostics/pocket_live_stream_schema.json
.jarvis_cache/diagnostics/pocket_live_stream_schema.txt
.jarvis_cache/diagnostics/pocket_chafor_schema.json
.jarvis_cache/diagnostics/pocket_chafor_schema.txt
.jarvis_cache/diagnostics/pocket_live_history_absence.json
.jarvis_cache/diagnostics/pocket_live_history_absence.txt
```

Atualizar também:

```text
pocket_real_validation.json
pocket_real_validation.txt
```

---

## 25. Segurança

Nunca persistir:

```text
token
cookie
authorization
bearer
SSID
password
e-mail
user id
account id
saldo
payload auth
headers completos
query string completa
```

O teste deve falhar se algum segredo aparecer.

---

## 26. Validação automatizada

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

## 27. Fora de escopo

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
payout operacional
CALL
PUT
AutoTrade
IA
Strategy Engine
```

---

## 28. Git

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

Não remover código Polarium.

Não adicionar relatórios ou perfil Chrome ao Git.

---

## 29. Entrega obrigatória

Entregar:

1. objetivo;
2. evidência inicial;
3. arquitetura auditada;
4. shape HAR;
5. shape live;
6. classificação de compatibilidade;
7. causa dos ticks zerados;
8. caminhos de asset/timestamp/price;
9. auditoria da sanitização;
10. auditoria Socket.IO;
11. análise de chafor;
12. causa/categoria do histórico ausente;
13. timing do attach;
14. socket ownership;
15. patch mínimo;
16. arquivos criados;
17. arquivos modificados;
18. relatórios;
19. testes de schema;
20. testes Socket.IO;
21. testes stream;
22. testes de sanitização;
23. testes chafor;
24. testes histórico;
25. regressões;
26. resultado dos testes Pocket;
27. resultado do parser;
28. resultado do discovery;
29. suíte completa;
30. build;
31. validação real;
32. ticks reais processados;
33. histórico real observado ou categoria;
34. zero outbound;
35. cleanup;
36. git status;
37. git diff;
38. riscos;
39. lacunas;
40. decisão sobre V1.4B ou V1.5;
41. próximos passos;
42. sugestão de commit.

---

## 30. Sugestão de commit

```text
fix(pocket): support observed live stream schema variants
```