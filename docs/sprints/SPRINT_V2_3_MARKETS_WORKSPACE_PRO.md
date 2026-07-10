# FRIDAY TRADE V2.3

# MARKETS WORKSPACE PRO

Status

PLANNED

---

# Objetivo

Transformar Markets na principal tela do Friday Trade.

A partir desta Sprint:

Dashboard = Home

Markets = Centro de Operações

AI Analysis = Resultado

Replay = Histórico

Connections = Conector

Settings = Configurações

---

# Regras

NÃO alterar:

Backend

Connector

Providers

OAuth

APIs

Dependências

package.json

package-lock.json

Não fazer commit.

Não fazer push.

---

# Antes de começar

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

Confirmar que tudo continua verde.

---

# Objetivo visual

Markets deve parecer um software profissional.

Não um dashboard cheio de widgets.

Eliminar poluição visual.

Dar destaque para:

ativo

timeframe

gráfico

análise

---

# Layout

Topo:

Broker

Conta

Ambiente

Status

Última atualização

---

Linha seguinte

Selecionar ativo

Pesquisar ativo

Timeframe

M1

M5

M15

---

Depois

Top 12 ativos

Somente ativos válidos.

Sem seleção automática.

Ao clicar:

ativo torna-se o ativo operacional.

---

Depois

Watchlist

Favoritos

Preparar estrutura.

Sem banco.

---

Depois

Gráfico

Não renderizar enquanto não existir ativo válido.

Mostrar:

"Selecione um ativo para visualizar o gráfico."

---

Depois

Painel

Fonte dos dados

Broker

Origem

Última atualização

Disponibilidade

Qualidade

---

Botão principal

Analisar Ativo

Ele leva para:

/analysis

---

# Seleção de ativo

Hoje existe problema:

durante digitação

WebSocket tenta conectar com:

B

EU

USD

etc.

Isso NÃO pode acontecer.

Criar validação.

Somente aceitar:

ativos existentes.

Enquanto usuário digita:

não abrir gráfico

não abrir websocket

não abrir scanner

---

# Top 12

Top 12 deve ser clicável.

Ao clicar:

preencher ativo

renderizar gráfico

habilitar botão

Analisar Ativo

---

# Timeframe

Somente

M1

M5

M15

Sem H1 nesta Sprint.

---

# Gráfico

Renderizar apenas quando:

ativo válido

timeframe válido

Nunca antes.

---

# Estado vazio

Sem ativo:

Mostrar:

"Selecione um ativo para iniciar a análise."

---

# Estado carregando

Mostrar Loading.

Nunca tela branca.

---

# Analysis

Ao clicar:

Analisar Ativo

Enviar apenas:

ativo

timeframe

broker

ambiente

origem

Nenhum indicador.

Nenhuma IA.

Nenhuma probabilidade.

---

# UX

Markets deve ficar extremamente limpa.

Prioridade:

ativo

↓

gráfico

↓

analisar

Todo o resto é secundário.

---

# Como testar

Backend

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

.venv/bin/python -m uvicorn app.main:app --reload
```

Frontend

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend

npm run dev
```

Testar:

/markets

Sem ativo

↓

nenhum gráfico

↓

nenhum websocket

Digitar:

B

↓

nenhum websocket

Digitar:

USD

↓

nenhum websocket

Selecionar:

USDCHF-OTC

↓

gráfico aparece

↓

websocket permitido

↓

botão habilitado

↓

Analisar Ativo

↓

/analysis

Conferir:

Console limpo.

---

# Critérios de aprovação

Markets é a principal tela do Friday Trade.

Zero conexões antes do ativo válido.

Zero seleção automática.

Gráfico somente quando permitido.

Build aprovado.

Pytest aprovado.

Nenhum backend alterado.

---

# Entrega Obrigatória

1. Objetivo

2. Arquivos modificados

3. Arquivos criados

4. Componentes alterados

5. Fluxo da seleção de ativo

6. Resultado do pytest

7. Resultado do build

8. Como testar

9. Console antes/depois

10. git status --short

11. git diff --stat

12. Sugestão de commit

Sugestão:

feat(frontend): redesign Markets workspace for Friday Trade V2

Não fazer commit.

Não fazer push.