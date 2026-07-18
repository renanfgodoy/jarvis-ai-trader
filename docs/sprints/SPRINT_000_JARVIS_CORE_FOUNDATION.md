# 🚀 SPRINT 0 — FRIDAY AI PLATFORM
## J.A.R.V.I.S CORE FOUNDATION

Status:
PLANNING

Versão:
2.0

Objetivo:

Transformar definitivamente a Friday de um projeto focado em Trading para uma Plataforma de Inteligência Artificial modular, escalável e preparada para crescimento de longo prazo.

---

# VISÃO

A Friday deixa de ser apenas uma aplicação que envia prompts para um modelo de IA.

Ela passa a ser uma plataforma onde a IA é apenas um dos componentes.

Toda inteligência da aplicação será organizada dentro do J.A.R.V.I.S Core.

---

# NOVA ARQUITETURA

Friday AI Platform

Core

Modules

Shared

API

Frontend

---

# CRIAR

/core

/core/identity

/core/prompts

/core/memory

/core/vision

/core/decision

/core/risk

/core/context

/core/learning

/core/analytics

/core/audit

/core/providers

/modules

/modules/trading

/shared

/docs

---

# DOCUMENTAÇÃO

Criar:

docs/

FRIDAY_ARCHITECTURE.md

Conteúdo:

- Visão do produto
- Objetivos
- Filosofia
- Estrutura do projeto
- Responsabilidades
- Fluxo de IA
- Roadmap
- Convenções

---

# DEFINIR

J.A.R.V.I.S Core

Motores oficiais

Identity Engine

Responsável por:

- identidade
- personalidade
- comportamento

---

Prompt Engine

Responsável por:

- construir prompts
- padronizar contexto
- controlar temperatura
- controlar tokens
- instruções globais

---

Vision Engine

Responsável por:

- imagens
- screenshots
- OCR (futuro)
- pré-processamento

---

Memory Engine

Responsável por:

- histórico
- preferências
- contexto
- cache

---

Decision Engine

Responsável por:

- transformar resposta da IA
- validar formato
- gerar decisão final

---

Risk Engine

Responsável por:

- risco
- confiança
- score

---

Analytics Engine

Responsável por:

- estatísticas
- dashboards
- métricas

---

Audit Engine

Responsável por:

- logs
- auditoria
- rastreabilidade

---

Provider Engine

Responsável por:

- OpenAI
- futuros modelos
- abstração

Nunca permitir acesso direto dos módulos aos providers.

Todo acesso deve passar pelo Core.

---

# REGRA DE OURO

PROIBIDO

Module

↓

Provider

OBRIGATÓRIO

Module

↓

J.A.R.V.I.S Core

↓

Provider

↓

J.A.R.V.I.S Core

↓

Module

---

# RENOMEAR

Toda referência visual

Friday AI Trader

↓

Friday AI Platform

Sempre preservar o nome Friday.

Trading passa a ser apenas um módulo.

---

# MÓDULOS

Criar arquitetura para:

Trading

Finance

Marketing

SEO

Documents

Automation

Sites

CRM

Todos inicialmente como placeholders.

---

# PREPARAR

Sistema para múltiplos providers.

Estrutura:

Provider Interface

OpenAI Provider

Mock Provider

Provider Factory

Não implementar outros modelos ainda.

Apenas preparar a arquitetura.

---

# NÃO IMPLEMENTAR NESTA SPRINT

OpenAI API

Vision

Chat

Trading

OCR

Aprendizado

Banco vetorial

RAG

Automação

---

# OBJETIVO FINAL

Ao terminar esta Sprint, a Friday deverá possuir uma arquitetura preparada para crescer durante anos sem necessidade de reestruturação.

Nenhuma funcionalidade nova deve ser criada.

A Sprint é exclusivamente arquitetural.