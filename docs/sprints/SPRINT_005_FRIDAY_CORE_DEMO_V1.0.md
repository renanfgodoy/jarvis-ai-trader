# SPRINT 005

# FRIDAY CORE DEMO V1.0

Friday AI Platform

Versão:

1.0

Status:

PLANNING

Tipo:

Frontend + Core Integration

---

# 1. OBJETIVO

Criar oficialmente a primeira demonstração funcional da Friday AI Platform.

O objetivo desta Sprint não é adicionar novas Engines.

O objetivo é provar que toda a arquitetura criada nas quatro primeiras Sprints funciona integrada.

A Demo deverá utilizar:

- Core Orchestrator
- Identity Engine
- Prompt Engine
- Provider Engine
- Mock Provider

Nenhuma chamada externa deverá ser realizada.

---

# 2. MISSÃO

Permitir que qualquer desenvolvedor execute:

npm run dev

Abra o navegador.

Digite uma mensagem.

Clique em Executar.

E visualize toda a arquitetura funcionando.

---

# 3. FLUXO OFICIAL

Frontend

↓

Demo Module

↓

Core Orchestrator

↓

Identity Engine

↓

Prompt Engine

↓

Provider Engine

↓

Mock Provider

↓

Execution Response

↓

Frontend

Nenhum componente poderá acessar Engines diretamente.

Todo fluxo deverá passar pelo Core Orchestrator.

---

# 4. PRINCÍPIOS

Princípio da Orquestração Única

Somente o Core Orchestrator coordena Engines.

Princípio da Substituição Transparente

Providers e Engines podem ser substituídos.

Princípio da Responsabilidade Única

Cada camada executa apenas sua função.

---

# 5. ARQUITETURA

frontend/

pages/

CoreDemo.tsx

components/

ExecutionForm.tsx

ExecutionPanel.tsx

PipelineViewer.tsx

DebugPanel.tsx

ResponseCard.tsx

StatusBadge.tsx

IdentitySelector.tsx

ProviderSelector.tsx

LanguageSelector.tsx

hooks/

useExecution.ts

services/

demoService.ts

---

# 6. TELA PRINCIPAL

Criar:

CoreDemo

Será a página oficial de demonstração da Friday.

Ela deverá conter:

Título

Logo Friday

Seleção de Identity

Seleção de Provider

Seleção de Idioma

Campo de Mensagem

Botão Executar

Painel da Resposta

Pipeline

Debug

---

# 7. EXECUTION FORM

Criar:

ExecutionForm

Campos:

Identity

Provider

Language

Message

Botão Execute Friday

O formulário nunca deverá chamar Engines diretamente.

Apenas demoService.

---

# 8. DEMO SERVICE

Criar:

demoService

Responsabilidade:

Montar ExecutionRequest.

Enviar para Core Orchestrator.

Receber ExecutionResponse.

Retornar ao Frontend.

Nenhuma regra de negócio.

---

# 9. HOOK

Criar:

useExecution()

Responsabilidades:

loading

response

error

execute()

reset()

Toda comunicação da tela deverá ocorrer através deste Hook.

---

# 10. RESPONSE CARD

Criar:

ResponseCard

Exibir:

Status

Identity

Provider

Latency

Fingerprint

Resposta

Timestamp

Metadata

Nunca exibir objetos internos.

Sempre utilizar ExecutionResponse.

---

# 11. STATUS BADGE

Criar:

StatusBadge

Estados:

READY

RUNNING

SUCCESS

FAILED

Visual simples.

---

# 12. PIPELINE VIEWER

Criar:

PipelineViewer

Mostrar:

✔ Validation

✔ Identity

✔ Prompt

✔ Provider

✔ Response

Animação simples de execução.

Sem dependências externas.

---

# 13. DEBUG PANEL

Criar:

DebugPanel

Objetivo:

Exibir o estado interno da Friday AI Platform durante a execução.

Exibir:

Core Orchestrator

Identity Engine

Prompt Engine

Provider Engine

Mock Provider

Pipeline Version

Execution Time

Execution ID

Request ID

Modo

Development

Todos os dados deverão ser obtidos através do ExecutionResponse.

---

# 14. PIPELINE ANIMATION

Durante a execução:

Validation

↓

Identity

↓

Prompt

↓

Provider

↓

Response

Cada etapa deverá mudar de estado:

WAITING

↓

RUNNING

↓

SUCCESS

Em caso de erro:

FAILED

Sem bibliotecas externas.

Utilizar apenas React.

---

# 15. EXECUTION REQUEST

O Frontend deverá criar:

ExecutionRequest

Campos:

module

identity

provider

language

message

metadata

Nunca criar objetos internos das Engines.

---

# 16. EXECUTION RESPONSE

Toda a interface utilizará apenas:

ExecutionResponse

Nunca acessar:

IdentityResult

PromptResult

ProviderResponse

ExecutionContext

Esses objetos permanecem internos do Core.

---

# 17. ERROR VIEW

Criar componente:

ExecutionError

Mostrar:

Status

Mensagem

Pipeline interrompido

Timestamp

Request ID

Nunca mostrar stack trace.

Nunca mostrar exceções internas.

---

# 18. LOADING STATE

Enquanto executa:

Botão desabilitado

Mostrar spinner

Atualizar Pipeline

Atualizar StatusBadge

Não permitir múltiplas execuções simultâneas.

---

# 19. DESIGN SYSTEM

Visual:

Tema escuro

Cinza grafite

Azul discreto

Tipografia limpa

Cards arredondados

Espaçamento consistente

Design inspirado em ferramentas para desenvolvedores.

---

# 20. TESTES

Criar testes para:

ExecutionForm

ResponseCard

PipelineViewer

DebugPanel

StatusBadge

useExecution

demoService

CoreDemo

Garantir:

✓ botão executa apenas uma vez

✓ loading funciona

✓ resposta aparece

✓ erro aparece

✓ pipeline atualiza

✓ debug atualiza

---

# 21. DOCUMENTAÇÃO

Criar:

docs/FRIDAY_CORE_DEMO.md

Conteúdo:

Objetivo

Arquitetura

Fluxo

Tela

Componentes

Pipeline

Debug

Roadmap

Atualizar:

docs/FRIDAY_ARCHITECTURE.md

Adicionar oficialmente o Developer Console como ambiente oficial de desenvolvimento da Friday.

---

# 22. CRITÉRIOS DE ACEITAÇÃO

A Sprint será considerada concluída quando:

✓ CoreDemo implementado

✓ ExecutionForm implementado

✓ DemoService implementado

✓ useExecution implementado

✓ ResponseCard implementado

✓ PipelineViewer implementado

✓ DebugPanel implementado

✓ Loading implementado

✓ Error View implementado

✓ Developer Console implementado

✓ Testes passando

✓ Build passando

✓ Nenhuma API externa

✓ Nenhum Provider real

✓ Fluxo completo funcionando

---

# 23. FORA DO ESCOPO

Não implementar:

OpenAI

Anthropic

Vision

Trading

Memory

Learning

Streaming

Banco

Login

Usuários

Persistência

Chat histórico

---

# 24. RELATÓRIO FINAL

Ao concluir entregar:

Resumo

Arquivos criados

Arquivos modificados

Tela criada

Fluxo integrado

Componentes

Testes

Build

Problemas

Decisões arquiteturais

Limitações

Próxima Sprint

Confirmar:

✓ Nenhuma API externa utilizada

✓ Nenhum Provider real utilizado

✓ Fluxo completo passando pelo Core Orchestrator

✓ Nenhum Module acessa Engines diretamente

# CRIADOR DE SPRINT — FRIDAY AI PLATFORM

Sprint:

SPRINT_005_FRIDAY_CORE_DEMO_V1.0

Objetivo:

Criar a primeira demonstração funcional da Friday AI Platform.

Fluxo obrigatório:

Frontend
↓
Demo Module
↓
Core Orchestrator
↓
Identity Engine
↓
Prompt Engine
↓
Provider Engine
↓
Mock Provider
↓
ExecutionResponse
↓
Frontend

Antes de alterar qualquer arquivo:

1. Ler a Sprint completa.
2. Revisar a arquitetura oficial.
3. Revisar Core Orchestrator.
4. Preservar compatibilidade.
5. Evitar duplicação.

Implementar apenas:

- CoreDemo
- ExecutionForm
- DemoService
- useExecution
- ResponseCard
- PipelineViewer
- DebugPanel
- StatusBadge
- ExecutionError
- Developer Console

Não implementar:

- APIs externas
- Streaming
- Vision
- Trading
- Memory
- Learning
- Banco
- Login
- Persistência

Executar:

- testes específicos
- suíte completa
- build

Somente declarar a Sprint concluída quando todos os critérios de aceitação forem atendidos.