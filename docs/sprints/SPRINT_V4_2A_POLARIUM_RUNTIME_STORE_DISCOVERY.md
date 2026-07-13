# Friday Trade — Sprint V4.2A

# Polarium Runtime Store Discovery

## Status

PLANNED

---

## Objetivo

Executar uma inspeção estrutural passiva dentro da aba autenticada da Polarium para descobrir onde a própria interface mantém os candles já renderizados.

Esta Sprint não deve buscar histórico novamente no repositório.

A investigação deve ocorrer no runtime real da página, no contexto MAIN world, usando somente leitura e metadados sanitizados.

O objetivo é localizar qualquer estrutura que contenha:

```text
1 active_id
1 raw_size
2 ou mais timestamps
```

Não exigir 100 candles.

Aceitar qualquer quantidade real disponível.

---

## Hipótese atual

A interface da Polarium exibe histórico visual, mas esse histórico ainda não foi encontrado nos eventos WebSocket já analisados.

Possíveis locais:

```text
window globals
React fiber
Redux store
MobX store
Zustand store
Context
chart engine
datafeed
cache de séries
cache de candles
worker
canvas engine
IndexedDB
localStorage
sessionStorage
```

A Sprint deve comprovar ou descartar essas hipóteses.

---

## Regras absolutas de segurança

Nunca:

- modificar objetos da página;
- alterar store;
- despachar actions;
- chamar métodos de escrita;
- controlar o gráfico;
- clicar;
- enviar requests;
- reproduzir requests;
- abrir WebSocket;
- copiar payload completo;
- serializar preços;
- expor OHLC;
- expor token;
- expor cookie;
- expor Authorization;
- expor bearer;
- expor SSID;
- expor headers;
- expor credenciais;
- expor dados de conta;
- expor saldo;
- expor ordens;
- expor posições.

Somente leitura estrutural e contagens.

---

## Arquitetura

Reutilizar a extensão existente:

```text
tools/polarium-browser-bridge/
```

Criar uma camada diagnóstica MAIN world que:

1. enumere candidatos seguros;
2. classifique tipo;
3. registre apenas chaves e contagens;
4. identifique estruturas compatíveis com candles;
5. envie somente metadados sanitizados ao backend;
6. exponha o resultado em status read-only.

Não criar nova extensão.

Não criar outro endpoint paralelo se o status atual puder ser ampliado.

---

## Fontes a investigar

### Window globals

Inspecionar nomes relacionados a:

```text
chart
charts
candle
candles
bar
bars
history
series
datafeed
market
price
ohlc
active
asset
store
cache
redux
mobx
zustand
tradingview
lightweight
quadcode
```

Não registrar valores dos objetos.

Registrar somente:

```text
nome sanitizado
tipo
quantidade de chaves
nomes de chaves permitidos
presença de campos candidatos
```

---

## React

Investigar passivamente:

```text
__reactFiber
__reactProps
__reactContainer
React root
```

Somente metadados estruturais.

Não percorrer indefinidamente.

Aplicar:

```text
profundidade máxima
limite de nós
timeout
```

Detectar nomes de props/state relacionados a:

```text
candles
bars
series
history
active_id
size
timeframe
```

Nunca registrar valores OHLC.

---

## Redux

Procurar apenas evidência de:

```text
store
getState
subscribe
dispatch
```

Se encontrar `getState`, permitir somente leitura de estrutura sanitizada:

```text
top-level slice names
quantidade de slices
caminhos candidatos
contagens de arrays/objetos
```

Não chamar `dispatch`.

Não registrar estado completo.

---

## MobX / Zustand / Outros Stores

Detectar apenas por estrutura:

```text
getState
toJS
observable
subscribe
store
state
```

Não executar métodos de escrita.

Somente inspecionar nomes de campos e contagens.

---

## Chart engines e datafeeds

Procurar candidatos com:

```text
setData
update
datafeed
getBars
subscribeBars
series
candles
bars
history
```

Não chamar métodos.

Registrar somente:

```text
nome sanitizado
métodos presentes
quantidade de séries
quantidade de itens quando passivamente acessível
```

---

## Canvas e DOM

Investigar apenas metadados:

```text
canvas elements
iframe elements
shadow roots
data attributes
component roots
```

Não ler pixels.

Não usar OCR.

Não capturar conteúdo visual.

---

## Web Workers

Identificar presença de:

```text
Worker
SharedWorker
service worker
```

Não interceptar mensagens privadas nesta Sprint.

Somente registrar presença e nomes sanitizados quando disponíveis.

---

## Storage local

Investigar:

```text
IndexedDB
localStorage
sessionStorage
```

Somente:

```text
nomes sanitizados de bancos
nomes de stores
quantidade de registros
chaves estruturais
```

Não ler valores completos.

Não registrar dados sensíveis.

Se houver qualquer risco de segredo, interromper aquela fonte.

---

## Critério de candidato histórico

Uma estrutura será candidata quando houver evidência de:

```text
distinct_active_ids = 1
distinct_raw_sizes = 1
distinct_timestamps >= 2
```

Ou, quando os valores não puderem ser lidos por segurança, quando houver:

```text
caminho estrutural compatível
coleção com 2 ou mais itens
campos estruturais de candle
```

Classificação:

```text
SHORT  = 2–19
USEFUL = 20–99
BROAD  = 100+
```

---

## Status sanitizado

Adicionar seção:

```text
runtime_store_discovery
```

Campos sugeridos:

```text
scan_started_at
scan_completed_at
scan_duration_ms

window_globals_scanned
react_nodes_scanned
redux_candidates
mobx_candidates
zustand_candidates
chart_engine_candidates
datafeed_candidates
storage_candidates
worker_candidates

candidate_found
candidate_type
candidate_ref
candidate_path
candidate_collection_type
candidate_collection_length
candidate_distinct_timestamps
candidate_distinct_raw_sizes
candidate_distinct_active_ids
candidate_quality
candidate_readable_passively

last_error_code
```

---

## Catálogo sanitizado

Adicionar catálogo limitado:

```text
runtime_store_candidates
```

Cada item:

```text
candidate_ref
source_type
name_sanitized
path_sanitized
object_type
top_level_keys
method_names
array_paths
object_paths
collection_length
distinct_timestamps
distinct_raw_sizes
distinct_active_ids
quality
readable_passively
occurrences
```

Limite máximo de candidatos.

Nunca incluir valores de mercado.

---

## Botão/comando de diagnóstico

Permitir disparo explícito e controlado da varredura pela própria extensão, por exemplo:

```javascript
window.__FRIDAY_TRADE_POLARIUM_BRIDGE__.scanRuntimeStores()
```

O comando deve:

- apenas iniciar leitura estrutural;
- não modificar a página;
- não bloquear UI;
- não repetir infinitamente;
- retornar somente status sanitizado.

Também pode existir endpoint local de disparo, desde que não aceite credenciais.

---

## Performance

A varredura deve ter:

```text
limite de profundidade
limite de objetos
limite de tempo
proteção contra ciclos
WeakSet
throttling
```

Nunca travar a página.

Nunca fazer varredura contínua por padrão.

Somente sob comando explícito.

---

## Não implementar

Não:

- extrair OHLC;
- enviar candles ao backend;
- preencher CandleStore;
- criar parser;
- alterar Chart API;
- alterar MarketPipeline;
- alterar CandleStore;
- criar persistência;
- criar histórico;
- criar IA;
- criar indicadores;
- executar ordens.

Esta Sprint termina apenas com descoberta estrutural.

---

## Testes obrigatórios

Criar testes para:

1. varredura limitada;
2. proteção contra ciclos;
3. limite de profundidade;
4. limite de objetos;
5. timeout;
6. candidato window global;
7. candidato React;
8. candidato Redux;
9. candidato MobX/Zustand;
10. candidato chart engine;
11. candidato datafeed;
12. candidato IndexedDB estrutural;
13. candidato localStorage estrutural;
14. nenhuma leitura de valores OHLC;
15. nenhuma exposição de segredo;
16. nenhum método de escrita chamado;
17. nenhuma alteração em objetos;
18. comando explícito não roda automaticamente;
19. catálogo limitado;
20. falha de um candidato não derruba scan.

---

## Validação real

Após implementação:

1. reiniciar backend;
2. recarregar extensão;
3. fechar abas antigas;
4. abrir nova aba Polarium;
5. aguardar o gráfico carregar;
6. abrir Console;
7. executar:

```javascript
window.__FRIDAY_TRADE_POLARIUM_BRIDGE__.scanRuntimeStores()
```

8. aguardar conclusão;
9. abrir:

```text
http://127.0.0.1:8000/api/v1/polarium/browser-bridge/status
```

10. copiar somente:

```text
runtime_store_discovery
runtime_store_candidates
```

Não copiar payloads, preços ou objetos brutos.

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
2. Arquitetura implementada.
3. Fontes inspecionadas.
4. Limites de segurança.
5. Window globals encontrados.
6. React candidates.
7. Redux candidates.
8. MobX/Zustand candidates.
9. Chart/datafeed candidates.
10. Storage candidates.
11. Worker candidates.
12. Candidato histórico encontrado ou não.
13. Caminho sanitizado.
14. Quantidade aproximada.
15. Qualidade SHORT/USEFUL/BROAD.
16. Pode ser lido passivamente?
17. Arquivos criados.
18. Arquivos modificados.
19. Testes criados.
20. Resultado dos testes específicos.
21. Resultado da suíte completa.
22. Resultado do build.
23. Como testar para o Renan.
24. Dados sanitizados que o Renan deve enviar.
25. Riscos conhecidos.
26. Próximo passo recomendado.
27. git status --short.
28. git diff --stat.
29. Sugestão de commit.

Mensagem sugerida:

```text
chore(polarium): inspect runtime chart data stores
```

---

## Regra final

Não fazer commit.

Não fazer push.

Não extrair candles nesta Sprint.

Não alterar a aplicação Polarium.

Somente descobrir onde o histórico renderizado pode estar armazenado.