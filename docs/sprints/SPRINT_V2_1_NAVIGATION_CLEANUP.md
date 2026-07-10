# FRIDAY TRADE V2.1
# NAVIGATION CLEANUP

Status

PLANNED

---

# Objetivo

Iniciar oficialmente a Friday Trade V2 reorganizando a experiência do usuário.

Esta Sprint NÃO altera backend.

Esta Sprint NÃO altera APIs.

Esta Sprint NÃO altera Connector.

Esta Sprint NÃO altera Providers.

Esta Sprint NÃO altera testes do backend.

Esta Sprint é exclusivamente de Frontend.

Objetivo:

Transformar a navegação em uma experiência limpa, profissional e focada em análise.

---

# Regras

NÃO fazer commit.

NÃO fazer push.

Antes de alterar qualquer arquivo:

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

pwd
git rev-parse --show-toplevel
git branch --show-current
git status --short

.venv/bin/python -m pytest -q

cd frontend
npm run build
```

Confirmar que tudo continua passando.

---

# Nova Sidebar

A Sidebar oficial passa a ser:

```text
Dashboard

Markets

AI Analysis

Replay

Connections

Settings

------------------

Developer

└── Polarium Lab
```

Remover da Sidebar principal:

- Operation
- Market Data
- Market Intelligence
- Diagnostics
- Branding
- páginas experimentais
- AutoTrade
- Execution

Essas páginas poderão continuar existindo temporariamente, mas não devem aparecer na navegação principal.

---

# Dashboard

Objetivo:

Ser apenas um resumo.

Mostrar apenas:

- broker
- ambiente
- conta
- moeda
- ativo selecionado
- timeframe
- status da conexão
- última sincronização
- botão para abrir Markets

Remover widgets técnicos.

Remover painéis enormes.

Remover qualquer fluxo operacional.

O Dashboard não deve parecer um terminal.

Deve parecer uma Home.

---

# Markets

Esta passa a ser a tela principal do sistema.

Objetivo:

Escolher o ativo.

Escolher o timeframe.

Visualizar o mercado.

Preparar a análise.

A tela deverá conter:

- seletor de timeframe
- seletor de ativo
- Top 12 ativos
- Watchlist
- gráfico
- botão

```text
Analisar Ativo
```

Sem ativo selecionado:

Mostrar:

```text
Selecione um ativo para iniciar.
```

Não selecionar automaticamente o primeiro ativo.

Não inventar ativos.

Não inventar candles.

---

# AI Analysis

Nova rota oficial:

```text
/analysis
```

Esta Sprint NÃO implementa IA.

Ela apenas prepara a tela.

Mostrar:

```text
AI Analysis

Aguardando dados do mercado.

Selecione um ativo em Markets para iniciar.
```

Se existir ativo:

Mostrar:

- ativo
- timeframe
- broker
- ambiente
- origem dos dados

Nada além disso.

Sem probabilidade.

Sem CALL.

Sem PUT.

Sem EMA.

Sem RSI.

Sem indicadores fictícios.

---

# Replay

Criar estrutura da página.

Mostrar:

```text
Replay

Nenhuma análise registrada.
```

Adicionar botão:

```text
Novo Registro
```

Ainda sem banco.

Ainda sem IA.

Preparar arquitetura.

---

# Connections

Manter a Central de Conexões.

Não alterar backend.

Não alterar OAuth.

Não alterar Connector.

Apenas adequar o visual ao restante da aplicação.

---

# Settings

Manter:

- Tema
- Broker
- Preferências
- Perfil
- Notificações

Remover da interface:

AutoTrade

Execution

Martingale

Execution Gate

---

# Branding

Continuar utilizando:

Friday Trade

Trade Smarter.

Não alterar logo nesta Sprint.

---

# Navegação

Atualizar:

App.tsx

Sidebar

Hooks

Rotas

Remover apenas da navegação.

Não apagar páginas antigas.

---

# Componentes Duplicados

Verificar:

Header.tsx

Header/index.tsx

Sidebar.tsx

Sidebar/index.tsx

Descobrir qual implementação realmente está sendo usada.

Se existir duplicação:

Manter apenas uma implementação oficial.

Atualizar imports.

Remover a duplicada somente se não houver referências.

---

# Como Testar

Backend:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

.venv/bin/python -m uvicorn app.main:app --reload
```

Frontend:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend

npm run dev
```

Validar:

/dashboard

/markets

/analysis

/replay

/connections/polarium

/settings

/labs/polarium

Confirmar:

✓ Sidebar nova

✓ Dashboard limpo

✓ Markets como tela principal

✓ AI Analysis criada

✓ Replay criado

✓ Connections funcionando

✓ Settings funcionando

✓ Build aprovado

✓ Pytest aprovado

---

# Critérios de Aprovação

Nenhum backend alterado.

Nenhuma API alterada.

Nenhum Connector alterado.

Nenhum Provider alterado.

Nenhum teste quebrado.

Nenhuma página gigante.

Sidebar simplificada.

Produto visualmente mais limpo.

Fluxo mais intuitivo.

---

# Entrega Obrigatória

Ao finalizar entregar:

1. Objetivo

2. Arquivos modificados

3. Arquivos criados

4. Rotas alteradas

5. Sidebar final

6. Componentes consolidados

7. Resultado do pytest

8. Resultado do build

9. Como testar

10. Riscos conhecidos

11. git status --short

12. git diff --stat

13. Sugestão de commit

Sugestão:

```text
refactor(frontend): simplify navigation for Friday Trade V2
```

Não fazer commit.

Não fazer push.