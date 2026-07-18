# FRIDAY AI TRADER

# SPRINT V5.8D — HISTORICAL REQUEST SEQUENCE

## Status

PLANEJADA

---

## 1. Objetivo

Descobrir e reproduzir a sequência real de requisições históricas utilizada pela página autenticada da Polarium após a seleção de um ativo.

A seleção programática já consegue:

- enviar `subscribeMessage`;
- enviar `get-first-candles`;
- mudar o Session Context;
- receber realtime;
- alimentar o CandleStore.

Entretanto, `get-first-candles` entrega apenas um candle inicial. O histórico completo chega posteriormente em mensagens separadas do tipo `candles`.

Esta Sprint deverá identificar quais requisições de saída originam esses lotes e, somente após comprovação, reutilizar essa sequência no fluxo programático.

---

## 2. Evidência real comprovada

Para todos os ativos testados, `first-candles` trouxe:

```text
payload=1
parser=1
validation=1
written=1
Para EURUSD e USDBRL, depois chegaram mensagens:

response_message_type=candles
payload=11 ou 12
payload=100
payload=200

Esses lotes promoveram o histórico para READY.

Para XAUUSD e BTCUSD selecionados programaticamente, somente o primeiro candle foi recebido e o estado permaneceu:

history_count=1
readiness=LIMITED
3. Causa raiz atual

O fluxo programático reproduz apenas a etapa inicial:

subscribeMessage
→ get-first-candles

Ele ainda não reproduz a sequência completa de requisições históricas que gera os lotes posteriores do tipo candles.

Não assumir previamente o nome ou o formato das requisições faltantes.

A sequência deve ser capturada da sessão real.

4. Objetivo técnico

Capturar e correlacionar mensagens WebSocket de saída durante dois cenários:

Cenário manual
usuário seleciona ativo na interface da Polarium
→ histórico completo chega
Cenário programático
POST /api/dev/select-market
→ histórico permanece em 1 candle

Comparar ambas as sequências para identificar:

mensagens existentes somente no fluxo manual;
ordem das mensagens;
request_id;
name/event;
active_id;
raw_size;
count;
from/to;
offset;
paginação;
parâmetros temporais;
dependências entre requests.
5. Instrumentação permitida

Instrumentar somente mensagens WebSocket de saída relacionadas a mercado e histórico.

Registrar de forma sanitizada:

direção: outbound;
timestamp;
ordem;
request_id;
name;
active_id;
raw_size;
count;
from;
to;
offset;
campos estruturais não sensíveis;
origem:
PAGE_NATIVE;
FRIDAY_PROGRAMMATIC.

Não registrar:

cookies;
tokens;
SSID;
authorization;
headers;
credenciais;
payloads de autenticação;
payload bruto completo.
6. Relatórios

Gerar:

.jarvis_cache/diagnostics/historical_request_sequence.json
.jarvis_cache/diagnostics/historical_request_sequence.txt

O relatório deve comparar:

MANUAL FLOW
1. mensagem...
2. mensagem...
3. mensagem...

PROGRAMMATIC FLOW
1. mensagem...
2. mensagem...

MISSING IN PROGRAMMATIC FLOW
- mensagem...
- parâmetros...
- ordem...
7. Correção funcional

A Sprint pode implementar a sequência faltante somente se ela estiver comprovada pela captura real e puder ser reutilizada com segurança.

Não inventar parâmetros.

Não criar candles sintéticos.

Não marcar bootstrap como pronto apenas porque first-candles foi recebido.

A condição real de conclusão deve continuar sendo:

readiness == READY
history_count >= history_required

bootstrap_ready deve refletir essa condição real.

8. Fora de escopo

Não alterar:

Parser;
CandleStore;
validação temporal;
Readiness Tracker;
Chart API;
frontend visual;
scanner;
ranking;
estratégia;
IA;
execução;
OAuth;
Browser Bridge;
extensão;
automação por clique;
DOM;
Selenium;
Playwright.
9. Testes obrigatórios

Adicionar testes para:

first-candles unitário não significa READY;
bootstrap_ready=false quando history_count < history_required;
captura sanitizada da sequência outbound;
diferenciação entre PAGE_NATIVE e FRIDAY_PROGRAMMATIC;
comparação de sequências;
reprodução da sequência comprovada;
lotes de candles atualizando o histórico;
M1;
M5;
M15;
timeout quando os lotes históricos não chegam;
nenhuma regressão no realtime.

Mocks não podem inventar uma sequência diferente daquela comprovada na captura real.

10. Validação real
Fluxo manual
Limpar o relatório.
Selecionar EURUSD M5 pela interface da Polarium.
Aguardar READY.
Salvar a sequência outbound.
Fluxo programático

Executar:

curl -sS -X POST http://127.0.0.1:8000/api/dev/select-market \
  -H "Content-Type: application/json" \
  -d '{"active_id":1857,"raw_size":300}' | python -m json.tool

Comparar as mensagens enviadas.

Depois aplicar somente a sequência comprovada e repetir.

11. Critérios de aceitação

A Sprint somente será concluída quando:

a sequência histórica manual estiver documentada;
a divergência programática estiver comprovada;
bootstrap_ready não gerar falso positivo;
XAUUSD ou BTCUSD programático atingir:
history_count >= 50;
readiness=READY;
bootstrap_complete=true;
analysis_blocked=false;
nenhuma seleção manual do ativo for necessária.
12. Entrega obrigatória
objetivo;
arquitetura auditada;
sequência manual capturada;
sequência programática capturada;
diferença comprovada;
causa raiz;
arquivos criados;
arquivos modificados;
correção aplicada, se comprovada;
testes;
resultados;
build;
validação real;
git status;
git diff;
riscos;
próximos passos;
sugestão de commit.
13. Git

Não executar:

git add
git commit
git push

sem autorização explícita do Renan.

14. Sugestão de commit
fix(polarium): reproduce native historical request sequence