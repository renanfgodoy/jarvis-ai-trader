# FRIDAY AI TRADER

# SPRINT V5.9B — EXACT GET-CANDLES ENVELOPE

## Status

PLANEJADA

---

## 1. Objetivo

Capturar e reproduzir exatamente o envelope nativo de:

```text
sendMessage → get-candles

utilizado pela página autenticada da Polarium.

A Sprint também deverá impedir que o fluxo programático possua dois proprietários concorrentes enviando get-first-candles.

Não inventar campos ou parâmetros.

2. Evidência real comprovada

A Sprint V5.9A enviou:

subscribeMessage → candles-generated
sendMessage → get-first-candles
sendMessage → get-first-candles
sendMessage → get-candles
sendMessage → get-candles
sendMessage → get-candles

Todos os requests foram enviados com sucesso pelo WebSocket real.

Entretanto:

history_count = 1
readiness = LIMITED
bootstrap_complete = false

Nenhum dos três get-candles recebeu resposta.

Isso comprova que:

active_id + size

não são suficientes para formar o request nativo completo.

3. Concorrência comprovada

O relatório mostrou dois requests de bootstrap distintos para o mesmo ativo e timeframe:

friday_native_get_first_candles_...
friday_get_first_candles_...

O primeiro pertence ao NativeHistoricalBootstrapOrchestrator.

O segundo pertence ao bootstrap automático já existente no runtime.

A Sprint deverá identificar os dois pontos emissores e garantir que uma seleção programática tenha apenas um proprietário de bootstrap.

Não remover o bootstrap automático do fluxo manual.

4. Objetivo técnico principal

Capturar a estrutura sanitizada completa dos frames outbound nativos relacionados a:

get-first-candles
get-candles

Registrar todos os níveis estruturais relevantes:

top-level keys
nested keys
name
msg.name
body keys
data keys
params keys
request_id
active_id
size
count
from
to
offset
index
timestamp
start
end

Também registrar tipos dos valores:

string
integer
float
boolean
list
dict
null

Não registrar payload bruto completo.

5. Captura nativa obrigatória

Durante uma seleção manual que atinja READY, capturar cada get-candles enviado pela página.

Para cada request, gerar uma representação sanitizada semelhante a:

{
  "name": "sendMessage",
  "request_id": "186",
  "inner_name": "get-candles",
  "payload_path": "msg.body",
  "shape": {
    "active_id": "integer",
    "size": "integer",
    "from": "integer",
    "to": "integer",
    "count": "integer"
  },
  "safe_values": {
    "active_id": 76,
    "size": 300,
    "from": 1783927200,
    "to": 1783986900,
    "count": 200
  }
}

Os nomes e campos acima são apenas exemplo.

A implementação deve registrar somente o que realmente existir no frame nativo.

6. Comparação obrigatória

Gerar comparação entre:

PAGE_NATIVE get-candles
FRIDAY_PROGRAMMATIC get-candles

Informar:

missing keys
different nesting
different value types
different field values
different message name
different request envelope
7. Relatório

Gerar:

.jarvis_cache/diagnostics/get_candles_envelope_report.json
.jarvis_cache/diagnostics/get_candles_envelope_report.txt

O relatório TXT deve possuir:

NATIVE ENVELOPE
PROGRAMMATIC ENVELOPE
STRUCTURAL DIFFERENCES
MISSING FIELDS
DUPLICATE BOOTSTRAP OWNERS
8. Correção permitida

Somente após a captura comprovar o envelope exato:

ajustar a factory do get-candles programático;
reproduzir exatamente o nesting e os campos nativos;
impedir bootstrap automático duplicado durante uma seleção programática;
preservar integralmente o bootstrap manual já funcional.

Não inventar paginação.

Não deduzir parâmetros sem evidência.

9. Propriedade do bootstrap

Durante:

POST /api/dev/select-market

o NativeHistoricalBootstrapOrchestrator deverá ser o único proprietário do bootstrap solicitado.

O bootstrap automático do runtime não deverá emitir outro get-first-candles para a mesma chave:

(active_id, raw_size)

enquanto a seleção programática estiver ativa.

A proteção deve ser:

isolada
temporária
idempotente
por active_id + raw_size

Não bloquear bootstrap de outros ativos ou timeframes.

10. Fora de escopo

Não alterar:

Parser;
CandleStore;
validação temporal;
Readiness Tracker;
Chart API;
frontend;
Strategy Engine;
scanner;
ranking;
IA;
OAuth;
Browser Bridge;
extensão;
DOM;
clique visual;
Selenium;
Playwright.
11. Testes obrigatórios

Adicionar testes para:

extração de campos em diferentes níveis aninhados;
tipos dos campos preservados;
sanitização de dados sensíveis;
comparação de envelope nativo e programático;
detecção de campos ausentes;
apenas um get-first-candles por seleção programática;
fluxo manual continua usando bootstrap automático;
XAUUSD M5;
BTCUSD M5;
M1;
M15;
timeout quando get-candles não recebe resposta;
READY somente após history_count >= history_required.

Mocks não podem declarar resposta de get-candles sem representar o envelope nativo capturado.

12. Validação automatizada

Executar:

python -m pytest tests/market/providers -v
python -m pytest -v

Depois:

cd frontend
npm run build
13. Validação real
Etapa 1 — captura manual
Limpar os relatórios.
Selecionar manualmente EURUSD M5.
Aguardar READY.
Ler:
get_candles_envelope_report.txt
Etapa 2 — seleção programática

Sem clicar em XAUUSD:

curl -sS -X POST http://127.0.0.1:8000/api/dev/select-market \
  -H "Content-Type: application/json" \
  -d '{"active_id":1857,"raw_size":300}' | python -m json.tool

Esperado após a correção:

accepted = true
subscribe_sent = true
bootstrap_sent = true
bootstrap_ready = true
history_count >= 50
history_state = READY
bootstrap_complete = true
analysis_blocked = false

Depois repetir com BTCUSD.

14. Critério de conclusão

A Sprint somente será concluída quando:

o envelope nativo estiver documentado;
as diferenças estiverem comprovadas;
o programático reproduzir o mesmo envelope;
não existir bootstrap duplicado;
pelo menos XAUUSD ou BTCUSD atingir READY sem clique manual.
15. Entrega obrigatória
objetivo;
envelope nativo capturado;
envelope programático anterior;
diferenças estruturais;
causa raiz;
proprietários duplicados identificados;
arquivos criados;
arquivos modificados;
correção aplicada;
testes;
resultados;
build;
validação real;
git status;
git diff;
riscos;
sugestão de commit.
16. Git

Não executar:

git add
git commit
git push

sem autorização explícita do Renan.

17. Sugestão de commit
fix(polarium): reproduce exact native get-candles envelope