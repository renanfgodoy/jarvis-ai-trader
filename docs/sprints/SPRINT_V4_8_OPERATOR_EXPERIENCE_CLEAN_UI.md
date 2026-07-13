# SPRINT V4.8 — OPERATOR EXPERIENCE CLEAN UI

## Objetivo

Refatorar a interface principal do `/market-chart` para uma experiência realmente limpa, focada no operador e no futuro painel de estratégias.

A tela atual ainda exibe informações repetidas e técnicas demais, mesmo no Modo Operador.

A prioridade desta Sprint é:

```text
gráfico
→ controles essenciais
→ estratégia
→ contexto operacional simples
```

Não implementar estratégia real.

Não criar CALL, PUT, score, probabilidade ou entrada.

---

# CONTEXTO

A Friday V1 já possui:

- Modo Operador;
- Modo Desenvolvedor;
- gráfico real;
- lista de ativos;
- timeframe;
- countdown;
- Strategy Engine foundation;
- diagnóstico técnico preservado.

Porém, no Modo Operador ainda aparecem elementos que poluem a tela:

- API ONLINE;
- PROVIDER SIMULATED;
- CONTA N/D;
- MOEDA N/D;
- OFFLINE;
- HORA LOCAL;
- USUÁRIO;
- AMBIENTE Desenvolvimento;
- informações repetidas de ativo, mercado e timeframe;
- contexto lateral redundante;
- status técnicos ainda muito presentes.

A interface deve deixar de parecer um dashboard administrativo.

---

# REGRA PRINCIPAL

No Modo Operador, cada informação deve responder a uma pergunta útil:

- Qual ativo estou analisando?
- Qual timeframe?
- Quando abre a próxima vela?
- O mercado está utilizável?
- Qual estratégia está ativa?
- O que a Friday está observando?

Se a informação não ajuda nessas perguntas, deve ser removida da tela principal ou movida para o Modo DEV.

---

# PARTE 1 — CABEÇALHO

## 1. Simplificação completa

No Modo Operador, remover do cabeçalho principal:

- API ONLINE;
- PROVIDER SIMULATED;
- CONTA N/D;
- MOEDA N/D;
- OFFLINE;
- HORA LOCAL;
- USUÁRIO;
- cards técnicos;
- badges de infraestrutura.

Manter apenas:

```text
FRIDAY TRADE
Simulação
```

ou equivalente visual simples.

Pode manter logo e identidade.

---

## 2. Perfil e configurações

Usuário e configurações podem ficar:

- no menu lateral;
- em dropdown de perfil;
- no Modo DEV;
- em Settings.

Não ocupar a faixa principal.

---

# PARTE 2 — SIDEBAR

## 3. Card Ambiente

Remover do Modo Operador o card:

```text
AMBIENTE
Desenvolvimento
Execução real bloqueada
```

Essa informação pode permanecer no Modo DEV.

---

## 4. Versão

Mover a versão:

```text
v0.24.0
```

para:

- rodapé discreto;
- Settings;
- Modo DEV.

Não precisa ocupar espaço visual fixo no operador.

---

# PARTE 3 — CONTROLES ESSENCIAIS

## 5. Barra de controles

Manter apenas:

```text
Mercado
Ativo
Timeframe
Próxima vela
```

A barra deve ser compacta e clara.

O ativo deve ter maior destaque visual.

---

## 6. Status de mercado

Manter apenas um badge pequeno:

```text
MERCADO ATIVO
```

ou:

```text
MERCADO LENTO
DADOS LIMITADOS
DADOS ATRASADOS
SEM DADOS
VERIFICANDO
```

Não criar banner grande quando o mercado estiver saudável.

Quando houver problema, exibir mensagem curta e objetiva.

---

# PARTE 4 — GRÁFICO

## 7. Prioridade máxima

O gráfico deve ocupar a maior parte da área útil.

Meta visual:

```text
70% a 80% da largura disponível
```

em tela larga.

Não fixar porcentagem rígida se isso prejudicar responsividade.

---

## 8. Cabeçalho do gráfico

Exibir somente:

```text
AUD/CAD OTC
M1
502 candles
```

ou equivalente compacto.

Remover:

```text
CANDLE STORE
raw_size 60
```

do Modo Operador.

Essas informações técnicas podem permanecer no DEV.

---

## 9. Espaço vertical

Reduzir áreas vazias e cards redundantes.

O gráfico deve começar mais próximo dos controles.

---

# PARTE 5 — LATERAL DE ESTRATÉGIA

## 10. Remover contexto repetido

No Modo Operador, remover o card lateral que repete:

- ativo;
- mercado;
- timeframe;
- candles;
- status;
- próxima vela.

Essas informações já estão nos controles e no gráfico.

---

## 11. Friday Strategy Panel

Transformar a lateral em um painel único focado na estratégia.

Título:

```text
FRIDAY STRATEGY
```

Estado atual:

```text
Nenhuma estratégia carregada
```

Mostrar somente:

### Estratégia ativa

```text
Nenhuma selecionada
```

### Status

```text
Aguardando configuração
```

### Confluências

```text
0 avaliadas
```

### Decisão

```text
Nenhuma análise ativa
```

Não usar `AGUARDAR` como decisão operacional enquanto o motor estiver inativo.

---

## 12. Texto neutro

Usar:

```text
Selecione uma estratégia para iniciar a leitura do mercado.
```

Não usar linguagem que pareça sinal.

---

# PARTE 6 — MODO DESENVOLVEDOR

## 13. Preservar tudo no DEV

No Modo DEV, manter:

- API;
- provider;
- conta;
- moeda;
- status de conexão;
- SSE;
- polling;
- heartbeat;
- latência;
- Runtime Guard;
- ambiente;
- versão;
- CandleStore;
- raw_size;
- diagnóstico;
- contexto técnico;
- erros;
- retry;
- logs.

Nada técnico deve ser apagado do projeto.

---

## 14. Acesso discreto

No Modo Operador, o acesso ao DEV deve ser um botão pequeno:

```text
DEV
```

ou ícone de engrenagem.

Não usar card grande.

---

# PARTE 7 — ERROS

## 15. Linguagem para operador

Trocar mensagens técnicas no Modo Operador.

Exemplo técnico:

```text
IQ Option candles timeout
```

Exemplo operador:

```text
Não foi possível atualizar este ativo.
```

Botão:

```text
Tentar novamente
```

A mensagem técnica completa permanece no DEV.

---

# PARTE 8 — RESPONSIVIDADE

## 16. Tela larga

Estrutura:

```text
Controles
Gráfico grande | Friday Strategy
```

---

## 17. Janela dividida

Estrutura:

```text
Controles
Gráfico
Friday Strategy
```

A lateral deve cair abaixo do gráfico.

---

## 18. Tela pequena

Estrutura vertical:

```text
Mercado
Ativo
Timeframe
Próxima vela
Status
Gráfico
Friday Strategy
DEV
```

---

## 19. Critérios visuais

Não aceitar:

- informações duplicadas;
- cards técnicos no operador;
- cabeçalho administrativo;
- sobreposição;
- texto cortado;
- ellipsis em status importante;
- área vazia excessiva;
- gráfico comprimido;
- mensagens técnicas para o operador.

---

# PARTE 9 — ESCOPO TÉCNICO

## 20. Arquivos permitidos

Alterar preferencialmente:

```text
frontend/src/pages/MarketChart.tsx
frontend/src/components/
frontend/src/**/*.css
tests/frontend/
```

Pode extrair componentes visuais se reduzir a complexidade.

---

## 21. Não alterar

Não alterar:

- backend;
- IQ worker;
- runtime;
- provider;
- SSE;
- polling;
- CandleStore;
- Chart API;
- endpoints;
- lista de ativos;
- parsing;
- símbolos;
- candles;
- conexão.

---

# PARTE 10 — TESTES

## 22. Testes frontend

Adicionar ou ajustar testes para:

1. API ONLINE não aparece no Modo Operador;
2. provider não aparece no Modo Operador;
3. conta não aparece no Modo Operador;
4. moeda não aparece no Modo Operador;
5. hora local não aparece no Modo Operador;
6. usuário não aparece no topo do Modo Operador;
7. ambiente não aparece no Modo Operador;
8. versão não aparece de forma fixa no operador;
9. controles essenciais continuam visíveis;
10. gráfico continua visível;
11. CandleStore não aparece no operador;
12. raw_size não aparece no operador;
13. contexto repetido é removido;
14. Friday Strategy aparece;
15. não existe CALL;
16. não existe PUT;
17. não existe score;
18. não existe probabilidade;
19. não existe `AGUARDAR` como decisão operacional;
20. DEV preserva diagnóstico;
21. troca de modo não altera assets;
22. troca de modo não altera candles;
23. lista de ativos permanece completa;
24. timeframe continua funcionando;
25. próxima vela continua visível.

Executar:

```bash
.venv/bin/python -m pytest tests/frontend -q
```

---

## 23. Suíte completa

```bash
.venv/bin/python -m pytest -q
```

---

## 24. Build

```bash
cd frontend
npm run build
cd ..
```

---

# PARTE 11 — VALIDAÇÃO MANUAL

## 25. Modo Operador

Confirmar:

- cabeçalho limpo;
- sem API/provider/conta/moeda/hora/usuário;
- sem card Ambiente;
- gráfico maior;
- controles simples;
- lateral focada em estratégia;
- sem contexto repetido;
- sem erro técnico exposto;
- dropdown de ativos funcionando.

---

## 26. Modo DEV

Confirmar:

- todas as informações técnicas continuam disponíveis;
- diagnóstico abre e fecha;
- ambiente e versão continuam acessíveis;
- erro técnico completo continua disponível;
- não altera o feed.

---

## 27. Troca de ativos e timeframe

Testar:

```text
EURUSD-OTC
→ AUDCAD-OTC
→ GBPUSD-OTC
```

e:

```text
M1
→ M5
→ M15
→ M1
```

Sem regressões.

---

# PARTE 12 — GIT

## 28. Não executar

Não executar:

```bash
git add .
```

Não executar staging.

Não fazer commit.

Não fazer push.

---

# ENTREGA ESPERADA

Entregar relatório contendo:

1. elementos removidos do cabeçalho;
2. elementos removidos da sidebar;
3. elementos removidos da lateral;
4. nova estrutura do gráfico;
5. nova estrutura do Friday Strategy;
6. linguagem de erro do operador;
7. itens preservados no DEV;
8. componentes criados;
9. arquivos modificados;
10. diff funcional;
11. resultado da lista de ativos;
12. troca de ativo;
13. troca de timeframe;
14. testes frontend;
15. suíte completa;
16. build;
17. validação em tela cheia;
18. validação em janela dividida;
19. validação em tela pequena;
20. validação do DEV;
21. `git status --short`;
22. `git diff --stat`;
23. riscos restantes;
24. sugestão de commit;
25. confirmação de que não fez commit;
26. confirmação de que não fez push.

Não implementar estratégia real.

Não criar sinais.

Não alterar arquitetura de mercado.