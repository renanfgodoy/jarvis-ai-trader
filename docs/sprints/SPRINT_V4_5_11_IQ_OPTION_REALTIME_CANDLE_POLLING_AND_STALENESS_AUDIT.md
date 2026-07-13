# SPRINT V4.5.11 — IQ OPTION REALTIME CANDLE POLLING AND STALENESS AUDIT

## Objetivo

Auditar e corrigir o fluxo de atualização contínua dos candles da IQ Option.

Problema observado manualmente:

- alguns ativos carregam o gráfico inicial;
- depois o gráfico aparenta ficar estático;
- o contador de tempo não avança;
- exemplo informado: CADCHF;
- outros ativos, como EURUSD-OTC e AMAZON, já conseguiram carregar candles.

Não criar nova arquitetura.

Não alterar a descoberta de ativos sem prova.

Não executar ordens.

---

## Situação já comprovada

As Sprints anteriores comprovaram:

- assets OTC e REGULAR são listados;
- símbolos incompatíveis com candles são filtrados ou traduzidos;
- EURUSD-OTC carrega candles;
- AMAZON OTC carrega candles usando provider symbol `AMAZON`;
- RealCandleChart renderiza;
- bootstrap inicial funciona;
- Runtime Guard permanece read-only.

Novo problema:

```text
bootstrap
→ candles aparecem
→ atualização contínua não é percebida em alguns ativos
```

---

## Perguntas obrigatórias

A auditoria deve responder:

1. O polling frontend continua executando após o bootstrap?
2. Qual intervalo real está sendo usado?
3. O endpoint de candles recebe chamadas repetidas?
4. As respostas repetidas possuem timestamps novos?
5. A vela atual altera OHLC antes de fechar?
6. O CandleStore aceita atualização do mesmo timestamp?
7. O Chart API devolve a vela atual atualizada?
8. O React recebe novo array ou reutiliza referência anterior?
9. O RealCandleChart redesenha quando somente `close`, `high` ou `low` muda?
10. O contador é baseado em relógio local ou timestamp do último candle?
11. CADCHF está recebendo feed recente ou apenas histórico antigo?
12. O ativo está aberto no binary/turbo, mas com dados congelados?
13. Existe diferença entre OTC e REGULAR?
14. Respostas atrasadas estão sobrescrevendo candles mais recentes?

---

## Ativos de controle

Auditar obrigatoriamente:

### Controle conhecido

```text
EURUSD-OTC
```

### Ativo relatado como estático

```text
CADCHF
```

Registrar o símbolo técnico real retornado em `/assets`.

### Outro ativo OTC funcional

Usar:

```text
AMAZON
```

caso esteja disponível e aberto.

### REGULAR

Usar um ativo REGULAR listado e aberto no momento.

Não presumir que mercado REGULAR terá atualizações fora do horário adequado.

---

## Fase 1 — Auditoria do polling frontend

Localizar em:

```text
frontend/src/pages/MarketChart.tsx
```

ou arquivos relacionados:

- `setInterval`;
- `setTimeout`;
- função de fetch de candles;
- condição que inicia polling;
- condição que encerra polling;
- cleanup;
- AbortController;
- estado de bootstrap;
- estado de loading;
- dependências do `useEffect`.

Registrar:

1. intervalo configurado;
2. momento em que o polling começa;
3. condições que impedem nova chamada;
4. dependências do efeito;
5. comportamento ao trocar símbolo;
6. comportamento no React Strict Mode;
7. se uma chamada em andamento bloqueia chamadas futuras;
8. se erro ou payload vazio encerra o polling indevidamente.

Não aplicar correção antes de localizar a cadeia real.

---

## Fase 2 — Auditoria das chamadas reais

Para cada ativo de controle, registrar pelo menos cinco ciclos consecutivos.

Em cada ciclo informar:

- horário local da chamada;
- símbolo enviado;
- market_type;
- raw_size;
- limit;
- duração;
- HTTP status;
- `chart.count`;
- timestamp do último candle;
- open;
- high;
- low;
- close;
- se o último candle mudou;
- se surgiu um timestamp novo;
- se a resposta foi descartada ou aplicada.

Não expor credenciais.

Não registrar payload completo desnecessariamente.

---

## Fase 3 — Probe direto no worker

Executar probes read-only consecutivos para CADCHF e EURUSD-OTC.

Realizar chamadas em intervalos controlados.

Para cada resposta registrar:

- timestamp mais recente;
- idade do último candle em segundos;
- quantidade retornada;
- OHLC do último candle;
- diferença em relação à chamada anterior.

Determinar uma destas condições:

```text
LIVE
```

O último candle possui timestamp recente e OHLC muda ou novos candles surgem.

```text
QUIET
```

O candle atual é recente, mas não houve alteração de preço durante o período observado.

```text
STALE
```

O último candle está atrasado além do limite esperado.

```text
NO_DATA
```

Nenhum candle retornado.

Não classificar como congelamento do frontend antes de comparar diretamente o worker.

---

## Fase 4 — CandleStore

Auditar o merge/upsert de candles.

Confirmar se o CandleStore:

- insere novo timestamp;
- substitui candle existente com mesmo timestamp;
- preserva a versão mais recente de OHLC;
- não rejeita uma atualização apenas por timestamp duplicado;
- mantém ordenação;
- não mistura símbolos;
- não mistura timeframes;
- não mistura OTC e REGULAR.

Caso o mesmo candle de M1 seja recebido com novo `close`:

```text
timestamp igual
close diferente
```

o CandleStore deve atualizar a vela existente.

Adicionar teste específico para isso.

---

## Fase 5 — Chart API e React state

Confirmar:

- se o Chart API devolve o candle atualizado;
- se `response.chart.candles` contém valores novos;
- se o frontend aplica a resposta;
- se `setCandles()` recebe uma nova referência;
- se resposta antiga é ignorada;
- se resposta mais antiga pode sobrescrever uma nova;
- se o componente recebe candles atualizados.

Registrar o ponto exato onde uma atualização é perdida, caso isso ocorra.

---

## Fase 6 — RealCandleChart

Auditar se o gráfico reage quando:

### Caso A

Novo candle é adicionado.

### Caso B

O candle atual mantém o timestamp, mas muda:

- close;
- high;
- low.

Confirmar se a biblioteca gráfica exige:

- `series.update(candle)`;
- recriação dos dados;
- atualização explícita;
- nova referência do array.

Não recriar completamente o gráfico a cada polling sem necessidade.

Não causar zoom resetado ou flicker.

---

## Fase 7 — Contador de tempo

Localizar o contador mencionado na interface.

Determinar:

- arquivo e linha;
- fonte do horário;
- se usa `Date.now()`;
- se usa timestamp do último candle;
- se possui `setInterval`;
- se o intervalo é limpo incorretamente;
- se depende de novo fetch para atualizar;
- se representa horário local, countdown da vela ou horário da última atualização.

Se for countdown da vela M1:

```text
segundos_restantes = timeframe_seconds - (epoch_atual % timeframe_seconds)
```

O contador visual deve avançar independentemente da chegada de novo preço.

Se for horário da última atualização, o rótulo deve deixar isso explícito.

Não misturar:

- relógio local;
- countdown da vela;
- timestamp do candle;
- horário da última resposta.

---

## Fase 8 — Staleness

Criar critério explícito para identificar dados atrasados.

Exemplo conceitual:

```text
idade = agora - timestamp_do_último_candle
```

O limite deve considerar o timeframe.

Para M1, não declarar feed ao vivo quando o último candle estiver muitos minutos atrasado.

Caso o ativo esteja aberto na descoberta, mas o feed esteja stale:

- não substituir silenciosamente por outro ativo;
- não mostrar status de atualização normal;
- apresentar estado como `Dados atrasados` ou equivalente;
- preservar o histórico já carregado;
- não apagar candles válidos.

Não criar UI nova nesta Sprint sem necessidade comprovada.

Primeiro provar o problema.

---

## Correção mínima permitida

Aplicar apenas a menor correção comprovada.

Possibilidades:

1. restaurar polling encerrado incorretamente;
2. corrigir dependências do `useEffect`;
3. impedir AbortController antigo de cancelar ciclo atual;
4. usar upsert para atualizar candle com mesmo timestamp;
5. impedir resposta atrasada de sobrescrever resposta recente;
6. atualizar explicitamente a vela atual no RealCandleChart;
7. desacoplar contador visual do polling;
8. identificar estado stale;
9. corrigir polling que usa limite ou símbolo incorreto.

Não:

- aumentar frequência excessivamente;
- executar chamadas abaixo de 1 segundo;
- recriar worker;
- alterar provider sem prova;
- implementar WebSocket novo;
- adicionar streaming nesta fase;
- usar Polarium;
- mascarar feed stale com candles de outro ativo.

---

## Frequência de polling

Registrar a frequência atual.

Não reduzir o intervalo por impulso.

A frequência deve respeitar:

- carga no worker;
- estabilidade da biblioteca;
- M1, M5 e M15;
- ausência de chamadas concorrentes;
- timeout atual.

Caso seja necessário alterar, justificar com evidência.

---

## Testes obrigatórios

Adicionar testes para:

1. polling começa após bootstrap;
2. polling continua após resposta vazia transitória, quando apropriado;
3. troca de símbolo encerra o ciclo anterior;
4. resposta antiga não sobrescreve símbolo atual;
5. candle com mesmo timestamp e OHLC novo é atualizado;
6. novo timestamp é inserido;
7. candles antigos não substituem os novos;
8. CADCHF usa o símbolo técnico correto;
9. contador avança sem depender de novo candle;
10. estado stale é calculado corretamente, caso implementado;
11. EURUSD-OTC continua funcionando;
12. AMAZON continua funcionando;
13. Runtime Guard permanece ativo.

Executar:

```bash
.venv/bin/python -m pytest tests/market/providers -q
```

```bash
.venv/bin/python -m pytest tests/frontend -q
```

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

## Validação real obrigatória

### CADCHF

Observar por pelo menos três minutos em M1.

Registrar:

- horário inicial;
- contador;
- timestamp inicial do último candle;
- OHLC inicial;
- chamadas do polling;
- timestamp final;
- OHLC final;
- se surgiu vela nova;
- se houve atualização da vela atual;
- idade do feed.

### EURUSD-OTC

Executar o mesmo controle.

### AMAZON OTC

Executar ao menos dois ciclos para garantir ausência de regressão.

### Troca de ativo

Testar:

```text
EURUSD-OTC
→ CADCHF
→ AMAZON
→ EURUSD-OTC
```

Confirmar:

- símbolo correto;
- candles corretos;
- polling correto;
- sem mistura de séries;
- sem resposta atrasada;
- contador funcionando.

---

## Entrega esperada

Entregar relatório contendo:

1. causa raiz comprovada;
2. significado exato do contador;
3. arquivo e linha do contador;
4. frequência atual do polling;
5. arquivo e linha do polling;
6. cinco ciclos reais de EURUSD-OTC;
7. cinco ciclos reais de CADCHF;
8. classificação de CADCHF: LIVE, QUIET, STALE ou NO_DATA;
9. resultado direto do worker;
10. resultado do provider;
11. resultado do CandleStore;
12. resultado da Chart API;
13. resultado do React state;
14. resultado do RealCandleChart;
15. ponto exato onde a atualização era perdida;
16. correção mínima aplicada;
17. arquivos modificados;
18. diff funcional por arquivo;
19. testes de provider;
20. testes frontend;
21. suíte completa;
22. build;
23. Runtime Guard;
24. validação visual CADCHF;
25. validação visual EURUSD-OTC;
26. validação visual AMAZON;
27. `git status --short`;
28. `git diff --stat`;
29. riscos restantes;
30. sugestão de commit.

Não fazer commit.

Não fazer push.

Não alterar arquivos fora do escopo.

Não declarar que o frontend está congelado sem comparar o worker e o endpoint.

Não declarar que um ativo está ao vivo apenas porque retornou histórico.