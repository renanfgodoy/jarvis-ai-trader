# SPRINT V4.5.12 — REALTIME TICK FEED AND CANDLE MOVEMENT AUDIT

## Objetivo principal

Fazer o gráfico do Friday Trade atualizar a vela aberta de forma progressiva e cadenciada, aproximando-se da experiência visual do gráfico da corretora.

Problema observado:

- o histórico carrega;
- o polling atual ocorre a cada 5 segundos;
- durante esse intervalo o gráfico permanece parado;
- quando a nova resposta chega, a vela dá um salto grande;
- a movimentação não parece em tempo real;
- alguns ativos podem ainda retornar dados stale.

Esta Sprint deve descobrir e implementar, somente se comprovadamente disponível, uma fonte passiva read-only de preço ou ticks entre os fechamentos das velas.

Não gerar movimento artificial.

Não interpolar preços inventados.

Não executar ordens.

---

## Diagnóstico técnico inicial

O fluxo atual é aproximadamente:

```text
get_candles()
→ snapshot OHLC
→ espera 5 segundos
→ novo snapshot OHLC
→ salto visual
```

Esse modelo não consegue reproduzir a cadência do gráfico da corretora.

O fluxo desejado é:

```text
get_candles()
→ histórico inicial

subscription passiva de preço/tick
→ preço novo
→ atualização incremental da vela aberta
→ RealCandleChart.series.update()
```

O polling de candles pode permanecer como:

- reconciliação;
- recuperação;
- confirmação de fechamento;
- fallback.

Ele não deve ser a única fonte da movimentação visual se existir um feed passivo mais frequente.

---

## Regra de honestidade do feed

É proibido:

- inventar ticks;
- interpolar preço entre duas respostas;
- animar a vela para posições não recebidas;
- suavizar preço criando valores intermediários falsos;
- usar candles de outro ativo;
- declarar “tempo real” sem medir a latência;
- simular movimento apenas para deixar o gráfico bonito.

Toda alteração da vela deve ser baseada em um preço real recebido da IQ Option.

---

## Resultado esperado

Quando houver feed válido:

- a vela aberta deve mudar progressivamente;
- close deve acompanhar os preços recebidos;
- high deve aumentar quando o preço superar a máxima;
- low deve diminuir quando o preço ficar abaixo da mínima;
- open deve permanecer fixo durante a vela;
- o gráfico não deve esperar cinco segundos para cada movimento;
- o eixo de preço não deve dar saltos exagerados por falha de atualização;
- o usuário deve visualizar a latência do feed.

Quando não houver feed válido:

- manter polling atual;
- marcar claramente a atualização como snapshot;
- indicar atraso ou ausência de movimento;
- nunca fingir movimentação instantânea.

---

# PARTE 1 — AUDITORIA DA FONTE EM TEMPO REAL

## 1. Inspeção da biblioteca instalada

Auditar somente no ambiente isolado:

```text
.jarvis_cache/iq_option_probe_venv
```

Versão:

```text
iqoptionapi 7.1.1
```

Pesquisar métodos e estruturas relacionados a:

- realtime candles;
- live candles;
- candle stream;
- tick;
- quote;
- price;
- mood;
- top assets;
- commission changed;
- instrument quotes;
- digital spot;
- binary price;
- websocket message handlers;
- subscriptions passivas.

Pesquisar especialmente métodos equivalentes a:

```python
start_candles_stream
get_realtime_candles
stop_candles_stream
```

e qualquer alternativa real existente na versão instalada.

Não presumir nomes. Registrar os métodos encontrados de fato.

---

## 2. Inspeção estática obrigatória

Para cada método candidato, informar:

1. arquivo;
2. linhas;
3. mensagem WebSocket utilizada;
4. estrutura de cache preenchida;
5. frequência esperada;
6. necessidade de subscription;
7. método de unsubscribe;
8. tipo de ativo suportado;
9. campos retornados;
10. riscos de bloqueio;
11. se usa active id ou symbol;
12. se consulta qualquer dado proibido.

Não modificar a biblioteca instalada.

Não aplicar monkey patch permanente.

---

## 3. Segurança

Continuam proibidos:

- buy;
- buy_multi;
- buy_digital_spot;
- sell_option;
- buy_order;
- close_position;
- change_balance;
- get_balance;
- get_positions;
- get_orders;
- qualquer execução ou consulta financeira equivalente.

Subscriptions passivas são permitidas somente para:

- candles;
- ticks;
- quotes;
- preços;
- dados públicos de mercado.

O Runtime Guard deve registrar todas as chamadas realizadas.

---

# PARTE 2 — PROBES REAIS

## 4. Ativos obrigatórios

Testar:

### Controle principal

```text
EURUSD-OTC
```

### Ativo corporativo traduzido

```text
AMAZON
```

com contexto de mercado OTC.

### Ativo relatado stale

```text
CADCHF
```

usando o símbolo técnico real retornado pelo provider.

### REGULAR

Um ativo regular aberto e compatível com candles no momento do teste.

---

## 5. Probe de realtime candles ou ticks

Para cada ativo, observar durante pelo menos 60 segundos.

Registrar cada evento recebido com dados sanitizados:

- horário local de recebimento;
- horário do servidor, se existir;
- timestamp do evento;
- símbolo;
- active id;
- preço;
- open;
- high;
- low;
- close;
- volume, se existir;
- source;
- intervalo desde o evento anterior;
- latência estimada;
- duplicado ou alteração real.

Não imprimir credenciais.

Não imprimir payload completo sem necessidade.

---

## 6. Métricas obrigatórias

Para cada ativo, calcular:

```text
event_count
```

Quantidade de eventos em 60 segundos.

```text
movement_count
```

Quantidade de eventos que alteraram o preço.

```text
average_event_interval_ms
```

Intervalo médio entre eventos.

```text
p50_event_interval_ms
p95_event_interval_ms
max_event_interval_ms
```

```text
feed_age_ms
```

Idade estimada do último evento.

```text
duplicate_ratio
```

Proporção de eventos idênticos.

Classificar a fonte como:

```text
STREAMING
```

Eventos reais frequentes e progressivos.

```text
NEAR_REALTIME
```

Eventos reais, mas com intervalos perceptíveis.

```text
SNAPSHOT
```

Somente atualizações espaçadas.

```text
STALE
```

Dados antigos ou sem evolução.

```text
UNAVAILABLE
```

Nenhuma fonte passiva utilizável.

---

## 7. Critério mínimo para implementação

Uma fonte só pode ser usada para mover a vela se:

1. for read-only;
2. retornar preço real;
3. possuir símbolo ou active id confiável;
4. não depender de método proibido;
5. possuir unsubscribe seguro;
6. não travar o worker;
7. não misturar ativos;
8. não deixar subscriptions órfãs;
9. apresentar cadência melhor que o polling de 5 segundos;
10. possuir evidência real em probe.

Não implementar apenas porque um método existe.

---

# PARTE 3 — DECISÃO DE IMPLEMENTAÇÃO

## 8. Caminho A — Streaming comprovado

Caso uma fonte streaming seja comprovada, implementar o menor fluxo possível:

```text
IQ Option persistent worker
→ subscription passiva
→ cache do último preço/evento
→ endpoint ou canal interno já compatível
→ frontend
→ update da vela atual
```

Não criar infraestrutura externa.

Não instalar dependências na `.venv` principal.

Não criar conexão paralela por componente React.

A conexão deve continuar centralizada no worker persistente.

---

## 9. Caminho B — Apenas realtime candles da biblioteca

Se a biblioteca oferecer cache de realtime candles:

- iniciar stream somente para o ativo e timeframe selecionados;
- recuperar atualizações frequentes do cache;
- encerrar stream ao trocar ativo ou timeframe;
- confirmar fechamento de vela com o timestamp;
- reconciliar periodicamente com `get_candles()`.

Não manter streams de centenas de ativos simultaneamente.

---

## 10. Caminho C — Apenas snapshots

Se nenhum streaming real for comprovado:

- não declarar gráfico instantâneo;
- manter polling de 5 segundos para histórico/reconciliação;
- avaliar polling adaptativo entre 1 e 2 segundos somente se:
  - o worker suportar;
  - não houver chamadas concorrentes;
  - os probes comprovarem estabilidade;
  - o timeout não acumular;
  - os testes de carga forem aprovados.

Mesmo nesse caso, informar visualmente:

```text
Atualização por snapshot
```

Não chamar de tick em tempo real.

---

# PARTE 4 — AGREGAÇÃO DA VELA ABERTA

## 11. Regras da vela

Para cada tick/preço real recebido:

```text
open
→ primeiro preço da janela, não muda
```

```text
close
→ último preço recebido
```

```text
high
→ max(high atual, preço recebido)
```

```text
low
→ min(low atual, preço recebido)
```

O timestamp da vela deve ser calculado pelo bucket do timeframe:

```text
bucket = floor(event_timestamp / timeframe_seconds) * timeframe_seconds
```

Ao entrar em um novo bucket:

1. fechar a vela anterior;
2. criar nova vela;
3. open = primeiro preço real do novo bucket;
4. high = preço;
5. low = preço;
6. close = preço.

Não gerar candles intermediários sem preço real.

---

## 12. Timeframes

Suportar:

```text
M1
M5
M15
```

O mesmo preço real pode atualizar a vela aberta do timeframe selecionado.

Trocar timeframe deve:

- cancelar ou reajustar a subscription anterior;
- reiniciar o estado da vela atual;
- carregar histórico do novo timeframe;
- não misturar buckets.

---

## 13. Reconciliação

Mesmo com streaming, manter reconciliação periódica com candles oficiais.

Objetivo:

- corrigir divergências;
- confirmar vela fechada;
- recuperar eventos perdidos;
- normalizar após reconexão.

Frequência inicial sugerida:

```text
15 segundos
```

A frequência final deve ser comprovada por teste.

Não sobrescrever uma vela mais nova com snapshot antigo.

Regra obrigatória:

```text
timestamp mais recente vence
```

Para timestamp igual:

- comparar OHLC;
- aplicar somente versão mais nova;
- preservar high/low verdadeiros;
- registrar divergência quando necessário.

---

# PARTE 5 — ENTREGA AO FRONTEND

## 14. Frequência de renderização

Receber vários eventos por segundo não significa renderizar sem limite.

Separar:

```text
frequência do feed
```

de:

```text
frequência de renderização
```

Aplicar atualização visual com limite inicial entre:

```text
100ms e 250ms
```

Somente se houver novo preço.

Isso permite aproximadamente:

```text
4 a 10 atualizações visuais por segundo
```

sem redesenhar inutilmente.

Não atrasar um evento por quatro ou cinco segundos.

Não usar animação falsa entre preços.

---

## 15. RealCandleChart

A vela atual deve usar atualização incremental equivalente a:

```ts
series.update(updatedCandle)
```

Não substituir todo o histórico a cada tick.

Não recriar o chart.

Não resetar zoom.

Não mover automaticamente a escala se o usuário estiver inspecionando uma região histórica, salvo comportamento já aprovado.

Adicionar atualização somente quando:

- OHLC mudou;
- timestamp mudou.

---

## 16. Controle de respostas atrasadas

Cada fluxo deve ser identificado por:

- provider;
- market_type;
- symbol;
- timeframe;
- generation/request id.

Ao trocar ativo ou timeframe:

- incrementar geração;
- ignorar eventos da geração anterior;
- cancelar subscription anterior;
- limpar timers relacionados;
- iniciar estado CHECKING.

Nenhum evento de EURUSD-OTC pode alterar AMAZON, CADCHF ou outro ativo.

---

# PARTE 6 — INDICADOR DE CONFIANÇA

## 17. Estados oficiais

Manter:

```text
CHECKING
LIVE
QUIET
STALE
NO_DATA
```

Adicionar informação da fonte:

```text
STREAMING
NEAR_REALTIME
SNAPSHOT
```

Exemplos:

```text
AO VIVO
Streaming ativo
Último movimento: 180 ms
```

```text
AO VIVO
Atualização próxima do tempo real
Último movimento: 1,2 s
```

```text
ATUALIZAÇÃO POR SNAPSHOT
Consulta a cada 5 s
```

```text
DADOS ATRASADOS
Não utilizar para análise
```

---

## 18. Métricas visuais

Exibir:

- estado do feed;
- modo da fonte;
- último preço;
- última mudança real;
- último evento recebido;
- último candle;
- próxima vela;
- latência estimada;
- frequência média recente;
- readiness para análise.

Exemplo:

```text
STATUS DO FEED
AO VIVO — STREAMING

Último movimento: 140 ms
Último evento: 120 ms
Latência estimada: 210 ms
Próxima vela: 00:37
Atualizações: 6,4/s

ANÁLISE DISPONÍVEL
```

Para snapshot:

```text
STATUS DO FEED
ATUALIZAÇÃO POR SNAPSHOT

Consulta: a cada 5 s
Último candle: há 3 s
Movimentação não instantânea

ANÁLISE COM RESSALVA
```

Para stale:

```text
STATUS DO FEED
DADOS ATRASADOS

Último candle: há 4 min
Último movimento: não detectado

ANÁLISE BLOQUEADA
```

Não depender apenas de cores.

---

## 19. Readiness

```text
STREAMING + LIVE
→ análise permitida
```

```text
NEAR_REALTIME + LIVE
→ análise permitida com informação de latência
```

```text
QUIET com candle recente
→ análise com ressalva
```

```text
SNAPSHOT
→ não liberar estratégias sensíveis a entrada instantânea
```

```text
STALE
→ bloqueado
```

```text
NO_DATA
→ bloqueado
```

```text
CHECKING
→ bloqueado
```

Ainda não gerar CALL ou PUT nesta Sprint.

---

# PARTE 7 — FALLBACK E RECONEXÃO

## 20. Perda de streaming

Se a subscription parar:

1. não congelar silenciosamente;
2. marcar `CHECKING` ou `SNAPSHOT`;
3. manter histórico;
4. tentar unsubscribe seguro;
5. tentar uma reconexão controlada;
6. não criar múltiplas subscriptions;
7. continuar reconciliação por candles;
8. informar a mudança de modo ao usuário.

---

## 21. Troca de ativo

Sequência obrigatória:

```text
cancelar stream anterior
→ confirmar cleanup
→ limpar métricas
→ carregar histórico
→ iniciar stream novo
→ aguardar eventos
→ classificar feed
```

Não manter stream oculto do ativo anterior.

---

# PARTE 8 — TESTES

## 22. Testes do worker

Adicionar testes para:

1. subscription utiliza somente métodos read-only;
2. inicia apenas para ativo solicitado;
3. encerra ao trocar ativo;
4. encerra ao desconectar;
5. não acumula subscriptions;
6. evento é associado ao símbolo correto;
7. evento antigo é ignorado;
8. Runtime Guard bloqueia métodos proibidos;
9. timeout não mata o worker;
10. reconexão não duplica eventos.

---

## 23. Testes de agregação

Adicionar testes para:

1. primeiro preço define open/high/low/close;
2. preço maior atualiza high e close;
3. preço menor atualiza low e close;
4. preço intermediário atualiza somente close;
5. novo bucket cria nova vela;
6. M1 calcula bucket correto;
7. M5 calcula bucket correto;
8. M15 calcula bucket correto;
9. evento atrasado não sobrescreve vela atual;
10. símbolo anterior não contamina o atual;
11. reconciliação preserva high/low corretos;
12. nenhum preço artificial é criado.

---

## 24. Testes frontend

Adicionar testes para:

1. atualização incremental usa candle atual;
2. não substitui todo o histórico por tick;
3. renderização é limitada entre 100 e 250ms;
4. não renderiza sem alteração de preço;
5. troca de símbolo ignora eventos antigos;
6. LIVE não depende apenas de HTTP 200;
7. modo STREAMING é exibido;
8. modo SNAPSHOT é exibido;
9. STALE bloqueia análise;
10. countdown continua em 1 segundo sem fetch;
11. próxima vela não depende do stream;
12. não existe interpolação visual falsa.

---

## 25. Testes de carga

Durante pelo menos cinco minutos em um ativo com movimento:

Registrar:

- eventos recebidos;
- eventos aplicados;
- atualizações renderizadas;
- CPU do processo, quando acessível;
- memória do worker;
- número de threads;
- subscriptions ativas;
- erros;
- reconexões;
- latência média;
- p95;
- maior intervalo sem evento.

Critérios:

- memória não cresce continuamente;
- threads não acumulam;
- apenas uma subscription por contexto;
- frontend permanece responsivo;
- gráfico não pisca;
- zoom não reseta.

---

## 26. Comandos obrigatórios

Provider/worker:

```bash
.venv/bin/python -m pytest tests/market/providers tests/market/store -q
```

Frontend:

```bash
.venv/bin/python -m pytest tests/frontend -q
```

Suíte completa:

```bash
.venv/bin/python -m pytest -q
```

Build:

```bash
cd frontend
npm run build
cd ..
```

---

# PARTE 9 — VALIDAÇÃO REAL

## 27. EURUSD-OTC

Observar por no mínimo três minutos.

Comprovar:

- quantidade de eventos;
- intervalo médio;
- movimento progressivo da vela;
- ausência de saltos causados apenas pelo polling;
- fechamento correto da vela;
- abertura correta da próxima;
- reconciliação sem regressão;
- status visual correto.

---

## 28. AMAZON OTC

Observar por no mínimo dois minutos.

Comprovar:

- contexto OTC preservado;
- símbolo técnico AMAZON;
- stream ou fallback correto;
- vela atual progressiva quando houver preço;
- nenhuma regressão para `AMA/ZON`.

---

## 29. CADCHF

Determinar:

- streaming disponível ou não;
- eventos atuais ou stale;
- idade do feed;
- comportamento visual correto;
- análise bloqueada se continuar stale.

Não tentar movimentar CADCHF artificialmente.

---

## 30. REGULAR

Testar ativo regular realmente aberto.

Não declarar falha se o mercado estiver fechado.

Registrar horário e condição real do ativo.

---

## 31. Comparação com a corretora

Comparar visualmente, sem afirmar igualdade absoluta:

- timestamp da vela;
- direção;
- abertura;
- fechamento atual;
- máxima;
- mínima;
- momento de abertura da próxima vela;
- frequência aparente de atualização.

Registrar diferenças observadas.

A meta é:

```text
mesma direção e OHLC compatível
+ atualização progressiva
+ baixa latência
```

Não prometer replicação exata caso a biblioteca comunitária entregue dados com atraso ou agregação diferente.

---

# PARTE 10 — ENTREGA ESPERADA

Entregar relatório com:

1. causa dos saltos atuais;
2. métodos de realtime encontrados;
3. arquivo e linhas da biblioteca;
4. fonte escolhida;
5. prova read-only;
6. frequência real de eventos;
7. latência média, p50 e p95;
8. resultado EURUSD-OTC;
9. resultado AMAZON;
10. resultado CADCHF;
11. resultado REGULAR;
12. modo final: STREAMING, NEAR_REALTIME ou SNAPSHOT;
13. arquitetura aplicada;
14. regra de agregação da vela;
15. regra de reconciliação;
16. frequência de renderização;
17. tratamento de troca de ativo;
18. tratamento de reconexão;
19. indicador visual;
20. readiness;
21. arquivos modificados;
22. diff funcional;
23. testes de worker/provider;
24. testes de store;
25. testes frontend;
26. suíte completa;
27. build;
28. teste de carga;
29. Runtime Guard;
30. comparação visual com a corretora;
31. limitações honestas;
32. `git status --short`;
33. `git diff --stat`;
34. riscos restantes;
35. sugestão de commit.

Não fazer commit.

Não fazer push.

Não instalar `iqoptionapi` na `.venv` principal.

Não executar ordens.

Não criar preços artificiais.

Não afirmar tempo real sem métricas.