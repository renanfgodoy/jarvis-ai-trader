# FRIDAY AI TRADER

# SPRINT FRIDAY RESET V1.0 — VISION-FIRST CLEANUP

## Status

REESTRUTURAÇÃO CONTROLADA DA FRIDAY PARA O MODELO DE ANÁLISE POR IMAGEM

---

## 1. Objetivo

Transformar a Friday em uma aplicação Vision-First.

Novo fluxo principal:

```text
Usuário
→ cola ou envia print do gráfico
→ informa ativo, timeframe e expiração
→ backend valida a imagem
→ IA multimodal analisa
→ Friday exibe resposta estruturada
→ análise é salva no histórico
```

A Friday não terá mais como fluxo principal:

```text
integração direta com corretoras;
espelhamento de gráficos;
captura de WebSocket;
CDP;
captura de candles;
providers de corretoras;
sincronização de ativo;
sincronização de timeframe;
execução automática;
CALL ou PUT enviados à corretora.
```

---

## 2. Princípio de segurança da refatoração

Não apagar arquivos imediatamente sem inventário.

Executar a limpeza em quatro etapas:

```text
1. inventariar;
2. classificar;
3. desacoplar;
4. remover ou arquivar.
```

Não utilizar comandos destrutivos de Git.

Não executar:

```text
git reset
git checkout
git restore
git clean
git stash
```

---

## 3. Nova proposta da Friday

A aplicação deverá ficar concentrada nos seguintes módulos:

```text
Autenticação
Friday Vision
Upload e colagem de imagem
Análise multimodal
Motor de decisão
Gestão de risco
Histórico
Configurações
Diagnósticos
```

---

## 4. O que permanece

Preservar e adaptar quando útil:

```text
estrutura FastAPI;
estrutura React/Vite;
sistema de rotas;
configuração por environment;
sistema de testes;
componentes visuais reutilizáveis;
autenticação, caso já exista;
banco de dados, caso já exista;
tratamento de erros;
logging;
health check;
infraestrutura de deploy;
Market Analysis Engine, somente se for neutro e reutilizável;
modelos de decisão neutros;
tipos TypeScript reutilizáveis.
```

---

## 5. O que deixa de fazer parte do runtime principal

Remover do startup e do fluxo principal:

```text
PocketProviderAdapter
FakePocketProviderAdapter
PocketMarketRuntime
PocketCDPObservationTransport
PocketReplayTransport
PocketReadOnlyLiveSource
PocketSessionContext
PocketRealtimeCandleBuilder
PocketReadinessTracker
PocketRuntimeGuard
PocketTargetManager
Pocket protocol discovery
Pocket HAR parser
ProviderManager de corretoras
ProviderFactory de corretoras
ProviderRegistry de corretoras
ChartProviderService
sincronização Pocket
sincronização Polarium
CDP Chrome 9230
captura Socket.IO
updateStream
updateHistoryNewFast
changeSymbol
updateAssets
chart polling de corretoras
useRealCandles dependente de broker
RealCandleChart dependente de broker
fallback IQ Option
fallback Polarium
AutoTrade
ordens
CALL
PUT
saldo de corretora
payout de corretora
```

---

## 6. Importante: arquivamento antes da remoção definitiva

Código antigo relevante deverá ser movido para uma área fora do runtime:

```text
_archive/broker_integrations/
```

Estrutura sugerida:

```text
_archive/
  broker_integrations/
    pocket/
    polarium/
    provider_v2/
    chart_realtime/
    protocol_discovery/
```

Objetivo:

```text
preservar pesquisa técnica;
evitar imports ativos;
evitar startup acidental;
evitar regressão no novo sistema;
permitir consulta futura.
```

Não mover arquivos automaticamente antes de mapear dependências.

---

## 7. Inventário obrigatório

Criar:

```text
docs/audits/FRIDAY_VISION_FIRST_CLEANUP_INVENTORY.md
```

Para cada arquivo relacionado ao modelo antigo, registrar:

```text
caminho;
responsabilidade;
imports recebidos;
imports realizados;
uso no runtime;
uso em testes;
decisão;
justificativa.
```

Decisões possíveis:

```text
KEEP
ADAPT
ARCHIVE
DELETE
```

Nenhum arquivo deverá ser apagado sem aparecer no inventário.

---

## 8. Classificação

### KEEP

Código necessário para a nova Friday.

### ADAPT

Código neutro que pode ser reaproveitado no sistema Vision.

### ARCHIVE

Código antigo de integração com corretoras que não fará parte do runtime.

### DELETE

Somente:

```text
duplicações;
arquivos temporários;
código comprovadamente morto;
fixtures obsoletas;
componentes sem referência;
testes ligados exclusivamente a código removido.
```

---

## 9. Startup

O startup da Friday não deverá:

```text
abrir Chrome;
conectar em CDP;
iniciar provider;
iniciar Pocket runtime;
iniciar Polarium;
procurar WebSocket;
carregar HAR;
construir candles;
consultar corretoras.
```

O backend deverá iniciar somente com:

```text
configuração;
logging;
API;
autenticação;
banco;
Friday Vision;
health check.
```

---

## 10. Configurações antigas

Remover do runtime ou marcar como deprecated:

```text
MARKET_PROVIDER_V2_ENABLED
MARKET_PROVIDER_CURRENT
POCKET_CHART_INTEGRATION_ENABLED
POCKET_CDP_ENABLED
POCKET_REAL_OBSERVATION_AUTHORIZED
POCKET_READ_ONLY
POCKET_LIVE_CONNECTION_ENABLED
POCKET_CDP_OBSERVATION_ONLY
POCKET_CHART_MODE
```

Criar configuração nova:

```text
FRIDAY_VISION_ENABLED=true
FRIDAY_VISION_PROVIDER=openai
FRIDAY_VISION_MAX_IMAGE_MB=10
FRIDAY_VISION_ALLOWED_FORMATS=png,jpg,jpeg,webp
FRIDAY_VISION_ANALYSIS_TIMEOUT_SECONDS=60
FRIDAY_VISION_SAVE_IMAGES=false
FRIDAY_VISION_SAVE_HISTORY=true
FRIDAY_VISION_REQUIRE_AUTH=true
```

Não incluir chave de IA no frontend.

---

## 11. Rotas antigas

Mapear e remover do frontend principal:

```text
/api/v1/market/chart
/api/v1/market/chart/series
/api/v1/market/provider-v2/status
```

As rotas poderão temporariamente retornar:

```text
410 Gone
```

com mensagem:

```json
{
  "code": "BROKER_CHART_FEATURE_RETIRED",
  "message": "A Friday agora utiliza análise de mercado por imagem."
}
```

Não manter polling escondido para essas rotas.

---

## 12. Frontend antigo

Remover da navegação principal:

```text
gráfico espelhado;
status Pocket;
status Polarium;
provider selector;
readiness do broker;
active_id;
raw_size;
botões de conexão;
estado CDP;
estado WebSocket;
realtime candle chart.
```

Não redesenhar ainda toda a nova interface.

Nesta Sprint, criar apenas um placeholder:

```text
Friday Vision está sendo preparada.
```

Com CTA desabilitado:

```text
Analisar print
```

---

## 13. Nova navegação proposta

Manter somente:

```text
Dashboard
Friday Vision
Histórico
Gestão de Risco
Configurações
```

Remover links relacionados a:

```text
Pocket
Polarium
Provider V2
Broker Chart
Live Market
AutoTrade
```

---

## 14. Serviços antigos

Identificar e desacoplar:

```text
market runtime;
provider runtime;
broker services;
chart services;
CDP services;
Socket.IO services;
HAR services;
replay services.
```

Nenhum desses serviços deverá ser instanciado por:

```text
app/main.py;
app/market/runtime.py;
startup hooks;
dependency injection principal.
```

---

## 15. Market Analysis Engine

Avaliar o pacote:

```text
app/market/analysis/
```

Manter somente se for neutro.

Pode permanecer caso trabalhe com:

```text
AnalysisContext;
MarketAnalysis;
MarketState;
MarketHealth;
MarketStatistics;
decision models.
```

Arquivar ou adaptar partes que dependam de:

```text
ProviderHistory;
ProviderTicks;
ProviderContext;
candles de corretora;
ProviderRegistry.
```

O futuro motor deverá receber uma leitura extraída da imagem.

---

## 16. Novo domínio sugerido

Preparar, sem implementar a IA completa:

```text
app/vision/
```

Estrutura inicial:

```text
app/vision/
  __init__.py
  models.py
  enums.py
  exceptions.py
```

Modelos iniciais:

```text
VisionAnalysisRequest
VisionAnalysisResult
VisionMarketContext
VisionDecision
VisionRiskAssessment
VisionImageMetadata
```

Enums:

```text
CALL
PUT
WAIT
DO_NOT_TRADE
```

```text
BULLISH
BEARISH
SIDEWAYS
UNCLEAR
```

```text
LOW
MEDIUM
HIGH
EXTREME
```

---

## 17. Contrato futuro da análise

Preparar contrato conceitual:

```json
{
  "decision": "WAIT",
  "asset": "EURUSD OTC",
  "timeframe": "M1",
  "expiration": "1 minute",
  "trend": "BEARISH",
  "market_state": "SIDEWAYS",
  "risk": "HIGH",
  "confidence": 61,
  "summary": "Preço próximo de suporte após pressão vendedora.",
  "entry_condition": "Aguardar nova rejeição na resistência.",
  "warnings": [
    "Movimento esticado",
    "Histórico visual limitado"
  ]
}
```

Não integrar ainda com API externa nesta Sprint.

---

## 18. Banco e histórico

Preservar banco existente.

Não criar migração destrutiva.

Preparar somente o conceito de histórico:

```text
analysis_id
user_id
asset
timeframe
expiration
decision
risk
confidence
summary
image_hash
created_at
```

Imagens não deverão ser salvas por padrão.

---

## 19. Segurança

Garantir que:

```text
nenhuma chave de IA apareça no frontend;
nenhuma credencial antiga de corretora seja carregada;
nenhum cookie seja acessado;
nenhum Chrome seja aberto;
nenhum socket seja iniciado;
nenhuma ordem seja possível;
nenhuma rota AutoTrade permaneça funcional.
```

---

## 20. Dependências

Auditar:

```text
requirements.txt
pyproject.toml
package.json
package-lock.json
```

Remover somente dependências comprovadamente exclusivas do modelo antigo.

Não remover bibliotecas usadas em outras áreas.

Gerar relatório:

```text
docs/audits/FRIDAY_UNUSED_DEPENDENCIES.md
```

---

## 21. Testes antigos

Classificar testes em:

```text
manter;
adaptar;
arquivar;
remover.
```

Testes de código arquivado não precisam permanecer na suíte principal.

Preservar testes de:

```text
API;
segurança;
configuração;
autenticação;
banco;
análise neutra;
frontend reutilizável.
```

---

## 22. Novos testes

Criar testes para confirmar:

```text
backend não inicia CDP;
backend não inicia Pocket;
backend não inicia Polarium;
backend não inicia providers;
backend não abre Chrome;
nenhum WebSocket de broker é criado;
rotas antigas retornam 410 ou ficam removidas;
nova rota Friday Vision placeholder responde;
frontend não chama chart API antiga;
frontend não possui polling de broker;
frontend compila.
```

---

## 23. Rota placeholder Vision

Criar:

```text
GET /api/v1/vision/status
```

Resposta:

```json
{
  "enabled": true,
  "mode": "VISION_FIRST",
  "analysis_available": false,
  "message": "Friday Vision preparada para integração multimodal."
}
```

---

## 24. Tela placeholder

Criar rota frontend:

```text
/vision
```

Tela mínima:

```text
Friday Vision

Cole um print do gráfico e receba uma análise estruturada.

Em preparação.
```

Não integrar IA nesta Sprint.

---

## 25. Diagnóstico

Criar:

```text
.jarvis_cache/diagnostics/friday_vision_first_cleanup.json
.jarvis_cache/diagnostics/friday_vision_first_cleanup.txt
```

Registrar:

```text
files_kept
files_adapted
files_archived
files_deleted
routes_retired
services_disabled
dependencies_removed
broker_imports_remaining
broker_startup_hooks_remaining
frontend_broker_calls_remaining
tests_passed
build_passed
```

---

## 26. Busca obrigatória

Realizar busca no projeto por:

```text
Pocket
Polarium
ProviderManager
ProviderRegistry
ProviderFactory
PocketMarketRuntime
CDP
9230
Socket.IO
updateStream
updateHistoryNewFast
changeSymbol
active_id
raw_size
useRealCandles
RealCandleChart
AutoTrade
CALL
PUT
```

Separar ocorrências legítimas arquivadas das ocorrências ainda ativas.

---

## 27. Critérios de aprovação

A Sprint será aprovada quando:

```text
Friday iniciar sem corretora;
Friday iniciar sem Chrome;
Friday iniciar sem CDP;
Friday iniciar sem WebSocket de broker;
nenhum provider de corretora fizer parte do runtime;
frontend não consultar Chart API antiga;
rotas antigas forem aposentadas;
tela /vision existir;
endpoint /vision/status existir;
testes passarem;
build passar;
código antigo relevante estiver inventariado;
nenhuma remoção não documentada ocorrer.
```

---

## 28. Fora de escopo

Não implementar ainda:

```text
OpenAI API;
upload de imagem;
clipboard;
drag and drop;
OCR;
análise multimodal;
motor de sinais;
histórico funcional;
login novo;
deploy;
pagamentos;
captura automática de tela.
```

Esses itens pertencem à Sprint Friday Vision V1.0.

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

Exibir:

```text
git status --short
git diff --stat
```

---

## 30. Entrega obrigatória

Entregar:

1. resumo executivo;
2. inventário criado;
3. arquivos KEEP;
4. arquivos ADAPT;
5. arquivos ARCHIVE;
6. arquivos DELETE;
7. módulos desacoplados;
8. startup antes e depois;
9. rotas aposentadas;
10. frontend removido;
11. navegação nova;
12. configurações aposentadas;
13. configurações novas;
14. domínio vision criado;
15. endpoint vision status;
16. tela vision;
17. dependências removidas;
18. dependências preservadas;
19. testes removidos;
20. testes adaptados;
21. novos testes;
22. busca por imports antigos;
23. broker imports restantes;
24. hooks antigos restantes;
25. resultado da suíte;
26. resultado do build;
27. arquivos criados;
28. arquivos modificados;
29. arquivos movidos;
30. arquivos apagados;
31. diagnóstico;
32. riscos;
33. lacunas;
34. git status;
35. git diff;
36. sugestão de commit;
37. confirmação de que nenhum comando Git proibido foi executado.

---

## 31. Próxima Sprint

Após esta limpeza:

```text
SPRINT FRIDAY VISION V1.0 — SCREENSHOT MARKET ANALYSIS
```

Ela implementará:

```text
colar imagem;
drag and drop;
upload;
backend protegido;
OpenAI Vision;
resposta JSON estruturada;
painel de análise;
histórico inicial;
limite de uso;
segurança da API key.
```

---

## 32. Sugestão de commit

```text
refactor(core): migrate Friday to vision-first architecture
```