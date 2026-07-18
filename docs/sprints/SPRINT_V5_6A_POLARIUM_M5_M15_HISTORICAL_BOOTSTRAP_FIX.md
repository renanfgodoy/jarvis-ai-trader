# SPRINT V5.6A — POLARIUM M5/M15 HISTORICAL BOOTSTRAP FIX

## Objetivo

Corrigir o bootstrap histórico da Polarium para M5 e M15 sem alterar o fluxo M1 já funcional.

Sintoma real:

- M1 carrega histórico e readiness corretamente;
- M5 permanece em 0/50;
- uma nova vela M5 aparece somente a cada cinco minutos;
- portanto, realtime size=300 funciona;
- histórico size=300 não está entrando no Readiness.

Não alterar layout.

Não implementar scanner.

Não alterar estratégia.

Não fazer commit.

Não fazer push.

---

# DIAGNÓSTICO COMPROVADO

M5 atual:

```text
realtime candles-generated["300"]
→ funciona

Mas:

get-first-candles size=300
→ histórico
→ history_count

não funciona.

Não aceitar como solução esperar 50 velas realtime.

Realtime nunca deve substituir bootstrap histórico.

PARTE 1 — TROCA DE TIMEFRAME VISÍVEL

Auditar a sequência real:

M1 visible_raw_size=60
→ usuário troca para M5
→ visible_raw_size=300
→ novo contexto bootstrap

Confirmar:

visible_raw_size muda para 300;
visible_timeframe muda para M5;
o contexto active_id + 60 não é reutilizado;
o bootstrap M1 não impede o bootstrap M5;
o request pendente anterior é cancelado ou finalizado corretamente.

Registrar sanitizadamente:

active_id
previous_raw_size
new_raw_size
bootstrap_context_key
PARTE 2 — REQUEST M5

Confirmar que o request Friday para M5 contém:

{
  "name": "sendMessage",
  "request_id": "<único>",
  "msg": {
    "name": "get-first-candles",
    "body": {
      "active_id": "<ativo atual>",
      "size": 300
    }
  }
}

Comparar com o request PAGE_NATIVE real emitido ao trocar para M5.

Não assumir que o envelope M1 serve integralmente para M5 sem comparação.

Auditar possíveis campos adicionais observados:

count
to
from
only_closed
split_normalization

Não inventar campos.

PARTE 3 — REQUEST M15

Repetir a auditoria para:

size=900

Confirmar request independente e request_id próprio.

PARTE 4 — RESPOSTA HISTÓRICA

Para M5, registrar:

response name
request_id
available sizes
candles count size 300
matched active_id
matched raw_size

Para M15:

candles count size 900

Auditar formatos:

msg.candles_by_size["300"]
msg.candles_by_size[300]
msg.data["300"]
msg.candles["300"]
body/result/payload

Aceitar chave numérica ou string de forma explícita.

Não escolher automaticamente o primeiro size disponível.

PARTE 5 — CORRELAÇÃO

A chave oficial deve ser:

provider + active_id + raw_size

Garantir que:

resposta size=300 não seja correlacionada ao request size=60;
resposta size=900 não seja correlacionada ao request size=300;
ausência de size direto possa usar o request pendente correto;
só exista fallback por contexto quando houver exatamente um request pendente compatível.

Registrar:

pending_60
pending_300
pending_900
matched_60
matched_300
matched_900
unmatched_responses
PARTE 6 — PARSER

Para históricos M5 e M15:

time = from
open = open
high = max/high
low = min/low
close = close histórico real

Não usar msg.value como close de candles históricos fechados.

Ordenar por timestamp e deduplicar.

Validar alinhamento:

M5 timestamp % 300 == 0
M15 timestamp % 900 == 0

Se desalinhado:

DROP_INVALID_HISTORICAL_TIMESTAMP
PARTE 7 — READINESS

O Readiness Tracker deve manter contagens independentes:

active_id:60
active_id:300
active_id:900

Confirmar:

M1 READY não torna M5 READY;
M5 histórico incrementa somente history_count M5;
M15 histórico incrementa somente history_count M15;
realtime 300/900 não incrementa histórico;
troca de timeframe exibe a contagem do contexto visível correto.
PARTE 8 — CACHE E BLOQUEIO DE DUPLICIDADE

Auditar se o BootstrapManager considera apenas active_id e ignora raw_size.

A chave obrigatória deve incluir:

active_id + raw_size

Assim:

1857:60
1857:300
1857:900

são três bootstraps diferentes.

Não bloquear M5 porque M1 já foi solicitado ou concluído.

PARTE 9 — TESTES

Adicionar testes para:

M1 READY não bloqueia request M5;
troca 60 → 300 cria novo bootstrap;
troca 300 → 900 cria novo bootstrap;
request M5 usa size 300;
request M15 usa size 900;
resposta com chave string "300" é aceita;
resposta com chave numérica 300 é aceita;
parser seleciona somente size solicitado;
resposta M1 não preenche M5;
resposta M5 não preenche M15;
readiness M5 chega a 50;
readiness M15 chega a 50;
realtime M5 não incrementa history_count;
realtime M15 não incrementa history_count;
timestamps M5 são alinhados em 300s;
timestamps M15 são alinhados em 900s;
bootstrap não é bloqueado por contexto M1 existente;
troca rápida cancela request antigo corretamente.

Executar:

.venv/bin/python -m pytest -q tests/market/providers
.venv/bin/python -m pytest -q

Executar build somente se houver alteração frontend:

cd frontend
npm run build
cd ..
PARTE 10 — TESTE REAL

Executar:

Ativo OTC M1
→ confirmar READY

M1 → M5
→ confirmar request size=300
→ confirmar histórico recebido
→ sair de 0/50
→ chegar a READY

M5 → M15
→ confirmar request size=900
→ confirmar histórico recebido
→ sair de 0/50
→ chegar a READY

Não esperar cinco ou quinze minutos para validar bootstrap.

O histórico deve aparecer em segundos.

ENTREGA ESPERADA

Entregar:

causa raiz específica do M5;
causa raiz específica do M15;
valor de visible_raw_size na troca;
chave usada pelo BootstrapManager;
envelope PAGE_NATIVE M5;
envelope Friday M5;
envelope PAGE_NATIVE M15;
envelope Friday M15;
quantidade histórica recebida size 300;
quantidade histórica recebida size 900;
quantidade inserida;
history_count M5 antes/depois;
history_count M15 antes/depois;
correção aplicada;
arquivos modificados;
testes;
suíte completa;
build;
validação real;
git status;
git diff;
riscos;
sugestão de commit.

Não alterar o M1 funcional sem necessidade comprovada.

Não implementar scanner.

Não fazer commit.

Não fazer push.