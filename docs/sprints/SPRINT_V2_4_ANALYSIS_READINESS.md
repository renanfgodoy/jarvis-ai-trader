# FRIDAY TRADE V2.4

# ANALYSIS READINESS

Status

PLANNED

---

# Objetivo

Criar a tela oficial de preparação da análise.

Esta Sprint NÃO implementa IA.

Esta Sprint NÃO implementa indicadores.

Esta Sprint NÃO implementa Probability Engine.

Ela cria o processo de validação antes da análise.

O Friday Trade nunca deve analisar um ativo sem confirmar que possui dados suficientes.

---

# Regras

NÃO alterar:

- Backend
- APIs
- Connector
- Providers
- OAuth
- Dependências
- package.json
- package-lock.json

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

Tudo deve permanecer verde.

---

# Objetivo visual

A tela

/analysis

deve parecer um checklist profissional.

Não um dashboard.

Não uma tela técnica.

Ela deve responder apenas:

"Podemos analisar este ativo?"

---

# Layout

Topo

Ativo

Timeframe

Broker

Conta

Ambiente

---

Depois

CHECKLIST

---

Card 1

Ativo selecionado

Status

OK

ou

Não selecionado

---

Card 2

Timeframe

M1

M5

M15

ou

Não definido

---

Card 3

Broker

Disponível

ou

Indisponível

---

Card 4

Fonte dos dados

Polarium

TradingView

Provider

Indisponível

---

Card 5

Conexão

Conectado

Desconectado

---

Card 6

Candles disponíveis

Enquanto não existirem:

Mostrar

Não disponível

Nunca inventar quantidade.

---

Card 7

Quantidade mínima

Necessário

100 candles

Atual

Indisponível

---

Card 8

Última atualização

Mostrar timestamp conhecido.

Nunca inventar horário.

---

# Resultado

No final da tela

Mostrar apenas um estado.

READY

ou

NOT READY

ou

PARTIAL

Baseado apenas nos dados reais disponíveis.

---

# Motivos

Quando não estiver pronto

Mostrar exatamente o motivo.

Exemplo

```text
Análise indisponível.

Motivos:

• Candles não disponíveis.

• Fonte de dados insuficiente.

• Ativo não selecionado.
```

Nunca mostrar mensagens genéricas.

---

# Botão

Enquanto não estiver READY

Botão:

Iniciar Análise

deve permanecer desabilitado.

---

Quando estiver READY

Apenas mostrar:

```text
Sistema pronto para análise.

Engine de IA será implementada em Sprint futura.
```

Ainda não executar IA.

---

# Dados compartilhados

Consumir apenas:

Market Data Context

Broker

Conta

Ambiente

Ativo

Timeframe

Status da conexão

Última atualização

Nenhum endpoint novo.

---

# UX

Tela limpa.

Poucos cards.

Muito espaço.

Ícones discretos.

Sem poluição visual.

---

# Estados

Sem ativo

↓

NOT READY

Sem broker

↓

NOT READY

Sem conexão

↓

PARTIAL

Sem candles

↓

PARTIAL

Tudo disponível

↓

READY

Mesmo em READY

Não executar análise.

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

/analysis

Sem ativo

↓

NOT READY

Selecionar ativo em Markets

↓

Voltar

↓

Ativo aparece

↓

Timeframe aparece

↓

Broker aparece

↓

Fonte aparece

↓

Candles continuam indisponíveis

↓

Botão permanece desabilitado

Console deve permanecer limpo.

---

# Critérios de aprovação

Nenhum backend alterado.

Nenhuma API alterada.

Nenhum endpoint novo.

Nenhum indicador criado.

Nenhuma IA criada.

Nenhuma probabilidade criada.

Nenhum dado inventado.

Tela preparada para futura Engine de IA.

---

# Entrega Obrigatória

1. Objetivo

2. Arquivos modificados

3. Arquivos criados

4. Componentes criados

5. Fluxo READY / PARTIAL / NOT READY

6. Resultado do pytest

7. Resultado do build

8. Como testar

9. git status --short

10. git diff --stat

11. Sugestão de commit

Sugestão:

feat(frontend): implement analysis readiness workflow

Não fazer commit.

Não fazer push.