# Friday Trade — Sprint V4.1

# Compact Analysis Workspace

## Status

PLANNED

---

## Objetivo

Transformar a página `/market-chart` em uma central compacta de análise, otimizada para MacBook de 13 polegadas.

A tela deverá permitir:

- escolher o ativo que será analisado;
- escolher o timeframe disponível;
- visualizar o gráfico inteiro sem rolagem vertical excessiva;
- acompanhar o último candle;
- visualizar a preparação da entrada;
- acessar as principais informações operacionais na mesma tela.

Esta Sprint não executa operações.

Esta Sprint não envia CALL ou PUT.

Esta Sprint não cria AutoTrade.

Esta Sprint não inventa sinais, probabilidades ou indicadores.

---

## Fluxo oficial

Toda informação deve vir exclusivamente de:

```text
Polarium
→ Browser Bridge
→ Payload Adapter
→ MarketPipeline
→ CandleStore
→ Chart API
→ Compact Analysis Workspace
```

Não criar outra fonte de dados.

Não abrir outro WebSocket.

---

## Página principal

Modificar:

```text
/market-chart
```

A página deverá se tornar o workspace principal de análise.

Não criar uma página duplicada.

---

## Requisito principal de layout

O workspace deve ser totalmente utilizável em um MacBook de 13 polegadas.

Viewport de referência:

```text
1440 × 900
1366 × 768
1280 × 800
```

Em viewport desktop compacto, os elementos principais deverão caber em uma única tela:

- cabeçalho compacto;
- seletor de ativo;
- seletor de timeframe;
- gráfico;
- painel de preparação da entrada;
- último candle;
- status da fonte.

Evitar scroll vertical longo.

Não usar cards gigantes.

Não repetir informações já presentes no Header global.

---

## Estrutura visual recomendada

```text
┌────────────────────────────────────────────────────────────┐
│ Ativo | Timeframe | Fonte | Status | Última atualização   │
├──────────────────────────────────────┬─────────────────────┤
│                                      │ Contexto da análise │
│                                      │                     │
│             GRÁFICO                  │ Último candle       │
│                                      │ Entrada             │
│                                      │ Confirmações        │
│                                      │ Status              │
└──────────────────────────────────────┴─────────────────────┘
```

Distribuição aproximada:

```text
Gráfico: 75% da largura
Painel lateral: 25% da largura
```

O gráfico deve ter prioridade visual.

---

## Seleção do ativo

Criar seletor usando somente séries reais detectadas pelo Browser Bridge.

O seletor deverá usar os `active_id` observados e disponíveis no CandleStore.

Exemplo temporário:

```text
Active ID 1941
Active ID 1978
Active ID 2270
```

Não inventar nomes como EUR/USD, ETH/USD ou BTC/USD enquanto o mapeamento não estiver confirmado.

Mostrar no seletor, quando disponível:

```text
Active ID
quantidade de candles
último evento
status da série
```

Ao selecionar outro ativo:

- atualizar a série da Chart API;
- atualizar o gráfico;
- atualizar o último candle;
- atualizar o painel de análise;
- não recarregar a página inteira.

---

## Seleção do timeframe

Exibir somente timeframes reais observados para o ativo selecionado.

Mapeamentos confirmados:

```text
60  → M1
300 → M5
900 → M15
```

Outros valores:

```text
<raw_size>s
```

Não mostrar um timeframe que não possua série disponível no Store.

Ao trocar timeframe:

- trocar automaticamente a série;
- preservar o restante do layout;
- atualizar o gráfico sem reload completo;
- manter loading discreto.

---

## Gráfico

O gráfico deve:

- ficar totalmente visível no viewport compacto;
- ocupar a maior parte da área útil;
- preservar zoom;
- preservar pan;
- preservar crosshair;
- acompanhar atualizações dos candles;
- não ser recriado a cada polling;
- ajustar altura conforme o viewport;
- possuir altura mínima segura.

Evitar altura fixa excessiva.

Preferir cálculo responsivo baseado em:

```text
100dvh
altura do Header
altura da toolbar
margens
```

---

## Painel lateral

Criar painel lateral compacto com as seguintes seções.

### Último candle

Mostrar:

```text
Open
High
Low
Close
Data e hora formatadas
```

Não exibir apenas timestamp Unix como informação principal.

O timestamp bruto pode permanecer em área técnica ou tooltip.

### Preparação da entrada

Mostrar somente informações reais e estados conhecidos:

```text
Direção: Não calculada
Entrada: Aguardando análise
Expiração: Não definida
Confirmações: 0
Estado: Dados recebidos / Dados insuficientes
```

Não inventar:

- COMPRA;
- VENDA;
- CALL;
- PUT;
- confiança;
- probabilidade;
- assertividade;
- ponto exato de entrada;
- expiração recomendada.

A seção deve ficar preparada para receber essas informações em Sprints futuras.

### Checklist da análise

Exibir:

```text
Fonte real conectada
Ativo selecionado
Timeframe selecionado
Candles disponíveis
Quantidade mínima
Última atualização
```

Estados:

```text
READY
PARTIAL
BLOCKED
```

Usar dados reais.

---

## Quantidade de candles

Mostrar no workspace:

```text
5 candles carregados
```

e indicar a quantidade mínima futura para análise:

```text
5 de 100 candles
```

Isso não deve marcar a análise como pronta antes de atingir o requisito definido.

---

## Status da fonte

Mostrar de forma compacta:

```text
POLARIUM AUTHORIZED BROWSER LIVE
```

ou:

```text
DISCONNECTED
```

ou:

```text
SIMULATED / CONTROLLED DEVELOPMENT DATA
```

Nunca apresentar dados simulados como reais.

---

## Troca automática e manual

O Browser Bridge continuará detectando a série ativa da Polarium.

A seleção manual no Friday Trade deverá permitir analisar outra série já existente no CandleStore.

Regras:

- a detecção automática define a seleção inicial;
- o usuário pode alterar manualmente;
- novos eventos não devem sobrescrever imediatamente uma escolha manual;
- criar opção `Seguir Polarium`;
- quando `Seguir Polarium` estiver ativo, acompanhar as trocas realizadas na plataforma;
- quando estiver desativado, manter a seleção escolhida no Friday Trade.

---

## Responsividade

### Desktop amplo

Gráfico e painel lateral lado a lado.

### MacBook de 13 polegadas

Gráfico e painel lateral lado a lado, com cards compactos.

O gráfico precisa permanecer visível sem rolagem longa.

### Largura reduzida

O painel pode ficar abaixo do gráfico, mas sem quebrar a aplicação.

---

## Não alterar

Não alterar:

- Browser Bridge;
- Payload Adapter;
- MarketPipeline;
- CandleStore;
- Market Event Engine;
- Connector;
- OAuth;
- runtime real;
- runtime simulator;
- APIs de execução;
- Indicator Engine.

Alterar backend somente se for estritamente necessário criar uma leitura agregada e read-only das séries disponíveis.

Não duplicar Store.

---

## Não implementar

Não implementar:

- execução de ordem;
- AutoTrade;
- CALL;
- PUT;
- sinais;
- Probability Engine;
- IA;
- EMA;
- RSI;
- MACD;
- ATR;
- martingale;
- Gale;
- gestão financeira operacional.

---

## Testes obrigatórios

Criar ou atualizar testes para:

- detecção das séries disponíveis;
- seleção manual de ativo;
- seleção manual de timeframe;
- modo `Seguir Polarium`;
- preservação da escolha manual;
- troca da série sem reload;
- último candle atualizado;
- timestamp formatado;
- estado vazio;
- fonte desconectada;
- poucos candles;
- readiness;
- ausência de sinal inventado;
- layout sem overflow horizontal;
- viewport compacto.

Quando possível, criar teste estrutural garantindo que o workspace não use alturas fixas incompatíveis com MacBook de 13 polegadas.

---

## Validação visual obrigatória

Testar em:

```text
1440 × 900
1366 × 768
1280 × 800
```

Confirmar:

- toolbar visível;
- seletor de ativo visível;
- seletor de timeframe visível;
- gráfico integralmente utilizável;
- painel lateral visível;
- sem scroll vertical excessivo;
- sem sobreposição;
- sem cards cortados;
- sem overflow horizontal;
- gráfico atualizando.

Enviar prints em pelo menos:

```text
1440 × 900
1280 × 800
```

---

## Testes e build

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

.venv/bin/python -m pytest -q

cd frontend
npm run build
```

---

## Entrega obrigatória

1. Objetivo.
2. Diagnóstico do layout atual.
3. Arquitetura visual adotada.
4. Arquivos criados.
5. Arquivos modificados.
6. Como funciona a seleção de ativo.
7. Como funciona a seleção de timeframe.
8. Como funciona `Seguir Polarium`.
9. Como a escolha manual é preservada.
10. Como o gráfico foi otimizado para 13 polegadas.
11. Como a altura é calculada.
12. Informações exibidas no painel de entrada.
13. Readiness implementado.
14. Testes criados.
15. Resultado dos testes específicos.
16. Resultado da suíte completa.
17. Resultado do build.
18. Como testar.
19. Validação visual.
20. Riscos conhecidos.
21. Débitos técnicos.
22. `git status --short`.
23. `git diff --stat`.
24. Sugestão de commit.

Mensagem sugerida:

```text
feat(chart): add compact asset analysis workspace
```

---

## Regra final

Não fazer commit.

Não fazer push.

Não inventar sinais, nomes de ativos ou informações de entrada.

Priorizar a usabilidade em MacBook de 13 polegadas e a visualização integral do gráfico.