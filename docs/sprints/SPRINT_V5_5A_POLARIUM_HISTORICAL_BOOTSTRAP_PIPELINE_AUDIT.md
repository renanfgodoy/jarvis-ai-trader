# SPRINT V5.5A — POLARIUM HISTORICAL BOOTSTRAP PIPELINE AUDIT

## Objetivo

Descobrir exatamente por que o histórico Polarium permanece travado em:

```text
0/50
```

mesmo quando:

- a Polarium está conectada;
- o ativo foi identificado;
- o timeframe foi identificado;
- o realtime está funcionando;
- existe pelo menos um candle atual no gráfico.

Esta Sprint é exclusivamente de auditoria e correção mínima do pipeline histórico.

Não alterar o layout.

Não implementar scanner.

Não implementar estratégia.

Não implementar IA.

Não criar candles sintéticos.

Não fazer commit.

Não fazer push.

---

# SINTOMA CONFIRMADO

Na Friday:

```text
Ativo: USDBRL-OTC
Timeframe: M1
Candles visuais: 1
Histórico: 0/50
Status: CARREGANDO HISTÓRICO
```

Isso comprova:

```text
candles-generated realtime
→ está chegando
```

Mas:

```text
get-first-candles
→ first-candles / candles
→ histórico
```

não está concluindo corretamente.

---

# PIPELINE A SER AUDITADO

Rastrear integralmente:

```text
visible_active_id
+
visible_raw_size
↓
bootstrap solicitado
↓
get-first-candles enviado
↓
request_id criado
↓
frame realmente enviado no MARKET_WEBSOCKET
↓
resposta recebida
↓
first-candles ou candles
↓
correlação com request_id
↓
parser
↓
normalização
↓
Market Router
↓
CandleStore
↓
Readiness Tracker
↓
history_count
↓
frontend 0/50
```

Não assumir onde está o erro.

---

# PARTE 1 — ESTADO INICIAL DO BOOTSTRAP

Para cada contexto visível:

```text
provider
active_id
symbol
raw_size
```

registrar sanitizadamente:

```text
bootstrap_state
bootstrap_requested_at
bootstrap_request_id
bootstrap_attempts
bootstrap_completed_at
bootstrap_error_code
```

Não registrar payload bruto.

---

# PARTE 2 — ENVIO DO GET-FIRST-CANDLES

Confirmar se a Friday realmente envia:

```text
sendMessage
→ get-first-candles
```

Registrar apenas:

```text
request_id
active_id
raw_size
count solicitado
market_socket_id sanitizado
sent_at
```

Responder:

1. O envelope foi construído?
2. Passou pelo Runtime Guard?
3. Foi enviado pelo CDP?
4. Foi enviado no WebSocket correto?
5. O socket estava aberto?
6. Houve erro de envio?
7. Foi enviado mais de uma vez desnecessariamente?

---

# PARTE 3 — CONTRATO REAL DO REQUEST

Auditar o envelope real observado na sessão e nos HARs.

Confirmar os campos necessários de:

```text
sendMessage -> get-first-candles
```

Possíveis campos a verificar:

```text
active_id
size
count
to
from
split_normalization
only_closed
```

Não inventar campos.

Comparar:

```text
PAGE_NATIVE get-first-candles
```

versus:

```text
FRIDAY_PROBE get-first-candles
```

Responder se o envelope Friday é equivalente ao envelope nativo necessário.

---

# PARTE 4 — REQUEST_ID E CORRELAÇÃO

Auditar:

- formato do request_id;
- armazenamento do request pendente;
- tempo de expiração;
- correlação da resposta;
- remoção do request depois da resposta;
- colisão de request_id;
- resposta sem request_id;
- resposta correlacionada pelo active_id.

Criar diagnóstico:

```text
pending_bootstrap_requests
matched_bootstrap_responses
unmatched_bootstrap_responses
expired_bootstrap_requests
```

---

# PARTE 5 — RESPOSTA DO SERVIDOR

Observar e contabilizar separadamente:

```text
first-candles
candles
```

Para cada resposta:

```text
name
request_id sanitizado
active_id, se presente
sizes disponíveis
quantidade por size
received_at
matched_context
```

Responder claramente:

```text
get-first-candles enviado: SIM/NÃO
resposta recebida: SIM/NÃO
tipo da resposta: first-candles/candles/outro
candles recebidos: N
```

---

# PARTE 6 — RUNTIME GUARD

Confirmar que inbound permite:

```text
first-candles
candles
```

Auditar se alguma resposta histórica está sendo descartada como:

```text
server_inbound_discarded
unknown_market_message
unmatched_response
invalid_payload
```

Registrar somente motivo sanitizado.

Não registrar OHLC completo em logs permanentes.

---

# PARTE 7 — PARSER HISTÓRICO

Auditar o parser de:

```text
first-candles
candles
```

Confirmar formatos reais possíveis:

```text
msg.candles
msg.candles_by_size
msg.data
payload direto
array de candles
objeto indexado por size
```

Não assumir apenas um formato.

Para o raw_size visível, confirmar:

```text
60
300
900
```

Mapeamento obrigatório:

```text
time = from
open = open
high = max ou high
low = min ou low
close = close real existente no histórico
```

No histórico fechado, não usar `msg.value` como close de todos os candles.

Se campo obrigatório faltar:

```text
DROP_INVALID_HISTORICAL_CANDLE
```

---

# PARTE 8 — NORMALIZAÇÃO E STORE

Para cada resposta histórica válida:

1. normalizar candles;
2. ordenar por timestamp;
3. remover timestamps duplicados;
4. filtrar somente o active_id correto;
5. filtrar somente o raw_size correto;
6. inserir no CandleStore compartilhado;
7. não misturar provider;
8. não misturar símbolo;
9. não substituir candles por série antiga.

Registrar:

```text
historical_received_count
historical_valid_count
historical_dropped_count
historical_inserted_count
historical_duplicate_count
```

---

# PARTE 9 — READINESS

Auditar por que:

```text
CandleStore visual count = 1
```

mas:

```text
history_count = 0
```

Confirmar se o Readiness Tracker conta somente candles marcados como históricos.

Verificar:

- o parser marca origem `HISTORICAL`;
- o adapter preserva origem;
- o tracker recebe os candles;
- timestamps únicos são registrados;
- o contexto usa active_id/raw_size corretos;
- o contador está lendo a mesma série do gráfico.

Não contar realtime como histórico.

---

# PARTE 10 — FRONTEND

Não alterar o layout.

Auditar apenas o contrato recebido pelo frontend:

```text
historyState
historyCount
historyRequired
historyProgress
bootstrapComplete
bootstrapError
```

Confirmar se o backend envia valores corretos e se o frontend apenas os exibe.

Não corrigir `0/50` artificialmente no frontend.

---

# PARTE 11 — DIAGNÓSTICO DEV TEMPORÁRIO

Adicionar status sanitizado e opcional, somente DEV:

```json
{
  "bootstrap": {
    "state": "BOOTSTRAPPING",
    "request_sent": true,
    "request_id_present": true,
    "response_received": false,
    "response_type": null,
    "received_count": 0,
    "valid_count": 0,
    "inserted_count": 0,
    "history_count": 0,
    "last_error": null
  }
}
```

Não mostrar isso na UI do operador.

---

# PARTE 12 — CORREÇÃO MÍNIMA

Somente após localizar o ponto exato, aplicar a menor correção necessária.

Possíveis classes de correção:

```text
REQUEST_NOT_SENT
WRONG_WEBSOCKET
WRONG_REQUEST_ENVELOPE
RESPONSE_DROPPED_BY_GUARD
UNMATCHED_REQUEST_ID
UNSUPPORTED_RESPONSE_SHAPE
PARSER_REJECTED
WRONG_ACTIVE_ID
WRONG_RAW_SIZE
STORE_NOT_UPDATED
READINESS_NOT_UPDATED
```

Não refatorar arquitetura inteira.

---

# PARTE 13 — TESTES AUTOMATIZADOS

Adicionar testes para:

1. bootstrap cria request pendente;
2. get-first-candles passa pelo guard;
3. request é enviado no market socket;
4. first-candles correlaciona pelo request_id;
5. candles correlaciona pelo request_id;
6. resposta sem request_id pode ser correlacionada com segurança quando o contrato permitir;
7. candles_by_size seleciona raw_size correto;
8. array histórico é normalizado;
9. timestamps são ordenados;
10. duplicados são removidos;
11. CandleStore recebe histórico;
12. readiness recebe timestamps históricos;
13. realtime não incrementa history_count;
14. history_count chega a 50;
15. bootstrap muda para READY;
16. resposta inválida não cria candle;
17. ativo diferente não recebe histórico;
18. timeframe diferente não recebe histórico;
19. bootstrap não repete enquanto já está pendente;
20. timeout gera erro sanitizado e permite retry controlado.

Executar:

```bash
.venv/bin/python -m pytest -q tests/market/providers
.venv/bin/python -m pytest -q tests/market/store tests/market/chart
.venv/bin/python -m pytest -q tests/frontend
.venv/bin/python -m pytest -q
```

Executar build somente se houver alteração frontend:

```bash
cd frontend
npm run build
cd ..
```

---

# PARTE 14 — TESTE REAL

Com sessão Polarium real:

1. abrir ativo OTC M1;
2. identificar active_id;
3. confirmar bootstrap request enviado;
4. aguardar resposta;
5. registrar quantidade recebida;
6. confirmar CandleStore preenchido;
7. confirmar progresso sair de 0/50;
8. confirmar READY quando atingir o mínimo;
9. aguardar candle realtime;
10. confirmar que histórico não duplica.

Resultado esperado:

```text
0/50
→ 50/50
→ PRONTO PARA ANÁLISE
```

Se a resposta tiver menos de 50 candles:

```text
N/50
→ HISTÓRICO INSUFICIENTE
```

Não fingir READY.

---

# ENTREGA ESPERADA

Entregar obrigatoriamente:

1. causa raiz comprovada;
2. get-first-candles foi enviado ou não;
3. envelope real usado;
4. WebSocket alvo;
5. request_id;
6. resposta recebida ou não;
7. tipo de resposta;
8. quantidade de candles recebidos;
9. quantidade válida;
10. quantidade inserida;
11. descartes e motivos;
12. history_count antes/depois;
13. estado final do bootstrap;
14. correção mínima aplicada;
15. arquivos modificados;
16. testes adicionados;
17. testes específicos;
18. suíte completa;
19. build;
20. validação real;
21. git status;
22. git diff;
23. riscos;
24. sugestão de commit.

Não implementar scanner.

Não implementar estratégia.

Não alterar layout.

Não fazer commit.

Não fazer push.