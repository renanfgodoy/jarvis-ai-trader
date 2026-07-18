# FRIDAY AI TRADER

# SPRINT V6.0A — CHART BINDING AUDIT

## Status

AUDITORIA FRONTEND — BACKEND CONGELADO

---

## 1. Objetivo

Auditar exclusivamente o caminho dos candles entre a Chart API e a renderização visual do gráfico da Friday.

O backend Polarium está congelado nesta Sprint.

Não implementar correção especulativa.

Primeiro identificar exatamente em qual ponto os candles deixam de existir:

```text
Chart API
→ fetch
→ useRealCandles
→ estado React
→ seleção da fonte
→ normalização
→ props do gráfico
→ renderização
2. Evidência real comprovada

O backend já demonstrou possuir séries reais e prontas.

Exemplo real:

active_id=2298
raw_size=300
history_count=312
readiness=READY

O backend também registrou chamadas contínuas com resposta HTTP 200:

GET /api/v1/market/chart?active_id=2298&raw_size=300&limit=200
200 OK

Mesmo assim, a interface permaneceu mostrando:

Candles: 0
Histórico: 0/50
Aguardando dados reais da Polarium

Portanto, a investigação desta Sprint começa na resposta da Chart API e termina na renderização do gráfico.

3. Regra absoluta

Nenhum arquivo Python pode ser modificado.

Não alterar:

PolariumCDPLiveSource;
CDP;
WebSocket;
Runtime Guard;
Parser;
Market Router;
CandleStore;
HistoricalBootstrapManager;
Readiness;
Chart API;
Session Context backend;
seleção programática;
Browser Bridge;
OAuth;
extensão.

Se algum desses arquivos for alterado, a Sprint deve ser considerada inválida.

4. Arquivos permitidos

Apenas frontend e testes frontend relacionados ao gráfico.

Arquivos principais permitidos:

frontend/src/pages/MarketChart.tsx
frontend/src/hooks/useRealCandles.ts
frontend/src/hooks/usePolariumLive.ts
frontend/src/components/**
frontend/src/debug/chartBindingTrace.ts
tests/frontend/**

É permitido criar:

frontend/src/debug/chartBindingTrace.ts

Não alterar layout visual.

Não adicionar painel permanente.

Não alterar identidade da Friday.

5. Pipeline a auditar

Registrar, em ordem:

Session Context recebido
→ active_id escolhido
→ raw_size escolhido
→ endpoint construído
→ fetch iniciado
→ resposta HTTP recebida
→ JSON interpretado
→ candles recebidos
→ candles normalizados
→ estado React atualizado
→ fonte final escolhida
→ candles enviados ao componente gráfico
→ gráfico renderizado
6. Hipóteses prioritárias

Auditar especialmente:

O frontend recebe active_id=2298, mas continua consultando 76.
O frontend recebe raw_size=300, mas mantém 60.
useRealCandles recebe candles, mas não atualiza o estado.
Uma resposta antiga sobrescreve uma resposta mais nova.
Existe race condition entre Session Context e polling.
MarketChart.tsx escolhe uma fonte vazia apesar de polariumLive.candles conter dados.
O array é limpo durante estado transitório.
A normalização rejeita candles válidos.
O componente gráfico recebe os candles, mas não atualiza a série.
Uma chave React incorreta preserva o gráfico antigo.
O gráfico recebe timestamps em unidade incompatível.
O estado de loading continua ativo mesmo depois do fetch bem-sucedido.

Não assumir nenhuma hipótese antes da instrumentação.

7. Instrumentação obrigatória

Criar:

frontend/src/debug/chartBindingTrace.ts

O trace deve ser habilitado somente em desenvolvimento.

Registrar eventos sanitizados:

SESSION_CONTEXT_RECEIVED
ACTIVE_KEY_RESOLVED
CHART_FETCH_START
CHART_FETCH_SUCCESS
CHART_FETCH_EMPTY
CHART_FETCH_ERROR
STALE_RESPONSE_IGNORED
CANDLES_NORMALIZED
CANDLE_STATE_UPDATED
SOURCE_SELECTED
GRAPH_PROPS_UPDATED
GRAPH_RENDERED
GRAPH_EMPTY
GRAPH_LOADING
GRAPH_ERROR

Cada registro deve conter apenas dados técnicos não sensíveis:

timestamp
event
active_id
raw_size
symbol
endpoint
http_status
response_count
normalized_count
state_count
selected_source
graph_prop_count
first_candle_time
last_candle_time
request_sequence
reason

Nunca registrar:

cookies;
tokens;
headers;
Authorization;
payload de autenticação;
dados pessoais;
conteúdo bruto completo.
8. Armazenamento do diagnóstico

Como o código do navegador não pode escrever diretamente em .jarvis_cache, armazenar o trace de desenvolvimento em:

window.__FRIDAY_CHART_BINDING_TRACE__

e também em:

localStorage["friday_chart_binding_trace"]

Limitar a no máximo 500 registros para evitar crescimento infinito.

Disponibilizar em desenvolvimento:

window.__FRIDAY_EXPORT_CHART_BINDING_TRACE__()

Essa função deve retornar uma string de texto pronta para copiar, contendo:

Friday Trade - Chart Binding Trace

active_id
raw_size
endpoint
response_count
normalized_count
state_count
selected_source
graph_prop_count
last_successful_stage
failure_stage
failure_reason

Não modificar a interface visual para exibir esse diagnóstico.

9. Identidade da requisição

Cada fetch do gráfico deve possuir uma sequência local crescente:

request_sequence

Exemplo:

101
102
103

Quando uma resposta antiga chegar depois de uma resposta nova, registrar:

STALE_RESPONSE_IGNORED

e impedir que ela apague ou substitua candles do contexto atual.

Nesta Sprint, só implementar essa proteção se a auditoria comprovar que ela já é necessária para preservar a integridade do trace. Não refatorar o hook inteiro.

10. Fonte final do gráfico

Registrar claramente qual fonte foi escolhida em MarketChart.tsx.

Possíveis valores:

POLARIUM_CHART_API
POLARIUM_LIVE
EMPTY
LEGACY_IQ_BLOCKED
UNKNOWN

O relatório deve informar:

candles recebidos pela Chart API
candles presentes no hook
candles escolhidos pela página
candles entregues ao componente gráfico
11. Verificação de contrato

Auditar o contrato real retornado por:

/api/v1/market/chart

Confirmar se o frontend lê corretamente:

provider
active_id
symbol
raw_size
count
candles

Auditar os campos de cada candle:

timestamp/time/from
open
high
low
close
volume

Não inventar campos.

Se houver divergência entre o contrato backend e o tipo TypeScript, documentar exatamente:

campo esperado
campo recebido
arquivo
linha
efeito causado
12. Testes obrigatórios

Adicionar ou ajustar testes frontend para:

Requisição
usa active_id atual;
usa raw_size atual;
chama /api/v1/market/chart;
não chama IQ Option;
atualiza a URL após troca de ativo;
atualiza a URL após troca de timeframe.
Resposta
resposta com 312 candles gera estado com 312 candles;
resposta vazia gera estado explícito;
resposta antiga não sobrescreve contexto novo;
erro HTTP não apaga uma série válida sem motivo explícito;
normalização preserva candles válidos.
Fonte
Polarium Chart API é escolhida quando possui candles;
fonte vazia não substitui série válida durante transição;
IQ Option permanece bloqueada no baseline Polarium;
mudança 76/300 → 2298/300 troca a fonte corretamente.
Gráfico
componente recebe quantidade correta;
primeiro e último timestamps são preservados;
render atualiza após mudança de ativo;
render atualiza após mudança de timeframe;
loading termina após resposta válida;
gráfico não permanece em zero quando o hook possui candles.
Diagnóstico
trace registra todas as etapas;
trace não contém dados sensíveis;
trace limita 500 registros;
exportação retorna texto legível;
produção não expõe instrumentação de desenvolvimento.
13. Auditoria estática obrigatória

Executar:

grep -RniE \
"useRealCandles|polariumLive\\.candles|setCandles|selectedCandles|chartCandles|active_id|raw_size|market/chart" \
frontend/src/pages frontend/src/hooks frontend/src/components

Executar:

grep -RniE \
"iq-option/candles|iqCandles|iqAssets|IQ_OPTION" \
frontend/src

Informar no relatório:

arquivo
linha
função
responsabilidade
14. Validação automatizada

Executar os testes frontend existentes.

Primeiro verificar os scripts:

cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
cat package.json

Executar os comandos de teste definidos no projeto.

Também executar:

cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

python -m pytest tests/frontend -v
python -m pytest -v

Build:

cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run build
15. Validação real

Subir frontend:

cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run dev

Subir backend sem alterar o backend:

cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

POLARIUM_CDP_LIVE_ENABLED=true \
POLARIUM_PROGRAMMATIC_SELECTION_ENABLED=false \
.venv/bin/uvicorn app.main:app \
--host 127.0.0.1 \
--port 8000

Na Polarium:

1. Selecionar USDBRL-OTC M5.
2. Aguardar backend chegar a READY.
3. Observar a Friday.

No console da aba Friday, executar:

window.__FRIDAY_EXPORT_CHART_BINDING_TRACE__()

O resultado deve indicar exatamente:

active_id usado
raw_size usado
endpoint chamado
candles recebidos
candles normalizados
candles no estado
fonte selecionada
candles enviados ao gráfico
última etapa bem-sucedida
primeira etapa que falhou
16. Critério de conclusão da auditoria

A Sprint termina somente quando for possível responder com evidência:

Qual active_id o frontend utilizou?
Qual raw_size utilizou?
Qual endpoint chamou?
Quantos candles a API retornou?
Quantos candles o hook armazenou?
Quantos candles a página selecionou?
Quantos candles o gráfico recebeu?
Qual foi a primeira etapa onde a quantidade caiu para zero?

Não implementar uma grande correção nesta Sprint.

Se a causa for uma condição simples e inequívoca, apresentar o patch sugerido separadamente, sem aplicá-lo sem autorização no Markdown.

17. Entrega obrigatória

Entregar:

objetivo;
arquitetura frontend auditada;
arquivos criados;
arquivos modificados;
active_id usado;
raw_size usado;
endpoint chamado;
quantidade retornada pela API;
quantidade após normalização;
quantidade no estado;
fonte selecionada;
quantidade enviada ao gráfico;
última etapa bem-sucedida;
primeira etapa de falha;
causa raiz comprovada ou estado pendente;
testes adicionados;
resultado dos testes frontend;
resultado da suíte completa;
resultado do build;
procedimento de validação real;
git status --short;
git diff --stat;
riscos;
patch mínimo recomendado;
sugestão de commit.
18. Git

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

19. Sugestão de commit
chore(chart): trace Polarium chart binding pipeline