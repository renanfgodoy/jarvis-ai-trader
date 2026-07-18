# FRIDAY AI TRADER

# SPRINT V5.9G — LIVE BOOTSTRAP REQUEST OWNERSHIP FIX

## Status

EMERGÊNCIA — REGRESSÃO REAL NÃO RESOLVIDA

---

## 1. Objetivo

Descobrir e corrigir por que o ativo visível na Polarium atualiza o Session Context, mas não gera um bootstrap histórico efetivo no Market WebSocket real.

A Sprint V5.9F passou nos testes automatizados, porém falhou na validação real.

---

## 2. Evidência real

A Polarium e a Friday identificaram:

```text
symbol=USDBRL-OTC
active_id=2298
raw_size=300
timeframe=M5
Entretanto, a Chart API retornou:

{
  "provider": "POLARIUM",
  "active_id": 2298,
  "raw_size": 300,
  "count": 0,
  "candles": []
}

A listagem de séries continuou contendo somente:

POLARIUM:76:60  count=206
POLARIUM:76:300 count=1

Não foi criado:

POLARIUM:2298:300

Portanto, a V5.9F não restaurou o pipeline real.

3. Regra principal

Não alterar o frontend.

Não alterar Chart API.

Não avançar seleção programática.

Manter:

POLARIUM_PROGRAMMATIC_SELECTION_ENABLED=false

O foco exclusivo é o bootstrap manual do ativo visível na sessão real.

4. Pipeline obrigatório

Auditar com evidência:

PAGE_NATIVE visible context 2298/300
→ decisão de ownership
→ BootstrapRequestFactory
→ pending request
→ WebSocket.send
→ Market WebSocket requestId
→ first-candles/candles inbound
→ correlação
→ parser
→ Market Router
→ CandleStore POLARIUM:2298:300

Para cada etapa, registrar sucesso ou falha.

5. Perguntas obrigatórias

Responder antes de aplicar o patch:

O runtime realmente cria um request para (2298, 300)?
Qual é o request_id criado?
O request entra em pending requests?
O WebSocket.send é executado?
Em qual requestId CDP o frame é enviado?
Esse requestId corresponde ao Market WebSocket atual?
A Polarium responde first-candles ou candles?
A resposta contém o mesmo request_id?
A resposta é rejeitada por ownership ou correlação?
Algum owner PAGE_NATIVE residual bloqueia o request da Friday?
Algum lock anterior permanece depois de stop/start?
O runtime está anexado ao target e socket corretos após reinicialização?
6. Instrumentação mínima obrigatória

Adicionar relatório sanitizado:

.jarvis_cache/diagnostics/live_bootstrap_request_report.json
.jarvis_cache/diagnostics/live_bootstrap_request_report.txt

Registrar por (active_id, raw_size):

visible_context_observed
owner_selected
owner_reason
auto_bootstrap_decision
request_created
request_id
pending_registered
socket_request_id
market_socket_match
send_attempted
send_succeeded
response_received
response_type
response_request_id
correlation_result
parser_count
store_key
store_written
history_count
readiness
failure_stage
failure_reason

Não registrar tokens, cookies, SSID, headers, Authorization ou payload bruto.

7. Estados de falha

Classificar obrigatoriamente:

VISIBLE_CONTEXT_NOT_OBSERVED
OWNER_BLOCKED
OWNER_STALE
REQUEST_NOT_CREATED
PENDING_NOT_REGISTERED
MARKET_SOCKET_NOT_RESOLVED
WRONG_CDP_SOCKET
SEND_NOT_ATTEMPTED
SEND_FAILED
NO_RESPONSE
RESPONSE_NOT_CORRELATED
RESPONSE_REJECTED
PARSER_EMPTY
STORE_NOT_WRITTEN
READINESS_NOT_UPDATED
SUCCESS
UNKNOWN
8. Isolamento programático

Com:

POLARIUM_PROGRAMMATIC_SELECTION_ENABLED=false

comprovar:

NativeHistoricalBootstrapOrchestrator não executa;
nenhum owner programático é criado;
nenhum lock programático existe;
nenhuma assinatura programática é registrada;
somente o bootstrap manual/automático oficial atua.

Se qualquer estado experimental existir, corrigir o cleanup.

9. Correção permitida

Somente após a instrumentação apontar a etapa real da falha, aplicar o menor patch em:

PolariumCDPLiveSource;
HistoricalBootstrapManager;
registro de pending requests;
resolução do Market WebSocket;
correlação de resposta;
ownership do bootstrap;
cleanup de locks e signatures.

Não alterar Parser, CandleStore ou Readiness sem evidência direta.

10. Teste real obrigatório no desenvolvimento

O Forge deverá, quando possível, usar a sessão CDP local existente para inspecionar:

http://127.0.0.1:9227/json

e confirmar:

target /traderoom;
Market WebSocket atual;
requestId do socket;
frames enviados para 2298/300.

Não usar DOM, clique, Selenium ou Playwright.

11. Testes automatizados

Adicionar testes para:

2298/300 observado;
owner correto selecionado;
request criado;
pending registrado;
socket correto selecionado;
send executado;
resposta correlacionada;
bucket POLARIUM:2298:300 criado;
stop/start limpa owner e socket antigo;
socket não-market não bloqueia bootstrap;
seleção programática desligada não interfere;
M1, M5 e M15 preservados.

Executar:

cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

python -m pytest tests/market/providers -v
python -m pytest tests/market/chart -v
python -m pytest tests/frontend -v
python -m pytest -v

Build:

cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run build
12. Validação real

Backend:

POLARIUM_CDP_LIVE_ENABLED=true \
POLARIUM_PROGRAMMATIC_SELECTION_ENABLED=false \
.venv/bin/uvicorn app.main:app \
--host 127.0.0.1 \
--port 8000

Na Polarium, selecionar manualmente:

USDBRL-OTC M5

Esperado:

request de 2298/300 criado
request enviado no Market WebSocket
resposta histórica recebida
bucket POLARIUM:2298:300 criado
count >= 50
readiness READY
Friday desenha o gráfico

Validar:

curl -sS http://127.0.0.1:8000/api/v1/market/chart/series | python -m json.tool

e:

curl -sS \
"http://127.0.0.1:8000/api/v1/market/chart?active_id=2298&raw_size=300&limit=1000" \
| python -m json.tool
13. Critério de aceitação

Não declarar sucesso apenas com testes.

A Sprint somente termina quando a sessão real apresentar:

POLARIUM:2298:300
count >= 50
history READY
14. Git

Não executar:

git add
git commit
git push
git reset
git checkout
git restore
git clean
15. Entrega obrigatória

Entregar:

causa raiz real;
etapa exata da falha;
request_id criado;
socket/requestId CDP usado;
owner selecionado;
arquivos modificados;
patch mínimo;
testes;
resultados;
build;
relatório real;
validação real;
git status;
git diff;
riscos;
sugestão de commit.
16. Sugestão de commit
fix(polarium): restore live visible bootstrap request ownership