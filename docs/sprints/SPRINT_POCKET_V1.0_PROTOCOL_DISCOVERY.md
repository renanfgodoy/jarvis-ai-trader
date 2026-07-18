# FRIDAY AI TRADER

# SPRINT POCKET V1.0 — PROTOCOL DISCOVERY

## Status

AUDITORIA TÉCNICA — SOMENTE LEITURA — SEM AUTOMAÇÃO DE OPERAÇÕES

---

## 1. Objetivo

Executar uma auditoria técnica completa dos dois arquivos HAR da Pocket Option fornecidos pelo Renan, com o objetivo de mapear o protocolo de mercado utilizado pela plataforma.

Arquivos HAR fornecidos:

```text
/mnt/data/pocketoption.com.har
/mnt/data/pocketoption.com(1).har

A Sprint deve identificar, documentar e testar passivamente:

Pocket Option
→ Socket.IO / WebSocket
→ autenticação da sessão
→ lista de ativos
→ troca de ativo
→ troca de timeframe
→ histórico de candles
→ atualização em tempo real
→ payout
→ tempo de expiração
→ dados necessários para análise

Esta Sprint não deve integrar a Pocket à Friday ainda.

O objetivo é descobrir se o protocolo da Pocket é tecnicamente mais simples, previsível e estável que o protocolo da Polarium.

2. Escopo obrigatório

Analisar integralmente os dois HARs.

Mapear:

conexões WebSocket;
conexões Socket.IO;
endpoints HTTP relevantes;
eventos enviados pelo navegador;
eventos recebidos pelo navegador;
formato das mensagens;
troca de ativo;
troca de timeframe;
histórico de candles;
ticks e atualizações em tempo real;
lista e estado dos ativos;
payout;
horário do servidor;
expiração;
heartbeat;
reconexão;
autenticação;
dependências de sessão;
dados sensíveis presentes no HAR;
viabilidade de um Pocket Market Adapter somente leitura.
3. Evidências já observadas

Os HARs aparentam conter um WebSocket principal semelhante a:

wss://api-us-south.po.market/socket.io/?EIO=4&transport=websocket

Eventos já observados preliminarmente:

changeSymbol
updateStream
updateCharts
updateHistoryNewFast
updateAssets
saveCharts

Exemplo preliminar observado:

42["changeSymbol",{"asset":"EURUSD_otc","period":300}]

Essas informações devem ser confirmadas diretamente nos HARs.

Não assumir que qualquer observação preliminar esteja correta sem validar os dados completos.

4. Regra principal

Esta Sprint é somente de descoberta.

Não implementar:

conexão viva com a Pocket;
login automatizado;
envio de mensagens;
troca programática de ativo;
execução CALL ou PUT;
leitura de saldo;
leitura de dados pessoais;
IA;
Strategy Engine;
AutoTrade;
Browser Bridge;
extensão;
Playwright;
Selenium;
clique automatizado;
integração com o frontend;
modificação do provider Polarium.

Não modificar a Friday funcional existente.

5. Segurança obrigatória

Os arquivos HAR podem conter:

cookies
tokens
SSID
authorization
bearer
session id
user id
account id
e-mail
saldo
credenciais temporárias

Nenhum desses dados poderá:

aparecer em relatórios;
ser impresso em testes;
ser salvo em cache;
ser adicionado ao Git;
ser utilizado para conexão;
ser reutilizado para autenticação;
ser enviado para qualquer servidor.

Todo conteúdo sensível deve ser sanitizado.

Valores sensíveis devem ser substituídos por:

[REDACTED]

A análise deve ser exclusivamente local e passiva.

6. Arquitetura da auditoria

Criar um módulo isolado:

tools/pocket_discovery/

Estrutura recomendada:

tools/pocket_discovery/
├── __init__.py
├── har_loader.py
├── socketio_parser.py
├── websocket_analyzer.py
├── http_analyzer.py
├── event_catalog.py
├── protocol_mapper.py
├── sanitizer.py
├── report_generator.py
└── models.py

Criar testes em:

tests/tools/pocket_discovery/

A ferramenta não deve depender do runtime principal da Friday.

7. Carregamento dos HARs

O analisador deverá receber caminhos explícitos:

/mnt/data/pocketoption.com.har
/mnt/data/pocketoption.com(1).har

Validar:

existência;
tamanho;
JSON válido;
estrutura log.entries;
quantidade de requests;
quantidade de conexões WebSocket;
frames enviados;
frames recebidos;
timestamps;
conteúdo compactado ou codificado.

Se um HAR estiver incompleto, registrar isso claramente.

8. Análise dos WebSockets

Catalogar cada conexão WebSocket encontrada.

Para cada conexão registrar:

host
path
query keys
transport
socket.io version
timestamp de abertura
timestamp de fechamento
frames enviados
frames recebidos
tipos de frame
eventos Socket.IO
heartbeat
erros
reconexões

Não registrar valores de query sensíveis.

Gerar uma classificação:

MARKET_SOCKET
ACCOUNT_SOCKET
CHAT_SOCKET
ANALYTICS_SOCKET
UNKNOWN_SOCKET

A classificação deve ser baseada em evidência.

9. Parser Socket.IO

Implementar parser passivo para frames como:

0
2
3
40
42[...]

Interpretar, quando aplicável:

Engine.IO open
ping
pong
Socket.IO connect
Socket.IO event
Socket.IO disconnect

Para mensagens 42[...], extrair:

event_name
payload_type
payload_keys
payload_size
direction
timestamp

Não persistir payload bruto sensível.

10. Catálogo de eventos

Criar um catálogo de eventos encontrados.

Para cada evento registrar:

event_name
direction
count
first_seen
last_seen
payload_shape
payload_keys
sample_sanitized
probable_responsibility
confidence

Eventos prioritários:

changeSymbol
updateStream
updateCharts
updateHistoryNewFast
updateAssets
saveCharts

Também catalogar todos os eventos desconhecidos.

11. Troca de ativo

Mapear completamente o evento responsável pela troca de ativo.

Responder:

Qual evento é enviado?
Qual campo representa o ativo?
Existe asset, symbol, pair ou ID numérico?
O ativo OTC possui padrão próprio?
Existe unsubscribe do ativo anterior?
Existe subscribe do ativo novo?
Qual resposta confirma a troca?
Qual evento começa a entregar dados do novo ativo?
O histórico é enviado automaticamente?
Existe race condition durante a troca?

Exemplo a confirmar:

{
  "asset": "EURUSD_otc",
  "period": 300
}
12. Timeframes

Identificar como os timeframes são representados.

Mapear pelo menos:

M1
M5
M15

Possíveis valores:

60
300
900

Confirmar:

campo utilizado;
unidade utilizada;
se o timeframe faz parte de changeSymbol;
se existe evento separado;
se a troca de timeframe recarrega histórico;
se ticks continuam independentes do timeframe;
se o gráfico monta candles localmente.
13. Histórico de candles

Investigar obrigatoriamente:

updateHistoryNewFast
updateCharts
saveCharts

Responder:

Qual evento contém histórico?
Quantos candles são enviados?
O formato é OHLC?
Existe volume?
O timestamp está em segundos ou milissegundos?
Os candles vêm ordenados?
Existe candle atual incompleto?
Existe paginação?
Existe limite configurável?
O histórico depende do ativo e timeframe?
O histórico é enviado em uma única mensagem?
O histórico chega automaticamente após changeSymbol?
Existe mensagem HTTP adicional?
Existe compressão ou encoding?

Mapear o shape de cada candle de forma sanitizada:

timestamp
open
high
low
close
volume
asset
period

Não inventar campos ausentes.

14. Atualização em tempo real

Investigar updateStream.

Responder:

O evento contém tick ou candle?
Qual campo contém o preço?
Qual campo contém o ativo?
Existe timestamp?
Qual a frequência média?
O evento traz múltiplos ativos?
O evento contém ativo OTC?
É possível montar candles localmente?
Existe sequência ou número incremental?
Há mensagens duplicadas?

Calcular, quando possível:

frames por segundo
intervalo médio
intervalo mínimo
intervalo máximo
ativos presentes
15. Lista de ativos

Investigar updateAssets e eventos relacionados.

Extrair de forma sanitizada:

symbol
display_name
market_type
OTC ou real
status aberto/fechado
payout
categoria
disponibilidade
identificador interno

Confirmar se é possível construir uma lista de ativos para a Friday sem clicar na Pocket.

16. Payout

Investigar se os HARs contêm:

payout
profit
return
percentage
percent
profitPercent

Responder:

Em qual evento aparece?
O payout é por ativo?
O payout muda em tempo real?
O payout depende da duração?
O payout é enviado junto com a lista de ativos?
É possível filtrar ativos por payout?

Não declarar suporte se não houver evidência.

17. Expiração e relógio

Investigar:

server time
expiration
duration
timer
countdown
close time
open time

Responder:

Existe relógio do servidor?
Existe diferença entre horário local e servidor?
A expiração é enviada pelo backend?
A duração é definida em segundos?
É possível sincronizar entrada na próxima vela?
Existe latência observável?
18. HTTP / Fetch / XHR

Catalogar endpoints HTTP relacionados a:

assets
candles
history
chart
quotes
session
profile
account
auth
payout

Para cada endpoint relevante registrar:

host
path sanitizado
method
status
content type
response shape
responsabilidade provável

Não registrar headers sensíveis.

Determinar se o histórico depende de HTTP ou apenas do WebSocket.

19. Comparação dos dois HARs

Comparar os HARs e responder:

eventos iguais
eventos novos
ativos diferentes
timeframes diferentes
quantidade de frames
mudanças de protocolo
mudanças de host
diferenças de histórico
diferenças de sessão

Gerar uma matriz comparativa.

20. Relatórios

Gerar relatórios em:

.jarvis_cache/diagnostics/pocket_discovery_report.json
.jarvis_cache/diagnostics/pocket_discovery_report.txt

Também gerar:

.jarvis_cache/diagnostics/pocket_event_catalog.json
.jarvis_cache/diagnostics/pocket_event_catalog.txt

E:

.jarvis_cache/diagnostics/pocket_protocol_map.md

Todos devem ser ignorados pelo Git.

21. Conteúdo do relatório principal

O relatório deve apresentar:

HARs analisados
quantidade total de requests
quantidade de WebSockets
socket principal
protocolo detectado
eventos enviados
eventos recebidos
evento de troca de ativo
representação do timeframe
evento de histórico
quantidade de candles históricos
evento de tempo real
evento de ativos
payout
expiração
heartbeat
reconexão
dados sensíveis encontrados
viabilidade do Pocket Adapter
riscos
lacunas
22. Mapa do protocolo

O pocket_protocol_map.md deve apresentar algo semelhante a:

LOGIN MANUAL
    ↓
Socket.IO connect
    ↓
sessão autenticada
    ↓
updateAssets
    ↓
changeSymbol(asset, period)
    ↓
updateHistoryNewFast
    ↓
updateCharts
    ↓
updateStream contínuo

Somente registrar etapas comprovadas.

Etapas não comprovadas devem ser marcadas:

NÃO COMPROVADO
23. Classificação de viabilidade

Ao final, classificar a Pocket para a Friday:

EXCELLENT
GOOD
LIMITED
NOT_RECOMMENDED

Avaliar separadamente:

detecção do ativo
troca de ativo
troca de timeframe
histórico
tempo real
lista de ativos
payout
expiração
estabilidade
complexidade
segurança
manutenção

Usar notas de 0 a 10.

24. Critério para avançar

A Pocket só poderá avançar para um PocketMarketAdapter se forem comprovados:

ativo identificável
timeframe identificável
histórico OHLC utilizável
tempo real utilizável
troca de ativo previsível
troca de timeframe previsível
protocolo legível
sem criptografia impeditiva

Critério recomendado:

nota técnica geral >= 7,5
25. Fora de escopo

Não implementar:

PocketMarketAdapter
Pocket login
Pocket live connection
Pocket WebSocket client
Pocket order execution
Pocket balance
Pocket account
CALL/PUT
IA
frontend Pocket
automação

Esta Sprint termina no relatório técnico.

26. Testes obrigatórios

Criar testes para:

carregamento dos dois HARs;
parser Engine.IO;
parser Socket.IO;
evento 42;
evento sem payload;
payload inválido;
sanitização;
detecção de token;
detecção de cookie;
catálogo de eventos;
classificação do socket principal;
detecção de changeSymbol;
detecção de period;
detecção de histórico;
detecção de stream;
geração dos relatórios;
comparação entre HARs;
ausência de dados sensíveis nos relatórios.
27. Comandos de execução

Executar a auditoria com:

cd /Users/renangodoy/Desktop/jarvis-ai-trader

source .venv/bin/activate

.venv/bin/python -m tools.pocket_discovery \
  --har "/mnt/data/pocketoption.com.har" \
  --har "/mnt/data/pocketoption.com(1).har"

Se necessário, criar:

tools/pocket_discovery/__main__.py
28. Validação automatizada

Executar testes específicos:

cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

.venv/bin/python -m pytest tests/tools/pocket_discovery -v

Executar suíte completa:

.venv/bin/python -m pytest -v

Executar build para garantir que a Friday não foi afetada:

cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run build
29. Git

Não executar:

git add
git commit
git push
git reset
git checkout
git restore
git clean
git stash

Não apagar arquivos da Polarium.

Não modificar arquivos da Polarium.

Não adicionar HARs ao Git.

Garantir no .gitignore:

*.har
.jarvis_cache/

Só alterar .gitignore se necessário.

30. Entrega obrigatória

Entregar:

objetivo;
arquitetura da auditoria;
HARs analisados;
quantidade de requests;
quantidade de sockets;
socket principal;
protocolo detectado;
catálogo de eventos;
evento de troca de ativo;
formato do ativo;
formato do timeframe;
evento de histórico;
formato dos candles;
quantidade histórica;
evento de tempo real;
formato dos ticks;
lista de ativos;
payout;
expiração;
autenticação sanitizada;
riscos de segurança;
comparação dos dois HARs;
mapa do protocolo;
nota por funcionalidade;
classificação final;
decisão de avançar ou não;
arquivos criados;
arquivos modificados;
testes;
resultados;
build;
git status;
git diff;
riscos;
lacunas;
próximos passos;
sugestão de commit.
31. Próxima Sprint possível

Somente se a Pocket for classificada como GOOD ou EXCELLENT, recomendar:

SPRINT POCKET V1.1 — OFFLINE PROTOCOL PARSER

Objetivo futuro:

frames sanitizados
→ parser
→ eventos de domínio
→ candles normalizados
→ CandleStore isolado

Ainda sem conexão real.

32. Sugestão de commit
chore(pocket): add passive HAR protocol discovery lab