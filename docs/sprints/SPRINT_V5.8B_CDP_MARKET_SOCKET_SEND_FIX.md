# FRIDAY AI TRADER

# SPRINT V5.8B — CDP MARKET SOCKET SEND FIX

## Status

PLANEJADA

---

## 1. Objetivo

Corrigir exclusivamente a falha real de envio do `subscribeMessage` pela seleção programática da Friday.

A validação real da Sprint V5.8A retornou:

```text
accepted: false
subscribe_sent: false
bootstrap_sent: false
error_code: SUBSCRIBE_MESSAGE_SEND_FAILED
A sessão Polarium estava operacional:

websocket_state: ONLINE
authenticated: true
connection_status: ONLINE
feed_status: READY

Portanto, a falha está no caminho utilizado para escrever no Market WebSocket real através do CDP.

2. Evidência real

Request:

{
  "active_id": 76,
  "raw_size": 300
}

Resultado:

SUBSCRIBE_MESSAGE_SEND_FAILED

O mesmo ocorreu para:

active_id=2270
raw_size=300

Nenhum bootstrap foi iniciado porque o subscribe falhou antes.

3. Objetivo técnico

Auditar e corrigir o menor ponto possível entre:

POST /api/dev/select-market
↓
PolariumCDPLiveSource
↓
referência do Market WebSocket
↓
CDP Runtime.evaluate ou mecanismo existente
↓
WebSocket.send
↓
subscribeMessage

A correção deverá reutilizar o socket e o protocolo reais já observados.

4. Perguntas obrigatórias

Antes de modificar código, comprovar:

Onde a referência ao Market WebSocket é capturada?
Essa referência permite apenas leitura ou também escrita?
Em qual CDP target e execution context ela existe?
O envio ocorre no target principal da traderoom?
O objeto WebSocket ainda está em estado OPEN?
O payload gerado corresponde ao formato real observado?
O erro vem de:
ausência de socket;
socket fechado;
contexto errado;
exceção JavaScript;
payload inválido;
método send indisponível?
5. Instrumentação obrigatória

A resposta do endpoint e os logs devem distinguir:

MARKET_SOCKET_REFERENCE_MISSING
MARKET_SOCKET_NOT_OPEN
CDP_TARGET_NOT_FOUND
CDP_EXECUTION_CONTEXT_INVALID
RUNTIME_EVALUATE_FAILED
WEBSOCKET_SEND_EXCEPTION
SUBSCRIBE_PAYLOAD_INVALID
SUBSCRIBE_MESSAGE_SEND_FAILED

Não retornar apenas uma falha genérica quando a causa interna puder ser determinada.

Não expor tokens, cookies, SSID, headers ou credenciais.

6. Correção permitida

É permitido modificar somente:

endpoint dev de seleção;
PolariumCDPLiveSource;
componente responsável pelo socket CDP;
testes relacionados.

Aplicar o menor patch possível.

7. Fora de escopo

Não alterar:

Parser;
CandleStore;
Readiness;
HistoricalBootstrapManager;
BootstrapRequestFactory;
Chart API;
frontend;
Session Context funcional;
scanner;
ranking;
estratégia;
IA;
layout;
OAuth;
Browser Bridge;
extensão;
automação visual;
DOM click;
Selenium;
Playwright.
8. Regra arquitetural

Não criar um segundo WebSocket externo.

Não autenticar novamente.

Não copiar cookies ou tokens.

A seleção deve reutilizar a sessão e o Market WebSocket reais da aba autenticada da Polarium.

URL oficial:

https://trade.polariumbroker.com/traderoom
9. Testes obrigatórios

Adicionar testes para:

referência do socket ausente;
socket não aberto;
target CDP incorreto;
exceção em Runtime.evaluate;
WebSocket.send executado com sucesso;
payload real de subscribeMessage;
envio M1;
envio M5;
envio M15;
falha de subscribe impede bootstrap;
sucesso de subscribe permite bootstrap;
resposta sanitizada;
regressão inexistente no fluxo apenas de leitura.

Mocks não podem declarar sucesso sem comprovar que o caminho real de envio foi chamado.

10. Validação automatizada

Executar:

python -m pytest tests/market/providers/test_polarium_cdp_live_source.py -v
python -m pytest tests/market/providers -v
python -m pytest -v

Executar:

cd frontend
npm run build
11. Validação real

Com Polarium autenticada e Friday aberta:

curl -sS -X POST http://127.0.0.1:8000/api/dev/select-market \
  -H "Content-Type: application/json" \
  -d '{"active_id":76,"raw_size":300}' | python -m json.tool

Esperado:

accepted: true
subscribe_sent: true
bootstrap_sent: true
bootstrap_ready: true
chart_count > 0

Depois validar:

active_id=1857 raw_size=300
active_id=2270 raw_size=300

Sem clicar na interface da Polarium.

12. Critério de conclusão

A Sprint somente será concluída quando a validação real provar:

WebSocket.send executado
subscribeMessage aceito
get-first-candles enviado
bootstrap concluído
Chart API usando o bucket solicitado

Testes automatizados sozinhos não concluem esta Sprint.

13. Entrega obrigatória
objetivo;
arquitetura auditada;
causa raiz real do send failed;
arquivos modificados;
patch aplicado;
payload sanitizado utilizado;
testes adicionados;
resultados;
build;
comandos de validação real;
git status;
git diff;
riscos;
sugestão de commit.
14. Git

Não executar:

git add
git commit
git push

sem autorização explícita do Renan.

15. Sugestão de commit
fix(polarium): send programmatic subscription through live market socket