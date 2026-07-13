# Friday Trade — Sprint V4.1.1

# Monotonic Live Candle Stream

## Status

PLANNED

---

## Objetivo

Corrigir a fluidez do gráfico real do Friday Trade.

Durante o teste real, a série chegou a exibir aproximadamente seis candles e depois voltou para dois candles, causando:

- encolhimento da série;
- mudanças bruscas no gráfico;
- perda de continuidade visual;
- reposicionamento indesejado;
- experiência diferente da Polarium e do TradingView.

O objetivo desta Sprint é garantir que, dentro da mesma série:

```text
active_id + raw_size
```

o histórico exibido seja monotônico e incremental.

Fluxo esperado:

```text
2 candles
→ 3 candles
→ 4 candles
→ 5 candles
→ 6 candles
→ 7 candles
```

Nunca:

```text
2
→ 6
→ 2
→ 5
→ 2
```

---

## Problema confirmado

O problema continua mesmo após a estabilização do modo `Seguir Polarium`.

A seleção do par:

```text
active_id + raw_size
```

agora permanece mais estável, porém a quantidade de candles exibidos ainda diminui durante o polling.

Isso pode estar relacionado a:

- resposta parcial da Chart API;
- substituição integral da série no frontend;
- race condition entre requisições;
- resposta antiga aplicada depois de uma resposta recente;
- diferença de `limit` entre chamadas;
- uso incorreto de `setData()`;
- reset de gráfico durante polling;
- alternância entre snapshots de tamanhos diferentes;
- Store contendo uma série maior do que a exibida.

A causa deve ser comprovada antes da correção final.

---

## Escopo da investigação

Revisar obrigatoriamente:

```text
frontend/src/hooks/useRealCandles.ts
frontend/src/components/chart/RealCandleChart/index.tsx
frontend/src/components/chart/RealCandleChart/sync.ts
frontend/src/pages/MarketChart.tsx

app/api/routes/market_chart.py
app/market/chart/runtime_service.py
app/market/chart/service.py
app/market/store/
```

Responder:

1. O CandleStore continua com seis candles quando o frontend volta para dois?
2. A Chart API retorna uma janela menor em alguma chamada?
3. O parâmetro `limit` muda entre requisições?
4. O frontend substitui toda a série pela última resposta?
5. Existe request antigo sobrescrevendo request novo?
6. Existe troca indevida de contexto?
7. `setData()` está sendo chamado durante atualização normal?
8. `fitContent()` está sendo executado repetidamente?
9. O gráfico está sendo recriado?
10. Zoom, pan ou visible range são resetados durante polling?

---

## Regra de série monotônica

Para a mesma combinação:

```text
active_id + raw_size
```

a série exibida deve seguir estas regras:

### Candle existente

Quando um candle chega com o mesmo campo:

```text
time
```

ele deve atualizar apenas:

```text
open
high
low
close
```

O candle não deve ser duplicado.

### Candle novo

Quando chega um candle com:

```text
time > último time exibido
```

ele deve ser acrescentado ao final.

### Resposta parcial

Se a interface possui seis candles e a API devolve apenas dois:

- não substituir a série de seis pela de dois;
- realizar merge pelo campo `time`;
- preservar candles anteriores;
- atualizar os candles presentes;
- não apagar histórico válido.

### Resposta vazia

Uma resposta vazia temporária não pode apagar candles já exibidos.

### Erro temporário

Timeout, erro HTTP ou polling incompleto não pode limpar o gráfico.

### Limite

Quando for necessário aplicar limite máximo:

- remover apenas candles mais antigos;
- nunca remover candles mais recentes;
- manter ordenação cronológica.

---

## Estratégia de merge

Implementar uma reconciliação monotônica por:

```text
time
```

Regras:

1. Criar mapa de candles anteriores pelo `time`.
2. Aplicar os candles novos sobre o mapa.
3. Atualizar candles com mesmo timestamp.
4. Acrescentar timestamps inéditos.
5. Ordenar por `time`.
6. Deduplicar.
7. Aplicar limite máximo somente depois do merge.
8. Nunca diminuir a série apenas porque a resposta atual veio menor.

Não inventar candles.

Não interpolar preços.

Não criar dados sintéticos.

---

## Controle de concorrência

Cada requisição deve possuir:

```text
active_id
raw_size
request_sequence
```

A resposta só pode ser aplicada se:

- ainda pertencer ao contexto atual;
- for mais recente que a última resposta aplicada;
- não tiver sido cancelada;
- não pertencer a uma série anterior.

Utilizar:

```text
AbortController
```

ou mecanismo equivalente quando apropriado.

Uma resposta antiga nunca pode substituir uma resposta mais nova.

---

## Reset controlado

Uma limpeza completa da série só pode ocorrer quando:

- o `active_id` mudar de verdade;
- o `raw_size` mudar de verdade;
- o usuário selecionar outra série;
- ocorrer reset explícito do workspace;
- o CandleStore for reiniciado e o contexto for reconhecido como novo.

Não realizar reset por:

- polling vazio;
- erro temporário;
- `timeSync`;
- ausência momentânea de `last_trace`;
- resposta atrasada;
- snapshot parcial;
- atualização do candle aberto.

---

## Lightweight Charts

Preservar:

- zoom;
- pan;
- crosshair;
- escala;
- posição do usuário;
- instância do gráfico;
- instância da série.

Não recriar:

```text
createChart()
```

durante polling.

Não recriar a candlestick series durante polling.

### Usar `series.update()`

Utilizar para:

- atualização do candle aberto;
- inclusão de um novo candle;
- atualização do último candle.

### Usar `series.setData()`

Usar apenas em:

- carga inicial;
- troca real de série;
- reset explícito;
- reconciliação de histórico/gap que realmente exija substituição.

### `fitContent()`

Não executar em cada polling.

Executar apenas em:

- carga inicial;
- troca de série;
- ação explícita do usuário.

---

## Comportamento visual esperado

### Candle aberto

```text
mesmo timestamp
→ corpo e pavio mudam
→ gráfico não pula
→ escala não reinicia
```

### Candle novo

```text
novo timestamp
→ append
→ contador aumenta
→ histórico permanece
```

### Usuário no canto direito

Se o usuário estiver acompanhando o candle atual, o gráfico pode acompanhar o novo candle de forma suave.

### Usuário analisando histórico

Se o usuário tiver feito pan para trás, a chegada de um candle novo não deve puxar automaticamente o gráfico para o presente.

---

## Chart API

A Chart API deve:

- retornar janela ordenada;
- usar `limit` estável;
- manter contrato consistente;
- não devolver candles duplicados;
- não alterar arbitrariamente a quantidade da janela;
- retornar os candles mais recentes dentro do limite.

Preferência:

```text
limit = 200
```

ou outro valor estável já aprovado no projeto.

Não criar endpoint paralelo.

---

## Seguir Polarium

Com `Seguir Polarium` ligado:

- o par ativo deve permanecer atômico;
- o histórico da série selecionada deve ser monotônico;
- `timeSync` não pode resetar o gráfico;
- uma resposta menor não pode encolher a série;
- a troca real de ativo/timeframe deve realizar reset controlado;
- a série atual deve permanecer até a nova série possuir candles.

---

## Modo manual

Com `Seguir Polarium` desligado:

- a série manual deve permanecer estável;
- eventos da Polarium não devem sobrescrever a seleção;
- o histórico também deve ser monotônico;
- polling temporariamente vazio não pode apagar os candles.

---

## Não alterar

Não alterar:

- Browser Bridge;
- Payload Adapter;
- MarketPipeline;
- Market Event Engine;
- CandleStore como arquitetura;
- Connector;
- OAuth;
- execução;
- AutoTrade;
- IA;
- indicadores;
- origem dos dados;
- segurança da integração.

Alterar Store ou Chart API apenas se for necessário corrigir leitura/ordenação real, sem criar nova fonte ou duplicação.

---

## Não implementar

Não implementar:

- dados simulados para preencher lacunas;
- interpolação de candles;
- sinais;
- CALL;
- PUT;
- entradas automáticas;
- IA;
- EMA;
- RSI;
- MACD;
- ATR;
- Probability Engine.

---

## Testes obrigatórios

Criar testes para:

1. Série com seis candles seguida de resposta com dois permanece com seis.
2. Candle com mesmo timestamp atualiza OHLC.
3. Candle com timestamp novo é acrescentado.
4. Candle duplicado não aumenta o total.
5. Resposta vazia preserva histórico.
6. Erro de polling preserva histórico.
7. Resposta atrasada não sobrescreve resposta mais nova.
8. Request de série antiga é ignorado após troca.
9. Merge ordena candles por `time`.
10. Limite remove apenas candles mais antigos.
11. Série não diminui durante mesma seleção.
12. `series.update()` é usado em atualização normal.
13. `series.update()` é usado no append.
14. `setData()` não é usado para resposta parcial normal.
15. `fitContent()` não executa a cada polling.
16. Zoom e pan não são resetados.
17. Seguir Polarium mantém série monotônica.
18. Modo manual mantém série monotônica.
19. Troca real de série realiza reset controlado.
20. Resposta antiga de outro contexto não altera a tela atual.

---

## Validação visual obrigatória

Após implementação:

1. Alimentar o CandleStore com dados reais da Polarium.
2. Abrir `/market-chart`.
3. Manter `Seguir Polarium` ligado.
4. Observar o gráfico por pelo menos dois minutos.
5. Confirmar que a contagem segue ordem crescente ou permanece estável.
6. Confirmar que não ocorre regressão de seis para dois candles.
7. Confirmar que o candle aberto atualiza suavemente.
8. Confirmar que novos candles surgem sem reset.
9. Fazer zoom.
10. Fazer pan.
11. Aguardar novo candle.
12. Confirmar que zoom/pan não são destruídos.
13. Desligar `Seguir Polarium`.
14. Confirmar estabilidade em modo manual.

---

## Testes e build

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

.venv/bin/python -m pytest -q tests/market/chart tests/frontend

.venv/bin/python -m pytest -q

cd frontend
npm run build
```

---

## Entrega obrigatória

1. Objetivo.
2. Causa raiz comprovada.
3. Origem do encolhimento: API, frontend, race condition ou combinação.
4. Arquivos criados.
5. Arquivos modificados.
6. Estratégia de merge monotônico.
7. Estratégia contra respostas atrasadas.
8. Estratégia de reset controlado.
9. Como preserva zoom e pan.
10. Como utiliza `series.update()`.
11. Quando utiliza `setData()`.
12. Como preserva histórico em resposta parcial.
13. Como preserva histórico em erro temporário.
14. Testes criados.
15. Resultado dos testes específicos.
16. Resultado da suíte completa.
17. Resultado do build.
18. Como testar para o Renan.
19. Validação visual necessária.
20. Riscos conhecidos.
21. Débitos técnicos.
22. `git status --short`.
23. `git diff --stat`.
24. Sugestão de commit.

Mensagem sugerida:

```text
fix(chart): preserve monotonic live candle history
```

---

## Regra final

Não fazer commit.

Não fazer push.

Não inventar candles.

Não mascarar o problema com dados sintéticos.

A experiência final deve se aproximar do comportamento contínuo e incremental de plataformas como Polarium e TradingView.