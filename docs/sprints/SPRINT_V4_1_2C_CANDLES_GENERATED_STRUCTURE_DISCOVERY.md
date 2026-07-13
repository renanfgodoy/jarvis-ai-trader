# Friday Trade — Sprint V4.1.2C

# Candles-Generated Structure Discovery

## Status

PLANNED

---

## Objetivo

Descobrir a estrutura real e sanitizada do evento:

```text
candles-generated
```

observado na sessão autorizada da Polarium.

O objetivo é determinar se esse evento contém uma coleção histórica de múltiplos candles para uma única série:

```text
active_id + raw_size
```

Não implementar parser por hipótese.

Não modificar MarketPipeline.

Não modificar CandleStore.

Não criar candles.

---

## Evidência real existente

A Sprint V4.1.2B confirmou:

```text
candidate_requests_seen = 653
candidate_responses_seen = 37
last_request_event_name = sendMessage
last_response_event_name = candles-generated
```

Porém:

```text
last_collection_path = null
last_collection_length = null
last_distinct_timestamps = 0
last_distinct_raw_sizes = 0
last_distinct_active_ids = 0
historical_series_confirmed = false
```

Isso significa que o evento `candles-generated` existe, mas sua estrutura interna ainda não foi reconhecida.

---

## Objetivos técnicos

Responder com evidência sanitizada:

1. Qual é o tipo top-level de `candles-generated`?
2. Quais são suas chaves top-level?
3. Qual é o tipo de `msg`?
4. Quais são as chaves de `msg`?
5. Existe `body`?
6. Existe array em:
   - `msg`;
   - `msg.body`;
   - `msg.candles`;
   - `msg.data`;
   - `data`;
   - `params`;
   - outro caminho?
7. A coleção é:
   - array de candles;
   - objeto indexado por timestamp;
   - objeto indexado por size;
   - mapa por active_id;
   - string JSON;
   - lista aninhada?
8. Quantos itens existem?
9. Quantos timestamps distintos existem?
10. Quantos raw_size distintos existem?
11. Quantos active_id distintos existem?
12. Existe correlação por request_id?
13. Qual request client → server precede o evento?
14. A resposta representa histórico de uma única série?

---

## Critério de histórico real

Somente classificar como histórico real se:

```text
distinct_active_ids = 1
distinct_raw_sizes = 1
distinct_timestamps >= 20
```

Preferência:

```text
distinct_timestamps >= 100
```

---

## Instrumentação sanitizada

Adicionar seção específica:

```text
candles_generated_diagnostic
```

Com:

```text
seen_main
relayed
received_backend
top_level_type
top_level_keys
msg_type
msg_keys
body_type
body_keys
nested_array_paths
nested_object_paths
candidate_collection_path
candidate_collection_type
candidate_collection_length
distinct_timestamps
distinct_raw_sizes
distinct_active_ids
request_ref
direction
received_at
last_error_code
```

Nunca expor:

- OHLC;
- preços;
- payload bruto;
- request_id bruto;
- token;
- cookie;
- Authorization;
- bearer;
- SSID;
- headers.

---

## Descoberta recursiva controlada

Implementar inspeção estrutural recursiva somente para metadados:

- profundidade máxima limitada;
- registrar caminhos de arrays;
- registrar caminhos de objetos;
- registrar comprimento de arrays;
- registrar chaves;
- nunca registrar valores;
- nunca serializar candles completos.

Exemplo permitido:

```text
msg.body.result.candles
type = array
length = 120
```

Exemplo proibido:

```json
{
  "open": 1.1234,
  "close": 1.1250
}
```

---

## Correlação request/response

Usar `request_ref` sanitizado.

Responder:

```text
request-N
→ client event_name
→ structural keys

request-N
→ server candles-generated
→ collection path
→ collection length
```

Não expor request_id real.

---

## Não implementar nesta Sprint

Não:

- criar parser definitivo;
- alterar Payload Adapter;
- alterar MarketPipeline;
- alterar CandleStore;
- enviar request;
- modificar WebSocket;
- criar histórico;
- criar persistência;
- alterar frontend;
- alterar gráfico;
- criar IA;
- criar indicadores;
- executar ordens.

---

## Testes obrigatórios

Criar testes para:

1. descoberta de array aninhado;
2. descoberta de objeto indexado;
3. limite de profundidade;
4. nenhum valor OHLC exposto;
5. nenhum request_id bruto exposto;
6. nenhuma chave sensível exposta;
7. correlação sanitizada;
8. coleção de uma série com 100 timestamps;
9. coleção multi-timeframe não confirmada como histórico;
10. evento desconhecido não derruba diagnóstico.

---

## Validação real

Após implementação:

1. reiniciar backend;
2. recarregar extensão;
3. fechar abas antigas;
4. abrir nova aba Polarium;
5. trocar ativo;
6. trocar timeframe;
7. fazer zoom/pan;
8. aguardar 30 segundos;
9. consultar:

```text
/api/v1/polarium/browser-bridge/status
```

10. copiar somente:

```text
candles_generated_diagnostic
historical_series_discovery
```

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
2. Estrutura sanitizada real de candles-generated.
3. Caminhos de arrays encontrados.
4. Caminhos de objetos encontrados.
5. Caminho candidato da coleção.
6. Quantidade de itens.
7. Quantidade de timestamps.
8. Quantidade de raw_size.
9. Quantidade de active_id.
10. Correlação request/response.
11. Histórico real confirmado ou não.
12. Arquivos criados.
13. Arquivos modificados.
14. Instrumentação.
15. Testes.
16. Resultado dos testes específicos.
17. Resultado da suíte completa.
18. Resultado do build.
19. Como testar para o Renan.
20. Dados sanitizados que o Renan deve enviar.
21. Riscos conhecidos.
22. Próximo passo recomendado.
23. git status --short.
24. git diff --stat.
25. Sugestão de commit.

Mensagem sugerida:

```text
chore(market): inspect candles-generated structure
```

---

## Regra final

Não fazer commit.

Não fazer push.

Não criar parser por hipótese.

A Sprint deve apenas revelar a estrutura real e sanitizada de `candles-generated`.