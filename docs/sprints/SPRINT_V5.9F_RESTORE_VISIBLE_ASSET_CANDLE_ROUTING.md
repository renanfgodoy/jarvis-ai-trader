# FRIDAY AI TRADER

# SPRINT V5.9F — RESTORE VISIBLE ASSET CANDLE ROUTING

## Status

EMERGÊNCIA — CORREÇÃO DE REGRESSÃO

---

## 1. Objetivo

Restaurar o roteamento de candles reais do ativo atualmente visível na Polarium até o CandleStore e a Chart API.

Não alterar o frontend.

Não alterar layout.

Não avançar seleção programática.

---

## 2. Evidência real

A Friday identificou corretamente:

```text
symbol=USDBRL-OTC
raw_size=300
timeframe=M5
Porém exibiu:

history_count=0
candles=0

A Chart API informou somente:

POLARIUM:76:60  count=206
POLARIUM:76:300 count=1

Não existe série correspondente ao ativo visível USDBRL-OTC, cujo active_id observado anteriormente é 2298.

Isso comprova uma divergência:

Session Context visível = USDBRL-OTC
CandleStore disponível = EURUSD-OTC
3. Regra principal

O gráfico principal já foi restaurado para consumir:

/api/v1/market/chart
/api/v1/market/chart/series

Não voltar ao IQ Option.

A correção desta Sprint deve ocorrer somente no backend Polarium.

4. Pipeline a auditar

Auditar de ponta a ponta:

PAGE_NATIVE
→ active_id/raw_size visíveis
→ HistoricalBootstrapManager
→ pending request
→ first-candles/candles
→ Parser
→ Market Router
→ PolariumCandleStoreAdapter
→ CandleStore
→ Chart API

Comparar especificamente:

active_id visível
active_id do request
active_id da resposta
active_id usado no Store
active_id consultado pela Chart API
5. Hipóteses prioritárias

Investigar:

bootstrap manual deixou de iniciar para o ativo visível;
ownership programático ainda bloqueia o bootstrap manual;
lock residual bloqueia active_id=2298/raw_size=300;
resposta chega, mas é correlacionada ao active_id anterior;
Market Router continua usando active_id=76;
CandleStore recebe chave antiga;
target/runtime está observando eventos antigos;
o contexto muda, mas a subscription do ativo novo não é registrada.

Não assumir a causa sem auditar o código e os testes.

6. Isolamento experimental

Manter:

POLARIUM_PROGRAMMATIC_SELECTION_ENABLED=false

Com a flag desligada:

nenhum NativeHistoricalBootstrapOrchestrator deve executar;
nenhum lock programático deve existir;
nenhum get-candles programático deve ser enviado;
o bootstrap manual deve ser o único proprietário;
o endpoint dev não deve alterar Session Context ou Store.
7. Correção permitida

Aplicar o menor patch necessário em:

PolariumCDPLiveSource;
PolariumMarketFeedRuntime;
HistoricalBootstrapManager;
Market Router;
adapter do CandleStore;
ownership/locks experimentais.

Somente se a auditoria comprovar necessidade.

8. Fora de escopo

Não alterar:

frontend;
MarketChart.tsx;
useRealCandles.ts;
Chart API contratual;
Parser sem evidência;
CandleStore interno sem evidência;
Readiness sem evidência;
scanner;
ranking;
estratégia;
IA;
execução;
Browser Bridge;
OAuth;
extensão;
DOM ou automação visual.
9. Testes obrigatórios

Adicionar testes para:

ativo visível 2298 gera bootstrap para 2298;
resposta histórica de 2298 grava em POLARIUM:2298:300;
troca 76 → 2298 não mantém chave 76;
Chart API retorna série do ativo visível;
M1, M5 e M15;
seleção programática desligada não cria lock;
nenhum owner residual bloqueia fluxo manual;
stop/start limpa estado transitório;
realtime continua sem incrementar histórico;
frontend permanece consumindo a Chart API Polarium.
10. Validação automatizada

Executar:

cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

python -m pytest tests/market/providers -v
python -m pytest tests/market/chart -v
python -m pytest tests/frontend -v
python -m pytest -v

Executar:

cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run build
11. Validação real

Executar com seleção programática desligada:

POLARIUM_CDP_LIVE_ENABLED=true \
POLARIUM_PROGRAMMATIC_SELECTION_ENABLED=false \
.venv/bin/uvicorn app.main:app \
--host 127.0.0.1 \
--port 8000

Na Polarium, selecionar manualmente:

EURUSD-OTC M5
USDBRL-OTC M5
XAUUSD-OTC M5

Para cada ativo confirmar:

Session Context correto
bucket POLARIUM:<active_id>:300 criado
history_count >= 50
readiness READY
Chart API retorna candles
Friday desenha o gráfico

Confirmar:

curl -sS http://127.0.0.1:8000/api/v1/market/chart/series \
| python -m json.tool
12. Critério de aceitação

A Sprint somente termina quando o ativo visível manualmente possuir seu próprio bucket na Chart API.

Para USDBRL M5:

POLARIUM:2298:300
count >= 50

Não declarar sucesso apenas porque o Session Context mudou.

13. Git

Não executar:

git add
git commit
git push
git reset
git checkout
git restore
git clean
14. Entrega obrigatória
causa raiz;
ponto exato da divergência;
arquivos modificados;
patch mínimo;
testes;
resultados;
build;
validação real;
git status;
git diff;
riscos;
sugestão de commit.
15. Sugestão de commit
fix(polarium): restore visible asset candle routing