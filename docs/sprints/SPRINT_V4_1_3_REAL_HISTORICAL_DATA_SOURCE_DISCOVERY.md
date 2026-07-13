# Friday Trade — Sprint V4.1.3

# Real Historical Data Source Discovery

## Status

PLANNED

---

## Objetivo

Descobrir qual fonte real utilizada pela página da Polarium entrega candles anteriores de uma única série:

```text
active_id + raw_size
```

A investigação não deve mais exigir exatamente 100 candles.

O objetivo passa a ser:

```text
carregar a maior quantidade real disponível
→ sem inventar candles
→ sem completar artificialmente
→ continuar atualizando com candle-generated
```

Uma fonte será considerada útil se entregar:

```text
1 active_id
1 raw_size
2 ou mais timestamps distintos
```

Classificação sugerida:

```text
2–19 candles   → histórico curto
20–99 candles  → histórico útil
100+ candles   → histórico amplo
```

---

## Evidências já confirmadas

### first-candles

Estrutura:

```text
msg.candles_by_size
```

Características:

- snapshot multi-timeframe;
- 19 raw sizes;
- candles sem active_id interno utilizável;
- não representa histórico de uma única série.

### candles-generated

Estrutura:

```text
msg.active_id
msg.candles.<raw_size>
```

Características:

- snapshot multi-timeframe do candle atual;
- não contém vários timestamps da mesma série;
- útil para atualizações correntes, não para bootstrap histórico.

### candle-generated

Características:

- evento incremental;
- atualiza candle aberto;
- acrescenta candle novo;
- não entrega histórico anterior.

---

## Hipóteses de fonte histórica

A página pode carregar candles anteriores por:

```text
WebSocket
Fetch
XMLHttpRequest
REST
RPC
GraphQL
requisição durante inicialização
requisição ao trocar ativo
requisição ao trocar timeframe
requisição ao fazer pan/zoom para a esquerda
dados embutidos no JavaScript inicial
cache local da aplicação
```

A Sprint deve investigar passivamente essas fontes.

Não assumir que o histórico vem pelo WebSocket.

---

## Fluxos a observar

### WebSocket

```text
client_to_server
server_to_client
```

### Fetch

```text
window.fetch
```

### XMLHttpRequest

```text
XMLHttpRequest.open
XMLHttpRequest.send
XMLHttpRequest response
```

### Outros

Somente documentar caso exista evidência real:

```text
GraphQL
RPC
REST
Service Worker
IndexedDB
LocalStorage
SessionStorage
```

Não extrair dados privados desnecessários.

---

## Regras de segurança

Nunca expor:

```text
token
cookie
Authorization
bearer
SSID
password
credentials
headers privados
request body bruto
response body bruto
HAR bruto
```

Registrar apenas metadados estruturais sanitizados.

A extensão não deve alterar requests ou responses.

A extensão não deve bloquear requests.

A extensão não deve reproduzir requests.

A extensão não deve controlar a página.

---

## Instrumentação passiva

Adicionar diagnóstico sanitizado para:

```text
historical_transport_discovery
```

Campos sugeridos:

```text
fetch_requests_seen
fetch_responses_seen
xhr_requests_seen
xhr_responses_seen
websocket_candidates_seen

last_transport
last_method
last_url_host
last_url_path_sanitized
last_status_code
last_content_type

candidate_collection_path
candidate_collection_type
candidate_collection_length

distinct_timestamps
distinct_raw_sizes
distinct_active_ids

historical_candidate_found
historical_quality
historical_transport
historical_request_ref
last_error_code
```

Não expor query strings privadas.

Não expor domínio completo caso contenha identificadores privados.

Pode expor apenas host conhecido da Polarium/Quadcode e caminho sanitizado.

---

## Catálogo de formatos

Criar catálogo limitado:

```text
historical_transport_shapes
```

Cada shape deve conter somente:

```text
shape_ref
transport
method
host
path_shape
content_type
top_level_type
top_level_keys
nested_array_paths
nested_object_paths
candidate_collection_path
candidate_collection_length
distinct_timestamps
distinct_raw_sizes
distinct_active_ids
occurrences
```

Nunca salvar valores OHLC.

Nunca salvar payload completo.

Limitar quantidade de shapes para evitar crescimento indefinido.

---

## Critério de histórico válido

Uma resposta será considerada histórico real quando:

```text
distinct_active_ids = 1
distinct_raw_sizes = 1
distinct_timestamps >= 2
```

Classificação:

```text
2–19 timestamps   = SHORT
20–99 timestamps  = USEFUL
100+ timestamps   = BROAD
```

Não exigir 100 candles.

Não descartar histórico real curto.

---

## Inspeção estrutural

A inspeção pode detectar:

```text
arrays
objetos indexados por timestamp
objetos indexados por candle id
listas aninhadas
strings JSON decodificáveis
```

Mas deve registrar somente:

```text
tipo
chaves
caminhos
quantidade
contagens distintas
```

Não registrar:

```text
open
high
low
close
volume
preço
saldo
dados de conta
```

---

## Interação manual durante validação

Renan deverá:

1. abrir a Polarium;
2. entrar manualmente em conta DEMO;
3. abrir ativo em M1;
4. aguardar carregamento;
5. trocar de ativo;
6. trocar para M5;
7. voltar para M1;
8. fazer zoom;
9. arrastar fortemente o gráfico para a esquerda;
10. aguardar carregamento de candles antigos;
11. atualizar a página;
12. repetir a navegação.

A extensão não deve automatizar essas ações.

---

## Diagnóstico do carregamento inicial

Registrar a ordem temporal sanitizada:

```text
page_bridge_installed_at
fetch_interceptor_installed_at
xhr_interceptor_installed_at
websocket_created_at
first_historical_candidate_at
```

Determinar se o histórico é carregado:

```text
antes do WebSocket
depois do WebSocket
durante troca de ativo
durante troca de timeframe
durante pan/zoom
```

---

## Resultado esperado

Ao final da validação real, o status deverá indicar algo como:

```json
{
  "historical_transport_discovery": {
    "historical_candidate_found": true,
    "historical_transport": "fetch",
    "candidate_collection_path": "data.candles",
    "candidate_collection_length": 58,
    "distinct_timestamps": 58,
    "distinct_raw_sizes": 1,
    "distinct_active_ids": 1,
    "historical_quality": "USEFUL"
  }
}
```

Esse exemplo é apenas de formato.

Não inventar o resultado.

---

## Não implementar nesta Sprint

Não:

- criar parser definitivo;
- enviar request capturado;
- reproduzir fetch/XHR;
- modificar request;
- modificar response;
- preencher CandleStore;
- criar histórico sintético;
- criar persistência;
- alterar frontend;
- alterar Chart API;
- alterar MarketPipeline;
- alterar CandleStore;
- criar IA;
- criar indicadores;
- executar ordens.

---

## Testes obrigatórios

Criar testes para:

1. interceptação passiva de fetch;
2. interceptação passiva de XHR;
3. preservação do comportamento original;
4. nenhuma modificação em request;
5. nenhuma modificação em response;
6. URL sanitizada;
7. query string sensível removida;
8. headers não expostos;
9. body bruto não exposto;
10. resposta com 2 timestamps classificada como SHORT;
11. resposta com 20 timestamps classificada como USEFUL;
12. resposta com 100 timestamps classificada como BROAD;
13. coleção multi-timeframe não classificada;
14. coleção multi-active não classificada;
15. catálogo limitado;
16. nenhum OHLC exposto;
17. nenhuma credencial exposta;
18. falha de parsing não derruba a página;
19. instrumentação não escreve no CandleStore;
20. instrumentação não envia requests extras.

---

## Validação real

Após implementação:

1. reiniciar backend;
2. recarregar extensão;
3. fechar abas antigas;
4. abrir nova aba Polarium;
5. executar as ações manuais;
6. aguardar 60 segundos;
7. consultar:

```text
http://127.0.0.1:8000/api/v1/polarium/browser-bridge/status
```

8. copiar somente:

```text
historical_transport_discovery
historical_transport_shapes
```

Não copiar:

```text
last_trace
payload bruto
response body
request body
headers
tokens
cookies
SSID
HAR
```

---

## Testes e build

Executar:

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
2. Transportes investigados.
3. Estrutura da instrumentação.
4. Requests Fetch observados.
5. Responses Fetch observadas.
6. Requests XHR observados.
7. Responses XHR observadas.
8. Candidatos WebSocket observados.
9. Fonte histórica confirmada ou não.
10. Transporte histórico confirmado.
11. Caminho da coleção.
12. Quantidade de candles encontrada.
13. Quantidade de timestamps.
14. Quantidade de raw sizes.
15. Quantidade de active IDs.
16. Qualidade do histórico.
17. Momento do carregamento.
18. Arquivos criados.
19. Arquivos modificados.
20. Testes criados.
21. Resultado dos testes específicos.
22. Resultado da suíte completa.
23. Resultado do build.
24. Como testar para o Renan.
25. Dados sanitizados que o Renan deve enviar.
26. Riscos conhecidos.
27. Próximo passo recomendado.
28. `git status --short`.
29. `git diff --stat`.
30. Sugestão de commit.

Mensagem sugerida:

```text
chore(market): discover real historical candle transport
```

---

## Regra final

Não fazer commit.

Não fazer push.

Não exigir exatamente 100 candles.

Aceitar qualquer quantidade real disponível.

Não inventar candles.

Não reproduzir requests.

A Sprint deve somente descobrir a verdadeira fonte do histórico.