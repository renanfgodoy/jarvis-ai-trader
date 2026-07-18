# FRIDAY AI TRADER

# SPRINT FRIDAY VISION V1.0 — SCREENSHOT MARKET ANALYSIS

## Status

IMPLEMENTAÇÃO DO PRIMEIRO FLUXO FUNCIONAL DE ANÁLISE DE GRÁFICOS POR IMAGEM

---

## 1. Objetivo

Criar o primeiro fluxo funcional da Friday Vision:

```text
usuário abre a página Friday Vision
→ cola, arrasta ou seleciona um print
→ informa ativo, timeframe e expiração
→ frontend envia a imagem ao backend
→ backend valida e protege a requisição
→ OpenAI analisa o gráfico
→ resultado estruturado retorna
→ frontend exibe a análise
```

Esta Sprint substitui definitivamente o fluxo broker-first como experiência principal da Friday.

---

## 2. Marco obrigatório

A Sprint somente poderá ser considerada concluída quando for validado:

```text
print real de gráfico
→ upload pelo frontend
→ backend Friday Vision
→ OpenAI API
→ resposta estruturada
→ painel visual da Friday
```

Não basta:

```text
mock;
fixture;
fake client;
teste unitário;
JSON estático;
placeholder;
simulação visual.
```

É obrigatória uma validação real com uma imagem enviada por Renan.

---

## 3. Princípio do sistema

A Friday será uma assistente de análise visual.

A Friday deverá:

```text
ler o que está visível na imagem;
identificar contexto;
identificar tendência aparente;
identificar estado de mercado;
avaliar risco;
avaliar qualidade do print;
descrever possíveis regiões;
responder de maneira estruturada;
poder recomendar aguardar ou não operar.
```

A Friday não deverá afirmar que prevê o mercado.

A Friday não deverá prometer acerto.

---

## 4. Decisões permitidas

O resultado poderá conter somente:

```text
CALL
PUT
WAIT
DO_NOT_TRADE
```

Definições:

```text
CALL:
contexto visual sugere possibilidade compradora, condicionado à confirmação descrita.

PUT:
contexto visual sugere possibilidade vendedora, condicionado à confirmação descrita.

WAIT:
há elementos relevantes, mas ainda não existe condição visual suficiente.

DO_NOT_TRADE:
imagem ruim, contexto confuso, risco extremo, mercado inadequado ou leitura insuficiente.
```

A IA não deverá ser forçada a escolher CALL ou PUT.

---

## 5. Limites da análise

Toda resposta deverá reconhecer que:

```text
a imagem representa apenas um momento;
o histórico visível pode ser limitado;
preços podem estar ilegíveis;
o próximo candle é desconhecido;
indicadores podem estar ocultos;
o contexto fora da tela não está disponível;
a análise não garante resultado.
```

---

## 6. Arquitetura alvo

```text
Vision.tsx
→ VisionUploader
→ VisionAnalysisForm
→ visionApi
→ POST /api/v1/vision/analyze
→ VisionRequestValidator
→ VisionImageProcessor
→ OpenAIVisionClient
→ VisionAnalysisService
→ VisionResultValidator
→ resposta JSON
→ VisionAnalysisPanel
```

---

## 7. Backend

Criar ou completar:

```text
app/vision/
  __init__.py
  enums.py
  models.py
  exceptions.py
  prompts.py
  validators.py
  image_processor.py
  service.py
  result_validator.py
  clients/
    __init__.py
    base.py
    openai_client.py
    fake_client.py
```

---

## 8. Rota principal

Criar:

```text
POST /api/v1/vision/analyze
```

Content-Type:

```text
multipart/form-data
```

Campos:

```text
image
asset
timeframe
expiration
strategy_mode
user_notes
```

Obrigatórios:

```text
image
timeframe
expiration
```

O ativo poderá ser:

```text
informado manualmente;
detectado visualmente;
desconhecido.
```

---

## 9. Rota de status

Atualizar:

```text
GET /api/v1/vision/status
```

Resposta esperada:

```json
{
  "enabled": true,
  "mode": "VISION_FIRST",
  "provider": "openai",
  "analysis_available": true,
  "allowed_formats": [
    "png",
    "jpg",
    "jpeg",
    "webp"
  ],
  "max_image_mb": 10,
  "require_auth": true
}
```

Não expor chave ou configuração sensível.

---

## 10. Configurações

Usar:

```text
FRIDAY_VISION_ENABLED=true
FRIDAY_VISION_PROVIDER=openai
FRIDAY_VISION_MODEL=
FRIDAY_VISION_MAX_IMAGE_MB=10
FRIDAY_VISION_ALLOWED_FORMATS=png,jpg,jpeg,webp
FRIDAY_VISION_ANALYSIS_TIMEOUT_SECONDS=60
FRIDAY_VISION_SAVE_IMAGES=false
FRIDAY_VISION_SAVE_HISTORY=true
FRIDAY_VISION_REQUIRE_AUTH=true
OPENAI_API_KEY=
```

Regras:

```text
OPENAI_API_KEY somente backend;
nenhum prefixo VITE_;
nenhuma chave no bundle;
nenhuma chave no localStorage;
nenhuma chave enviada ao navegador;
nenhuma chave nos logs;
nenhuma chave nos diagnósticos.
```

---

## 11. Cliente OpenAI

Criar:

```text
app/vision/clients/openai_client.py
```

Responsabilidades:

```text
receber bytes processados da imagem;
receber contexto manual;
enviar imagem à API;
solicitar resposta estruturada;
aplicar timeout;
traduzir erros;
não registrar base64;
não registrar chave;
não persistir imagem;
retornar objeto neutro.
```

Criar interface:

```text
VisionAIClient
```

Método sugerido:

```python
async def analyze(
    self,
    *,
    image_bytes: bytes,
    mime_type: str,
    context: VisionAnalysisRequest
) -> VisionAnalysisResult:
    ...
```

---

## 12. Cliente fake

Criar:

```text
app/vision/clients/fake_client.py
```

Finalidade:

```text
testes;
desenvolvimento local sem consumo;
validação do frontend;
falhas controladas.
```

O fake não poderá ser usado silenciosamente em produção.

Se provider for OpenAI e a chave estiver ausente:

```text
VISION_PROVIDER_NOT_CONFIGURED
```

Não fazer fallback automático para fake.

---

## 13. Processamento da imagem

Criar:

```text
app/vision/image_processor.py
```

Responsabilidades:

```text
validar assinatura real do arquivo;
validar formato;
validar tamanho;
corrigir orientação EXIF;
normalizar modo de cor;
reduzir imagem excessivamente grande;
preservar legibilidade do gráfico;
remover metadata EXIF;
gerar hash SHA-256;
não salvar por padrão.
```

Formatos permitidos:

```text
PNG
JPEG
WEBP
```

Não confiar apenas na extensão.

---

## 14. Limites de imagem

Default:

```text
máximo 10 MB;
mínimo 320x240;
máximo processado 2048 px no maior lado;
sem animação;
uma imagem por análise;
```

Erros:

```text
VISION_IMAGE_TOO_LARGE
VISION_IMAGE_TOO_SMALL
VISION_IMAGE_UNSUPPORTED
VISION_IMAGE_CORRUPTED
VISION_IMAGE_EMPTY
```

---

## 15. Validação de qualidade

Antes de chamar a IA, validar:

```text
imagem não vazia;
dimensão suficiente;
proporção razoável;
arquivo decodificável.
```

A IA também deverá avaliar:

```text
chart_visible;
candles_visible;
price_scale_visible;
timeframe_visible;
indicators_visible;
image_quality;
```

---

## 16. Modelo de requisição

Completar:

```text
VisionAnalysisRequest
```

Campos:

```text
asset: string | null
timeframe: string
expiration: string
strategy_mode: string
user_notes: string | null
image_hash: string
image_width: int
image_height: int
mime_type: string
```

Timeframes inicialmente permitidos:

```text
M1
M5
M15
```

Expirações inicialmente permitidas:

```text
1 minuto
5 minutos
15 minutos
```

---

## 17. Strategy mode

Permitir inicialmente:

```text
COMPLETE
PRICE_ACTION
SUPPORT_RESISTANCE
TREND
```

Default:

```text
COMPLETE
```

Nesta Sprint, todos poderão usar o mesmo prompt-base com pequenas instruções específicas.

---

## 18. Resultado estruturado

Completar:

```text
VisionAnalysisResult
```

Campos obrigatórios:

```text
analysis_id
decision
asset_detected
timeframe_detected
expiration_considered
trend
market_state
risk
confidence
image_quality
chart_visible
candles_visible
summary
market_reading
entry_condition
invalidation_condition
support_zones
resistance_zones
warnings
limitations
created_at
model
processing_time_ms
```

---

## 19. Enums

### VisionDecision

```text
CALL
PUT
WAIT
DO_NOT_TRADE
```

### VisionTrend

```text
BULLISH
BEARISH
SIDEWAYS
UNCLEAR
```

### VisionMarketState

```text
TRENDING
RANGING
BREAKOUT
REVERSAL_ATTEMPT
EXHAUSTION
CHOPPY
UNCLEAR
```

### VisionRiskLevel

```text
LOW
MEDIUM
HIGH
EXTREME
```

### VisionImageQuality

```text
GOOD
ACCEPTABLE
POOR
UNUSABLE
```

---

## 20. Confiança

`confidence` deverá variar entre:

```text
0 e 100
```

Ela representa:

```text
confiança na leitura visual;
não probabilidade de lucro;
não taxa de acerto;
não chance garantida da operação.
```

O frontend deverá deixar isso explícito.

---

## 21. Regras obrigatórias de decisão

A resposta deverá ser `DO_NOT_TRADE` quando:

```text
gráfico não estiver visível;
candles não estiverem visíveis;
imagem for ilegível;
timeframe necessário não estiver informado;
contexto visual for insuficiente;
houver conflito grave na leitura.
```

A resposta deverá tender a `WAIT` quando:

```text
preço estiver no meio de uma faixa;
movimento estiver esticado;
não houver confirmação;
houver lateralização;
suporte ou resistência estiverem muito próximos;
o candle atual ainda estiver indeciso.
```

CALL ou PUT somente poderão aparecer com:

```text
contexto;
condição de entrada;
condição de invalidação;
alertas;
nível de risco.
```

---

## 22. Prompt do sistema

Criar em:

```text
app/vision/prompts.py
```

O prompt deverá instruir a IA a atuar como analisador visual conservador de gráfico.

Regras obrigatórias:

```text
não inventar preços;
não inventar indicadores;
não inventar ativo;
não inventar timeframe;
não assumir contexto fora da imagem;
não prometer lucro;
não afirmar certeza;
preferir WAIT ou DO_NOT_TRADE em caso de dúvida;
distinguir confiança visual de chance de ganho;
considerar expiração informada;
descrever limitações;
responder apenas conforme schema.
```

---

## 23. Structured Output

A resposta do provedor deverá seguir JSON Schema estrito.

Não aceitar texto livre como resposta principal.

O backend deverá:

```text
validar schema;
validar enums;
validar confidence;
validar listas;
validar campos obrigatórios;
rejeitar resposta incompleta;
normalizar campos.
```

Erro:

```text
VISION_INVALID_PROVIDER_RESPONSE
```

---

## 24. Tratamento de recusa

Se o provedor não analisar ou recusar:

```text
decision = DO_NOT_TRADE
risk = EXTREME
confidence = 0
```

Mostrar mensagem apropriada, sem inventar análise.

---

## 25. Tratamento de erro

Mapear:

```text
VISION_DISABLED
VISION_AUTH_REQUIRED
VISION_IMAGE_TOO_LARGE
VISION_IMAGE_UNSUPPORTED
VISION_IMAGE_CORRUPTED
VISION_PROVIDER_NOT_CONFIGURED
VISION_PROVIDER_TIMEOUT
VISION_PROVIDER_RATE_LIMIT
VISION_PROVIDER_UNAVAILABLE
VISION_INVALID_PROVIDER_RESPONSE
VISION_INTERNAL_ERROR
```

Nunca devolver traceback ao frontend.

---

## 26. Rate limit

Criar controle inicial simples:

```text
máximo configurável por usuário;
bloqueio de clique duplicado;
uma análise simultânea por usuário;
cooldown curto;
resposta 429 quando excedido.
```

Configuração sugerida:

```text
FRIDAY_VISION_MAX_ANALYSES_PER_HOUR=30
FRIDAY_VISION_COOLDOWN_SECONDS=3
```

Não criar cobrança nesta Sprint.

---

## 27. Idempotência

Evitar que duplo clique gere duas análises.

Frontend deverá gerar:

```text
request_id
```

Backend deverá aceitar:

```text
X-Request-ID
```

Durante uma janela curta, o mesmo usuário e mesmo request ID não deverão consumir novamente.

---

## 28. Privacidade

Default:

```text
FRIDAY_VISION_SAVE_IMAGES=false
```

A imagem será:

```text
recebida;
validada;
processada em memória;
enviada ao provedor;
descartada.
```

Pode salvar:

```text
hash;
dimensões;
mime type;
resultado;
data;
usuário.
```

Não salvar o conteúdo da imagem por padrão.

---

## 29. Histórico inicial

Se `FRIDAY_VISION_SAVE_HISTORY=true`, salvar:

```text
analysis_id
user_id
image_hash
asset_informed
asset_detected
timeframe_informed
timeframe_detected
expiration
decision
trend
market_state
risk
confidence
summary
warnings
limitations
model
processing_time_ms
created_at
```

Não criar migração destrutiva.

Se ainda não houver banco adequado, criar repositório abstrato e implementação local compatível.

---

## 30. Endpoints de histórico

Criar:

```text
GET /api/v1/vision/history
GET /api/v1/vision/history/{analysis_id}
```

Parâmetros:

```text
limit
offset
decision
asset
```

Não retornar imagem.

---

## 31. Frontend principal

Substituir o placeholder de:

```text
frontend/src/pages/Vision.tsx
```

por uma tela funcional.

A página deverá conter:

```text
cabeçalho;
área de upload;
preview;
campos;
botão de análise;
estado de carregamento;
painel de resultado;
erros;
aviso de risco.
```

---

## 32. Upload de imagem

Criar componente:

```text
frontend/src/components/vision/VisionUploader.tsx
```

Permitir:

```text
clicar para selecionar;
arrastar e soltar;
colar com Command + V;
colar com Control + V;
remover imagem;
substituir imagem;
visualizar preview.
```

Não enviar imagem automaticamente.

---

## 33. Clipboard

A captura de clipboard deverá funcionar somente quando:

```text
o clipboard possuir imagem;
a página estiver ativa;
o usuário estiver na tela Friday Vision.
```

Não capturar texto.

Não interceptar colagem em inputs de texto.

Mostrar:

```text
Imagem colada com sucesso.
```

---

## 34. Preview

O preview deverá:

```text
usar object URL local;
revogar URL anterior;
mostrar dimensões;
mostrar tamanho;
permitir remover;
não converter em base64 permanente;
não armazenar no localStorage.
```

---

## 35. Formulário

Campos:

```text
Ativo
Timeframe
Expiração
Modo de análise
Observações
```

Ativo:

```text
opcional;
placeholder: EUR/USD OTC.
```

Timeframe:

```text
obrigatório;
M1 como default.
```

Expiração:

```text
obrigatória;
1 minuto como default.
```

Modo:

```text
COMPLETE como default.
```

---

## 36. Botão de análise

Texto normal:

```text
ANALISAR GRÁFICO
```

Durante processamento:

```text
FRIDAY ESTÁ ANALISANDO...
```

Desabilitar quando:

```text
não houver imagem;
formulário inválido;
análise em andamento;
cooldown ativo.
```

---

## 37. Painel de resultado

Criar:

```text
frontend/src/components/vision/VisionAnalysisPanel.tsx
```

Exibir em destaque:

```text
decisão;
confiança visual;
risco;
tendência;
estado de mercado.
```

Exibir também:

```text
resumo;
leitura do mercado;
condição de entrada;
condição de invalidação;
suportes;
resistências;
alertas;
limitações.
```

---

## 38. Representação visual

CALL:

```text
Possível cenário comprador
```

PUT:

```text
Possível cenário vendedor
```

WAIT:

```text
Aguardar confirmação
```

DO_NOT_TRADE:

```text
Não operar neste contexto
```

Não usar mensagens como:

```text
entrada garantida;
sinal certeiro;
chance de lucro;
operação segura.
```

---

## 39. Aviso fixo

Exibir abaixo da análise:

```text
A Friday realiza uma leitura visual do print enviado. A análise não garante resultado e não substitui sua gestão de risco.
```

---

## 40. Tipos frontend

Criar:

```text
frontend/src/types/vision.ts
```

Com tipos correspondentes ao backend.

Não duplicar enums em múltiplos arquivos.

---

## 41. API frontend

Criar:

```text
frontend/src/services/visionApi.ts
```

Responsabilidades:

```text
montar FormData;
adicionar request ID;
enviar arquivo;
cancelar requisição;
interpretar erros;
não reenviar automaticamente;
não armazenar imagem.
```

---

## 42. Cancelamento

Ao trocar de página ou iniciar uma nova análise:

```text
cancelar requisição anterior;
não aplicar resposta antiga;
não mostrar erro falso por abort.
```

Usar:

```text
AbortController
```

---

## 43. Estados frontend

Implementar:

```text
IDLE
IMAGE_READY
VALIDATING
ANALYZING
SUCCESS
ERROR
COOLDOWN
```

---

## 44. Autenticação

Respeitar:

```text
FRIDAY_VISION_REQUIRE_AUTH=true
```

Se o projeto já possuir autenticação:

```text
usar usuário autenticado.
```

Se ainda não possuir fluxo funcional completo:

```text
implementar dependência de autenticação substituível;
não criar senha hardcoded;
não expor rota publicamente sem proteção de deploy.
```

---

## 45. Segurança do frontend

Confirmar:

```text
OPENAI_API_KEY ausente do bundle;
nenhuma chamada direta do browser à OpenAI;
nenhum base64 em logs;
nenhuma imagem em localStorage;
nenhuma imagem em sessionStorage;
nenhum segredo em VITE_*.
```

---

## 46. Diagnóstico

Criar:

```text
.jarvis_cache/diagnostics/friday_vision_v1_analysis.json
.jarvis_cache/diagnostics/friday_vision_v1_analysis.txt
```

Registrar somente dados sanitizados:

```text
request_id
analysis_id
image_hash_prefix
mime_type
image_width
image_height
provider
model
provider_called
provider_success
provider_latency_ms
decision
risk
confidence
history_saved
image_saved
error_code
```

Não registrar:

```text
imagem;
base64;
API key;
prompt completo;
resposta bruta sensível.
```

---

## 47. Testes backend

Criar testes para:

```text
status disponível;
análise desativada;
sem autenticação;
imagem vazia;
imagem grande;
formato inválido;
arquivo corrompido;
imagem pequena;
requisição válida;
fake client;
OpenAI client mockado;
timeout;
rate limit;
erro do provider;
resposta inválida;
schema válido;
confidence válido;
enums válidos;
imagem não salva;
histórico salvo;
request ID duplicado;
sem fallback para fake.
```

---

## 48. Testes frontend

Testar:

```text
render da página;
seleção de arquivo;
drag and drop;
clipboard;
preview;
remoção;
campos obrigatórios;
botão bloqueado;
loading;
sucesso;
erro;
cancelamento;
resultado CALL;
resultado PUT;
resultado WAIT;
resultado DO_NOT_TRADE;
aviso fixo;
ausência de chamadas chart antigas;
ausência de chamada direta à OpenAI.
```

---

## 49. Testes de segurança

Comprovar:

```text
API key não aparece no frontend;
API key não aparece no build;
imagem não aparece em logs;
imagem não é persistida;
broker runtime não inicia;
rotas broker continuam 410;
nenhuma conexão Pocket/Polarium;
nenhuma ordem;
nenhum WebSocket de broker.
```

---

## 50. Teste real obrigatório

Após mocks e testes automatizados:

# 🔴 VALIDAÇÃO REAL NECESSÁRIA

Renan deverá:

```text
configurar OPENAI_API_KEY no backend;
iniciar backend;
iniciar frontend;
abrir /vision;
colar um print real;
selecionar M1;
selecionar expiração;
clicar em ANALISAR GRÁFICO;
verificar o painel.
```

A validação deverá usar uma imagem real de gráfico.

---

## 51. Critérios da validação real

Confirmar:

```text
imagem aparece no preview;
upload funciona;
análise inicia;
backend chama OpenAI;
resposta retorna;
decisão é válida;
risco é válido;
confidence está entre 0 e 100;
resumo aparece;
condição de entrada aparece;
limitações aparecem;
imagem não é salva;
histórico é registrado;
nenhuma chave aparece no navegador.
```

---

## 52. Build

Executar:

```bash
cd frontend
npm run build
```

---

## 53. Suíte

Executar testes específicos.

Depois:

```bash
.venv/bin/python -m pytest -v
```

---

## 54. Critério de aprovação automatizada

A automação será aprovada quando:

```text
backend receber imagem;
imagem for validada;
fake client funcionar;
OpenAI client estiver implementado;
resposta estruturada for validada;
frontend aceitar upload/clipboard/drop;
frontend mostrar painel;
histórico funcionar;
testes passarem;
build passar;
segurança da chave estiver comprovada.
```

---

## 55. Critério de conclusão real

A Sprint somente será concluída quando:

```text
Renan enviar um print real;
OpenAI analisar o print;
Friday exibir a resposta;
resultado estiver legível e útil;
nenhum segredo estiver exposto;
nenhum componente broker for utilizado.
```

---

## 56. Fora de escopo

Não implementar:

```text
captura automática da tela;
análise contínua;
monitoramento da vela;
integração Pocket;
integração Polarium;
espelhamento de gráfico;
WebSocket;
CDP;
AutoTrade;
CALL ou PUT enviados à corretora;
notificações;
aplicativo móvel nativo;
pagamento;
planos;
multi-tenant completo.
```

---

## 57. Git

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

## 58. Entrega obrigatória

Entregar:

1. resumo executivo;
2. arquitetura implementada;
3. backend Vision;
4. rota de análise;
5. rota de status;
6. processamento de imagem;
7. validações;
8. modelos;
9. enums;
10. prompt;
11. JSON Schema;
12. cliente abstrato;
13. cliente OpenAI;
14. cliente fake;
15. tratamento de erros;
16. rate limit;
17. idempotência;
18. privacidade;
19. histórico;
20. endpoints de histórico;
21. tela Vision;
22. uploader;
23. clipboard;
24. drag and drop;
25. preview;
26. formulário;
27. API frontend;
28. estados;
29. painel;
30. avisos;
31. autenticação;
32. diagnóstico;
33. arquivos criados;
34. arquivos modificados;
35. testes backend;
36. testes frontend;
37. testes segurança;
38. testes regressão;
39. suíte completa;
40. build;
41. variáveis necessárias;
42. instrução de configuração;
43. validação real pendente;
44. riscos;
45. lacunas;
46. git status;
47. git diff;
48. confirmação de Git;
49. sugestão de commit;
50. próximos passos.

---

## 59. Sugestão de commit

```text
feat(vision): add screenshot market analysis workflow
```

---

## 60. Próxima Sprint

Após validação real:

```text
SPRINT FRIDAY VISION V1.1 — ANALYSIS QUALITY AND STRATEGY ENGINE
```

Objetivos futuros:

```text
melhorar prompt;
calibrar confiança;
comparar análises;
criar estratégia oficial;
avaliar qualidade das entradas;
adicionar feedback WIN/LOSS;
criar métricas;
ajustar a IA com dados reais.
```