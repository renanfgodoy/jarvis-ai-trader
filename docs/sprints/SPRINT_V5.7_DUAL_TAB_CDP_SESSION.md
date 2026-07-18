# FRIDAY AI TRADER

## SPRINT V5.7 — DUAL-TAB CDP SESSION

### Status

PLANEJADA

---

## 1. Objetivo

Evoluir o inicializador CDP da Friday para utilizar o mesmo Chrome dedicado com duas abas:

1. Polarium autenticada;
2. Friday frontend local.

A aba da Polarium deverá permanecer aberta e operacional para manter:

- sessão autenticada;
- Market WebSocket;
- eventos reais de mercado;
- comunicação CDP;
- Runtime Guard;
- Parser;
- Market Router;
- CandleStore.

A Friday deverá ser aberta em uma segunda aba do mesmo Chrome dedicado, sem substituir ou fechar a aba da Polarium.

---

## 2. Contexto técnico

O fluxo oficial atual é:

```text
Chrome dedicado
↓
CDP
↓
Polarium autenticada
↓
Market WebSocket
↓
Runtime Guard
↓
Parser
↓
Market Router
↓
CandleStore
↓
Chart API
↓
Frontend

O backend é iniciado com:

POLARIUM_CDP_LIVE_ENABLED=true \
.venv/bin/uvicorn app.main:app \
--host 127.0.0.1 \
--port 8000

Configurações já existentes:

polarium_cdp_live_enabled
polarium_cdp_port
polarium_cdp_chrome_path
polarium_cdp_profile_dir
polarium_trade_url

O Chrome dedicado já utiliza um profile próprio e persistente.

3. Arquitetura desejada
Chrome dedicado
│
├── Aba 1 — Polarium
│   ├── login real
│   ├── sessão autenticada
│   ├── Market WebSocket
│   └── feed real de mercado
│
└── Aba 2 — Friday
    ├── frontend local
    ├── gráfico
    ├── Session Context
    └── controles futuros

As duas abas deverão utilizar:

mesmo processo do Chrome
mesmo profile_dir
mesma conexão CDP

A Friday não deverá tentar ler diretamente:

cookies da Polarium;
localStorage da Polarium;
sessionStorage da Polarium;
cache da Polarium;
tokens pelo frontend;
variáveis internas da página.

Toda integração deverá continuar passando pelo backend e pelo CDP.

4. Escopo permitido

Esta Sprint pode:

detectar targets existentes no Chrome via CDP;
identificar a aba da Polarium;
identificar se a aba Friday já está aberta;
criar uma nova aba para a Friday;
reutilizar uma aba Friday existente;
impedir abas duplicadas;
preservar a aba da Polarium;
adicionar configuração para URL do frontend;
adicionar logs estruturados;
adicionar testes do gerenciamento de targets;
abrir a Friday somente quando houver condição segura.
5. Fora de escopo

Não implementar:

seleção de ativo pela Friday;
scanner multiativos;
ranking de ativos;
estratégia;
CALL;
PUT;
IA;
backtest;
execução de ordens;
saldo;
portfólio;
OAuth novo;
Browser Bridge;
extensão de Chrome;
leitura direta de cookies;
alteração de layout;
alterações no parser histórico;
alterações no CandleStore;
alterações no Readiness;
alterações no bootstrap M1, M5 ou M15.
6. Regra de preservação da Polarium

A aba da Polarium nunca poderá ser:

substituída pela Friday;
fechada automaticamente;
recarregada sem necessidade;
reutilizada para navegar até localhost;
descartada após a abertura da Friday.

A aba da Polarium precisa permanecer operacional durante toda a sessão.

7. URL oficial da Friday

Adicionar uma configuração explícita para o frontend local.

Nome sugerido:

FRIDAY_FRONTEND_URL

Valor padrão sugerido:

http://127.0.0.1:5173

A configuração deverá seguir o padrão já utilizado em app/core/config.py.

8. Condição para abertura da Friday

A Friday não deve roubar o foco durante o login da Polarium.

A abertura deverá ocorrer apenas após uma condição segura já disponível na arquitetura.

Prioridade de sinais:

target da Polarium detectado;
conexão CDP estabelecida;
página da Polarium carregada;
Market WebSocket identificado ou runtime de mercado operacional.

O Forge deverá auditar o código existente e utilizar o sinal mais confiável já disponível.

Não criar um segundo sistema de autenticação ou um readiness paralelo.

9. Gerenciamento de targets CDP

Antes de abrir uma nova aba, consultar os targets do Chrome.

Identificação da Polarium:

URL contendo:
trade.polariumbroker.com

Identificação da Friday:

URL correspondente a:
FRIDAY_FRONTEND_URL

Comportamento obrigatório:

Friday não aberta
Polarium operacional
↓
frontend disponível
↓
abrir nova aba Friday
Friday já aberta
não criar outra aba
↓
reutilizar target existente
Polarium ainda em login
não ativar a Friday prematuramente
↓
preservar foco da Polarium
Frontend indisponível
registrar aviso
↓
não derrubar backend
↓
não fechar Chrome
↓
não fechar Polarium
↓
permitir nova tentativa controlada
10. Controle de tentativas

Não criar loop agressivo.

A tentativa de abertura da Friday deverá:

possuir intervalo controlado;
evitar chamadas repetidas em alta frequência;
ser idempotente;
parar quando a aba Friday for encontrada;
não criar múltiplas tasks concorrentes;
respeitar o encerramento do backend.
11. Logs obrigatórios

Adicionar logs claros e estruturados.

Exemplos:

[POLARIUM_CDP] Chrome dedicated instance started
[POLARIUM_CDP] Polarium target detected
[POLARIUM_CDP] Waiting for Polarium market session
[POLARIUM_CDP] Market WebSocket detected
[POLARIUM_CDP] Friday frontend available
[POLARIUM_CDP] Opening Friday tab
[POLARIUM_CDP] Friday tab opened successfully
[POLARIUM_CDP] Friday tab already exists
[POLARIUM_CDP] Friday frontend unavailable
[POLARIUM_CDP] Polarium tab preserved

Os logs não podem exibir:

cookies;
tokens;
senhas;
headers sensíveis;
payloads de autenticação.
12. Proteções obrigatórias

A implementação deverá garantir:

nenhuma extensão de Chrome;
nenhuma Browser Bridge;
nenhuma leitura direta de cookies;
nenhuma substituição da aba Polarium;
nenhuma regressão no Chrome dedicado atual;
nenhuma regressão no Market WebSocket;
nenhuma regressão no bootstrap histórico;
nenhuma regressão no M1;
nenhuma regressão no M5;
nenhuma regressão no M15;
nenhuma alteração no Session Context sem necessidade.
13. Testes obrigatórios

Adicionar testes automatizados para:

13.1 Abertura da Friday
abre a Friday quando a condição segura é atingida;
utiliza FRIDAY_FRONTEND_URL;
cria um novo target sem substituir a Polarium.
13.2 Preservação da Polarium
não fecha o target da Polarium;
não navega o target da Polarium para localhost;
mantém o target original após abrir a Friday.
13.3 Idempotência
não cria segunda aba quando a Friday já está aberta;
reutiliza target Friday existente;
chamadas repetidas continuam criando no máximo uma aba.
13.4 Login
não rouba o foco antes da condição segura;
não abre Friday prematuramente durante login.
13.5 Frontend indisponível
indisponibilidade do frontend não derruba o backend;
indisponibilidade não fecha a Polarium;
registra erro controlado;
permite retry controlado.
13.6 Regressão
testes Polarium existentes continuam passando;
M1 continua funcional;
M5 e M15 permanecem isolados;
realtime continua não incrementando histórico;
Runtime Guard continua funcional.
14. Validação automatizada

Executar:

cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate
python -m pytest tests/market/providers -v

Depois:

python -m pytest -v

Frontend:

cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run build
15. Validação real
Terminal 1 — Frontend

Iniciar primeiro o frontend:

cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run dev
Terminal 2 — Backend com CDP
cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

POLARIUM_CDP_LIVE_ENABLED=true \
FRIDAY_FRONTEND_URL=http://127.0.0.1:5173 \
.venv/bin/uvicorn app.main:app \
--host 127.0.0.1 \
--port 8000
16. Resultado real esperado
1. Chrome dedicado abre.
2. Polarium abre na primeira aba.
3. O usuário realiza login normalmente.
4. A Friday não rouba o foco durante o login.
5. O Market WebSocket é detectado.
6. A Friday abre em uma segunda aba.
7. A aba da Polarium continua aberta.
8. O Market WebSocket permanece ativo.
9. O gráfico da Friday continua recebendo dados reais.
10. M1 continua chegando a READY.
11. M5 e M15 continuam sem regressão.
12. Reinicializações não criam múltiplas abas Friday.
17. Critérios de aceitação

A Sprint somente poderá ser considerada concluída se:

Chrome dedicado continuar sendo iniciado pelo backend;
Polarium abrir e permitir login;
Friday abrir no mesmo Chrome dedicado;
Friday abrir em aba separada;
Polarium permanecer aberta;
nenhuma extensão for utilizada;
Market WebSocket permanecer conectado;
Friday não for duplicada;
testes automatizados passarem;
suíte completa passar;
build frontend passar;
validação real for comprovada.
18. Entrega obrigatória do Forge

O relatório final deverá conter:

Objetivo;
Arquitetura encontrada;
Arquitetura implementada;
Arquivos criados;
Arquivos modificados;
Causa raiz;
Correção aplicada;
Configurações adicionadas;
Testes adicionados;
Resultado dos testes específicos;
Resultado dos testes Polarium;
Resultado da suíte completa;
Resultado do build;
Procedimento de validação real;
git status --short;
git diff --stat;
resumo técnico do git diff;
riscos;
próximos passos;
sugestão de commit.
19. Restrições Git

Não executar:

git add
git commit
git push

Sem autorização explícita do Renan.

20. Sugestão de commit
feat(polarium): open Friday alongside authenticated CDP session
21. Próximo passo futuro

Somente após a validação real desta Sprint:

selecionar um ativo pela Friday
↓
enviar assinatura pelo runtime autenticado
↓
carregar bootstrap histórico
↓
receber realtime
↓
sem clicar visualmente no ativo na Polarium