# SPRINT 002

# J.A.R.V.I.S Identity Engine V1.0

Friday AI Platform

Versão:

1.0

Status:

PLANNING

Tipo:

Core Architecture

---

# 1. OBJETIVO

Implementar oficialmente a Identity Engine da Friday AI Platform.

A Identity Engine será responsável por definir QUEM é o J.A.R.V.I.S.

Ela NÃO responde perguntas.

Ela NÃO conversa com o usuário.

Ela NÃO monta prompts.

Ela NÃO chama Providers.

Ela apenas produz uma identidade consistente que será utilizada pelo Prompt Engine.

Fluxo obrigatório:

Module
↓

Identity Request

↓

Identity Engine

↓

Identity Profile

↓

Prompt Engine

↓

Prompt Package

↓

Provider

---

# 2. VISÃO

Toda inteligência da Friday deverá possuir uma identidade explícita.

Nenhum módulo poderá definir personalidade manualmente.

Exemplo PROIBIDO

Trading Module

↓

"Você é um especialista em trading..."

↓

Provider

Exemplo CORRETO

Trading Module

↓

Identity Engine

↓

Trading Identity

↓

Prompt Engine

↓

Provider

---

# 3. MISSÃO DA IDENTITY ENGINE

A Identity Engine deverá responder apenas uma pergunta:

"Quem deve responder esta solicitação?"

Nunca:

"Como responder?"

Essa responsabilidade pertence ao Prompt Engine.

---

# 4. RESPONSABILIDADES

A Identity Engine será responsável por:

- selecionar identidade
- carregar perfil
- aplicar personalidade
- aplicar princípios
- aplicar idioma
- aplicar estilo
- aplicar restrições
- aplicar capacidades
- aplicar limitações
- aplicar metadata
- versionamento
- compatibilidade

Não deverá:

- montar PromptMessages
- chamar Provider
- chamar OpenAI
- chamar Vision
- acessar banco
- acessar memória
- interpretar imagens
- responder usuário

---

# 5. ARQUITETURA

core/

identity/

engine.py

registry.py

contracts.py

models.py

profiles.py

validators.py

exceptions.py

resolver.py

builder.py

config.py

metadata.py

tests/

docs/

---

# 6. CONCEITO

Identity Engine produz:

IdentityProfile

Prompt Engine produz:

PromptPackage

Provider produz:

AI Response

Cada camada possui apenas uma responsabilidade.

---

# 7. PRINCÍPIOS

Princípio 1

Identidade é imutável durante uma requisição.

Princípio 2

A identidade nunca chama Provider.

Princípio 3

Toda identidade possui versão.

Princípio 4

Toda identidade possui fingerprint.

Princípio 5

Toda identidade possui metadata.

Princípio 6

Nenhum módulo cria personalidade própria.

---

# 8. REGRA DE OURO DA FRIDAY

NENHUM MÓDULO ACESSA PROVIDERS.

NENHUM MÓDULO GERA PROMPTS.

NENHUM MÓDULO DEFINE PERSONALIDADE.

Fluxo obrigatório:

Module

↓

Identity Engine

↓

Prompt Engine

↓

Provider

↓

Resposta

Qualquer implementação fora desse fluxo deve ser considerada violação arquitetural.

---

# 9. IDENTITY PROFILE

Criar um contrato chamado:

IdentityProfile

Campos mínimos:

identity_id

version

display_name

description

language

tone

style

principles

capabilities

limitations

metadata

fingerprint

created_at

---

# 10. IDENTITY REQUEST

Criar:

IdentityRequest

Campos:

module

requested_identity

language

metadata

context

---

# 11. IDENTITY RESULT

Criar:

IdentityResult

Campos:

request_id

identity_profile

resolved_identity

metadata

fingerprint

timestamp

---

# 12. PRIMEIRAS IDENTIDADES

Criar apenas quatro identidades oficiais.

jarvis.default

Identidade neutra.

jarvis.trading

Especializada em análise financeira.

Sem emitir sinais automáticos.

jarvis.marketing

Especializada em marketing digital.

jarvis.finance

Especializada em gestão financeira.

Nenhuma outra identidade deverá existir nesta Sprint.

---

# 13. REGISTRY

Criar:

IdentityRegistry

Responsabilidades:

- registrar identidades
- impedir duplicidade
- localizar identidade
- localizar versão
- listar identidades
- listar versões
- definir identidade padrão
- falhar explicitamente quando não existir

Não utilizar auto-discovery nesta Sprint.

Todo registro deverá ser explícito.

---

# 14. RESOLVER

Criar:

IdentityResolver

Responsabilidades:

Receber:

IdentityRequest

Resolver:

IdentityProfile

Regras:

Caso o módulo não informe identidade:

↓

jarvis.default

Caso informe uma identidade inexistente:

↓

lançar exceção

Nunca realizar fallback silencioso.

---

# 15. BUILDER

Criar:

IdentityBuilder

Responsabilidades:

- montar IdentityResult
- aplicar metadata
- aplicar fingerprint
- aplicar timestamp
- validar estrutura

Não montar PromptMessages.

---

# 16. VERSIONAMENTO

Toda identidade deverá possuir:

identity_id

version

Exemplos:

jarvis.default@1.0

jarvis.trading@1.0

jarvis.marketing@1.0

jarvis.finance@1.0

Nunca sobrescrever versões existentes.

---

# 17. FINGERPRINT

Toda IdentityResult deverá possuir fingerprint determinístico.

Base sugerida:

identity_id

version

language

tone

style

principles

capabilities

limitations

metadata normalizada

Não utilizar:

request_id

timestamp

created_at

---

# 18. VALIDAÇÃO

Criar:

IdentityValidator

Validar:

- id obrigatório
- versão obrigatória
- idioma válido
- estilo válido
- tom válido
- princípios presentes
- capabilities serializáveis
- limitations serializáveis

Falhar explicitamente.

---

# 19. CONFIGURAÇÃO

Criar:

IdentityConfig

Campos mínimos:

default_identity

default_language

default_version

supported_languages

supported_modules

strict_validation

future_provider_support

Nenhuma configuração deverá depender de OpenAI.

---

# 20. OBSERVABILIDADE

Registrar:

request_id

identity_id

version

module

fingerprint

created_at

resolver_version

Não registrar conteúdo sensível.

---

# 21. TESTES

Criar testes para:

IdentityProfile

IdentityRequest

IdentityResult

Registry

Resolver

Builder

Validator

Versionamento

Fingerprint determinístico

Metadata

Fallback padrão

Identidade inexistente

Duplicidade

Compatibilidade

Arquitetura

Verificar que:

Identity Engine

↓

não importa Provider

↓

não chama rede

↓

não importa Vision

↓

não importa Memory

↓

não importa Prompt Engine

A dependência deve ser unidirecional.

---

# 22. DOCUMENTAÇÃO

Criar:

docs/JARVIS_IDENTITY_ENGINE.md

Conteúdo mínimo:

Objetivo

Arquitetura

Fluxo

Contratos

Profiles

Registry

Resolver

Builder

Versionamento

Fingerprint

Validação

Limitações

Roadmap

Atualizar:

docs/FRIDAY_ARCHITECTURE.md

Adicionar oficialmente:

Identity Engine

como segunda engine do J.A.R.V.I.S Core.

---

# 23. CRITÉRIOS DE ACEITAÇÃO

A Sprint será considerada concluída quando:

✓ Identity Engine implementada

✓ Registry funcional

✓ Resolver funcional

✓ Builder funcional

✓ Validator funcional

✓ Profiles registrados

✓ Versionamento funcional

✓ Fingerprint funcional

✓ Configuração criada

✓ Documentação criada

✓ Testes passando

✓ Build passando

✓ Nenhuma API chamada

✓ Nenhum Provider chamado

✓ Nenhum módulo define personalidade própria

---

# 24. FORA DO ESCOPO

Não implementar:

OpenAI

Vision

OCR

Trading

Memory

Learning

Embeddings

Banco Vetorial

Frontend

Streaming

Chat

Agentes

Ferramentas

RAG

Function Calling

JSON Schema avançado

---

# 25. RELATÓRIO FINAL

Ao concluir entregar:

Resumo

Arquivos criados

Arquivos modificados

Profiles criados

Contratos

Registry

Resolver

Builder

Validator

Testes

Build

Problemas

Limitações

Decisões arquiteturais

Próxima Sprint

Confirmação:

- nenhuma chamada externa
- nenhum Provider chamado
- nenhum acesso Module → Provider
- nenhum Git executado

# CRIADOR DE SPRINT — FRIDAY AI PLATFORM

Sprint:

SPRINT_002_JARVIS_IDENTITY_ENGINE_V1.0

Objetivo:

Implementar oficialmente a Identity Engine da Friday AI Platform.

Antes de alterar qualquer arquivo:

1. Ler completamente o Markdown da Sprint.
2. Revisar docs/FRIDAY_ARCHITECTURE.md.
3. Revisar Prompt Engine implementado.
4. Identificar contratos reutilizáveis.
5. Planejar implementação evitando duplicação.

REGRAS OBRIGATÓRIAS

NÃO implementar OpenAI.

NÃO implementar Vision.

NÃO implementar Trading.

NÃO implementar Memory.

NÃO implementar Learning.

NÃO implementar frontend.

NÃO criar PromptMessages.

NÃO chamar Provider.

NÃO acessar rede.

NÃO executar Git.

REGRA DE OURO DA FRIDAY

Module

↓

Identity Engine

↓

Prompt Engine

↓

Provider

↓

Resposta

É PROIBIDO:

Module

↓

Provider

OU

Module

↓

Prompt

OU

Module

↓

Personalidade manual

A Identity Engine deverá apenas produzir um IdentityProfile consistente.

Executar:

- testes específicos
- suíte completa
- build

Somente declarar a Sprint concluída quando todos os critérios de aceitação forem atendidos.