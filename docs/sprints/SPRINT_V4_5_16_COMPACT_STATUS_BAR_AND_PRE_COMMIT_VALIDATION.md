# SPRINT V4.5.16 — COMPACT STATUS BAR AND PRE-COMMIT VALIDATION

## Objetivo

Corrigir definitivamente a faixa superior de status do Market Chart, eliminando:

- textos sobrepostos;
- palavras quebradas;
- cards excessivamente altos;
- informações técnicas demais na área principal;
- layout ruim em janela dividida.

Depois da correção visual, executar uma validação funcional completa e preparar o repositório para um checkpoint Git seguro.

Não fazer commit automaticamente.

Não fazer push.

---

# Contexto comprovado

As Sprints anteriores implementaram:

- IQ Option read-only;
- candles reais;
- realtime candle stream;
- SSE;
- fallback por polling;
- classificação de qualidade do feed;
- HUD DEV;
- responsividade inicial.

Problema atual observado manualmente:

Mesmo sem palavras quebradas no meio, os cards superiores continuam estreitos demais e os textos passam uns sobre os outros.

Exemplo observado:

```text
FONTE
IQ OPTION
READ ONLY

MODO
PRÓXIMO DO TEMPO REAL
Fluxo saudável

ENTREGA
SSE ATIVO
Latência local

FEED
Próxima vela
Resposta
```

Em janela dividida, os conteúdos se sobrepõem.

A causa não deve ser corrigida diminuindo exageradamente a fonte.

A área principal deve mostrar apenas informações essenciais.

As informações técnicas detalhadas devem permanecer no HUD DEV recolhível.

---

# PARTE 1 — NOVA FAIXA DE STATUS

## 1. Regra visual principal

Substituir os quatro cards grandes por uma faixa compacta de indicadores.

Informações essenciais:

```text
IQ OPTION
NEAR REALTIME
SSE
FEED OK
```

Os valores devem ser curtos e fáceis de compreender.

Não mostrar parágrafos nessa faixa.

---

## 2. Conteúdo oficial

### Fonte

Valor principal:

```text
IQ OPTION
```

Texto secundário opcional:

```text
READ ONLY
```

### Qualidade

Valores possíveis:

```text
TEMPO REAL
PRÓXIMO DO TEMPO REAL
SNAPSHOT
DADOS ATRASADOS
SEM DADOS
VERIFICANDO
```

Usar o valor real já calculado pelo sistema.

### Entrega

Valores possíveis:

```text
SSE
POLLING 1s
RECONECTANDO
DESCONECTADO
```

### Feed

Valores possíveis:

```text
FEED OK
SEM MOVIMENTO
LIMITADO
ATRASADO
SEM DADOS
```

Não mostrar horário completo ou latência nessa área.

---

## 3. Informações que devem sair da faixa principal

Mover ou manter somente no HUD DEV:

- horário exato da última resposta;
- latência local;
- p95;
- média;
- sequência;
- eventos;
- updates;
- coalescing;
- heartbeat;
- reconexões;
- fallbacks;
- última aplicação;
- quantidade de assinantes.

A faixa principal não é um painel técnico.

---

## 4. Layout para tela larga

Em largura suficiente:

```text
IQ OPTION | PRÓXIMO DO TEMPO REAL | SSE | FEED OK
```

Pode usar quatro itens em uma linha.

Cada item deve possuir:

- ícone;
- rótulo curto;
- valor curto;
- altura uniforme.

---

## 5. Layout para janela média

Em janela dividida ou largura intermediária:

```text
IQ OPTION | PRÓXIMO DO TEMPO REAL
SSE       | FEED OK
```

Usar duas colunas.

Não comprimir quatro itens em uma única linha.

---

## 6. Layout estreito

Em telas menores:

- duas colunas, quando possível;
- uma coluna apenas se necessário;
- nunca sobreposição;
- nunca texto fora do card;
- nunca quebra no meio de palavras.

---

## 7. Regras obrigatórias de CSS

Aplicar proteção equivalente a:

```css
min-width: 0;
word-break: normal;
overflow-wrap: normal;
hyphens: none;
```

Para valores curtos, considerar:

```css
white-space: nowrap;
```

Somente usar ellipsis se:

- o texto completo estiver disponível em `title`;
- o valor não for crítico;
- não esconder estado operacional importante.

Não usar:

```css
word-break: break-all;
```

Não usar fontes minúsculas para mascarar falta de espaço.

---

## 8. Estratégia de grid

Auditar os breakpoints atuais.

A faixa não deve utilizar quatro colunas cedo demais.

Estratégia desejada:

```text
base: 1 ou 2 colunas
md: 2 colunas
xl: 4 colunas
```

Os breakpoints finais devem ser escolhidos com base no layout real do projeto.

Registrar as classes ou CSS aplicados.

---

## 9. Altura e alinhamento

Os indicadores devem:

- possuir altura uniforme;
- alinhar ícone e texto;
- manter padding consistente;
- não aumentar muito a altura do cabeçalho;
- não empurrar o gráfico para baixo sem necessidade.

---

# PARTE 2 — INDICADOR VISUAL

## 10. Uso de cores

A cor pode ajudar, mas não pode ser a única forma de informação.

Exemplos:

```text
SSE
Conectado
```

```text
POLLING 1s
Modo de segurança
```

```text
DADOS ATRASADOS
Análise bloqueada
```

O texto deve sempre existir.

---

## 11. Status do feed

Mapear o estado real para uma mensagem compacta.

### NEAR_REALTIME

```text
FEED OK
```

### SNAPSHOT ou LIMITED

```text
FEED LIMITADO
```

### QUIET

```text
SEM MOVIMENTO
```

### STALE

```text
DADOS ATRASADOS
```

### NO_DATA

```text
SEM DADOS
```

### CHECKING

```text
VERIFICANDO
```

Não mostrar `FEED OK` quando o feed estiver snapshot, limited ou stale.

---

## 12. Próxima vela

Retirar a contagem de próxima vela dos cards principais caso ela prejudique a responsividade.

Mover para:

- cabeçalho do gráfico;
- contexto lateral;
- HUD;
- ou pequeno contador dedicado.

O countdown deve continuar visível em algum lugar adequado.

Não remover a funcionalidade.

---

# PARTE 3 — HUD DEV

## 13. Estado recolhido

Quando recolhido, mostrar somente:

```text
DIAGNÓSTICO DEV
SSE • GOOD • 0 FALLBACKS
```

ou equivalente em português.

O resumo não deve quebrar.

---

## 14. Estado expandido

Manter as métricas técnicas:

- entrega;
- qualidade;
- eventos de candle;
- atualizações do gráfico;
- eventos agrupados;
- último evento;
- última aplicação;
- latência local média;
- p95 local;
- sequência;
- reconexões;
- fallbacks;
- heartbeat;
- status;
- assinantes, caso disponível.

Usar o termo:

```text
LATÊNCIA LOCAL
```

Não usar apenas:

```text
LATÊNCIA
```

---

## 15. HUD responsivo

### Largura grande

Pode usar várias colunas.

### Janela dividida

Usar duas colunas.

### Largura estreita

Usar uma coluna ou duas compactas.

Nenhuma métrica pode passar por cima da outra.

---

# PARTE 4 — VALIDAÇÃO FUNCIONAL

## 16. SSE

Confirmar no frontend real:

- `SSE` aparece quando a conexão está saudável;
- heartbeat é recebido;
- fallback permanece 0;
- polling realtime de 1 segundo não roda paralelamente enquanto SSE estiver saudável;
- reconciliação de 5 segundos continua ativa.

---

## 17. Fallback

Simular ou testar de forma segura:

- SSE indisponível;
- fallback passa para polling de 1 segundo;
- texto muda para `POLLING 1s`;
- recuperação do SSE desliga o fallback;
- não existem dois pollings ativos;
- não há candles duplicados.

Não alterar backend apenas para produzir o erro.

---

## 18. Troca de ativo

Testar:

```text
EURUSD-OTC
→ GBPUSD-OTC
→ USDJPY-OTC
→ EURUSD-OTC
```

Confirmar:

- EventSource antigo fechado;
- sequência reiniciada;
- fallback antigo encerrado;
- requestAnimationFrame antigo cancelado;
- card volta para VERIFICANDO;
- novo ativo recebe eventos;
- nenhum dado cruzado.

---

## 19. Troca de timeframe

Testar:

```text
M1
→ M5
→ M15
→ M1
```

Confirmar:

- raw_size correto;
- EventSource anterior fechado;
- novo contexto iniciado;
- contador correto;
- candles não misturados;
- status visual correto.

---

## 20. Feed quality

Validar visualmente:

### EURUSD-OTC

Esperado:

```text
PRÓXIMO DO TEMPO REAL
SSE
FEED OK
```

### Ativo snapshot/limited

Esperado:

```text
SNAPSHOT
SSE ou POLLING
FEED LIMITADO
```

### AMAZON ou ativo stale

Esperado:

```text
DADOS ATRASADOS
ANÁLISE BLOQUEADA
```

A faixa principal deve refletir o estado real.

---

# PARTE 5 — RESPONSIVIDADE

## 21. Larguras obrigatórias

Validar aproximadamente:

```text
1440px
1200px
1024px
768px
```

Também validar:

- janela dividida igual ao print do Renan;
- tela cheia;
- zoom 100%;
- zoom 90%;
- zoom 80%.

Não usar zoom como solução.

---

## 22. Critérios de aprovação visual

Em todas as larguras:

- nenhuma sobreposição;
- nenhuma palavra partida;
- nenhum card vazando;
- nenhum texto escondido atrás de outro;
- ícones alinhados;
- alturas uniformes;
- espaçamento consistente;
- HUD utilizável;
- gráfico mantém área adequada.

---

# PARTE 6 — TESTES AUTOMATIZADOS

## 23. Testes frontend

Adicionar ou ajustar testes para:

1. faixa principal usa textos compactos;
2. horários completos não aparecem na faixa principal;
3. latência não aparece na faixa principal;
4. grid utiliza quatro colunas somente em largura maior;
5. layout possui duas colunas intermediárias;
6. nenhuma classe `break-all`;
7. nenhuma quebra agressiva;
8. status NEAR_REALTIME mostra FEED OK;
9. SNAPSHOT mostra FEED LIMITADO;
10. STALE mostra DADOS ATRASADOS;
11. CHECKING mostra VERIFICANDO;
12. SSE saudável mostra SSE;
13. fallback mostra POLLING 1s;
14. HUD recolhido mostra resumo;
15. HUD expandido mostra LATÊNCIA LOCAL;
16. countdown continua disponível fora da faixa principal;
17. troca de ativo limpa estado;
18. troca de timeframe limpa estado;
19. EventSource é fechado ao desmontar;
20. fallback não fica paralelo ao SSE saudável;
21. não existe interpolação de preço.

Executar:

```bash
.venv/bin/python -m pytest tests/frontend -q
```

---

## 24. Testes API/provider

Confirmar ou ajustar testes para:

1. SSE mantém `text/event-stream`;
2. assinante entra e sai corretamente;
3. troca de contexto mantém somente um assinante;
4. heartbeat funciona;
5. fallback HTTP continua disponível;
6. Runtime Guard permanece read-only.

Executar:

```bash
.venv/bin/python -m pytest tests/api tests/market/providers -q
```

---

## 25. Suíte completa

```bash
.venv/bin/python -m pytest -q
```

---

## 26. Build

```bash
cd frontend
npm run build
cd ..
```

---

# PARTE 7 — VALIDAÇÃO VISUAL MANUAL

## 27. Prints obrigatórios

Solicitar ao Renan após auditoria:

### Print A

Faixa superior em tela cheia.

### Print B

Faixa superior em janela dividida.

### Print C

HUD recolhido.

### Print D

HUD expandido.

### Print E

SSE ativo e fallback 0.

### Print F

Ativo stale ou limited exibindo o aviso correto.

---

# PARTE 8 — PREPARAÇÃO DO CHECKPOINT GIT

## 28. Não fazer commit ainda

Após concluir a correção, preparar relatório de Git.

Executar:

```bash
git status --short
```

```bash
git diff --stat
```

```bash
git diff --name-status
```

Listar separadamente:

- arquivos modificados rastreados;
- arquivos novos de produção;
- testes novos;
- documentos de Sprint;
- arquivos temporários;
- caches;
- probes;
- arquivos ignorados.

---

## 29. Auditoria de arquivos não rastreados

Confirmar que não serão adicionados:

```text
.jarvis_cache/
__pycache__/
*.pyc
node_modules/
dist/
arquivos de credenciais
logs
scripts temporários de probe
```

Não usar:

```bash
git add .
```

Preparar lista explícita de arquivos seguros para staging.

---

## 30. Plano de commit

Propor commits coerentes, por exemplo:

### Commit 1 — Infraestrutura IQ Option

```text
feat(iq-option): add isolated read-only provider and persistent worker
```

### Commit 2 — Assets e candles

```text
feat(market): add IQ Option assets, candles and chart data flow
```

### Commit 3 — Realtime e SSE

```text
feat(iq-option): add realtime candle stream and SSE delivery
```

### Commit 4 — Interface e diagnóstico

```text
fix(ui): stabilize realtime status bar and diagnostics HUD
```

O FORGE deve recomendar se é seguro separar dessa forma com o estado atual do diff.

Não executar staging ou commit.

---

# PARTE 9 — ENTREGA ESPERADA

Entregar relatório contendo:

1. causa exata da sobreposição;
2. nova estrutura da faixa principal;
3. informações removidas da faixa;
4. informações movidas ao HUD;
5. arquivo e linhas alteradas;
6. regras de grid;
7. regras de tipografia;
8. resultado em 1440px;
9. resultado em 1200px;
10. resultado em 1024px;
11. resultado em 768px;
12. resultado em janela dividida;
13. HUD recolhido;
14. HUD expandido;
15. estado SSE;
16. estado fallback;
17. troca de ativo;
18. troca de timeframe;
19. resultado NEAR_REALTIME;
20. resultado SNAPSHOT/LIMITED;
21. resultado STALE;
22. arquivos modificados;
23. diff funcional;
24. testes frontend;
25. testes API/provider;
26. suíte completa;
27. build;
28. Runtime Guard;
29. `git status --short`;
30. `git diff --stat`;
31. `git diff --name-status`;
32. lista de arquivos não rastreados;
33. lista de arquivos que não devem entrar;
34. lista explícita sugerida para staging;
35. plano de commits;
36. riscos restantes.

Não fazer commit.

Não fazer push.

Não usar `git add .`.

Não esconder problemas reduzindo excessivamente a fonte.

Não deixar informações técnicas longas na faixa principal.