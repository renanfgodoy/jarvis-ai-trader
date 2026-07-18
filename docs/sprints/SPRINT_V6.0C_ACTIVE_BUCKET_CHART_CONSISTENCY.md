# FRIDAY AI TRADER

# SPRINT V6.0C — ACTIVE BUCKET / CHART CONSISTENCY

## Status

AUDITORIA DIRIGIDA COM CORREÇÃO MÍNIMA CONDICIONAL

---

## 1. Objetivo

Comprovar e corrigir, se necessário, a consistência entre:

```text
Session Context ativo
→ CandleStore bucket
→ Chart API
→ useRealCandles
→ gráfico

A investigação deve responder por que um ativo pode existir no CandleStore e estar ativo no Session Context, mas a Friday ainda exibir uma série antiga, incompleta ou vazia.

2. Evidências reais comprovadas

A auditoria anterior comprovou:

SessionContext:
XAUUSD-OTC
active_id=1857
raw_size=300

CandleStore bucket exists:
SIM

Também foram observados no CandleStore:

POLARIUM:76:60
POLARIUM:76:300
POLARIUM:1857:300
POLARIUM:2298:300
POLARIUM:76:900

O Market WebSocket continua entregando candles para active_id=1857, e o runtime continua processando-os.

A auditoria frontend comprovou que, quando recebe active_id=76/raw_size=300, o frontend:

chama /api/v1/market/chart
recebe HTTP 200
normaliza todos os candles
atualiza o estado
seleciona POLARIUM_CHART_API
envia candles ao gráfico
renderiza corretamente

Portanto, a falha restante deve ser localizada na transição de uma chave ativa para outra ou na leitura do bucket solicitado.

3. Regra principal

Não voltar a alterar:

captura CDP;
Market WebSocket;
Runtime Guard;
parser;
bootstrap histórico;
readiness;
seleção programática;
Browser Bridge;
OAuth;
layout.

A captura Polarium está congelada nesta Sprint.

4. Pipeline obrigatório

Auditar, para cada chave:

(active_id, raw_size)

o seguinte caminho:

Session Context
→ chave solicitada pelo frontend
→ chave recebida pela rota Chart API
→ chave consultada no CandleStore
→ bucket encontrado
→ quantidade retornada
→ quantidade recebida pelo hook
→ quantidade entregue ao gráfico

Testar obrigatoriamente:

76 / 300
1857 / 300
2298 / 300
5. Perguntas obrigatórias

Responder com evidência:

Quantos candles existem no bucket POLARIUM:1857:300?
Quantos candles existem no bucket POLARIUM:2298:300?
Qual chave a Chart API consulta quando recebe active_id=1857&raw_size=300?
A rota consulta exatamente POLARIUM:1857:300?
A resposta contém active_id=1857 ou dados de outro bucket?
Algum fallback usa a chave anterior 76/300?
Algum cache da rota é compartilhado entre ativos?
O useRealCandles mantém uma requisição anterior ativa após troca?
Uma resposta de 76/300 pode chegar depois da resposta de 1857/300?
Uma resposta vazia pode limpar uma série válida durante a troca?
O componente gráfico possui key ou identidade vinculada ao ativo/timeframe?
O contador de histórico e o array do gráfico usam a mesma fonte?
6. Instrumentação backend permitida

Instrumentar somente a rota Chart API e o adapter de leitura do CandleStore.

Registrar em desenvolvimento:

CHART_REQUEST_RECEIVED
CHART_STORE_KEY_RESOLVED
CHART_BUCKET_FOUND
CHART_BUCKET_MISSING
CHART_RESPONSE_CREATED

Campos:

timestamp
active_id_requested
raw_size_requested
store_key
bucket_exists
bucket_count
response_active_id
response_raw_size
response_count
first_timestamp
last_timestamp

Não registrar payload bruto ou dados sensíveis.

Gerar:

.jarvis_cache/diagnostics/chart_bucket_consistency.json
.jarvis_cache/diagnostics/chart_bucket_consistency.txt
7. Instrumentação frontend

Reutilizar:

window.__FRIDAY_CHART_BINDING_TRACE__
window.__FRIDAY_EXPORT_CHART_BINDING_TRACE__()

Não criar um segundo sistema de trace.

Adicionar somente os campos necessários para correlacionar:

request_sequence
requested_active_id
requested_raw_size
response_active_id
response_raw_size
response_count
current_context_active_id
current_context_raw_size
response_applied
response_ignored
8. Correlação obrigatória

Cada request frontend deve possuir um identificador local crescente.

A resposta só poderá atualizar o estado quando corresponder ao contexto atual:

response.active_id == current active_id
response.raw_size == current raw_size
request_sequence não é anterior ao último request aplicado

Se a arquitetura atual já garante isso, apenas comprovar.

Se não garante e a evidência demonstrar race condition, aplicar o menor patch possível.

Registrar respostas descartadas como:

STALE_ACTIVE_KEY_RESPONSE_IGNORED
9. Preservação de série durante transição

Auditar a troca:

76/300
→ 1857/300

Uma resposta vazia temporária da nova chave não pode apresentar candles da chave antiga como se fossem do novo ativo.

Também não pode manter o gráfico antigo sem indicar que está aguardando o bucket novo.

Regra:

nunca misturar ativos;
nunca apresentar candles antigos com rótulo do ativo novo;
nunca mascarar ausência de dados;
manter estado explícito de transição quando o bucket novo ainda não estiver disponível.

Não criar dados sintéticos.

10. Chart API

Auditar:

app/api/routes/market_chart.py
app/market/runtime.py
CandleStore/list/read adapters utilizados pela rota

Confirmar que:

GET /api/v1/market/chart?active_id=1857&raw_size=300

retorna somente o bucket:

POLARIUM:1857:300

e que:

GET /api/v1/market/chart?active_id=2298&raw_size=300

retorna somente:

POLARIUM:2298:300

Não usar Session Context para substituir parâmetros explícitos da rota.

11. Causa possível do contador divergente

Auditar por que a tela pode mostrar, por exemplo:

Histórico: 21/50
Candles: 27

Identificar:

fonte de history_count;
fonte de candles.length;
se realtime entra no array visual;
se histórico conta apenas timestamps históricos;
se isso é comportamento correto ou divergência.

Não alterar a semântica sem evidência.

12. Correção permitida

Somente após a auditoria comprovar a causa, é permitido corrigir:

resolução da chave na Chart API;
cache incorreto por ativo/timeframe;
resposta de bucket errado;
race condition no useRealCandles;
resposta stale sobrescrevendo contexto novo;
identidade do componente gráfico;
limpeza indevida de estado;
divergência inequívoca entre parâmetros e resposta.

Não aplicar refatoração ampla.

13. Testes obrigatórios — backend

Adicionar testes para:

76/300 retorna somente bucket 76/300;
1857/300 retorna somente bucket 1857/300;
2298/300 retorna somente bucket 2298/300;
bucket inexistente retorna vazio explicitamente;
parâmetros explícitos não são substituídos pelo Session Context;
ativos não compartilham cache;
timeframes não compartilham cache;
resposta preserva active_id e raw_size solicitados;
primeiro e último timestamps pertencem ao bucket solicitado.
14. Testes obrigatórios — frontend

Adicionar testes para:

troca 76/300 → 1857/300;
troca 1857/300 → 2298/300;
resposta antiga de 76 não sobrescreve 1857;
resposta antiga de 1857 não sobrescreve 2298;
resposta vazia da chave nova não é confundida com a anterior;
série antiga nunca aparece rotulada como ativo novo;
resposta válida atualiza o gráfico;
response.active_id incompatível é rejeitado;
response.raw_size incompatível é rejeitado;
gráfico recebe a série da chave corrente;
loading termina quando a série correta chega.
15. Validação automatizada

Executar:

cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

python -m pytest tests/market/chart -v
python -m pytest tests/frontend -v
python -m pytest tests/market/providers -v
python -m pytest -v

Executar:

cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run build

Executar também os testes frontend definidos no package.json, se existirem.

16. Validação real

Subir frontend e backend normalmente, com seleção programática desligada.

Na Polarium:

1. Selecionar EURUSD-OTC M5.
2. Aguardar gráfico.
3. Trocar para XAUUSD-OTC M5.
4. Aguardar gráfico.
5. Trocar para USDBRL-OTC M5.
6. Aguardar gráfico.

Executar:

curl -sS \
"http://127.0.0.1:8000/api/v1/market/chart?active_id=76&raw_size=300&limit=200" \
| python -m json.tool
curl -sS \
"http://127.0.0.1:8000/api/v1/market/chart?active_id=1857&raw_size=300&limit=200" \
| python -m json.tool
curl -sS \
"http://127.0.0.1:8000/api/v1/market/chart?active_id=2298&raw_size=300&limit=200" \
| python -m json.tool

No console da Friday:

window.__FRIDAY_EXPORT_CHART_BINDING_TRACE__()

Comparar backend e frontend por chave.

17. Critério de aceitação

A Sprint somente termina quando:

Chart API 76/300 → somente candles de 76/300
Chart API 1857/300 → somente candles de 1857/300
Chart API 2298/300 → somente candles de 2298/300

E na Friday:

Session Context atual
=
endpoint solicitado
=
response active_id/raw_size
=
fonte selecionada
=
candles entregues ao gráfico

Nenhuma resposta stale pode sobrescrever a chave atual.

18. Entrega obrigatória

Entregar:

objetivo;
arquitetura auditada;
contagem dos buckets 76/300, 1857/300 e 2298/300;
chave solicitada por cada request;
chave usada pelo CandleStore;
chave devolvida pela API;
chave aplicada pelo frontend;
causa raiz comprovada;
arquivos criados;
arquivos modificados;
patch mínimo aplicado;
testes backend;
testes frontend;
resultados;
build;
validação real;
relatório de consistência;
git status;
git diff;
riscos;
sugestão de commit.
19. Git

Não executar:

git add
git commit
git push
git reset
git checkout
git restore
git clean
git stash

Não apagar arquivos não rastreados.

20. Sugestão de commit
fix(chart): keep active bucket consistent across API and frontend