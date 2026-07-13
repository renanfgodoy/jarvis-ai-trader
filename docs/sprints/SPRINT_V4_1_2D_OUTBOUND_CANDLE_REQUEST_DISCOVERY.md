# Friday Trade — Sprint V4.1.2D

# Outbound Candle Request Discovery

## Status

PLANNED

---

## Objetivo

Descobrir a estrutura sanitizada das mensagens `client_to_server` utilizadas pela Polarium para solicitar candles, especialmente mensagens com:

```text
sendMessage
get-first-candles
subscribeMessage
```

O objetivo é identificar, sem inventar ou enviar requests, se a plataforma realiza alguma solicitação capaz de retornar vários candles históricos para uma única série:

```text
active_id + raw_size
```

Esta Sprint é exclusivamente investigativa.

Não enviar mensagens à Polarium.

Não alterar mensagens existentes.

Não criar parser definitivo.

Não criar histórico.

---

## Evidências reais confirmadas

### first-candles

Estrutura:

```text
msg.candles_by_size
```

Características:

```text
19 itens
19 raw_size distintos
active_id ausente nos candles normalizados
```

Classificação:

```text
snapshot multi-timeframe
```

Não é histórico de uma série.

### candles-generated

Estrutura:

```text
msg.active_id
msg.at
msg.ask
msg.bid
msg.value
msg.phase
msg.candles
```

Dentro de:

```text
msg.candles
```

existem objetos indexados por tamanho:

```text
msg.candles.1
msg.candles.5
msg.candles.10
msg.candles.15
msg.candles.30
msg.candles.60
msg.candles.300
msg.candles.900
...
```

Classificação:

```text
snapshot/atualização multi-timeframe do ativo atual
```

Não é histórico com múltiplos timestamps de um único timeframe.

### Requests observados

Na validação real:

```text
candidate_requests_seen = 370
candidate_responses_seen = 42
last_request_event_name = sendMessage
last_response_event_name = candles-generated
```

A estrutura dos requests `sendMessage` ainda não foi identificada.

---

## Objetivos técnicos

Responder com evidência sanitizada:

1. Qual é a estrutura top-level de `sendMessage`?
2. Quais são as chaves de `msg`?
3. Existe campo interno `name`?
4. Existe campo interno `body`?
5. Existe:
   - `active_id`;
   - `size`;
   - `count`;
   - `from`;
   - `to`;
   - `offset`;
   - `limit`;
   - `chunk_size`;
   - `request_id`;
   - `version`;
   - `filters`?
6. Qual request precede:
   - `first-candles`;
   - `candles-generated`;
   - `candle-generated`?
7. Existe request cujo nome sugere:
   - get-candles;
   - get-first-candles;
   - candles-history;
   - get-candles-history;
   - load-more;
   - request-candles;
   - chart-history?
8. Existe resposta com múltiplos timestamps para um único tamanho?
9. Fazer pan/zoom para a esquerda provoca request diferente?
10. A troca de timeframe provoca request com `size` específico?
11. A troca de ativo provoca request com `active_id` específico?
12. Existe campo numérico que represente quantidade de candles?

---

## Instrumentação sanitizada de requests

Adicionar seção ao status:

```text
outbound_candle_request_diagnostic
```

Campos permitidos:

```text
seen_main
relayed
event_name
inner_event_name
direction
top_level_type
top_level_keys
msg_type
msg_keys
body_type
body_keys

has_active_id
has_size
has_count
has_from
has_to
has_limit
has_offset
has_chunk_size

numeric_field_names
string_field_names
array_paths
object_paths

request_ref
correlated_response_event_name
correlated_response_collection_path
correlated_response_collection_length
correlated_response_distinct_timestamps
received_at
last_error_code
```

Nunca expor os valores de:

```text
request_id
active_id
token
cookie
Authorization
bearer
SSID
headers
```

Nesta Sprint, pode informar apenas presença de `active_id`, não seu valor.

Para campos potencialmente relevantes como `size`, `count`, `limit`, `from` e `to`, inicialmente registrar somente:

```text
presente ou ausente
tipo do campo
```

Não registrar valor até revisão posterior.

---

## Catálogo sanitizado

Manter catálogo limitado dos formatos de requests observados.

Cada formato deve ser identificado por fingerprint estrutural:

```text
request_shape_1
request_shape_2
request_shape_3
```

Para cada shape:

```text
occurrences
inner_event_name
top_level_keys
msg_keys
body_keys
has_active_id
has_size
has_count
has_from
has_to
has_limit
has_offset
correlated_response_event_names
```

Limitar quantidade de shapes para evitar crescimento ilimitado.

Não armazenar payload bruto.

---

## Correlação temporal

Correlacionar passivamente:

```text
client request_ref
→ resposta server_to_client com request_ref correspondente
```

Quando não houver `request_id` correspondente, usar janela temporal curta apenas como:

```text
temporal_candidate
```

Não afirmar correlação definitiva sem request_id.

Classificações:

```text
CONFIRMED_BY_REQUEST_ID
TEMPORAL_CANDIDATE
UNRELATED
```

---

## Interação manual necessária

Durante validação real, Renan deverá:

1. abrir Polarium;
2. selecionar ativo em M1;
3. aguardar;
4. trocar para M5;
5. voltar para M1;
6. trocar de ativo;
7. fazer zoom;
8. arrastar o gráfico fortemente para a esquerda;
9. clicar em qualquer recurso nativo de mostrar histórico, caso exista;
10. aguardar entre cada ação.

A extensão não deve controlar a página.

---

## Critério para request histórico candidato

Um request será candidato se possuir pelo menos dois destes elementos:

```text
active_id
size
from
to
count
limit
offset
```

E se for seguido por uma resposta contendo:

```text
distinct_active_ids = 1
distinct_raw_sizes = 1
distinct_timestamps >= 20
```

---

## Diagnóstico de candles-generated

Corrigir apenas a leitura estrutural do diagnóstico para reconhecer:

```text
msg.candles
```

como mapa indexado por `raw_size`.

Apenas para fins diagnósticos:

```text
candidate_collection_path = msg.candles
candidate_collection_type = object_indexed_by_raw_size
candidate_collection_length = quantidade de chaves
distinct_raw_sizes = quantidade de chaves numéricas
distinct_active_ids = 1 quando msg.active_id existir
```

Não transformar isso em histórico.

Não enviar ao Store por conta própria.

---

## Não implementar

Não:

- enviar request;
- reproduzir request capturado;
- criar parser histórico;
- alterar MarketPipeline;
- alterar CandleStore;
- alterar frontend;
- criar histórico sintético;
- usar API externa;
- criar WebSocket;
- modificar a Polarium;
- executar ordens;
- criar IA ou indicadores.

---

## Testes obrigatórios

Criar testes para:

1. reconhecimento estrutural de `sendMessage`;
2. detecção de inner event name;
3. fingerprint de request sem valores;
4. request com active_id e size;
5. request com from/to;
6. request com count/limit;
7. catálogo com limite de shapes;
8. correlação por request_ref;
9. correlação temporal marcada apenas como candidata;
10. request_id bruto não exposto;
11. active_id bruto não exposto;
12. nenhuma credencial exposta;
13. `msg.candles` reconhecido como mapa por raw_size;
14. mapa multi-timeframe não classificado como histórico;
15. instrumentação não modifica frames;
16. instrumentação não envia requests.

---

## Validação real

Após implementação:

1. reiniciar backend;
2. recarregar extensão;
3. fechar abas antigas;
4. abrir nova aba Polarium;
5. executar a sequência manual de ativo/timeframe/zoom/pan;
6. aguardar 60 segundos;
7. consultar:

```text
/api/v1/polarium/browser-bridge/status
```

8. copiar somente:

```text
outbound_candle_request_diagnostic
outbound_request_shapes
historical_series_discovery
candles_generated_diagnostic
```

Não copiar payload bruto.

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
2. Estrutura sanitizada de sendMessage.
3. Inner event names encontrados.
4. Request shapes encontrados.
5. Campos estruturais presentes.
6. Requests com active_id/size.
7. Requests com from/to/count/limit.
8. Correlações request/response.
9. Request histórico candidato confirmado ou não.
10. Correção diagnóstica de msg.candles.
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
chore(market): inspect outbound candle request flow
```

---

## Regra final

Não fazer commit.

Não fazer push.

Não enviar nem reproduzir requests.

A Sprint deve apenas revelar os formatos reais das mensagens que a própria Polarium já envia.