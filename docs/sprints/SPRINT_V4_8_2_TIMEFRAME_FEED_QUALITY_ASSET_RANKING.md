# SPRINT V4.8.2 — TIMEFRAME FEED QUALITY ASSET RANKING

## Objetivo

Criar uma classificação dinâmica dos ativos da IQ Option conforme a qualidade real do feed no timeframe selecionado.

A lista principal do Friday deve priorizar apenas ativos adequados para análise naquele momento.

É aceitável reduzir a quantidade de ativos disponíveis.

A prioridade é:

```text
qualidade
→ atualização real
→ confiabilidade
→ quantidade
```

Não mostrar dezenas de ativos que apresentam candles atrasados, poucas atualizações ou feed inconsistente.

---

# REGRA PRINCIPAL

A qualidade deve ser calculada dinamicamente por:

```text
ativo
+
mercado
+
timeframe
+
sessão atual
```

Não criar ranking permanente.

Não assumir que um ativo sempre é bom ou sempre é ruim.

Exemplo:

```text
EURJPY-OTC M1 agora
→ EXCELLENT
```

Pode posteriormente virar:

```text
EURJPY-OTC M1
→ LIMITED
```

A classificação deve acompanhar o feed real.

---

# CONTEXTO COMPROVADO

Testes anteriores demonstraram diferenças importantes entre ativos.

Exemplos observados:

```text
EURJPY-OTC
USDJPY-OTC
GBPJPY-OTC
NZDUSD-OTC
→ ótima cadência em determinadas janelas
```

```text
EURUSD-OTC
GBPUSD-OTC
AUDCAD-OTC
EURGBP-OTC
USDCHF-OTC
→ feed bom
```

```text
CADCHF
BTCUSD
→ limitado em determinadas janelas
```

```text
AMAZON
→ stale em determinadas janelas
```

Esses exemplos são históricos de teste, não uma lista fixa.

---

# PARTE 1 — CLASSIFICAÇÃO OFICIAL

## 1. Estados

Classificar cada ativo em:

### EXCELLENT

Feed recente e adequado para o timeframe.

Referência inicial:

- último candle recente;
- eventos chegando normalmente;
- alterações reais frequentes;
- p95 de movimento compatível com o timeframe;
- sem gaps técnicos recorrentes;
- sem estado stale.

### GOOD

Feed confiável, mas com cadência inferior ao nível excelente.

Ainda adequado para análise.

### LIMITED

Feed existe, mas:

- possui poucos movimentos;
- gaps longos;
- atualização predominantemente por snapshot;
- não é adequado para entradas sensíveis ao tempo.

### STALE

Existe histórico, porém:

- último candle atrasado;
- feed imutável;
- série antiga;
- sem evolução real.

### NO_DATA

Nenhum candle utilizável.

### CHECKING

Ainda não existem dados suficientes para classificar.

---

## 2. Critério por timeframe

A classificação deve considerar o timeframe.

### M1

Mais exigente.

Priorizar:

- atualizações frequentes;
- baixa idade do candle;
- baixos gaps;
- resposta rápida após troca de ativo.

Ativos LIMITED, STALE e NO_DATA não devem aparecer na lista principal recomendada para M1.

### M5

Pode tolerar cadência um pouco menor.

GOOD e EXCELLENT são recomendados.

LIMITED pode aparecer somente em uma área secundária, claramente identificado.

### M15

Pode tolerar menos atualizações por minuto, desde que:

- o último candle seja recente;
- o feed continue evoluindo;
- não esteja stale.

Não reutilizar exatamente os limites de M1.

---

# PARTE 2 — MÉTRICAS

## 3. Métricas por contexto

Manter para cada:

```text
market_type
symbol
raw_size
```

as seguintes métricas:

- `first_event_latency_ms`
- `last_event_at`
- `last_movement_at`
- `last_candle_timestamp`
- `events_received`
- `ohlc_changes`
- `identical_reads`
- `movement_rate`
- `average_movement_interval_ms`
- `p50_movement_interval_ms`
- `p95_movement_interval_ms`
- `maximum_movement_gap_ms`
- `stale_age_seconds`
- `source_mode`
- `errors`
- `reconnects`

Não usar apenas quantidade de requisições HTTP.

---

## 4. Janela de avaliação

A classificação precisa de uma janela mínima.

Referência inicial:

```text
M1  → 15 a 30 segundos
M5  → 20 a 45 segundos
M15 → 30 a 60 segundos
```

Esses valores devem ser configuráveis.

Antes da janela mínima:

```text
CHECKING
```

Não marcar ativo como EXCELLENT após apenas um evento.

---

# PARTE 3 — DESCOBERTA E MEDIÇÃO

## 5. Não abrir streams para todos os ativos

É proibido manter dezenas de streams IQ simultaneamente.

Não assinar todos os ativos ao mesmo tempo.

A Sprint deve encontrar uma estratégia segura para avaliar qualidade sem sobrecarregar o worker.

Opções aceitáveis:

1. cache recente de ativos já visitados;
2. probe sequencial controlado;
3. pequeno lote limitado;
4. medição sob demanda;
5. ranking da sessão atualizado conforme o usuário navega;
6. background scanner com apenas um contexto por vez, se comprovadamente seguro.

Não criar uma conexão IQ por ativo.

Não manter subscriptions órfãs.

---

## 6. Scanner controlado

Se for implementado scanner:

- uma única conexão persistente;
- um ativo por vez;
- timeout por ativo;
- intervalo entre probes;
- cancelamento seguro;
- prioridade ao timeframe atual;
- não interromper o ativo que o usuário está visualizando;
- não degradar o gráfico principal;
- não criar 72 streams.

O scanner deve poder ser desativado.

---

# PARTE 4 — LISTA DE ATIVOS

## 7. Organização do dropdown

No timeframe selecionado, organizar a lista em grupos:

```text
RECOMENDADOS
```

Ativos EXCELLENT e GOOD.

```text
LIMITADOS
```

Opcionalmente visíveis, mas separados.

```text
INDISPONÍVEIS
```

STALE e NO_DATA não devem aparecer na lista principal do operador.

Podem aparecer somente no Modo DEV ou em opção:

```text
Mostrar todos os ativos
```

---

## 8. Modo Operador

Por padrão, mostrar somente:

```text
EXCELLENT
GOOD
```

Exemplo:

```text
RECOMENDADOS PARA M1

EUR/JPY OTC     Excelente
USD/JPY OTC     Excelente
EUR/USD OTC     Bom
GBP/USD OTC     Bom
```

Não exibir p95, SSE ou métricas técnicas no dropdown principal.

---

## 9. Opção Mostrar todos

Adicionar opção discreta:

```text
Mostrar todos os ativos
```

Quando ativada, permitir visualizar também:

- LIMITED;
- CHECKING;
- STALE;
- NO_DATA.

Cada ativo deve mostrar um rótulo simples:

```text
Excelente
Bom
Limitado
Dados atrasados
Sem dados
Verificando
```

Não esconder o risco.

---

## 10. Quantidade

É aceitável que:

```text
72 ativos abertos
```

resultem em:

```text
8 ativos recomendados para M1
```

A Friday deve preferir oito ativos confiáveis a dezenas de ativos ruins.

---

# PARTE 5 — SELEÇÃO E FALLBACK

## 11. Ativo selecionado

Se o ativo atual cair de GOOD para LIMITED:

- não trocar automaticamente no mesmo instante;
- mostrar aviso;
- bloquear ou limitar readiness;
- oferecer ativos melhores.

Exemplo:

```text
Este ativo perdeu qualidade para M1.
Melhores opções disponíveis: EURJPY-OTC, USDJPY-OTC.
```

Não alterar o ativo sem ação do usuário.

---

## 12. Ativo inicial

Ao abrir o Friday:

1. aguardar classificação mínima;
2. selecionar o melhor ativo disponível, se não houver seleção persistida;
3. preservar seleção anterior apenas se ela continuar utilizável;
4. caso não seja utilizável, mostrar aviso e recomendação.

Não substituir silenciosamente por EURUSD-OTC sem informar.

---

# PARTE 6 — PAINEL FRIDAY STRATEGY

## 13. Readiness

O Strategy Engine deve receber a qualidade do feed.

Regras iniciais:

```text
EXCELLENT
→ feed pronto
```

```text
GOOD
→ feed pronto
```

```text
LIMITED
→ análise limitada
```

```text
STALE
→ análise bloqueada
```

```text
NO_DATA
→ análise bloqueada
```

```text
CHECKING
→ aguardando feed
```

Ainda não gerar CALL ou PUT.

---

## 14. Mensagens humanas

### EXCELLENT

```text
Feed excelente para M1
```

### GOOD

```text
Feed adequado para M1
```

### LIMITED

```text
Feed limitado para este timeframe
```

### STALE

```text
Dados atrasados
Escolha outro ativo
```

### NO_DATA

```text
Sem dados disponíveis
```

### CHECKING

```text
Avaliando qualidade do ativo
```

---

# PARTE 7 — MODO DEV

## 15. Métricas técnicas

No Modo DEV, mostrar:

- ranking técnico;
- score interno, caso exista;
- janela de medição;
- p50;
- p95;
- maior gap;
- movimento por segundo;
- idade do candle;
- primeiro evento;
- source mode;
- quantidade de eventos;
- erros;
- classificação final;
- motivo da classificação.

O score técnico não deve aparecer como probabilidade operacional.

---

# PARTE 8 — PERFORMANCE

## 16. Limites

A implementação não pode:

- aumentar continuamente memória;
- abrir múltiplos workers;
- criar uma stream por ativo;
- atrasar o gráfico atual;
- disparar dezenas de requests por segundo;
- bloquear o backend;
- degradar SSE do ativo selecionado.

Registrar impacto de:

- CPU;
- memória;
- threads;
- subscriptions;
- tempo total de classificação.

---

# PARTE 9 — SEGURANÇA

## 17. Read-only

Preservar Runtime Guard.

Nunca chamar:

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
- equivalentes.

Não acessar saldo.

Não executar ordem.

Não expor credenciais.

---

# PARTE 10 — TESTES

## 18. Backend/provider

Adicionar testes para:

1. classificação EXCELLENT;
2. classificação GOOD;
3. classificação LIMITED;
4. classificação STALE;
5. classificação NO_DATA;
6. classificação CHECKING;
7. critérios diferentes entre M1, M5 e M15;
8. um ativo não cria uma conexão nova;
9. scanner não cria streams simultâneas em massa;
10. cancelamento do scanner;
11. ativo atual não é interrompido;
12. cache é isolado por timeframe;
13. Runtime Guard permanece ativo.

Executar:

```bash
.venv/bin/python -m pytest tests/market/providers tests/market/store tests/api -q
```

---

## 19. Frontend

Adicionar testes para:

1. M1 mostra somente EXCELLENT/GOOD por padrão;
2. M5 usa classificação própria;
3. M15 usa classificação própria;
4. Mostrar todos revela LIMITED/STALE/NO_DATA;
5. ativo selecionado não é trocado silenciosamente;
6. aviso aparece quando qualidade cai;
7. lista permanece utilizável;
8. dropdown não fica vazio durante CHECKING;
9. Strategy Engine recebe readiness;
10. STALE bloqueia análise;
11. LIMITED mostra ressalva;
12. Modo DEV mostra métricas;
13. Modo Operador não mostra p95 ou SSE;
14. troca de timeframe recalcula ranking;
15. lista não depende apenas de sufixo do símbolo.

Executar:

```bash
.venv/bin/python -m pytest tests/frontend -q
```

---

## 20. Suíte e build

```bash
.venv/bin/python -m pytest -q
```

```bash
cd frontend
npm run build
cd ..
```

---

# PARTE 11 — VALIDAÇÃO REAL

## 21. M1

Medir e classificar pelo menos:

```text
EURUSD-OTC
GBPUSD-OTC
USDJPY-OTC
EURJPY-OTC
AUDCAD-OTC
CADCHF
```

Registrar lista final recomendada.

---

## 22. M5

Repetir classificação para o timeframe M5.

Não copiar classificação do M1.

---

## 23. M15

Repetir classificação para o timeframe M15.

Não copiar classificação do M5.

---

## 24. Troca de timeframe

Testar:

```text
M1
→ M5
→ M15
→ M1
```

Confirmar que:

- ranking muda quando necessário;
- lista atualiza;
- ativo selecionado não é perdido indevidamente;
- gráfico continua correto.

---

# PARTE 12 — ENTREGA ESPERADA

Entregar relatório contendo:

1. arquitetura escolhida para medir ativos;
2. prova de que não existem streams em massa;
3. regras EXCELLENT/GOOD/LIMITED/STALE/NO_DATA/CHECKING;
4. limites M1;
5. limites M5;
6. limites M15;
7. janela mínima;
8. métricas utilizadas;
9. lista recomendada M1;
10. lista recomendada M5;
11. lista recomendada M15;
12. quantidade total versus recomendada;
13. comportamento de Mostrar todos;
14. comportamento quando qualidade cai;
15. integração com Strategy Engine;
16. arquivos modificados;
17. diff funcional;
18. testes backend/provider;
19. testes frontend;
20. suíte completa;
21. build;
22. teste de performance;
23. Runtime Guard;
24. `git status --short`;
25. `git diff --stat`;
26. riscos restantes;
27. sugestão de commit.

Não fazer commit.

Não fazer push.

Não criar ranking fixo.

Não inventar movimento.

Não abrir uma stream para cada ativo.