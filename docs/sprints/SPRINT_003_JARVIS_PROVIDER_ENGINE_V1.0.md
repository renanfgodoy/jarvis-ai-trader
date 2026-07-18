# SPRINT 003

# J.A.R.V.I.S Provider Engine V1.0

Friday AI Platform

Versão:

1.0

Status:

PLANNING

Tipo:

Core Architecture

---

# 1. OBJETIVO

Implementar oficialmente a Provider Engine da Friday AI Platform.

A Provider Engine será responsável por toda comunicação entre a Friday AI Platform e qualquer modelo de Inteligência Artificial.

Ela será a única camada autorizada a conversar com APIs externas de IA.

Toda a aplicação deverá utilizar esta camada.

Nunca diretamente.

---

# 2. MISSÃO

A Provider Engine deverá responder apenas uma pergunta:

"Como conversar com um Provider?"

Ela nunca deverá decidir:

- personalidade
- contexto
- prompts
- regras de negócio

Essas responsabilidades pertencem respectivamente à:

Identity Engine

Prompt Engine

Modules

---

# 3. REGRA DE OURO DA FRIDAY

É OBRIGATÓRIO:

Module

↓

Identity Engine

↓

Prompt Engine

↓

Provider Engine

↓

AI Provider

↓

Resposta

É PROIBIDO:

Module

↓

Provider

OU

Module

↓

API

OU

Module

↓

HTTP

OU

Prompt Engine

↓

Provider

OU

Identity Engine

↓

Provider

Toda chamada externa deverá obrigatoriamente passar pela Provider Engine.

---

# 4. NOVA REGRA OFICIAL

PRINCÍPIO DA SUBSTITUIÇÃO TRANSPARENTE

Qualquer Provider poderá ser removido ou substituído sem alterar:

Modules

Identity

Prompt

Vision

Trading

Memory

Learning

Apenas configuração.

---

# 5. RESPONSABILIDADES

A Provider Engine deverá:

- selecionar provider
- validar provider
- validar capabilities
- executar requisição
- normalizar resposta
- tratar erros
- retry
- fallback
- health check
- observabilidade
- métricas

Nunca deverá:

- criar prompts
- definir personalidade
- interpretar gráficos
- analisar trading
- acessar memória
- responder usuário diretamente

---

# 6. ARQUITETURA

core/

provider/

engine.py

factory.py

registry.py

contracts.py

models.py

config.py

health.py

capabilities.py

retry.py

fallback.py

errors.py

validators.py

metadata.py

tests/

docs/

---

# 7. PROVIDER ENGINE

Criar:

ProviderEngine

Responsabilidades:

receber PromptPackage

selecionar Provider

validar capabilities

executar provider

receber resposta

normalizar resposta

retornar ProviderResponse

Nunca retornar resposta bruta da API.

---

# 8. PROVIDER FACTORY

Criar:

ProviderFactory

Responsabilidades:

instanciar Providers

configurar Providers

reutilizar Providers

impedir criação duplicada

Suportar expansão futura.

---

# 9. PROVIDER REGISTRY

Criar:

ProviderRegistry

Responsabilidades:

registrar Providers

listar Providers

listar versões

identificar Provider padrão

identificar Provider ativo

validar duplicidade

---

# 10. PRIMEIROS PROVIDERS

Nesta Sprint criar apenas placeholders.

openai

anthropic

google

groq

ollama

lmstudio

Nenhum deverá chamar API.

Todos deverão implementar apenas contratos.

---

# 11. PROVIDER CONTRACT

Criar:

BaseProvider

Métodos mínimos:

connect()

health()

capabilities()

invoke()

close()

Todos deverão seguir exatamente esta interface.

---

# 12. PROVIDER RESPONSE

Criar:

ProviderResponse

Campos mínimos:

provider

provider_version

request_id

response

usage

latency

metadata

status

fingerprint

timestamp

Nunca expor resposta crua da API.

---

# 13. CAPABILITY REGISTRY

Criar:

ProviderCapabilityRegistry

Objetivo:

Permitir que a Friday descubra automaticamente quais funcionalidades cada Provider suporta.

Cada Provider deverá declarar explicitamente suas capacidades.

Exemplo:

OpenAI

- chat
- vision
- json
- streaming
- tool_calling
- embeddings

Anthropic

- chat
- vision
- streaming
- tool_use

Ollama

- chat
- local
- embeddings

Groq

- chat
- streaming

Nunca assumir capacidades por inferência.

---

# 14. HEALTH ENGINE

Criar:

ProviderHealth

Status possíveis:

ONLINE

OFFLINE

DEGRADED

LIMITED

RATE_LIMITED

UNKNOWN

A Provider Engine deverá consultar o estado do Provider antes da execução quando aplicável.

---

# 15. RETRY POLICY

Criar:

RetryPolicy

Responsabilidades:

- quantidade máxima de tentativas
- intervalo entre tentativas
- backoff exponencial futuro
- classificação de erros recuperáveis

Não executar retry infinito.

---

# 16. FALLBACK POLICY

Criar:

FallbackPolicy

Fluxo:

Provider Principal

↓

Falhou

↓

Provider Secundário

↓

Resposta

O fallback deverá ser opcional e configurável.

---

# 17. PROVIDER CONFIG

Criar:

ProviderConfig

Campos mínimos:

default_provider

fallback_provider

retry_enabled

retry_attempts

request_timeout

health_check_enabled

strict_capabilities

Nenhuma chave de API deverá ser obrigatória nesta Sprint.

---

# 18. PROVIDER VALIDATOR

Criar:

ProviderValidator

Validar:

- provider registrado
- capabilities obrigatórias
- configuração válida
- resposta válida
- metadata válida

Falhar explicitamente.

---

# 19. OBSERVABILIDADE

Registrar:

request_id

provider

provider_version

latency

status

retry_count

fallback_used

fingerprint

timestamp

Não registrar prompts completos nem dados sensíveis.

---

# 20. TESTES

Criar testes para:

ProviderRegistry

ProviderFactory

ProviderEngine

ProviderValidator

CapabilityRegistry

Health

Retry

Fallback

ProviderResponse

Configuração

Arquitetura

Verificar que:

- Modules não importam Providers
- Prompt Engine não acessa rede
- Identity Engine não acessa rede
- Apenas Provider Engine conversa com Providers

---

# 21. DOCUMENTAÇÃO

Criar:

docs/JARVIS_PROVIDER_ENGINE.md

Conteúdo mínimo:

- Objetivo
- Arquitetura
- Fluxo
- Contratos
- Providers
- Capabilities
- Health
- Retry
- Fallback
- Versionamento
- Observabilidade
- Roadmap

Atualizar:

docs/FRIDAY_ARCHITECTURE.md

Adicionar oficialmente a Provider Engine como terceira engine do J.A.R.V.I.S Core.

---

# 22. CRITÉRIOS DE ACEITAÇÃO

A Sprint será considerada concluída quando:

✓ Provider Engine implementada

✓ Factory implementada

✓ Registry implementado

✓ Contracts implementados

✓ Capability Registry funcional

✓ Health Engine funcional

✓ Retry Policy criada

✓ Fallback Policy criada

✓ Configuração criada

✓ Validator criado

✓ Documentação criada

✓ Testes passando

✓ Build passando

✓ Nenhuma API real conectada

✓ Nenhuma chave obrigatória

✓ Nenhum Module acessando Provider diretamente

---

# 23. FORA DO ESCOPO

Não implementar:

- chamadas reais para OpenAI
- chamadas para Anthropic
- chamadas para Gemini
- chamadas para Ollama
- streaming
- Vision
- Memory
- Trading
- Learning
- Frontend
- OCR
- Embeddings reais
- Function Calling

Todos os Providers deverão ser placeholders compatíveis com a arquitetura.

---

# 24. RELATÓRIO FINAL

Ao concluir entregar:

- Resumo
- Estrutura criada
- Arquivos criados
- Arquivos modificados
- Providers registrados
- Contracts
- Factory
- Registry
- Capability Registry
- Health
- Retry
- Fallback
- Testes
- Build
- Problemas
- Limitações
- Próxima Sprint

Confirmar:

- nenhuma API externa utilizada
- nenhum Provider real chamado
- nenhum Module acessa Provider
- nenhum comando Git de alteração executado

# CRIADOR DE SPRINT — FRIDAY AI PLATFORM

Sprint:

SPRINT_003_JARVIS_PROVIDER_ENGINE_V1.0

Objetivo:

Implementar oficialmente a Provider Engine da Friday AI Platform.

REGRA DE OURO

Module
↓
Identity Engine
↓
Prompt Engine
↓
Provider Engine
↓
AI Provider
↓
Resposta

É proibido:

Module → Provider

Module → HTTP

Module → API

Identity → Provider

Prompt → Provider

Vision → Provider

Trading → Provider

Antes de alterar qualquer arquivo:

1. Ler toda a Sprint.
2. Revisar docs/FRIDAY_ARCHITECTURE.md.
3. Revisar Prompt Engine.
4. Revisar Identity Engine.
5. Planejar implementação evitando duplicações.

Implementar apenas:

- ProviderEngine
- ProviderFactory
- ProviderRegistry
- ProviderContracts
- CapabilityRegistry
- Health
- Retry
- Fallback
- Validator
- Config
- Response
- Metadata
- Documentação
- Testes

Não implementar:

- OpenAI real
- Anthropic real
- Gemini real
- Ollama real
- Streaming
- Vision
- Trading
- Memory
- Learning
- Banco de dados
- Frontend

Executar:

- testes específicos
- suíte completa
- build

Somente declarar a Sprint concluída quando todos os critérios de aceitação forem atendidos.