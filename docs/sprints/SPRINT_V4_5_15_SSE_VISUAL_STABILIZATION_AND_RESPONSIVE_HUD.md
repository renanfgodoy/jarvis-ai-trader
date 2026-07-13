# SPRINT V4.5.15 — SSE VISUAL STABILIZATION AND RESPONSIVE HUD

## Objetivo

Corrigir a quebra visual dos cards superiores e do painel de diagnóstico do Friday Trade em janelas estreitas ou divididas.

Também homologar o ciclo completo do SSE no navegador real:

```text
conectar
→ receber eventos
→ atualizar gráfico
→ trocar ativo
→ trocar timeframe
→ fechar conexão anterior
→ evitar fallback indevido
→ evitar assinantes órfãos
```

Não criar nova arquitetura.

Não alterar a fonte IQ Option.

Não interpolar preços.

Não executar ordens.

---

# Contexto comprovado

A Sprint V4.5.14 implementou:

- endpoint SSE read-only;
- EventSource no frontend;
- sequência crescente;
- heartbeat;
- fallback para polling HTTP de 1 segundo;
- reconciliação por candles a cada 5 segundos;
- aplicação no próximo `requestAnimationFrame`;
- HUD DEV;
- cleanup ao trocar contexto.

Problema visual observado manualmente:

Em janela dividida, os cards superiores ficam estreitos e quebram palavras de forma incorreta.

Exemplos observados:

```text
ATUALI
ZAÇÃO
POR
SNAPS
HOT
```

```text
proxim
a vela
```

O layout precisa continuar legível sem esconder informações importantes.

---

# PARTE 1 — CORREÇÃO DOS CARDS SUPERIORES

## 1. Elementos afetados

Auditar os cards:

```text
FONTE
MODO
ENTREGA
FEED
```

e qualquer card adjacente da mesma faixa.

Localizar:

- container principal;
- grid;
- flex;
- largura mínima;
- gap;
- padding;
- tamanho da fonte;
- line-height;
- regras de quebra;
- overflow.

Registrar arquivo e linhas.

---

## 2. Regra de quebra de texto

É proibido quebrar palavras no meio.

Não permitir:

```text
proxim
a
```

ou:

```text
SNAPS
HOT
```

Aplicar regras equivalentes a:

```css
word-break: normal;
overflow-wrap: normal;
hyphens: none;
```

Textos podem quebrar apenas entre palavras.

---

## 3. Largura mínima

Cada card deve possuir largura mínima suficiente para manter leitura.

Usar abordagem responsiva equivalente a:

```css
grid-template-columns: repeat(4, minmax(...));
```

ou:

```css
display: flex;
flex-wrap: wrap;
```

A escolha deve preservar:

- equilíbrio visual;
- altura semelhante;
- textos completos;
- sem overflow lateral indevido.

Não fixar larguras que quebrem em telas menores.

---

## 4. Comportamento responsivo oficial

### Tela larga

Quatro cards em uma linha:

```text
FONTE | MODO | ENTREGA | FEED
```

### Janela média

Pode usar:

```text
FONTE | MODO
ENTREGA | FEED
```

### Janela estreita

Pode usar uma coluna ou rolagem horizontal controlada.

Preferir grid de duas colunas antes de usar uma coluna.

Não comprimir quatro cards até quebrar palavras.

---

## 5. Textos curtos

Revisar os textos para evitar redundância.

Exemplos desejados:

### Fonte

```text
IQ OPTION
READ ONLY
```

### Modo

```text
PRÓXIMO DO TEMPO REAL
```

ou:

```text
SNAPSHOT
```

### Entrega

```text
SSE
```

Texto secundário:

```text
Push em tempo real
```

Fallback:

```text
POLLING 1s
```

### Feed

```text
Próxima vela: 00:32
Resposta: há 1s
```

Evitar frases longas como:

```text
Entrega por polling de 1s
```

quando o espaço estiver reduzido.

---

## 6. Tipografia responsiva

Usar `clamp()` ou regra equivalente para:

- títulos;
- valores;
- textos secundários.

Não reduzir texto a ponto de ficar ilegível.

Manter contraste e identidade visual do Friday.

---

# PARTE 2 — HUD DEV RESPONSIVO

## 7. Painel de diagnóstico

Auditar o HUD DEV para larguras menores.

Ele deve exibir:

- entrega;
- qualidade;
- eventos;
- updates;
- coalescing;
- último evento;
- última aplicação;
- média;
- p95;
- sequência;
- reconexões;
- fallbacks;
- heartbeat;
- status.

Em tela estreita:

- usar duas colunas;
- ou uma coluna compacta;
- sem cortar valores;
- sem estourar o container.

---

## 8. HUD recolhível

O HUD DEV deve ser expansível/recolhível.

Estado recolhido:

```text
DIAGNÓSTICO DEV
SSE • GOOD • 0 fallbacks
```

Estado expandido:

mostrar todas as métricas.

O estado recolhido deve continuar mostrando o essencial.

Não ocupar grande parte da tela permanentemente.

---

## 9. Conteúdo técnico

Corrigir nomenclaturas para evitar interpretações erradas.

Usar:

```text
LATÊNCIA LOCAL
```

em vez de apenas:

```text
LATÊNCIA
```

Usar:

```text
EVENTOS DE CANDLE
```

em vez de:

```text
CANDLES
```

quando representar atualizações da mesma vela.

Não insinuar que 559 eventos são 559 velas diferentes.

---

# PARTE 3 — VALIDAÇÃO DO SSE NO FRONTEND REAL

## 10. Estado esperado

Com SSE saudável, os cards devem mostrar:

```text
ENTREGA
SSE
```

e:

```text
Fallbacks: 0
```

Não mostrar:

```text
Entrega por polling de 1s
```

quando o EventSource estiver conectado e recebendo heartbeat/eventos.

---

## 11. Diagnóstico de fallback indevido

Caso a tela continue mostrando polling de 1 segundo:

Auditar:

- URL do EventSource;
- CORS;
- resposta HTTP;
- `Content-Type: text/event-stream`;
- conexão mantida aberta;
- heartbeat;
- `onopen`;
- `onmessage`;
- `onerror`;
- timeout de heartbeat;
- condição que ativa fallback;
- condição que desativa fallback.

Não esconder o problema alterando apenas o texto.

---

## 12. Estados de entrega

Implementar claramente:

```text
CONNECTING
SSE
POLLING_FALLBACK
RECONNECTING
DISCONNECTED
```

Exibição em português:

```text
CONECTANDO
SSE ATIVO
POLLING DE SEGURANÇA
RECONECTANDO
DESCONECTADO
```

Não marcar SSE ativo apenas porque o EventSource foi criado.

Exigir:

- `onopen`;
- ou evento/heartbeat válido recente.

---

# PARTE 4 — LIFECYCLE E RECURSOS

## 13. Troca de ativo

Ao trocar:

```text
EURUSD-OTC
→ GBPUSD-OTC
```

confirmar:

1. `EventSource.close()` no contexto anterior;
2. `requestAnimationFrame` anterior cancelado;
3. heartbeat timer anterior limpo;
4. fallback anterior limpo;
5. sequência reiniciada;
6. contexto antigo ignorado;
7. novo SSE criado;
8. apenas uma conexão ativa no navegador.

---

## 14. Troca de timeframe

Ao trocar:

```text
M1
→ M5
→ M15
→ M1
```

confirmar:

- EventSource anterior fechado;
- `raw_size` correto;
- sequência reiniciada;
- sem eventos do timeframe anterior;
- countdown correto;
- nenhuma conexão duplicada.

---

## 15. Desmontagem

Ao sair de `/market-chart`:

- fechar EventSource;
- cancelar timers;
- cancelar animation frame;
- interromper fallback;
- remover assinante backend;
- não deixar reconexão automática ativa.

---

## 16. Contagem de assinantes

Adicionar diagnóstico interno ou teste que permita confirmar:

```text
subscribers_before
subscribers_after_connect
subscribers_after_switch
subscribers_after_disconnect
```

Resultado esperado em uma única tela:

```text
0
1
1
0
```

Não permitir crescimento:

```text
1
2
3
4
```

após trocas.

---

# PARTE 5 — HOMOLOGAÇÃO VISUAL

## 17. Larguras obrigatórias

Validar em aproximadamente:

```text
1440px
1200px
1024px
768px
```

e em janela dividida semelhante ao print enviado pelo Renan.

Também validar zoom do navegador:

```text
100%
90%
80%
```

Não utilizar zoom como correção do layout.

---

## 18. Critérios visuais

Confirmar:

- nenhuma palavra quebrada no meio;
- nenhum card estourando;
- nenhuma informação cortada;
- valores centralizados;
- alturas equilibradas;
- espaçamento consistente;
- gráfico preserva espaço suficiente;
- HUD não cobre o gráfico;
- sidebar e contexto permanecem utilizáveis.

---

## 19. Print obrigatório

Produzir ou solicitar prints de:

### Print A

Tela completa em largura normal.

### Print B

Janela dividida igual ao caso reportado.

### Print C

HUD DEV expandido.

### Print D

HUD DEV recolhido.

### Print E

SSE ativo com:

```text
Fallbacks: 0
```

### Print F

Fallback funcionando, apenas se for possível simular sem alterar arquitetura.

---

# PARTE 6 — TESTES

## 20. Frontend

Adicionar testes para:

1. cards não usam `word-break: break-all`;
2. palavras não são quebradas no meio;
3. grid muda de quatro para duas colunas;
4. layout possui fallback para largura estreita;
5. HUD é recolhível;
6. HUD recolhido mostra resumo;
7. latência é identificada como local;
8. eventos são identificados como atualizações;
9. SSE ativo mostra texto correto;
10. fallback mostra texto correto;
11. CONNECTING não aparece como SSE ativo;
12. troca de ativo fecha EventSource;
13. troca de timeframe fecha EventSource;
14. desmontagem fecha EventSource;
15. fallback é desativado quando SSE recupera;
16. somente um EventSource permanece ativo;
17. heartbeat recente mantém SSE saudável;
18. heartbeat vencido ativa fallback;
19. polling de 5s permanece reconciliação;
20. nenhuma interpolação é adicionada.

Executar:

```bash
.venv/bin/python -m pytest tests/frontend -q
```

---

## 21. Backend/API

Adicionar ou ajustar testes para:

1. assinante é adicionado ao conectar;
2. assinante é removido ao desconectar;
3. troca de contexto não acumula assinantes;
4. heartbeat mantém conexão;
5. fila é limitada;
6. conexão lenta não cresce indefinidamente;
7. contexto anterior não publica no novo;
8. endpoint mantém `text/event-stream`;
9. Runtime Guard permanece read-only.

Executar:

```bash
.venv/bin/python -m pytest tests/api tests/market/providers -q
```

---

## 22. Suíte completa

```bash
.venv/bin/python -m pytest -q
```

---

## 23. Build

```bash
cd frontend
npm run build
cd ..
```

---

# PARTE 7 — ARQUIVOS PREFERENCIAIS

Alterar preferencialmente:

```text
frontend/src/pages/MarketChart.tsx
frontend/src/components/
frontend/src/**/*.css
tests/frontend/
```

Backend somente se existir falha real de:

- assinantes;
- cleanup;
- lifecycle SSE.

Não alterar:

- worker IQ;
- descoberta de ativos;
- candles;
- CandleStore;
- Runtime Guard;
- Polarium.

---

# PARTE 8 — ENTREGA ESPERADA

Entregar relatório contendo:

1. causa exata da quebra visual;
2. arquivo e linhas afetadas;
3. estratégia responsiva aplicada;
4. regras de grid;
5. regras de tipografia;
6. comportamento em 1440px;
7. comportamento em 1200px;
8. comportamento em 1024px;
9. comportamento em 768px;
10. comportamento em janela dividida;
11. HUD expandido;
12. HUD recolhido;
13. estado real do SSE;
14. motivo de polling fallback, caso tenha ocorrido;
15. confirmação de `Content-Type`;
16. confirmação de heartbeat;
17. contagem de assinantes antes/depois;
18. resultado da troca de ativos;
19. resultado da troca de timeframe;
20. resultado da desmontagem;
21. arquivos modificados;
22. diff funcional;
23. testes frontend;
24. testes API/provider;
25. suíte completa;
26. build;
27. Runtime Guard;
28. prints ou roteiro de validação manual;
29. `git status --short`;
30. `git diff --stat`;
31. riscos restantes;
32. sugestão de commit.

Não fazer commit.

Não fazer push.

Não corrigir apenas escondendo textos.

Não ampliar CORS sem necessidade comprovada.

Não criar nova arquitetura.