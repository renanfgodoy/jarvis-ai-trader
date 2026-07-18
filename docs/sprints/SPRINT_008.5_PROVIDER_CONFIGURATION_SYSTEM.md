# SPRINT 008.5

# PROVIDER CONFIGURATION SYSTEM

Versão

0.2.1

Status

PLANNING

Tipo

Core Infrastructure

---

# OBJETIVO

Criar uma camada oficial de configuração para Providers.

O objetivo é permitir selecionar, habilitar, priorizar e monitorar Providers sem alterar código do Core.

Nenhum Provider real será implementado nesta Sprint.

---

# ARQUITETURA

Atual

Core Orchestrator

↓

Provider Engine

↓

Provider Loader

↓

Provider Registry

↓

Mock Provider

Nova

Core Orchestrator

↓

Provider Engine

↓

Provider Resolver

↓

Provider Configuration

↓

Provider Registry

↓

Selected Provider

---

# ESTRUTURA

core/providers/

config.py

settings.py

resolver.py

selector.py

feature_flags.py

health.py

environment.py

---

# PROVIDER CONFIGURATION

Criar ProviderConfiguration.

Campos

default_provider

enabled_providers

provider_priority

fallback_enabled

health_check_enabled

debug

environment

---

# PROVIDER RESOLVER

Responsabilidades

Selecionar Provider ativo.

Respeitar prioridade.

Respeitar feature flags.

Executar fallback quando necessário.

---

# FEATURE FLAGS

Criar suporte para:

mock

openai

gemini

anthropic

ollama

lmstudio

azure

Todos desabilitados, exceto Mock.

---

# HEALTH

Criar ProviderHealthManager.

Campos

status

uptime

last_execution

last_error

latency_average

request_count

---

# SETTINGS

Permitir configuração centralizada.

Nenhum valor hardcoded no Engine.

---

# DEVELOPER CONSOLE

Adicionar

Configuration

Environment

Default Provider

Enabled Providers

Fallback

Feature Flags

Health

---

# TESTES

Configuration

Resolver

Fallback

Feature Flags

Health

Developer Console

---

# DOCUMENTAÇÃO

Criar

docs/JARVIS_PROVIDER_CONFIGURATION.md

Atualizar

FRIDAY_ARCHITECTURE.md

Adicionar

Provider Configuration Layer

---

# CRITÉRIOS

ProviderConfiguration funcionando

Resolver funcionando

Feature Flags funcionando

Fallback funcionando

Health funcionando

Build OK

Todos testes OK

Nenhuma regressão

---

# FORA DO ESCOPO

OpenAI

Gemini

Anthropic

Ollama

LM Studio

Azure

Streaming

Vision

Memory