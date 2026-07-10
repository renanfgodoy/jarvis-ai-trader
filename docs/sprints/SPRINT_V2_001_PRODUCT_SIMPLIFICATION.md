# FRIDAY TRADE V2 — SPRINT 1
## PRODUCT SIMPLIFICATION & CONTROLLED CLEANUP

## Status

PLANNED

---

# Projeto

Friday Trade V2

Repositório oficial:

`/Users/renangodoy/Desktop/jarvis-ai-trader`

Branch esperada:

`main`

Python oficial:

`Python 3.11`

---

# REGRA OBRIGATÓRIA

NÃO faça commit.

NÃO faça push.

NÃO altere arquivos fora do repositório oficial.

NÃO utilize a pasta paralela:

`/Users/renangodoy/Desktop/friday-trade-v2`

Todo o trabalho deve acontecer exclusivamente em:

`/Users/renangodoy/Desktop/jarvis-ai-trader`

---

# OBJETIVO

Transformar o projeto atual no Friday Trade V2.

O produto deixa de ser um robô de execução automática e passa oficialmente a ser um:

## AI Trading Copilot

O Friday Trade V2 deve:

- analisar o mercado;
- exibir os 12 principais ativos;
- permitir seleção explícita do ativo;
- permitir seleção de timeframe M1, M5 ou M15;
- apresentar gráfico e dados reais disponíveis;
- preparar indicadores e análise técnica;
- futuramente calcular confiança e probabilidade;
- explicar os motivos da análise;
- registrar análises e resultados manuais;
- manter a entrada totalmente manual na Polarium.

O produto NÃO deverá executar ordens.

---

# PRINCÍPIO CENTRAL

O Friday Trade V2:

- observa;
- organiza dados;
- analisa;
- explica;
- registra;
- aprende com resultados manuais.

O Friday Trade V2 NÃO:

- clica em CALL;
- clica em PUT;
- executa ordem;
- utiliza Martingale automático;
- envia entrada para a corretora;
- decide valor de entrada;
- controla banca para execução automática.

---

# ETAPA 1 — CHECAGEM OBRIGATÓRIA

Antes de modificar qualquer arquivo, executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

pwd
git rev-parse --show-toplevel
git branch --show-current
git status --short
.venv/bin/python --version
.venv/bin/python -m pytest -q

cd frontend
npm run build
```

Confirmar:

- repositório correto;
- branch correta;
- Python 3.11;
- estado atual do Git;
- quantidade atual de testes;
- build atual do frontend.

Se houver alteração pendente no working tree, NÃO continuar silenciosamente.

Primeiro identificar quais Sprints estão pendentes e apresentar o risco.

---

# ETAPA 2 — AUDITORIA ANTES DA REMOÇÃO

Antes de apagar ou mover código, criar um mapa completo:

```text
MANTER
ADAPTAR
CONSOLIDAR
REMOVER
LEGADO TEMPORÁRIO
```

Para cada arquivo ou módulo relacionado a:

- AutoTrade;
- Execution;
- Risk de execução;
- Orders;
- Gate;
- Executor;
- filas;
- Martingale;
- operação automática;
- login direto experimental;
- painéis duplicados;
- páginas redundantes;
- componentes antigos;
- diretórios numerados;
- wrappers temporários;
- placeholders vazios.

Apresentar também:

```text
Origem → Destino
```

Não apagar nada antes de verificar:

- imports;
- rotas;
- testes;
- dependências;
- referências no frontend;
- referências na documentação.

---

# ESCOPO FUNCIONAL DO FRIDAY TRADE V2

A experiência principal deve ser simples.

Fluxo:

```text
Abrir Friday Trade
↓
Selecionar timeframe: M1, M5 ou M15
↓
Visualizar Top 12 ativos
↓
Selecionar ativo explicitamente
↓
Visualizar gráfico e dados disponíveis
↓
Solicitar análise
↓
Receber cenário, confiança e explicação
↓
Operador decide manualmente
↓
Operador registra WIN, LOSS ou NÃO ENTREI
```

Nenhuma ordem deve ser enviada à Polarium.

---

# NAVEGAÇÃO OFICIAL V2

A Sidebar principal deve conter apenas:

```text
Dashboard
Markets
AI Analysis
Replay
Connections
Settings
```

Área técnica separada e discreta:

```text
Developer
└── Polarium Lab
```

Remover da navegação principal:

- Operation antiga;
- Market Data como página separada;
- Market Intelligence como página separada;
- AutoTrade;
- Risk Center operacional;
- Orders automáticas;
- Execution;
- Diagnostics duplicado;
- páginas técnicas que confundem o operador.

Diagnostics técnico poderá continuar dentro de Developer ou Connections, caso ainda seja necessário.

---

# PÁGINAS OFICIAIS

## 1. Dashboard

Rota:

```text
/dashboard
```

Responsabilidade:

- resumo da plataforma;
- status da conexão;
- broker;
- conta;
- moeda;
- timeframe selecionado;
- ativo selecionado;
- última análise;
- dados disponíveis;
- aviso quando faltarem candles reais.

Não mostrar:

- execução;
- AutoTrade;
- fila de ordens;
- botões CALL/PUT;
- Martingale;
- controles técnicos complexos.

---

## 2. Markets

Rota:

```text
/markets
```

Esta será a principal tela de seleção e leitura do mercado.

Deve conter:

- seletor M1, M5 e M15;
- seletor explícito de ativo;
- Top 12 ativos;
- busca de ativo;
- watchlist;
- status do ativo;
- fonte do dado;
- última atualização;
- gráfico;
- estado dos candles;
- botão “Analisar ativo”.

Regras:

- não selecionar o primeiro ativo automaticamente;
- não utilizar ativo fixo;
- não inventar ativo;
- não inventar candle;
- não inventar preço;
- não inventar volume;
- não inventar spread;
- não inventar latência.

Sem ativo selecionado:

```text
Selecione um ativo para iniciar a análise.
```

Sem candles reais:

```text
Candles reais ainda não disponíveis.
```

---

## 3. AI Analysis

Rota:

```text
/analysis
```

Deve utilizar o mesmo ativo e timeframe selecionados em Markets.

Estrutura futura:

- ativo;
- timeframe;
- fonte dos dados;
- qualidade dos dados;
- tendência;
- força;
- volatilidade;
- momentum;
- suporte;
- resistência;
- confluências;
- cenário CALL;
- cenário PUT;
- confiança;
- evidências;
- riscos;
- explicação.

Nesta Sprint:

- não criar probabilidade fictícia;
- não criar CALL/PUT fictício;
- não criar indicadores usando dados simulados;
- mostrar “Dados insuficientes” quando faltarem candles reais.

A tela deve estar preparada para o futuro AI Decision Engine.

---

## 4. Replay

Rota:

```text
/replay
```

Responsabilidade:

- registrar análises;
- horário;
- ativo;
- timeframe;
- sugestão futura da IA;
- decisão do operador;
- resultado manual:
  - WIN;
  - LOSS;
  - NÃO ENTREI;
- observações;
- taxa de acerto futura.

Não executar ordens.

Nesta Sprint, pode ser uma base funcional local, sem banco novo, desde que:

- não guarde segredos;
- não invente resultados;
- não registre operação automaticamente.

---

## 5. Connections

Rota:

```text
/connections/polarium
```

Manter a Central de Conexões.

Responsabilidade:

- status;
- OAuth;
- sessão;
- WebSocket;
- conta;
- moeda;
- sincronização;
- erros sanitizados;
- origem dos dados.

Remover desta tela:

- ações de execução;
- transporte de ordens;
- qualquer botão de compra ou venda.

Manter o histórico de tentativas apenas em memória e sanitizado.

---

## 6. Settings

Rota:

```text
/settings
```

Manter somente:

- aparência;
- preferências;
- broker;
- notificações;
- comportamento da análise;
- configurações de Replay;
- perfil local.

Remover configurações de AutoTrade e execução automática.

---

# CONTEXTO COMPARTILHADO

Deve existir uma única fonte de verdade para:

- ativo selecionado;
- timeframe selecionado;
- broker;
- ambiente;
- conta;
- moeda;
- status da conexão;
- origem dos dados.

Reutilizar e simplificar o Market Data Context existente.

Regras:

- nenhum ativo padrão silencioso;
- nenhum timeframe operacional liberado sem seleção/ativação explícita;
- timeframes permitidos: M1, M5 e M15;
- H1 não deve aparecer;
- páginas não podem manter versões próprias do mesmo estado.

---

# TOP 12 ATIVOS

A tela Markets deve exibir os 12 principais ativos fornecidos pelas fontes existentes.

Não criar uma lista falsa apenas para preencher a tela.

Quando a fonte real não fornecer 12 ativos:

- mostrar somente os disponíveis;
- exibir mensagem clara;
- não completar com ativos inventados.

Cada ativo deve mostrar, quando disponível:

- nome;
- símbolo;
- mercado aberto/fechado;
- OTC ou mercado regular;
- fonte;
- última atualização;
- disponibilidade para análise.

Não mostrar score ou probabilidade sem engine real.

---

# BACKEND — MANTER

Manter e organizar:

```text
app/api/
app/connector/
app/market/
app/providers/
app/intelligence/
app/models/
app/schemas/
app/core/
app/utils/
```

Manter Connector Polarium isolado.

O Connector pode cuidar de:

- OAuth;
- sessão;
- WebSocket;
- parser;
- dados técnicos;
- diagnóstico de protocolo.

O Connector não pode decidir análise.

---

# BACKEND — REMOVER DO RUNTIME ATIVO

Remover gradualmente do runtime, após auditoria:

- AutoTrade;
- execução automática;
- executor de ordens;
- fila de execução;
- gate de execução;
- transporte de ordem que não seja necessário para leitura de dados;
- Martingale automático;
- rotas exclusivas de execução;
- schemas exclusivos de execução automática;
- serviços exclusivos de entrada automática.

IMPORTANTE:

Não apagar cegamente.

Se testes ou imports ainda dependerem desses módulos:

1. identificar;
2. atualizar testes;
3. remover referências;
4. somente depois remover arquivos.

Não manter código morto apenas para fazer testes antigos passarem.

Os testes devem refletir o novo produto.

---

# RISK

O Risk Manager de execução automática deixa de ser parte central do produto.

Manter apenas conceitos úteis para análise manual, caso existam:

- alerta de risco;
- qualidade do cenário;
- volatilidade;
- limite pessoal;
- aviso de excesso de operações;
- registro de sequência WIN/LOSS.

Remover:

- autorização automática de entrada;
- cálculo usado para enviar ordens;
- Gate de execução;
- Martingale automático;
- bloqueios ligados ao executor.

Não duplicar Risk nesta Sprint.

Se a separação for grande, documentar para uma Sprint posterior.

---

# FRONTEND — CONSOLIDAÇÃO

Consolidar:

```text
Markets
Market Data
Market Intelligence
```

em uma única experiência:

```text
Markets
```

Pode usar abas internas:

```text
Scanner
Dados
Inteligência
```

Mas não criar três páginas concorrentes.

Consolidar componentes duplicados:

```text
Header.tsx
Header/index.tsx

Sidebar.tsx
Sidebar/index.tsx
```

Manter somente uma implementação canônica de cada componente, após verificar qual está sendo usada.

Remover componentes antigos somente quando não houver mais imports.

---

# FRONTEND — LIMITE DE TAMANHO

Nenhuma página nova deve virar um arquivo gigante.

Regra:

- páginas: preferencialmente abaixo de 300 linhas;
- lógica em hooks;
- visual em componentes;
- cards em widgets;
- tipos em arquivos próprios;
- sem `as any` desnecessário.

---

# BRANDING

Manter:

- Friday Trade;
- Trade Smarter.;
- módulo centralizado de branding;
- logo atual como provisória.

Não investir em redesign de logo nesta Sprint.

A logo será revisada futuramente.

Não espalhar strings fixas de branding pelos componentes.

---

# DADOS REAIS

O produto deve distinguir claramente:

```text
REAL
SIMULADO
DEMO
INDISPONÍVEL
NÃO VERIFICADO
```

Nunca mostrar dado simulado como se fosse Polarium real.

Campos que devem ficar indisponíveis até haver fonte comprovada:

- candles reais Polarium;
- timestamp oficial do broker;
- volume real;
- spread real;
- liquidez real;
- latência real;
- probabilidade de WIN;
- sinal CALL/PUT;
- força real;
- indicadores calculados sem candles confiáveis.

---

# SEGURANÇA

Nunca expor ou versionar:

- tokens;
- cookies;
- bearer;
- authorization;
- refresh token;
- SSID;
- `.env`;
- HAR;
- credenciais;
- payloads sensíveis;
- `.jarvis_cache`.

Nunca copiar valores privados para documentação, fixtures ou logs.

---

# LIMPEZA DE REPOSITÓRIO

Auditar e remover, quando realmente presentes e sem uso:

- diretórios numerados duplicados;
- componentes duplicados;
- placeholders vazios desnecessários;
- caches;
- `.DS_Store`;
- `__pycache__`;
- `.pyc`;
- `.pytest_cache`;
- builds;
- arquivos temporários.

Não remover:

- documentação histórica relevante;
- ADRs;
- testes úteis;
- Connector;
- contratos necessários para dados.

---

# DOCUMENTAÇÃO

Atualizar obrigatoriamente:

```text
README.md
CHANGELOG.md
ROADMAP.md
docs/ARCHITECTURE.md
```

Criar:

```text
docs/FRIDAY_TRADE_V2.md
```

Conteúdo curto e objetivo:

- objetivo do produto;
- fluxo;
- telas;
- módulos mantidos;
- módulos removidos;
- limitações atuais;
- próximo passo.

Atualizar o documento desta Sprint com status final.

---

# TESTES

Os testes devem refletir o produto V2.

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader
.venv/bin/python -m pytest -q
```

Executar frontend:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run build
```

Não considerar a Sprint concluída se:

- houver import quebrado;
- frontend não compilar;
- testes antigos falharem por remoção incompleta;
- rotas principais não abrirem;
- Console apresentar erros vermelhos.

---

# COMO TESTAR A V2

O relatório final deve ensinar o Renan passo a passo.

## Backend

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader
.venv/bin/python -m uvicorn app.main:app --reload
```

## Frontend

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run dev
```

Validar:

```text
/dashboard
/markets
/analysis
/replay
/connections/polarium
/settings
/labs/polarium
```

Explicar o que conferir em cada tela.

Solicitar prints de:

- Dashboard;
- Markets;
- seletor de ativo;
- Top 12;
- seletor M1/M5/M15;
- AI Analysis em estado sem dados;
- Replay;
- Connections;
- Sidebar;
- Console;
- pytest;
- build.

---

# CRITÉRIOS DE APROVAÇÃO

A Sprint só estará pronta quando:

- o projeto oficial continuar sendo um repositório Git válido;
- Python 3.11 continuar configurado;
- produto estiver focado em análise manual;
- AutoTrade não aparecer na interface;
- execução automática não estiver no fluxo ativo;
- nenhuma ordem puder ser enviada;
- navegação estiver simplificada;
- Markets centralizar Scanner, Dados e Inteligência;
- existir seleção explícita de ativo;
- existir seleção M1/M5/M15;
- não existir H1;
- nenhum ativo for escolhido automaticamente;
- Top 12 usar dados existentes;
- AI Analysis não inventar sinais;
- Replay aceitar resultado manual;
- Connection Center continuar funcionando;
- build passar;
- testes passarem;
- documentação refletir a V2;
- nenhum segredo for exposto.

---

# ENTREGA OBRIGATÓRIA

Ao finalizar, entregar exatamente:

1. Objetivo.
2. Checagem inicial do ambiente.
3. Estado inicial do Git.
4. Mapa Manter/Adaptar/Consolidar/Remover.
5. Arquitetura V2 implementada.
6. Navegação final.
7. Arquivos criados.
8. Arquivos modificados.
9. Arquivos removidos.
10. Rotas removidas.
11. Rotas mantidas.
12. Componentes consolidados.
13. Módulos backend desativados ou removidos.
14. Testes atualizados.
15. Resultado do pytest.
16. Resultado do build.
17. Como testar, passo a passo.
18. Riscos conhecidos.
19. Débitos técnicos.
20. Documentação atualizada.
21. `git status --short`.
22. `git diff --stat`.
23. Sugestão de commit.

Mensagem sugerida:

```text
refactor(v2): simplify Friday Trade into an AI trading copilot
```

---

# REGRA FINAL

NÃO faça commit.

NÃO faça push.

Se a alteração ficar grande demais ou existir risco de apagar código ainda necessário, pare após a auditoria e entregue um plano dividido em fases.

Nunca faça uma remoção destrutiva sem verificar dependências e testes.