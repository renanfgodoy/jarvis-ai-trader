# FRIDAY TRADE V2.2
# RUNTIME CLEANUP

Status

PLANNED

---

# Objetivo

Eliminar carregamentos desnecessários do frontend.

Cada página deve carregar somente os componentes e conexões que realmente utiliza.

Esta Sprint NÃO altera:

- Backend
- APIs
- Connector
- Providers
- OAuth
- WebSocket Backend
- Banco
- Dependências
- package.json
- package-lock.json

É uma Sprint exclusivamente de arquitetura Frontend.

---

# Regras

Não fazer commit.

Não fazer push.

Executar antes:

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

Confirmar que tudo passa.

---

# Problema encontrado

Hoje o Console mostra:

WebSocket connection failed

mesmo estando em páginas como:

Replay

Dashboard

Settings

Isso significa que algum componente compartilhado inicia:

- WebSocket
- Chart
- Live Workspace
- Scanner

mesmo quando a página não precisa.

---

# Objetivo da Sprint

Cada página terá seu próprio runtime.

Nenhuma página deve iniciar serviços de mercado automaticamente.

---

# Dashboard

O Dashboard NÃO pode abrir:

- WebSocket
- Scanner
- Candles
- Live Workspace
- Streams

Mostrar somente:

- Broker
- Ambiente
- Conta
- Moeda
- Ativo
- Timeframe
- Última sincronização

---

# Replay

Replay NÃO pode carregar:

- ChartCard
- TopAssets
- MarketScanner
- WebSocket
- Candles
- Workspace Live

Console deve permanecer limpo.

---

# Settings

Settings NÃO pode abrir:

- Scanner
- WebSocket
- Market Feed

---

# Connections

Connections pode consultar apenas:

- status
- OAuth
- sessão
- conta
- moeda

Não abrir gráfico automaticamente.

---

# Markets

Markets passa a ser a ÚNICA página autorizada a iniciar:

- gráfico
- scanner
- live workspace
- websocket
- market feed

Mesmo assim:

Somente depois que existir ativo selecionado.

Jamais conectar automaticamente.

---

# AI Analysis

Também NÃO inicia WebSocket sozinho.

Somente recebe:

ativo

timeframe

broker

ambiente

origem

Quando futuramente existir análise, ela consumirá o Market Data Engine.

---

# Chart

Revisar:

ChartCard

Hooks

MarketScannerWidget

TopAssets

Workspace

Identificar:

Quem está iniciando WebSocket.

Mover essa responsabilidade para Markets.

---

# Runtime

Nenhum hook global deve abrir conexão.

Nenhum Provider global deve iniciar Scanner.

Nenhum Layout deve iniciar Chart.

Tudo deve ser lazy.

---

# Branding

Remover da interface:

simulated

AI TRADER

JARVIS

Qualquer texto legado.

Manter apenas:

Friday Trade

Trade Smarter.

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

Validar:

/dashboard

Console limpo

/replay

Console limpo

/settings

Console limpo

/connections/polarium

Sem gráfico automático

/markets

Nenhuma conexão antes da seleção de ativo

Selecionar ativo

Somente agora o gráfico pode iniciar

Abrir DevTools

Network

WS

Confirmar:

Replay → zero conexões WS

Dashboard → zero conexões WS

Settings → zero conexões WS

Markets sem ativo → zero conexões WS

Markets com ativo → WS permitido

---

# Critérios de aprovação

Zero WebSocket fora de Markets.

Zero Scanner fora de Markets.

Zero Chart fora de Markets.

Console limpo.

Backend inalterado.

APIs inalteradas.

Build aprovado.

Pytest aprovado.

---

# Entrega Obrigatória

1. Objetivo

2. Quem iniciava o WebSocket

3. Arquivos modificados

4. Hooks alterados

5. Componentes alterados

6. Resultado do pytest

7. Resultado do build

8. Como testar

9. Console antes/depois

10. git status --short

11. git diff --stat

12. Sugestão de commit

Sugestão:

refactor(frontend): isolate runtime to market workspace

Não fazer commit.

Não fazer push.