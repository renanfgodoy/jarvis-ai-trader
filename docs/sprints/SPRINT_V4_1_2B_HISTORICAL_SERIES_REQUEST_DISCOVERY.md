# Friday Trade — Sprint V4.1.2B

# Historical Series Request Discovery

## Status

PLANNED

---

## Objetivo

Descobrir, usando a sessão Polarium autorizada e o Browser Bridge já existente, qual mensagem real solicita e retorna uma coleção histórica de vários candles para uma única série:

```text
active_id + raw_size
```

Esta Sprint também deve diagnosticar por que o evento real `first-candles` em formato `candles_by_size` é parseado, mas rejeitado pelo `MarketPipeline`.

Não implementar histórico por hipótese.

Não inventar requests.

Não fabricar candles.

---

## Evidência real confirmada

O diagnóstico V4.1.2A confirmou:

```text
first_candles_seen_main = 2
first_candles_relayed = 2
first_candles_received_backend = 2
first_candles_adapter_accepted = 2
first_candles_parsed = 38
first_candles_stored = 0
first_candles_last_error_code = PIPELINE_REJECTED
```

Estrutura real:

```text
event_name = first-candles
direction = server_to_client
candidate_collection_path = msg.candles_by_size
candidate_collection_length = 19
```

Top-level:

```text
request_id
name
msg
status
```

`msg` contém:

```text
candles_by_size
```

Os tamanhos observados incluem:

```text
1
5
10
15
30
60
120
300
600
900
1800
3600
7200
14400
28800
43200
86400
604800
2592000
```

Conclusão comprovada:

`candles_by_size` representa snapshot de vários tamanhos/timeframes e não uma coleção de 100 candles de M1.

---

## Objetivos técnicos

Responder:

1. Por que os 38 candles parseados foram rejeitados pelo MarketPipeline?
2. O Pipeline rejeita coleções com múltiplos `raw_size`?
3. Existe erro estrutural no `RouteResult`?
4. Existe candle sem `active_id`, timestamp ou campo obrigatório?
5. O `PipelineResult` considera o evento inteiro inválido por algum item?
6. Quantos itens válidos e inválidos existem em cada evento?
7. `candles_by_size` deve ser armazenado como snapshot multi-timeframe?
8. Qual mensagem client → server precede uma coleção histórica real?
9. Existe `get-first-candles` com parâmetros como:
   - active_id;
   - size;
   - count;
   - from;
   - to;
   - chunk_size?
10. Existe resposta correlacionada por `request_id` sem nome explícito?
11. Existe evento `candles`, `candles-generated` ou outro contrato com vários candles do mesmo tamanho?
12. Qual coleção real contém múltiplos timestamps para:
   ```text
   active_id=76 + raw_size=60
   ```

---

## Parte A — Diagnóstico do Pipeline

Revisar:

```text
app/market/events/parsers/first_candles.py
app/market/events/router.py
app/market/pipeline/
app/market/store/
app/market/browser_bridge.py
```

Adicionar diagnóstico sanitizado para o evento `first-candles`:

```text
parsed_count
valid_count
invalid_count
rejected_count
stored_count
ignored_count
updated_count
route_status
pipeline_success
pipeline_errors
distinct_active_ids
distinct_raw_sizes
```

Não expor OHLC ou payload bruto.

Determinar exatamente por que:

```text
parsed = 38
stored = 0
PIPELINE_REJECTED
```

Corrigir somente se a causa estiver comprovada e a correção não alterar regra de negócio indevidamente.

---

## Parte B — Descoberta do histórico real

Instrumentar de forma sanitizada mensagens client → server e server → client relacionadas a:

```text
get-first-candles
first-candles
candles
candles-generated
sendMessage
subscribeMessage
```

Registrar somente:

```text
direction
event_name
request_id presente ou ausente
top_level_keys
msg_keys
body_keys
active_id presente
size presente
count presente
from presente
to presente
collection_path
collection_length
distinct_timestamps
distinct_raw_sizes
```

Não registrar:

```text
OHLC
token
cookie
Authorization
bearer
SSID
headers
payload bruto
```

---

## Critério para histórico real

Uma resposta somente poderá ser classificada como histórico real de uma série se:

```text
distinct_active_ids = 1
distinct_raw_sizes = 1
distinct_timestamps >= 20
```

Preferencialmente:

```text
distinct_timestamps >= 100
```

Não classificar `candles_by_size` como histórico, pois possui múltiplos `raw_size`.

---

## Correlação request → response

Usar `request_id` sanitizado por hash curto ou contador interno, sem expor valor original.

Exemplo:

```text
request_ref = request-3
```

Documentar:

```text
client request-3
→ event_name
→ campos estruturais

server request-3
→ event_name
→ collection_length
→ distinct_timestamps
```

---

## Interação do operador

Para provocar requests reais durante a validação:

1. abrir Polarium;
2. trocar ativo;
3. trocar timeframe;
4. usar zoom no gráfico;
5. navegar para candles antigos;
6. alternar M1/M5;
7. recarregar a sala de operações.

A Sprint não deve clicar ou controlar a página automaticamente.

---

## Status sanitizado

Adicionar ao endpoint existente:

```text
historical_series_discovery
```

Com campos como:

```text
candidate_events_seen
candidate_requests_seen
candidate_responses_seen
last_request_event_name
last_response_event_name
last_collection_path
last_collection_length
last_distinct_timestamps
last_distinct_raw_sizes
last_distinct_active_ids
historical_series_confirmed
historical_series_event_name
historical_series_request_ref
last_error_code
```

---

## Não implementar

Não:

- enviar request inventado;
- criar get-first-candles manual;
- modificar mensagens da Polarium;
- criar histórico sintético;
- preencher até 100 artificialmente;
- criar banco;
- criar persistência;
- alterar frontend;
- alterar gráfico;
- criar IA;
- criar indicadores;
- executar ordens.

---

## Testes obrigatórios

Criar testes para:

1. `candles_by_size` reconhecido como snapshot multi-timeframe.
2. Coleção com múltiplos raw_size não classificada como histórico.
3. Coleção com um raw_size e 100 timestamps classificada como histórico.
4. Diagnóstico do Pipeline mostra motivo real da rejeição.
5. Contadores valid/invalid/stored corretos.
6. Correlação sanitizada por request.
7. Nenhum request_id bruto exposto.
8. Nenhum OHLC exposto.
9. Nenhuma chave sensível exposta.
10. Evento desconhecido não derruba diagnóstico.
11. Instrumentação não altera o WebSocket original.
12. Instrumentação não grava candles por conta própria.

---

## Validação real

Após implementação:

1. reiniciar backend;
2. recarregar extensão;
3. fechar abas antigas da Polarium;
4. abrir nova sessão;
5. trocar ativo e timeframe;
6. fazer zoom/pan na Polarium;
7. aguardar 30 segundos;
8. consultar:

```text
/api/v1/polarium/browser-bridge/status
```

9. copiar apenas:

```text
historical_diagnostic
historical_series_discovery
```

Não copiar `last_trace.event_received`.

---

## Testes e build

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

.venv/bin/python -m pytest -q tests/market tests/tools tests/frontend

.venv/bin/python -m pytest -q

cd frontend
npm run build
```

---

## Entrega obrigatória

1. Objetivo.
2. Causa exata do PIPELINE_REJECTED.
3. Quantidade válida/inválida.
4. Correção aplicada ou bloqueio.
5. Classificação real de candles_by_size.
6. Requests candidatos encontrados.
7. Responses candidatos encontrados.
8. Correlação request/response.
9. Evento de histórico real confirmado ou não.
10. Quantidade de timestamps da série.
11. Arquivos criados.
12. Arquivos modificados.
13. Instrumentação.
14. Testes.
15. Resultado dos testes específicos.
16. Resultado da suíte completa.
17. Resultado do build.
18. Como testar para o Renan.
19. Dados sanitizados que o Renan deve enviar.
20. Riscos conhecidos.
21. Próximo passo recomendado.
22. git status --short.
23. git diff --stat.
24. Sugestão de commit.

Mensagem sugerida:

```text
chore(market): discover real historical candle series flow
```

---

## Regra final

Não fazer commit.

Não fazer push.

Não chamar snapshot multi-timeframe de histórico.

Não implementar request sem evidência real.