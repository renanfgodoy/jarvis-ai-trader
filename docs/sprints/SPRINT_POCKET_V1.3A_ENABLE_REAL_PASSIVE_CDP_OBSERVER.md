# FRIDAY AI TRADER

# SPRINT POCKET V1.3A — ENABLE REAL PASSIVE CDP OBSERVER

## Status

CORREÇÃO DE ORQUESTRAÇÃO — CDP REAL PASSIVO — CONTA DEMO — ZERO ENVIO

---

## 1. Objetivo

Habilitar no CLI `tools.pocket_live_observation` o uso real do `PocketCDPClient` quando houver autorização explícita por flags seguras.

A execução atual permaneceu em:

```text
FAKE_CDP_ONLY

mesmo com:

POCKET_CDP_ENABLED=true
POCKET_CDP_OBSERVATION_ONLY=true
POCKET_READ_ONLY=true
POCKET_LIVE_CONNECTION_ENABLED=false

Portanto, a Sprint Pocket V1.3 ainda não foi validada em sessão real.

Esta Sprint deve corrigir somente a seleção do cliente e a inicialização do Chrome/CDP passivo.

2. Evidência real

Comando executado:

POCKET_CDP_ENABLED=true \
POCKET_CDP_OBSERVATION_ONLY=true \
POCKET_READ_ONLY=true \
POCKET_LIVE_CONNECTION_ENABLED=false \
.venv/bin/python -m tools.pocket_live_observation

Saída:

Pocket Live Observation
Modo automatizado atual: FAKE_CDP_ONLY
Validacao real exige autorizacao expressa do Renan e login DEMO manual.
target_found: True
market_socket_found: True
history_batches: 1
ticks: 1
observer_stopped_cleanly: True

Conclusão:

o CLI ignorou a configuração real;
usou FakePocketCDPClient;
não abriu Chrome dedicado;
não observou sessão Pocket real.
3. Regra principal

O comportamento padrão deve continuar seguro:

sem flags explícitas → FAKE_CDP_ONLY

O CDP real só poderá ser ativado quando todas estas condições forem verdadeiras:

POCKET_CDP_ENABLED=true
POCKET_CDP_OBSERVATION_ONLY=true
POCKET_READ_ONLY=true
POCKET_LIVE_CONNECTION_ENABLED=false
POCKET_REAL_OBSERVATION_AUTHORIZED=true

Se faltar qualquer condição:

FAKE_CDP_ONLY

ou erro controlado, conforme o contrato existente.

4. Fora de escopo absoluto

Não implementar:

login automático
preenchimento de senha
captura de cookie
captura de token
captura de SSID
captura de Authorization
Socket.IO independente
WebSocket independente
auth enviado
changeSymbol enviado
Runtime.evaluate
websocket.send
socket.emit
sio.emit
CALL
PUT
ordem
saldo
conta real
frontend Pocket
Chart API Pocket
IA
5. Arquivos permitidos

Alterar somente o mínimo necessário em:

tools/pocket_live_observation/
app/market/providers/pocket/cdp_client.py
app/market/providers/pocket/config.py
app/market/providers/pocket/target_manager.py
app/market/providers/pocket/cdp_observation_transport.py
tests/market/providers/pocket/

Não alterar:

Polarium
frontend
runtime principal da Friday
Chart API
CandleStore genérico
parser V1.1
runtime Pocket V1.2, exceto integração estritamente necessária
6. Configuração nova obrigatória

Adicionar:

pocket_real_observation_authorized = false

Variável de ambiente:

POCKET_REAL_OBSERVATION_AUTHORIZED=false

Default obrigatório:

false
7. Matriz de decisão

Implementar uma função central e testável:

resolve_pocket_observation_mode()

Resultados possíveis:

FAKE_CDP_ONLY
REAL_PASSIVE_CDP
BLOCKED_UNSAFE_CONFIGURATION
FAKE_CDP_ONLY

Quando:

POCKET_REAL_OBSERVATION_AUTHORIZED=false

ou qualquer flag essencial estiver ausente.

REAL_PASSIVE_CDP

Somente quando:

POCKET_CDP_ENABLED=true
POCKET_CDP_OBSERVATION_ONLY=true
POCKET_READ_ONLY=true
POCKET_LIVE_CONNECTION_ENABLED=false
POCKET_REAL_OBSERVATION_AUTHORIZED=true
BLOCKED_UNSAFE_CONFIGURATION

Quando houver combinação perigosa, por exemplo:

POCKET_LIVE_CONNECTION_ENABLED=true
POCKET_READ_ONLY=false
POCKET_CDP_OBSERVATION_ONLY=false

Retornar código:

POCKET_UNSAFE_OBSERVATION_CONFIGURATION
8. Chrome dedicado real

No modo REAL_PASSIVE_CDP, o CLI deverá iniciar Chrome dedicado com:

remote-debugging-port=9230
user-data-dir=.jarvis_private/chrome-pocket-profile

Abrir apenas a URL configurada:

pocket_trade_url

O Chrome deverá permanecer aberto para login manual.

Não navegar após o login.

Não abrir Friday automaticamente.

9. Seleção do executável Chrome no macOS

Suportar localização padrão:

/Applications/Google Chrome.app/Contents/MacOS/Google Chrome

Permitir configuração:

POCKET_CHROME_EXECUTABLE

Se não encontrado:

POCKET_CHROME_EXECUTABLE_NOT_FOUND
10. Startup do CLI real

Fluxo esperado:

resolver modo
→ validar segurança
→ iniciar Chrome dedicado
→ aguardar endpoint CDP 127.0.0.1:9230
→ listar targets
→ localizar aba Pocket
→ anexar PocketCDPClient
→ iniciar PocketCDPObservationTransport
→ aguardar login manual
→ observar frames
→ processar eventos
→ encerrar somente com Control + C

Não finalizar automaticamente após um evento fake.

11. Mensagens visíveis no Terminal

No modo real, exibir:

Pocket Live Observation
Modo: REAL_PASSIVE_CDP
Chrome dedicado: iniciando na porta 9230
Faça login manualmente na conta DEMO da Pocket.
Nenhuma mensagem será enviada pela Friday.
Pressione Control + C para encerrar.

Depois, conforme o estado:

Aguardando target Pocket...
Target Pocket encontrado.
Aguardando Market WebSocket...
Market WebSocket confirmado.
Observação read-only ativa.

Nunca exibir credenciais ou URLs sensíveis completas.

12. Status contínuo

Opcionalmente, imprimir resumo sanitizado a cada intervalo razoável:

target_found
sockets_observed
market_socket_found
history_batches
historical_candles
stream_events
ticks
contexts
buckets
readiness

Não imprimir a cada frame.

13. PocketCDPClient real

Implementar o cliente CDP real apenas para comandos passivos:

Network.enable
Target.getTargets
receber eventos
fechar conexão

Não implementar métodos genéricos de envio que possam ser usados para modificar a página.

Proibidos:

Runtime.evaluate
Input.*
Fetch.enable
Storage.*
Network.setCookie
Page.navigate após startup
14. Transporte passivo

O PocketCDPObservationTransport deverá funcionar com:

FakePocketCDPClient
PocketCDPClient real

sem caminhos duplicados de processamento.

O pipeline de sanitização e parsing deve ser idêntico.

15. Login manual

O CLI nunca deverá:

pedir e-mail
pedir senha
ler campo de login
inspecionar formulário
armazenar credenciais
automatizar autenticação

Apenas aguardar o usuário concluir manualmente.

16. Lifecycle real

O processo deve permanecer ativo enquanto:

Chrome aberto
target disponível
observer não cancelado

Em reload da Pocket:

revalidar target
reabilitar Network
redescobrir Market WebSocket
continuar observação

Em target fechado:

WAITING_TARGET

Sem encerrar imediatamente, salvo timeout configurado ou Control + C.

17. Encerramento

Ao pressionar:

Control + C

executar:

parar observer
fechar conexão CDP
cancelar tasks
limpar fila
salvar relatórios
registrar observer_stopped_cleanly=true

O Chrome dedicado poderá permanecer aberto ou ser fechado conforme configuração explícita:

pocket_close_browser_on_stop = false

Default:

false
18. Relatórios reais

Reutilizar:

.jarvis_cache/diagnostics/pocket_live_observation_report.json
.jarvis_cache/diagnostics/pocket_live_observation_report.txt
.jarvis_cache/diagnostics/pocket_socket_observation_report.json
.jarvis_cache/diagnostics/pocket_socket_observation_report.txt
.jarvis_cache/diagnostics/pocket_live_context_report.json
.jarvis_cache/diagnostics/pocket_live_context_report.txt

Adicionar:

observation_mode
real_observation_authorized
cdp_port
chrome_started
real_target_observed

Não incluir query string completa ou credenciais.

19. Testes obrigatórios
Matriz de configuração

Testar:

nenhuma flag → FAKE_CDP_ONLY
somente CDP_ENABLED → FAKE_CDP_ONLY
autorização sem read-only → BLOCKED
live connection true → BLOCKED
todas seguras → REAL_PASSIVE_CDP
Chrome launcher

Testar:

executável encontrado
executável ausente
comando contém porta 9230
comando contém profile privado
URL configurada
sem credenciais na linha de comando
CLI

Testar:

modo fake continua funcionando
modo real seleciona PocketCDPClient
modo real não usa FakePocketCDPClient
modo real permanece ativo
Control + C encerra limpo
CDP real com fake server

Usar servidor CDP local falso para testar:

/json/version
/json
websocket debugger URL
Network.enable
eventos WebSocket
reconnect

Não conectar à Pocket durante pytest.

Segurança

Comprovar ausência de:

Runtime.evaluate
websocket.send
socket.emit
sio.emit
sendMessage
cookies
Storage.getCookies
Fetch.enable
20. Validação automatizada

Executar:

cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

.venv/bin/python -m pytest tests/market/providers/pocket -v
.venv/bin/python -m pytest tests/tools/pocket_parser -v
.venv/bin/python -m pytest tests/tools/pocket_discovery -v
.venv/bin/python -m pytest -v

Build:

cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run build
21. Validação real

Somente após testes aprovados, executar com Renan presente:

cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

POCKET_CDP_ENABLED=true \
POCKET_CDP_OBSERVATION_ONLY=true \
POCKET_READ_ONLY=true \
POCKET_LIVE_CONNECTION_ENABLED=false \
POCKET_REAL_OBSERVATION_AUTHORIZED=true \
.venv/bin/python -m tools.pocket_live_observation

Esperado:

Modo: REAL_PASSIVE_CDP
Chrome dedicado abre
processo permanece ativo
login DEMO é manual
target Pocket é encontrado
Market WebSocket é confirmado
frames são observados
nenhuma mensagem é enviada
22. Critério de aceitação real

A Sprint termina somente quando a sessão real demonstrar:

observation_mode=REAL_PASSIVE_CDP
chrome_started=true
real_target_observed=true
market_socket_found=true
history_batches > 0
historical_candles > 0
stream_events > 0
ticks > 0
observer_stopped_cleanly=true

E:

sensitive_events_discarded >= 0
outbound_messages_originated_by_friday = 0
23. Fora de escopo

Não implementar:

Chart API Pocket
frontend Pocket
seleção pela Friday
Socket.IO próprio
auth automático
payout
saldo
ordens
CALL
PUT
IA
Strategy Engine
24. Git

Não executar:

git add
git commit
git push
git reset
git checkout
git restore
git clean
git stash

Não apagar arquivos Polarium.

Não adicionar perfil Chrome ao Git.

Confirmar ignorados:

.jarvis_private/
*.har
.jarvis_cache/
*chrome-pocket-profile*
25. Entrega obrigatória

Entregar:

causa da execução permanecer em FAKE_CDP_ONLY;
regra de seleção corrigida;
configuração nova;
matriz de segurança;
Chrome launcher;
PocketCDPClient real;
integração do transporte;
comportamento do CLI;
lifecycle;
cleanup;
relatórios;
arquivos criados;
arquivos modificados;
testes de configuração;
testes do launcher;
testes do CLI;
testes CDP local falso;
testes de segurança;
resultados Pocket;
suíte completa;
build;
procedimento real;
validação real ou pendência explícita;
git status;
git diff;
riscos;
lacunas;
decisão sobre V1.4;
próximos passos;
sugestão de commit.
26. Sugestão de commit
fix(pocket): enable explicitly authorized passive real CDP observation