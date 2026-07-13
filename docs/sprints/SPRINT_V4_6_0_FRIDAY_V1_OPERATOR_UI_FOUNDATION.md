# SPRINT V4.6.0 — FRIDAY V1 OPERATOR UI FOUNDATION

## Objetivo

Iniciar oficialmente a nova interface Friday V1.

A tela principal deve deixar de parecer um painel de desenvolvimento e passar a parecer uma plataforma profissional de análise para o operador.

A prioridade desta Sprint é:

```text
clareza
→ simplicidade
→ gráfico
→ contexto da análise
→ futura estratégia
```

Não implementar estratégia, CALL, PUT, score ou IA nesta Sprint.

Criar somente a fundação visual necessária para essas funções futuras.

---

# CONTEXTO

A interface atual exibe muitas informações técnicas na tela principal:

- provider;
- read-only;
- SSE;
- polling;
- heartbeat;
- latência;
- fallback;
- feed mode;
- eventos;
- sequência;
- diagnóstico;
- runtime;
- conexão.

Essas informações foram importantes durante o desenvolvimento, mas prejudicam:

- leitura;
- responsividade;
- espaço do gráfico;
- aparência profissional;
- foco do operador.

A Friday V1 deve priorizar:

- ativo;
- mercado;
- timeframe;
- gráfico;
- qualidade resumida dos dados;
- estratégia selecionada;
- análise;
- confluências;
- decisão futura.

---

# REGRA PRINCIPAL

A tela principal não deve mostrar detalhes técnicos que o operador não precisa conhecer.

Informações técnicas devem ficar disponíveis apenas em:

```text
Modo Desenvolvedor
```

ou:

```text
Painel de Diagnóstico
```

recolhido por padrão.

Não apagar o diagnóstico existente.

Não remover a capacidade de investigar SSE, polling, provider ou feed.

Apenas retirar esses detalhes da experiência principal.

---

# PARTE 1 — MODOS DA INTERFACE

## 1. Modo Operador

Criar o modo padrão:

```text
OPERADOR
```

Ele deve ser ativado por padrão ao abrir `/market-chart`.

No Modo Operador, exibir somente:

- seletor de mercado;
- seletor de ativo;
- seletor de timeframe;
- gráfico;
- status resumido da qualidade do mercado;
- espaço reservado para estratégia;
- espaço reservado para análise;
- espaço reservado para decisão futura.

Não mostrar:

- provider;
- SSE;
- polling;
- fallback;
- heartbeat;
- latência;
- sequência;
- subscribers;
- eventos;
- coalescing;
- endpoint;
- runtime;
- worker;
- logs.

---

## 2. Modo Desenvolvedor

Preservar um modo:

```text
DESENVOLVEDOR
```

Acesso discreto, por exemplo:

- botão no canto;
- engrenagem;
- menu de configurações;
- toggle “Modo DEV”.

Quando ativado, pode exibir:

- provider;
- SSE;
- polling;
- fallback;
- feed mode;
- latência local;
- heartbeat;
- última resposta;
- eventos;
- sequência;
- reconexões;
- assinantes;
- Runtime Guard;
- diagnóstico existente.

Por padrão deve iniciar fechado.

Não colocar o botão DEV em destaque maior que os controles de operação.

---

## 3. Persistência

Pode persistir a escolha do modo em:

```text
localStorage
```

Regras:

- primeira visita: Modo Operador;
- usuário ativa DEV: pode permanecer DEV após reload;
- oferecer forma simples de retornar ao Modo Operador.

Não utilizar backend para essa preferência.

---

# PARTE 2 — CABEÇALHO DO MARKET CHART

## 4. Cabeçalho principal

O cabeçalho deve exibir de forma limpa:

```text
FRIDAY TRADE
Análise de mercado
```

e os controles:

```text
Mercado
Ativo
Timeframe
```

O ativo deve ser visualmente mais importante que informações técnicas.

Exemplo conceitual:

```text
EUR/USD OTC
M1
```

---

## 5. Status resumido

Mostrar apenas um status simples próximo ao gráfico.

Estados permitidos:

### Feed utilizável

```text
MERCADO ATIVO
```

### Sem movimento recente

```text
MERCADO LENTO
```

### Snapshot ou qualidade limitada

```text
DADOS LIMITADOS
```

### Stale

```text
DADOS ATRASADOS
```

### Sem candles

```text
SEM DADOS
```

### Carregando

```text
VERIFICANDO MERCADO
```

Não exibir:

```text
SSE
NEAR_REALTIME
POLLING
HTTP
PROVIDER
```

no Modo Operador.

O estado interno pode continuar técnico, mas o texto principal deve ser humano.

---

## 6. Aviso operacional

Quando o feed estiver inadequado:

### STALE

```text
Análise indisponível
Os dados deste ativo estão atrasados.
```

### NO_DATA

```text
Análise indisponível
Não há candles disponíveis.
```

### LIMITED

```text
Dados limitados
Evite decisões que dependem de entrada instantânea.
```

Não mostrar alertas longos quando o mercado estiver normal.

Não ocupar permanentemente uma faixa grande com estado saudável.

---

# PARTE 3 — ESTRUTURA DA TELA

## 7. Layout principal

Organizar a tela em três áreas:

```text
CONTROLES
↓
GRÁFICO
↓
PAINEL DE ANÁLISE
```

Em tela larga, o painel de análise pode ficar ao lado do gráfico.

Em janela dividida, deve ficar abaixo.

Prioridade de espaço:

1. gráfico;
2. controles;
3. análise;
4. diagnóstico DEV.

---

## 8. Gráfico

O gráfico deve ganhar mais espaço visual.

Remover da proximidade do gráfico:

- cards técnicos;
- status duplicados;
- mensagens repetidas;
- informações que já existem no HUD DEV.

Manter:

- ativo;
- timeframe;
- candles;
- preço;
- countdown da vela;
- status resumido do mercado.

---

## 9. Countdown

Manter o contador da próxima vela visível.

Exemplo:

```text
Próxima vela: 00:27
```

Pode ficar:

- no cabeçalho do gráfico;
- ao lado do timeframe;
- em uma área compacta.

Não colocar no HUD DEV, porque é útil ao operador.

---

# PARTE 4 — PAINEL DE ANÁLISE V1

## 10. Criar fundação visual

Criar um painel principal chamado:

```text
ANÁLISE FRIDAY
```

Nesta Sprint ele não terá inteligência real.

Deve mostrar estado neutro:

```text
Aguardando estratégia
```

Texto:

```text
Selecione ou cadastre uma estratégia para iniciar a análise deste ativo.
```

Não gerar:

- CALL;
- PUT;
- compra;
- venda;
- percentual;
- score fictício;
- confluências inventadas.

---

## 11. Espaços futuros

Preparar visualmente áreas para:

### Estratégia

```text
Estratégia ativa
Nenhuma estratégia selecionada
```

### Condição do mercado

```text
Condição
Aguardando análise
```

### Confluências

```text
Confluências
Nenhuma regra avaliada
```

### Decisão

```text
Decisão Friday
AGUARDAR
```

Neste estágio, `AGUARDAR` deve significar:

```text
motor de estratégia ainda não ativo
```

Não deve parecer um sinal real.

Adicionar texto:

```text
Análise estratégica ainda não iniciada.
```

---

## 12. Linguagem

Usar linguagem simples:

- Mercado ativo;
- Mercado lento;
- Dados atrasados;
- Aguardando estratégia;
- Nenhuma confluência avaliada;
- Análise indisponível.

Evitar na tela principal:

- provider;
- runtime;
- source mode;
- near realtime;
- snapshot internals;
- sequence;
- subscriber;
- payload;
- SSE.

---

# PARTE 5 — CONTEXTO LATERAL

## 13. Simplificação

O painel lateral atual deve mostrar somente informações relevantes para o operador:

```text
Ativo
Mercado
Timeframe
Próxima vela
Qualidade resumida
```

Remover ou esconder no modo normal:

- provider;
- pipeline;
- read-only repetido;
- conexão;
- source mode técnico;
- métricas de infraestrutura.

---

## 14. Informações legais e segurança

Pode manter discretamente:

```text
Somente análise
```

Não precisa repetir `READ ONLY` em vários lugares.

Não mostrar linguagem que sugira execução automática.

---

# PARTE 6 — PAINEL DEV

## 15. Preservação integral

Mover toda informação técnica existente para o painel DEV.

O painel DEV pode conter:

- provider;
- connection;
- Runtime Guard;
- SSE;
- polling;
- fallback;
- heartbeat;
- latência local;
- eventos;
- atualizações;
- coalescing;
- sequência;
- reconexões;
- assinantes;
- último evento;
- última aplicação;
- erros recentes.

Não excluir métricas que ainda ajudam no desenvolvimento.

---

## 16. Visual DEV

O painel deve:

- ficar recolhido por padrão;
- poder ser expandido;
- não quebrar o layout;
- permitir copiar informações;
- ter aparência secundária;
- não competir com o gráfico ou análise.

---

# PARTE 7 — RESPONSIVIDADE

## 17. Tela larga

Estrutura sugerida:

```text
Gráfico grande | Análise Friday
```

Controles acima.

DEV recolhido.

---

## 18. Janela dividida

Estrutura:

```text
Controles
Gráfico
Análise Friday
```

Sem sobreposição.

Sem textos cortados.

Sem cards técnicos ocupando largura.

---

## 19. Tela pequena

Estrutura vertical.

Ordem:

1. mercado;
2. ativo;
3. timeframe;
4. status resumido;
5. gráfico;
6. análise;
7. modo DEV.

---

## 20. Critérios visuais

Não aceitar:

- `...` em estados importantes;
- sobreposição;
- palavra quebrada no meio;
- áreas vazias enormes;
- quatro cards técnicos;
- mensagens duplicadas;
- fonte minúscula;
- gráfico excessivamente comprimido.

---

# PARTE 8 — ESCOPO TÉCNICO

## 21. Preferência de arquivos

Alterar preferencialmente:

```text
frontend/src/pages/MarketChart.tsx
frontend/src/components/
frontend/src/**/*.css
tests/frontend/
```

Pode extrair componentes pequenos:

```text
OperatorHeader
MarketHealthBadge
FridayAnalysisPanel
DeveloperDiagnostics
```

Somente se isso reduzir a complexidade de `MarketChart.tsx`.

---

## 22. Não alterar

Não alterar:

- IQ Option worker;
- runtime;
- provider;
- CandleStore;
- SSE backend;
- endpoints;
- polling;
- contratos de assets;
- contratos de candles;
- símbolos;
- lista de ativos;
- conexão;
- Runtime Guard.

Esta Sprint é de estrutura visual e separação de modos.

---

# PARTE 9 — TESTES

## 23. Testes frontend

Adicionar ou ajustar testes para:

1. Modo Operador é padrão;
2. Modo DEV fica recolhido;
3. provider não aparece no Modo Operador;
4. SSE não aparece no Modo Operador;
5. polling não aparece no Modo Operador;
6. fallback não aparece no Modo Operador;
7. diagnóstico continua disponível no Modo DEV;
8. ativo permanece visível;
9. timeframe permanece visível;
10. mercado permanece visível;
11. próxima vela permanece visível;
12. STALE mostra “DADOS ATRASADOS”;
13. LIMITED mostra “DADOS LIMITADOS”;
14. LIVE mostra “MERCADO ATIVO”;
15. análise mostra “Aguardando estratégia”;
16. não existe score fictício;
17. não existe CALL;
18. não existe PUT;
19. decisão neutra é claramente não operacional;
20. troca de modo não altera assets;
21. troca de modo não altera candles;
22. troca de modo não reinicia SSE;
23. lista de ativos permanece completa;
24. responsividade não usa ellipsis em status crítico.

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

# PARTE 10 — VALIDAÇÃO MANUAL

## 26. Modo Operador

Confirmar:

- tela limpa;
- sem provider;
- sem SSE;
- sem polling;
- sem cards técnicos;
- ativo fácil de localizar;
- gráfico com mais espaço;
- status simples;
- análise Friday visível;
- dropdown de ativos funcionando.

---

## 27. Modo Desenvolvedor

Confirmar:

- botão discreto;
- abre e fecha;
- todas as métricas continuam disponíveis;
- não altera feed;
- não altera ativos;
- não altera gráfico;
- não acumula EventSource;
- não reinicia o backend.

---

## 28. Trocas

Testar:

```text
EURUSD-OTC
→ GBPUSD-OTC
→ USDJPY-OTC
```

e:

```text
M1
→ M5
→ M15
→ M1
```

Confirmar ausência de regressões.

---

# PARTE 11 — GIT

## 29. Não executar

Não executar:

```bash
git add .
```

Não executar staging.

Não fazer commit.

Não fazer push.

---

# ENTREGA ESPERADA

Entregar relatório com:

1. estrutura anterior;
2. nova estrutura;
3. itens removidos do Modo Operador;
4. itens preservados no Modo DEV;
5. componentes criados;
6. arquivos modificados;
7. diff funcional;
8. regra de persistência do modo;
9. comportamento LIVE;
10. comportamento LIMITED;
11. comportamento STALE;
12. painel “Análise Friday”;
13. confirmação de ausência de sinais fictícios;
14. resultado da lista de ativos;
15. troca de ativo;
16. troca de timeframe;
17. testes frontend;
18. suíte completa;
19. build;
20. validação em tela cheia;
21. validação em janela dividida;
22. validação do Modo DEV;
23. `git status --short`;
24. `git diff --stat`;
25. riscos restantes;
26. sugestão de commit;
27. confirmação de que não fez commit;
28. confirmação de que não fez push.

Não criar estratégia nesta Sprint.

Não gerar CALL ou PUT.

Não apagar diagnóstico técnico.

Não alterar backend ou arquitetura de mercado.