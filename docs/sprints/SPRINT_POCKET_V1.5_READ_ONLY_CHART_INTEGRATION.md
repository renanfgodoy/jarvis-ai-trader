# FRIDAY AI TRADER

# SPRINT POCKET V1.5 — READ-ONLY CHART INTEGRATION

## Status

INTEGRAÇÃO FUNCIONAL CONTROLADA — POCKET READ-ONLY → CHART API → GRÁFICO FRIDAY

---

## 1. Objetivo

Fazer a Friday exibir, pela primeira vez, candles reais da Pocket no gráfico principal.

Fluxo obrigatório:

```text
Pocket DEMO aberta manualmente
→ CDP passivo
→ PocketCDPObservationTransport
→ PocketMarketRuntime
→ PocketProviderAdapter
→ ProviderManager
→ Chart Read Model
→ Chart API
→ useRealCandles
→ RealCandleChart
→ gráfico visível na Friday
```

A integração deverá permanecer exclusivamente read-only.

A Friday não poderá enviar nenhuma mensagem à Pocket.

---

## 2. Marco obrigatório

Esta Sprint somente poderá ser considerada concluída quando for visualmente comprovado:

```text
Pocket real
→ histórico real
→ ticks reais
→ gráfico da Friday
```

Não basta:

```text
testes automatizados;
fixtures;
replay;
FakePocketTransport;
relatórios;
bucket isolado;
Chart API simulada.
```

É necessária validação visual real ao final da implementação.

---

## 3. Evidências já comprovadas

As Sprints anteriores comprovaram:

```text
Pocket Socket.IO / Engine.IO
changeSymbol
updateHistoryNewFast
updateStream
updateAssets
```

Schema histórico comprovado:

```text
[timestamp, open, close, high, low, volume]
```

Schema realtime comprovado:

```text
[[asset, timestamp, price]]
```

Validação real já obtida:

```text
observation_mode = REAL_PASSIVE_CDP
target_found = true
market_socket_found = true
historical_candles = 99
ticks > 0
bucket real READY
outbound_messages_originated_by_friday = 0
observer_stopped_cleanly = true
```

Arquitetura Provider V2 existente:

```text
MarketProvider
ProviderFactory
ProviderRegistry
PocketProviderAdapter
FakePocketProviderAdapter
```

---

## 4. Regra principal

A Pocket deve alimentar o gráfico da Friday sem alterar ou apagar a integração Polarium.

É proibido:

```text
enviar auth;
enviar changeSymbol;
enviar chafor;
enviar Socket.IO;
usar WebSocket.send;
usar socket.emit;
usar sio.emit;
usar Runtime.evaluate para envio;
automatizar login;
ler senha;
ler cookies;
ler token;
ler SSID;
ler Authorization;
executar CALL;
executar PUT;
executar ordens;
consultar saldo;
implementar AutoTrade.
```

---

## 5. Preservação obrigatória

Não apagar nem quebrar:

```text
provider Polarium;
código de replay;
parser Pocket;
Pocket Discovery;
Provider V2;
Market Analysis Engine;
Chart API atual;
frontend atual.
```

A Pocket deverá entrar por configuração controlada e reversível.

---

## 6. Arquitetura alvo

Criar um fluxo de aplicação controlado:

```text
ProviderFactory
→ ProviderRegistry
→ ProviderManager
→ provider atual
→ ChartProviderService
→ Chart API
```

O frontend não deverá conhecer:

```text
PocketMarketRuntime;
PocketCDPObservationTransport;
Socket.IO;
CDP;
PolariumCDPLiveSource.
```

O frontend deverá consumir apenas a Chart API neutra.

---

## 7. Provider Manager

Criar:

```text
app/market/providers/manager.py
```

Responsabilidades:

```text
construir providers via ProviderFactory;
registrar providers;
definir provider atual;
iniciar provider explicitamente;
parar provider explicitamente;
consultar provider atual;
expor status sanitizado;
não iniciar provider automaticamente sem configuração.
```

Métodos sugeridos:

```text
initialize()
start_current()
stop_current()
get_current()
set_current()
status()
shutdown()
```

Não usar singleton oculto.

A instância deverá ser criada e injetada de forma explícita.

---

## 8. Configuração

Criar configurações:

```text
market_provider_v2_enabled = false
market_provider_current = POLARIUM
pocket_chart_integration_enabled = false
pocket_cdp_enabled = false
pocket_real_observation_authorized = false
pocket_read_only = true
pocket_live_connection_enabled = false
```

Defaults obrigatórios:

```text
market_provider_v2_enabled = false
market_provider_current = POLARIUM
pocket_chart_integration_enabled = false
pocket_cdp_enabled = false
pocket_real_observation_authorized = false
pocket_read_only = true
pocket_live_connection_enabled = false
```

A Pocket somente poderá assumir o gráfico quando explicitamente configurada.

---

## 9. Seleção de provider

Valores inicialmente permitidos:

```text
POLARIUM
POCKET
FAKE
```

Se `POCKET` for selecionado, exigir:

```text
market_provider_v2_enabled = true
pocket_chart_integration_enabled = true
pocket_cdp_enabled = true
pocket_real_observation_authorized = true
pocket_read_only = true
pocket_live_connection_enabled = false
```

Combinação insegura deve bloquear o startup Pocket com:

```text
POCKET_CHART_UNSAFE_CONFIGURATION
```

---

## 10. Chart Provider Service

Criar:

```text
app/market/chart/provider_service.py
```

Responsabilidades:

```text
obter provider atual;
ler ProviderContext;
ler ProviderHistory;
ler ProviderReadiness;
converter ProviderCandle para resposta Chart API;
listar séries do provider atual;
não conhecer Pocket ou Polarium diretamente.
```

Não duplicar o CandleStore.

Não introduzir cache cruzado entre providers.

---

## 11. Chave neutra de série

Criar modelo de chave neutro:

```text
provider
symbol
period
```

Exemplo Pocket:

```text
POCKET:EURUSD_otc:60
```

Exemplo Polarium:

```text
POLARIUM:76:60
```

A Chart API deverá preservar identidade do provider.

Nunca misturar:

```text
POCKET
POLARIUM
```

na mesma resposta de série.

---

## 12. Compatibilidade da Chart API

Preservar os endpoints existentes:

```text
GET /api/v1/market/chart
GET /api/v1/market/chart/series
```

Adicionar suporte neutro, sem quebrar chamadas antigas.

A rota deverá aceitar, quando Provider V2 estiver habilitado:

```text
provider
symbol
period
limit
```

Compatibilidade temporária com Polarium:

```text
active_id
raw_size
limit
```

Não remover parâmetros antigos nesta Sprint.

---

## 13. Resposta da Chart API

Resposta neutra sugerida:

```json
{
  "provider": "POCKET",
  "symbol": "EURUSD_otc",
  "period": 60,
  "timeframe": "M1",
  "count": 100,
  "readiness": "READY",
  "candles": []
}
```

Cada candle:

```json
{
  "timestamp": 0,
  "open": 0,
  "high": 0,
  "low": 0,
  "close": 0,
  "volume": 0,
  "is_closed": true
}
```

Manter aliases antigos somente quando necessários para compatibilidade.

---

## 14. Endpoint de status do provider

Criar:

```text
GET /api/v1/market/provider-v2/status
```

Resposta sanitizada:

```text
enabled
current_provider
running
connection_state
symbol
period
timeframe
history_count
readiness
last_price
last_update
read_only
outbound_messages_originated_by_friday
last_error
```

Não expor credenciais.

---

## 15. Endpoint de séries

`GET /api/v1/market/chart/series` deverá listar somente séries pertencentes ao provider atual quando Provider V2 estiver ativo.

Exemplo Pocket:

```json
{
  "series": [
    {
      "provider": "POCKET",
      "symbol": "EURUSD_otc",
      "period": 60,
      "timeframe": "M1",
      "count": 100,
      "readiness": "READY"
    }
  ]
}
```

---

## 16. Histórico Pocket

O `PocketProviderAdapter.get_history()` deverá fornecer candles reais do bucket atual.

Não usar:

```text
dados fake;
Polarium fallback;
IQ Option fallback;
candles antigos de outro provider.
```

Se não houver histórico:

```text
count = 0
readiness = EMPTY ou LIMITED
```

Não reutilizar série anterior para esconder ausência de dados.

---

## 17. Realtime Pocket

Ticks reais deverão atualizar o candle aberto do bucket atual.

A Chart API deverá refletir:

```text
close atualizado;
high atualizado;
low atualizado;
volume/tick_count atualizado;
timestamp correto.
```

O frontend deverá atualizar o gráfico sem recarregar a página.

---

## 18. Contexto Pocket

O contexto deverá vir do provider atual:

```text
provider = POCKET
symbol
asset
period
timeframe
last_price
history_count
readiness
```

Não usar:

```text
active_id=76;
EURUSD Polarium padrão;
raw_size Polarium padrão;
contexto restaurado da Polarium.
```

---

## 19. Frontend

Alterar somente o necessário em:

```text
MarketChart
useRealCandles
tipos da Chart API
status visual do provider
```

O frontend deve:

```text
consultar status Provider V2;
detectar provider atual;
usar symbol/period para Pocket;
manter active_id/raw_size para compatibilidade Polarium;
consultar Chart API neutra;
renderizar ProviderCandle;
não chamar IQ Option quando Pocket estiver ativa.
```

---

## 20. Identificação visual

Adicionar no gráfico um indicador discreto:

```text
Provider: Pocket — Read Only
```

Também exibir:

```text
ativo;
timeframe;
readiness.
```

Exemplo:

```text
POCKET • EURUSD OTC • M1 • READY • READ ONLY
```

Não redesenhar a interface inteira.

---

## 21. Estado de carregamento

Quando Pocket estiver conectando:

```text
Conectando à sessão Pocket Demo...
```

Quando aguardando histórico:

```text
Aguardando histórico real da Pocket...
```

Quando limitada:

```text
Histórico Pocket insuficiente para análise.
```

Quando pronta:

```text
Gráfico Pocket em tempo real.
```

Nunca mostrar mensagem IQ ou Polarium quando Pocket estiver selecionada.

---

## 22. Polling e atualização

Evitar polling excessivo.

Configuração recomendada:

```text
status: 1 a 2 segundos;
chart: 1 segundo ou mecanismo atual já existente;
series: somente quando necessário.
```

Não realizar três chamadas repetidas e independentes a cada render.

Cancelar requests obsoletos.

Ignorar resposta stale após troca de ativo/timeframe/provider.

---

## 23. Race condition

Proteger contra:

```text
resposta Pocket antiga aplicada após mudança de contexto;
resposta Polarium aplicada enquanto Pocket está ativa;
resposta de timeframe anterior;
candles vazios apagando uma série READY durante transição curta.
```

Criar chave ativa:

```text
provider:symbol:period
```

Somente aplicar resposta correspondente à chave atual.

---

## 24. Ausência de fallback cruzado

Quando `current_provider=POCKET`, é proibido buscar:

```text
IQ Option;
Polarium;
simulador;
fixture;
replay,
```

como fallback silencioso.

Erro Pocket deve permanecer erro Pocket.

Isso é essencial para a validação real.

---

## 25. Startup controlado

A Pocket poderá ser iniciada com comando dedicado ou configuração explícita.

Não exigir que o backend comum sempre abra Chrome.

Criar modo controlado, por exemplo:

```text
POCKET_CHART_MODE=true
```

O fluxo deverá:

```text
iniciar backend;
iniciar ProviderManager;
iniciar observer Pocket;
aguardar login manual Demo;
alimentar runtime;
expor Chart API;
servir frontend.
```

---

## 26. Chrome dedicado

Usar:

```text
porta CDP 9230;
profile .jarvis_private/chrome-pocket-profile;
login manual;
conta DEMO;
observação passiva.
```

Não abrir ou controlar operações.

---

## 27. Segurança

Manter:

```text
outbound_messages_originated_by_friday = 0
```

O gráfico poderá ler apenas:

```text
contexto de mercado;
candles;
ticks;
assets não sensíveis;
readiness.
```

Nunca expor:

```text
senha;
token;
cookie;
Authorization;
SSID;
account ID;
user ID;
saldo;
operações.
```

---

## 28. Diagnóstico de integração

Criar:

```text
.jarvis_cache/diagnostics/pocket_chart_integration_report.json
.jarvis_cache/diagnostics/pocket_chart_integration_report.txt
```

Registrar:

```text
provider_manager_enabled
current_provider
provider_running
pocket_target_found
market_socket_found
context
history_count
ticks
chart_requests
chart_responses
chart_response_count
frontend_active_key
frontend_received_count
frontend_rendered_count
stale_responses_ignored
cross_provider_fallbacks
outbound_messages_originated_by_friday
errors
```

---

## 29. Testes automatizados

Criar testes para:

### Provider Manager

```text
inicialização;
provider atual;
start explícito;
stop explícito;
shutdown;
configuração insegura bloqueada;
Pocket não inicia por padrão.
```

### Chart Provider Service

```text
Pocket history;
Pocket contexto;
Pocket readiness;
lista de séries;
provider inexistente;
provider parado;
resultado vazio;
limite de candles.
```

### Chart API

```text
Pocket por symbol/period;
Polarium legado por active_id/raw_size;
provider explícito;
provider atual;
resposta neutra;
erro controlado;
zero fallback cruzado.
```

### Frontend

```text
status Pocket;
query symbol/period;
active key provider:symbol:period;
não chamar IQ;
não chamar Polarium;
render Pocket;
loading Pocket;
empty Pocket;
stale response ignorada.
```

### Segurança

```text
zero outbound;
sem credenciais;
sem saldo;
sem operações;
read-only visível.
```

---

## 30. Testes com fake/replay

Antes da validação real, comprovar visualmente ou por integração automatizada:

```text
FakePocketProviderAdapter
→ Chart API
→ frontend
→ gráfico renderizado.
```

Também comprovar:

```text
PocketReplayTransport
→ Provider Adapter
→ Chart API
→ gráfico.
```

Esses testes não substituem a validação real.

---

## 31. Testes de regressão

Executar:

```text
Provider V2;
Pocket Adapter;
Pocket runtime;
Pocket parser;
Pocket discovery;
Market Analysis;
Chart API;
frontend;
suíte completa.
```

Polarium deverá continuar compilando e com testes existentes verdes.

---

## 32. Build

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run build
```

---

## 33. Critério automatizado

A implementação automatizada será aprovada quando:

```text
ProviderManager funcionar;
Pocket Adapter alimentar Chart Provider Service;
Chart API devolver candles Pocket;
frontend consumir resposta Pocket;
Fake/Replay desenhar gráfico;
zero fallback cruzado;
testes passarem;
build passar.
```

---

## 34. Validação real obrigatória

Após o Forge concluir a implementação:

# 🔴 VALIDAÇÃO REAL NECESSÁRIA

Renan deverá executar a Pocket Demo e a Friday juntas.

Tempo estimado:

```text
10 a 15 minutos
```

A Sprint não poderá ser declarada concluída antes desse teste.

---

## 35. Sequência da validação real

Executar inicialmente um único contexto estável:

```text
1. Iniciar frontend.
2. Iniciar backend em POCKET_CHART_MODE.
3. Chrome dedicado abre.
4. Fazer login manual na Pocket DEMO.
5. Selecionar um ativo OTC disponível.
6. Selecionar M1.
7. Aguardar histórico ficar READY.
8. Abrir a Friday.
9. Confirmar gráfico visível.
10. Aguardar de 2 a 3 minutos.
```

Somente depois validar troca:

```text
M1 → M5
ativo atual → outro ativo OTC
```

Não usar uma lista rígida de ativos caso estejam indisponíveis.

---

## 36. Critérios visuais

A Friday deverá mostrar:

```text
Provider: Pocket;
ativo correto;
timeframe correto;
candles históricos;
vela atual em movimento;
preço atual;
readiness READY;
READ ONLY.
```

---

## 37. Critérios técnicos reais

Confirmar:

```text
current_provider = POCKET
history_count >= 50
readiness = READY
chart response count >= 50
frontend rendered count >= 50
ticks aumentando
candle atual atualizando
outbound_messages_originated_by_friday = 0
cross_provider_fallbacks = 0
```

---

## 38. Critérios de troca

Ao trocar timeframe:

```text
a active key muda;
o gráfico muda para o novo period;
candles antigos não permanecem incorretamente;
não mistura M1 com M5.
```

Ao trocar ativo:

```text
symbol muda;
bucket muda;
gráfico muda;
candles do ativo anterior não são usados.
```

---

## 39. Critério de conclusão

A Sprint somente será concluída quando:

```text
gráfico Pocket real aparecer na Friday;
histórico real estiver visível;
vela realtime atualizar;
ativo/timeframe corretos;
zero dados Polarium/IQ;
zero outbound;
sem erro crítico;
cleanup limpo.
```

---

## 40. Fora de escopo

Não implementar:

```text
IA;
indicadores novos;
sinais;
probabilidade;
Decision Engine;
CALL;
PUT;
AutoTrade;
saldo;
payout operacional;
seleção de ativo enviada pela Friday.
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

Não apagar Polarium.

Não versionar:

```text
perfil Chrome;
HAR;
relatórios;
credenciais.
```

---

## 42. Entrega obrigatória

Entregar:

1. objetivo;
2. arquitetura final;
3. ProviderManager;
4. ChartProviderService;
5. configuração;
6. startup controlado;
7. Chart API Pocket;
8. compatibilidade Polarium;
9. frontend Pocket;
10. active key;
11. proteção stale;
12. ausência de fallback;
13. status visual;
14. estados de loading;
15. diagnóstico;
16. arquivos criados;
17. arquivos modificados;
18. testes ProviderManager;
19. testes Chart Service;
20. testes Chart API;
21. testes frontend;
22. testes segurança;
23. fake integration;
24. replay integration;
25. regressões;
26. testes Pocket;
27. testes Provider V2;
28. testes Market Analysis;
29. testes Chart;
30. testes frontend completos;
31. suíte completa;
32. build;
33. git status;
34. git diff;
35. riscos;
36. lacunas;
37. procedimento de validação real;
38. validação real pendente ou concluída;
39. decisão técnica;
40. próximos passos;
41. sugestão de commit.

---

## 43. Sugestão de commit

```text
feat(pocket): integrate read-only Pocket provider with Friday chart
```