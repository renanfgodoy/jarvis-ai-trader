# FRIDAY AI TRADER

# SPRINT V5.9E — RESTORE LAST KNOWN GOOD BASELINE

## Status

EMERGÊNCIA — RECUPERAÇÃO DE REGRESSÃO

---

## 1. Objetivo

Restaurar o último baseline funcional comprovado da Friday antes de qualquer nova evolução.

O baseline que precisa voltar a funcionar é:

```text
Backend
→ Chrome dedicado
→ Polarium /traderoom
→ sessão autenticada
→ Market WebSocket
→ Runtime Guard
→ Parser
→ Market Router
→ CandleStore
→ Chart API
→ Friday

Comportamento esperado:

Chrome dedicado abre;
Polarium abre;
Friday abre em segunda aba;
ativo selecionado manualmente na Polarium aparece na Friday;
timeframe selecionado manualmente aparece na Friday;
gráfico recebe candles reais;
M1 funciona;
M5 funciona;
M15 funciona;
histórico chega a READY.
2. Estado quebrado atual

A aplicação deixou de subir gráficos.

O log real mostra que o frontend está chamando:

GET /api/v1/market/providers/iq-option/candles

e recebe:

502 Bad Gateway

O projeto atual deveria usar a Chart API alimentada pelo runtime Polarium, e não depender do endpoint IQ Option para o gráfico principal.

Também existem alterações experimentais acumuladas relacionadas a:

seleção programática;
bootstrap nativo;
captura de envelopes;
locks de bootstrap;
ownership;
abertura automática da Friday;
diagnósticos.

Essas funcionalidades não podem interferir no baseline manual.

3. Regra principal

Não avançar seleção programática nesta Sprint.

Não tentar corrigir get-candles programático.

Não criar nova funcionalidade.

Apenas restaurar o baseline manual.

4. Proibições Git

Não executar:

git reset
git checkout
git restore
git clean
git stash
git add
git commit
git push

Não apagar arquivos não rastreados.

Não sobrescrever pendências autorizadas.

A recuperação deverá ser feita por auditoria e patch explícito.

5. Last known good funcional

Usar como referência funcional comprovada o estado posterior às Sprints V5.7A e V5.7B, quando a validação real mostrou:

EURUSD-OTC raw_size=300
XAUUSD-OTC raw_size=300
BTCUSD-OTC-op raw_size=300

Com todos apresentando:

bootstrap started=True
bootstrap finished=True
discarded=False
chart updated=True
frontend_updated=True
NO_DIVERGENCE_CLASSIFIED

A recuperação não precisa remover diagnósticos posteriores, mas deve impedir que recursos experimentais alterem o fluxo manual.

6. Auditoria obrigatória do frontend

Localizar todas as referências a:

/api/v1/market/providers/iq-option/candles

e identificar:

arquivo;
componente;
hook;
serviço;
fallback;
condição que escolhe o provider;
configuração padrão;
origem do symbol;
origem do raw_size;
motivo do gráfico principal usar IQ Option.

Auditar também referências a:

/api/v1/market/chart
/api/v1/market/chart/series

Determinar qual endpoint era usado no baseline funcional.

O gráfico principal da Friday deve consumir a fonte oficial definida pela arquitetura atual, sem fallback silencioso para IQ Option.

7. Auditoria obrigatória do backend

Auditar:

app/api/routes/market_chart.py;
registro das rotas em app/main.py;
runtime compartilhado em app/market/runtime.py;
PolariumMarketFeedRuntime;
PolariumCDPLiveSource;
DualTabCDPSessionManager;
seleção do target /traderoom;
Chart API;
CandleStore;
Session Context;
locks e owners experimentais.

Confirmar que o endpoint genérico da Chart API lê o CandleStore Polarium correto.

8. Isolamento experimental obrigatório

A seleção programática deve permanecer desligada por padrão:

POLARIUM_PROGRAMMATIC_SELECTION_ENABLED=false

Com a flag desligada:

nenhum NativeHistoricalBootstrapOrchestrator deve rodar;
nenhum lock programático deve ser criado;
nenhum get-candles programático deve ser enviado;
nenhum owner programático deve bloquear o bootstrap manual;
nenhum endpoint experimental deve alterar Session Context;
diagnósticos podem observar, mas não modificar o fluxo.
9. Estratégia de recuperação

Aplicar o menor conjunto de patches necessário para:

restaurar a fonte correta do gráfico;
remover fallback incorreto para IQ Option no gráfico Polarium;
garantir que frontend e Chart API usem a mesma chave:
provider;
active_id;
symbol;
raw_size;
preservar o espelhamento manual;
manter funcionalidades experimentais isoladas;
garantir cleanup no shutdown;
garantir que Friday abra sem depender de READY histórico.

Não mascarar erros com dados fictícios.

Não usar candles sintéticos.

10. Testes obrigatórios
Frontend

Adicionar testes para:

gráfico principal não chamar IQ Option quando a sessão ativa é Polarium;
gráfico usar /api/v1/market/chart ou endpoint oficial comprovado;
provider Polarium não cair em fallback IQ Option;
troca de ativo atualiza a consulta;
troca M1/M5/M15 atualiza a consulta;
erro de provider não apaga série válida sem estado explícito.
Backend

Adicionar testes para:

Chart API retorna candles Polarium;
Chart API usa active_id e raw_size do Session Context;
seleção manual atualiza Chart API;
M1 funciona;
M5 funciona;
M15 funciona;
runtime programático desligado não interfere;
locks experimentais vazios;
startup e shutdown limpos;
target /traderoom correto;
Friday abre em segunda aba.
Regressão

Preservar:

Parser;
CandleStore;
Readiness;
realtime não incrementa histórico;
troca atômica;
bootstrap manual;
frontend polling.
11. Comandos de investigação obrigatórios

Executar e incluir no relatório:

grep -Rni "/api/v1/market/providers/iq-option/candles" frontend app tests
grep -RniE "/api/v1/market/chart|market/chart/series" frontend app tests
git status --short
git diff --stat

Não usar Git para reverter arquivos.

12. Validação automatizada

Backend:

cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate
python -m pytest tests/market/providers -v
python -m pytest -v

Frontend:

cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run build

Executar também os testes frontend existentes relacionados ao gráfico, se houver comando definido no package.json.

13. Validação real obrigatória
Terminal 1
cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run dev
Terminal 2
cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

POLARIUM_CDP_LIVE_ENABLED=true \
POLARIUM_PROGRAMMATIC_SELECTION_ENABLED=false \
.venv/bin/uvicorn app.main:app \
--host 127.0.0.1 \
--port 8000

Validar sem chamar endpoint experimental:

1. Chrome dedicado abre.
2. Polarium abre em /traderoom.
3. Friday abre em segunda aba.
4. Login funciona.
5. Market WebSocket conecta.
6. EURUSD M1 espelha.
7. EURUSD M5 espelha.
8. EURUSD M15 espelha.
9. XAUUSD M5 espelha.
10. Candles passados aparecem.
11. Histórico chega a READY.
12. Nenhuma chamada do gráfico principal usa IQ Option.
13. Nenhum 502 de IQ Option ocorre no fluxo Polarium.
14. Critério de aceitação

A Sprint somente termina quando o baseline manual voltar a funcionar de ponta a ponta.

Não declarar sucesso apenas com testes automatizados.

Critérios mínimos:

Friday abre
Polarium espelha
gráfico aparece
ativo acompanha
timeframe acompanha
M1/M5/M15 funcionam
histórico READY
sem 502 IQ Option no gráfico principal
15. Entrega obrigatória

Entregar:

causa raiz;
referência exata que chamava IQ Option;
endpoint oficial restaurado;
arquivos criados;
arquivos modificados;
patch aplicado;
funcionalidades experimentais isoladas;
testes adicionados;
resultados dos testes;
build;
procedimento de validação real;
git status --short;
git diff --stat;
riscos;
próximos passos;
sugestão de commit.
16. Sugestão de commit
fix(friday): restore Polarium chart baseline and isolate experiments