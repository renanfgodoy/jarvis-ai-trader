# SPRINT V4.5.14 — REALTIME PUSH AND VISUAL FIDELITY

## Objetivo

Reduzir a latência visual entre um candle real recebido da IQ Option e sua exibição no Friday Trade.

O gráfico atual já utiliza realtime candle stream no worker, mas o frontend consulta o cache por HTTP aproximadamente a cada 1 segundo.

Fluxo atual:

```text
IQ candle-generated
→ worker atualiza cache
→ frontend espera próximo polling de 1 segundo
→ endpoint HTTP
→ React
→ RealCandleChart
```

Esse intervalo ainda produz percepção de atraso e pequenos saltos.

Fluxo desejado:

```text
IQ candle-generated
→ worker atualiza cache
→ backend envia evento imediatamente
→ frontend recebe
→ aplica OHLC real no próximo frame
→ RealCandleChart.series.update()
```

A Sprint deve priorizar fidelidade real, não animação artificial.

---

# REGRA DE OURO

É proibido:

- interpolar preços;
- criar valores intermediários;
- inventar ticks;
- suavizar o close para posições não recebidas;
- animar high ou low passando por valores não enviados;
- prever o próximo preço;
- gerar movimento visual apenas para parecer com a corretora.

Cada estado exibido da vela deve corresponder a um OHLC real recebido da IQ Option.

O Friday pode coordenar o momento da renderização, mas nunca alterar o conteúdo financeiro recebido.

---

# Contexto comprovado

As Sprints anteriores comprovaram:

- `start_candles_stream()` funciona em read-only;
- `get_realtime_candles()` fornece atualizações reais;
- EURUSD-OTC apresenta movimento próximo de 1 atualização por segundo;
- alguns ativos ficam LIMITED ou STALE;
- CandleStore atualiza candles com mesmo timestamp;
- `RealCandleChart` utiliza atualização incremental;
- polling realtime frontend ocorre aproximadamente a cada 1 segundo;
- polling de reconciliação permanece em 5 segundos;
- a qualidade varia por ativo;
- não existe igualdade absoluta com a corretora.

Problema restante:

Mesmo quando o worker recebe um evento real, o frontend pode esperar até o próximo polling HTTP para visualizá-lo.

---

# PARTE 1 — AUDITORIA DE LATÊNCIA PONTA A PONTA

## 1. Timestamps obrigatórios

Adicionar ou localizar timestamps suficientes para medir:

```text
provider_event_at
```

Momento informado pelo evento da IQ Option, quando disponível.

```text
worker_received_at
```

Momento em que o worker percebeu a alteração.

```text
backend_published_at
```

Momento em que o backend disponibilizou ou publicou o evento.

```text
frontend_received_at
```

Momento em que o navegador recebeu o evento.

```text
chart_applied_at
```

Momento em que o candle foi aplicado ao gráfico.

Não utilizar esses timestamps como preço.

Não expor credenciais ou payloads sensíveis.

---

## 2. Métricas

Calcular:

```text
worker_processing_ms
```

```text
backend_delivery_ms
```

```text
frontend_apply_ms
```

```text
total_delivery_ms
```

Quando `provider_event_at` não representar horário confiável de geração, declarar explicitamente que a latência absoluta não pode ser calculada.

Nesse caso, medir pelo menos:

```text
worker_received_at
→ chart_applied_at
```

Apresentar:

- média;
- p50;
- p95;
- maior valor;
- quantidade acima de 250ms;
- quantidade acima de 500ms;
- quantidade acima de 1000ms.

---

# PARTE 2 — CANAL DE ENTREGA AO FRONTEND

## 3. Auditoria das opções

Comparar tecnicamente:

### Opção A — polling HTTP atual

```text
GET realtime-candles a cada 1 segundo
```

### Opção B — Server-Sent Events

```text
backend → EventSource frontend
```

### Opção C — WebSocket

```text
backend ↔ frontend
```

A aplicação não precisa de comunicação bidirecional para esta função.

Preferir o menor canal unidirecional compatível com:

- FastAPI;
- React;
- conexão local;
- um ativo selecionado;
- cleanup simples;
- reconexão nativa;
- baixo risco;
- read-only.

SSE deve ser preferido ao WebSocket caso atenda integralmente ao caso.

Não implementar ambos.

---

## 4. Critério para implementação push

Implementar entrega push somente se:

1. reduzir o atraso do polling atual;
2. reutilizar o worker e o cache existentes;
3. não abrir nova conexão com a IQ Option;
4. não duplicar subscriptions IQ;
5. preservar read-only;
6. permitir cancelar o contexto anterior;
7. suportar ativo e timeframe selecionados;
8. possuir reconexão segura;
9. não exigir dependência nova desnecessária;
10. possuir testes automatizados.

Caso SSE ou WebSocket não seja tecnicamente viável, manter polling e explicar a limitação.

Não simular push no frontend.

---

# PARTE 3 — SSE PREFERENCIAL

## 5. Endpoint conceitual

Caso SSE seja escolhido, criar endpoint read-only equivalente a:

```text
GET /api/v1/market/providers/iq-option/realtime-candles/stream
```

Parâmetros esperados:

```text
symbol
market_type
raw_size
```

Não alterar os endpoints existentes.

O endpoint atual de realtime deve permanecer disponível como fallback e ferramenta de diagnóstico.

---

## 6. Contrato do evento

Cada evento deve possuir somente dados necessários e sanitizados.

Exemplo conceitual:

```json
{
  "provider": "IQ_OPTION",
  "market_type": "OTC",
  "symbol": "EURUSD-OTC",
  "raw_size": 60,
  "source_mode": "NEAR_REALTIME",
  "sequence": 152,
  "received_at": 1783900000123,
  "candle": {
    "timestamp": 1783899960,
    "open": 1.11310,
    "high": 1.11322,
    "low": 1.11308,
    "close": 1.11319
  }
}
```

Não enviar o histórico completo em cada evento.

Enviar apenas:

- candle alterado;
- metadata mínima;
- sequência;
- modo da fonte;
- timestamp de recebimento.

---

## 7. Sequência

Cada contexto realtime deve possuir uma sequência crescente:

```text
1
2
3
4
```

O frontend deve ignorar evento com sequência:

```text
<= última sequência aplicada
```

Ao trocar ativo, mercado ou timeframe:

- encerrar conexão anterior;
- zerar sequência local;
- iniciar novo contexto;
- voltar para CHECKING;
- não reutilizar evento anterior.

---

## 8. Heartbeat

O canal pode enviar heartbeat sem candle em intervalo controlado, por exemplo:

```text
10 segundos
```

O heartbeat deve servir apenas para:

- confirmar conexão;
- evitar timeout intermediário;
- detectar canal desconectado.

Heartbeat não conta como:

- movimento de preço;
- nova vela;
- atualização OHLC;
- feed LIVE.

---

## 9. Cleanup

Ao desconectar o navegador:

- remover assinante;
- não necessariamente parar imediatamente a stream IQ se outro assinante usar o mesmo contexto;
- não acumular filas;
- limpar recursos;
- evitar task órfã.

Ao trocar ativo:

```text
fechar EventSource anterior
→ backend remove assinante
→ runtime muda contexto
→ novo EventSource
```

Não permitir que falha no cleanup anterior contamine o novo ativo.

---

# PARTE 4 — FALLBACK

## 10. Fallback obrigatório

Se o canal push:

- falhar;
- desconectar;
- não receber eventos;
- retornar erro;
- ficar sem heartbeat;

o frontend deve voltar temporariamente para:

```text
polling realtime HTTP de 1 segundo
```

Exibir:

```text
MODO DE ENTREGA
POLLING DE FALLBACK
```

Quando o push reconectar:

- evitar candles duplicados;
- comparar sequência e timestamp;
- retomar sem apagar o histórico.

O polling oficial de reconciliação de 5 segundos continua existindo.

---

# PARTE 5 — APLICAÇÃO NO GRÁFICO

## 11. Aplicação exata

Ao receber OHLC real:

1. validar contexto;
2. validar sequência;
3. validar timestamp;
4. confirmar se houve mudança;
5. agendar aplicação no próximo `requestAnimationFrame`;
6. chamar atualização incremental;
7. registrar `chart_applied_at`.

O `requestAnimationFrame()` serve apenas para evitar alteração no meio do ciclo de pintura do navegador.

Não criar múltiplos frames intermediários.

Exemplo permitido:

```text
evento recebido
→ requestAnimationFrame
→ series.update(candle_real)
```

Exemplo proibido:

```text
close 1.1000
→ 1.1001
→ 1.1002
→ 1.1003
→ close real 1.1004
```

---

## 12. Coalescing

Se vários eventos reais chegarem antes do próximo frame:

- aplicar somente o evento real mais recente daquele candle no frame seguinte;
- preservar high máximo real;
- preservar low mínimo real;
- não perder novo timestamp;
- não contar eventos descartados como renderizados.

Registrar:

```text
events_received
events_coalesced
chart_updates
```

---

## 13. Novo candle

Ao receber timestamp de bucket novo:

- aplicar o candle anterior final, se necessário;
- adicionar a nova vela;
- não misturar com a anterior;
- não duplicar bucket;
- não depender do polling de 5 segundos para mostrar a abertura.

A reconciliação posterior pode corrigir divergências comprovadas.

---

# PARTE 6 — PAINEL DE DIAGNÓSTICO

## 14. HUD DEV

Adicionar um modo de diagnóstico discreto, preferencialmente expansível.

Informações:

```text
FONTE IQ
CANDLE STREAM
```

```text
ENTREGA
SSE
```

ou:

```text
ENTREGA
POLLING FALLBACK
```

```text
QUALIDADE
GOOD
```

```text
EVENTOS RECEBIDOS
84
```

```text
ATUALIZAÇÕES DO GRÁFICO
76
```

```text
ÚLTIMO EVENTO
há 180ms
```

```text
ÚLTIMA APLICAÇÃO
há 165ms
```

```text
ENTREGA MÉDIA
42ms
```

```text
P95
91ms
```

```text
SEQUÊNCIA
152
```

```text
RECONEXÕES
0
```

```text
FALLBACKS
0
```

Não misturar latência do backend com frequência do preço.

---

## 15. Indicador principal

O usuário normal deve continuar vendo:

```text
PRÓXIMO DO TEMPO REAL
```

ou:

```text
ATUALIZAÇÃO POR SNAPSHOT
```

ou:

```text
DADOS ATRASADOS
```

Adicionar o modo de entrega em texto secundário:

```text
Entrega instantânea por SSE
```

ou:

```text
Entrega por polling de 1s
```

Não utilizar a palavra “instantânea” se a medição mostrar atraso elevado.

Pode utilizar:

```text
Entrega por push
```

---

# PARTE 7 — COMPARAÇÃO VISUAL

## 16. Teste lado a lado

Comparar manualmente:

```text
IQ Option
Friday Trade
```

Configuração:

```text
EURUSD-OTC
M1
```

Observar ao menos três velas completas.

Verificar:

- direção;
- mudança do corpo;
- aparecimento dos pavios;
- nova máxima;
- nova mínima;
- abertura de nova vela;
- contador;
- preço atual;
- cadência;
- diferença perceptível.

Não comparar com Polarium como fonte principal da validação.

---

## 17. Medição visual

Registrar:

- tempo percebido entre movimento na IQ e no Friday;
- quantidade de movimentos percebidos primeiro na IQ;
- quantidade percebida praticamente junto;
- maior atraso visual;
- ocorrência de congelamento superior a 2 segundos;
- ocorrência de salto grande;
- consistência dos pavios.

Essa medição manual é aproximada e deve ser identificada como tal.

---

# PARTE 8 — PERFORMANCE

## 18. Teste contínuo

Executar EURUSD-OTC M1 por:

```text
10 minutos
```

Registrar:

- conexão push;
- eventos recebidos;
- atualizações aplicadas;
- eventos coalescidos;
- reconexões;
- fallbacks;
- erros;
- maior intervalo sem evento;
- número de assinantes;
- tasks do backend, quando acessível;
- threads do worker;
- crescimento de memória;
- renderizações React;
- recriações do gráfico;
- resets de zoom.

Critérios:

- sem crescimento contínuo de assinantes;
- sem EventSource duplicado;
- sem reconexão em loop;
- sem polling realtime paralelo quando SSE está saudável;
- reconciliação de 5s preservada;
- frontend responsivo.

---

## 19. Troca intensiva

Executar:

```text
EURUSD-OTC
→ GBPUSD-OTC
→ USDJPY-OTC
→ EURJPY-OTC
→ EURUSD-OTC
```

Repetir o ciclo três vezes.

Confirmar:

- apenas uma entrega ativa no frontend;
- assinante antigo removido;
- contexto anterior ignorado;
- nenhuma atualização cruzada;
- sem 502;
- sem vazamento;
- sem gráfico do ativo anterior.

---

## 20. Troca de timeframe

Executar:

```text
M1
→ M5
→ M15
→ M1
```

Confirmar:

- raw_size correto;
- endpoint push correto;
- contexto reiniciado;
- countdown correto;
- nenhuma vela de timeframe anterior.

---

# PARTE 9 — SEGURANÇA

## 21. Runtime Guard

Preservar integralmente.

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

O canal backend/frontend não pode introduzir qualquer operação.

Não expor:

- e-mail;
- senha;
- sessão;
- cookies;
- tokens;
- payload interno sensível.

---

# PARTE 10 — TESTES

## 22. Backend

Adicionar testes para:

1. endpoint push é read-only;
2. evento possui candle sanitizado;
3. sequência cresce;
4. heartbeat não conta como movimento;
5. assinante é removido ao desconectar;
6. troca de contexto invalida stream anterior;
7. evento antigo não é publicado no contexto atual;
8. múltiplos assinantes não criam múltiplas conexões IQ sem necessidade;
9. fila lenta não cresce indefinidamente;
10. disconnect limpa recurso;
11. fallback HTTP continua disponível;
12. Runtime Guard permanece ativo.

Executar:

```bash
.venv/bin/python -m pytest tests/market/providers tests/market/store tests/api -q
```

---

## 23. Frontend

Adicionar testes para:

1. abre EventSource no contexto correto;
2. fecha EventSource ao trocar ativo;
3. fecha ao desmontar;
4. ignora sequência antiga;
5. ignora contexto anterior;
6. aplica candle no próximo animation frame;
7. não interpola preço;
8. coalescing utiliza o último evento real;
9. novo timestamp adiciona nova vela;
10. queda do SSE ativa polling fallback;
11. reconexão desativa fallback duplicado;
12. polling de 5s continua para reconciliação;
13. HUD mostra entrega;
14. STALE permanece bloqueado;
15. heartbeat não marca movimento;
16. nenhuma animação cria OHLC intermediário.

Executar:

```bash
.venv/bin/python -m pytest tests/frontend -q
```

---

## 24. Suíte completa

```bash
.venv/bin/python -m pytest -q
```

---

## 25. Build

```bash
cd frontend
npm run build
cd ..
```

---

# PARTE 11 — ARQUIVOS PERMITIDOS

Alterar somente o necessário em:

```text
app/api/routes/
app/market/providers/iq_option/
frontend/src/pages/
frontend/src/components/
tests/
```

Pode criar helper pequeno e específico para:

- transporte SSE;
- métricas;
- aplicação de eventos;
- HUD.

Não criar plataforma genérica de eventos.

Não instalar dependência se FastAPI e navegador já atenderem ao caso.

Não alterar Polarium.

Não instalar `iqoptionapi` na `.venv` principal.

---

# PARTE 12 — ENTREGA ESPERADA

Entregar relatório contendo:

1. causa do atraso visual restante;
2. medição antes da correção;
3. comparação polling vs SSE vs WebSocket;
4. canal escolhido;
5. justificativa;
6. arquivos modificados;
7. diff funcional por arquivo;
8. contrato do evento;
9. regra de sequência;
10. regra de heartbeat;
11. regra de cleanup;
12. regra de fallback;
13. regra de requestAnimationFrame;
14. confirmação de que não existe interpolação;
15. eventos recebidos;
16. eventos aplicados;
17. eventos coalescidos;
18. latência média;
19. p50;
20. p95;
21. maior atraso;
22. resultado do teste de 10 minutos;
23. resultado da troca intensiva;
24. resultado da troca de timeframe;
25. resultado visual EURUSD-OTC;
26. diferença visual para IQ Option;
27. resultado do HUD;
28. testes backend;
29. testes frontend;
30. suíte completa;
31. build;
32. Runtime Guard;
33. `git status --short`;
34. `git diff --stat`;
35. limitações;
36. riscos;
37. sugestão de commit.

Não fazer commit.

Não fazer push.

Não inventar preços.

Não afirmar igualdade absoluta com a corretora.