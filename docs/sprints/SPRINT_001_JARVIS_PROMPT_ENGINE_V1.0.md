# SPRINT 001 — J.A.R.V.I.S PROMPT ENGINE V1.0

## FRIDAY AI PLATFORM

Status:

PLANNING

Versão:

1.0

Tipo:

Architecture + Core Implementation

---

# 1. OBJETIVO

Implementar a primeira versão funcional do J.A.R.V.I.S Prompt Engine.

O Prompt Engine será responsável por construir, organizar, validar e versionar todas as instruções enviadas aos providers de inteligência artificial.

Nenhum módulo da Friday deverá montar prompts livremente ou enviar instruções diretamente para um provider.

O fluxo obrigatório será:

```text
Module
  ↓
Prompt Request
  ↓
J.A.R.V.I.S Prompt Engine
  ↓
Prompt Package
  ↓
Core Provider Layer
```

Nesta Sprint, o Prompt Engine não deverá realizar chamadas reais para OpenAI ou qualquer outro provider externo.

---

# 2. CONTEXTO

A Friday AI Platform já possui uma fundação arquitetural composta por:

- core
- modules
- shared
- engines
- providers
- contratos base
- documentação arquitetural

Agora será implementada a primeira engine funcional do J.A.R.V.I.S Core.

O Prompt Engine será utilizado futuramente pelos módulos:

- Trading
- Finance
- Marketing
- SEO
- Documents
- Sites
- CRM
- Automation

Cada módulo poderá solicitar um prompt, mas não poderá controlar diretamente a estrutura final enviada ao modelo.

---

# 3. PRINCÍPIO CENTRAL

A construção de prompts deve ser centralizada.

PROIBIDO:

```text
Trading Module
  ↓
string manual de prompt
  ↓
OpenAI Provider
```

OBRIGATÓRIO:

```text
Trading Module
  ↓
PromptRequest
  ↓
Prompt Engine
  ↓
PromptPackage validado
  ↓
Provider
```

---

# 4. ESCOPO DA SPRINT

Implementar:

- contratos do Prompt Engine
- modelos de entrada
- modelos de saída
- templates de prompt
- registro de templates
- versionamento
- validação
- composição de contexto
- sanitização básica
- cálculo aproximado de tamanho
- identificação do módulo solicitante
- identificação do template utilizado
- metadata
- testes unitários
- documentação

Não implementar:

- chamadas reais para OpenAI
- integração com ChatGPT
- Vision
- OCR
- Memory persistente
- banco vetorial
- RAG
- análise de trading
- decisões CALL ou PUT
- interface visual
- streaming
- ferramentas externas
- function calling
- automações
- aprendizado

---

# 5. ESTRUTURA ESPERADA

Adaptar a estrutura aos padrões atuais do projeto sem criar duplicação desnecessária.

Estrutura conceitual desejada:

```text
core/
└── prompts/
    ├── __init__.py
    ├── engine.py
    ├── contracts.py
    ├── models.py
    ├── registry.py
    ├── validators.py
    ├── sanitizer.py
    ├── estimator.py
    ├── exceptions.py
    └── templates/
        ├── __init__.py
        ├── base.py
        ├── system.py
        └── generic.py
```

Caso a Sprint anterior já tenha criado arquivos equivalentes, reutilizar e evoluir a estrutura existente.

Não criar duas implementações para a mesma responsabilidade.

---

# 6. CONTRATOS PRINCIPAIS

## 6.1 PromptRequest

Criar um contrato representando uma solicitação de prompt.

Campos mínimos:

```text
module
template_id
template_version
user_input
context
metadata
language
response_format
```

Regras:

- `module` é obrigatório.
- `template_id` é obrigatório.
- `user_input` pode ser opcional dependendo do template.
- `context` deve aceitar estrutura serializável.
- `metadata` deve aceitar informações auxiliares.
- `language` deve possuir valor padrão.
- `response_format` deve aceitar formato textual ou estruturado.

---

## 6.2 PromptMessage

Representa uma mensagem individual.

Campos mínimos:

```text
role
content
name
metadata
```

Roles permitidas inicialmente:

```text
system
developer
user
assistant
```

O Prompt Engine não deverá aceitar roles desconhecidas sem validação.

---

## 6.3 PromptPackage

Representa o resultado final construído pelo Prompt Engine.

Campos mínimos:

```text
request_id
module
template_id
template_version
messages
metadata
estimated_size
created_at
fingerprint
```

O PromptPackage deverá ser imutável ou tratado como objeto finalizado depois de construído.

---

## 6.4 PromptTemplate

Contrato base para templates.

Campos mínimos:

```text
template_id
version
description
supported_modules
required_fields
```

Método principal conceitual:

```text
build(request) -> list[PromptMessage]
```

---

# 7. PROMPT ENGINE

Criar uma classe principal:

```text
PromptEngine
```

Responsabilidades:

1. receber um `PromptRequest`;
2. validar os dados recebidos;
3. localizar o template correto;
4. validar a versão do template;
5. sanitizar entradas;
6. construir as mensagens;
7. validar as mensagens finais;
8. calcular tamanho aproximado;
9. gerar fingerprint;
10. produzir um `PromptPackage`;
11. nunca realizar chamada de rede;
12. nunca chamar provider diretamente.

Interface conceitual:

```python
prompt_package = prompt_engine.build(request)
```

---

# 8. TEMPLATE REGISTRY

Criar um registro central de templates:

```text
PromptTemplateRegistry
```

Responsabilidades:

- registrar templates;
- impedir duplicidade de `template_id + version`;
- localizar template por ID;
- localizar versão específica;
- listar templates disponíveis;
- listar versões disponíveis;
- definir versão padrão quando aplicável;
- falhar explicitamente quando um template não existir.

Não utilizar descoberta automática complexa nesta Sprint.

Preferir registro explícito, previsível e testável.

---

# 9. TEMPLATES INICIAIS

Criar apenas templates genéricos para validar a arquitetura.

## 9.1 Core System Template

Identificador sugerido:

```text
core.system
```

Objetivo:

Gerar uma instrução base neutra da Friday AI Platform.

Não implementar ainda a personalidade completa do J.A.R.V.I.S.

A Identity Engine será responsável por isso em Sprint futura.

---

## 9.2 Generic Analysis Template

Identificador sugerido:

```text
core.generic_analysis
```

Objetivo:

Receber uma entrada do usuário e contexto opcional, produzindo uma estrutura de mensagens pronta para um provider futuro.

Este template não deve conter regras específicas de Trading.

---

## 9.3 Generic Structured Response Template

Identificador sugerido:

```text
core.structured_response
```

Objetivo:

Preparar uma solicitação de resposta estruturada.

Não implementar JSON Schema avançado nesta Sprint.

Apenas preparar metadata e instruções claras sobre o formato esperado.

---

# 10. VERSIONAMENTO

Todo template deverá possuir versão explícita.

Formato recomendado:

```text
1.0
1.1
2.0
```

O PromptPackage deverá registrar exatamente:

- template utilizado;
- versão utilizada;
- módulo solicitante;
- timestamp;
- fingerprint.

Não sobrescrever silenciosamente templates existentes.

---

# 11. FINGERPRINT

Cada PromptPackage deverá possuir um fingerprint determinístico.

O fingerprint poderá ser gerado com hash dos seguintes dados normalizados:

- module
- template_id
- template_version
- messages
- response_format

Não incluir no fingerprint dados voláteis como:

- created_at
- request_id aleatório

Objetivo futuro:

- auditoria;
- cache;
- comparação;
- rastreabilidade;
- prevenção de duplicação.

---

# 12. SANITIZAÇÃO

Implementar sanitização básica e segura.

A sanitização deve:

- remover bytes nulos;
- normalizar espaços excessivos quando apropriado;
- normalizar quebras de linha;
- rejeitar tipos incompatíveis;
- limitar entradas absurdamente grandes;
- preservar o significado original;
- não alterar conteúdo silenciosamente de forma agressiva.

Não implementar filtro de conteúdo ou moderação nesta Sprint.

Não tentar detectar prompt injection nesta versão.

Apenas preparar estrutura extensível para isso.

---

# 13. ESTIMATIVA DE TAMANHO

Criar um estimador simples.

O objetivo não é calcular tokens com precisão.

O estimador deverá fornecer:

```text
character_count
word_count
estimated_tokens
message_count
```

A estimativa de tokens poderá utilizar uma regra simples e documentada.

Exemplo conceitual:

```text
estimated_tokens = character_count / 4
```

Não adicionar bibliotecas externas apenas para tokenização nesta Sprint.

---

# 14. EXCEÇÕES PADRONIZADAS

Criar exceções específicas:

```text
PromptEngineError
InvalidPromptRequestError
PromptTemplateNotFoundError
PromptTemplateVersionNotFoundError
DuplicatePromptTemplateError
InvalidPromptMessageError
PromptSizeLimitExceededError
PromptBuildError
```

As exceções devem ser reutilizáveis e claramente documentadas.

---

# 15. CONFIGURAÇÃO

Criar configuração central do Prompt Engine sem duplicar o sistema de configuração existente.

Configurações mínimas:

```text
default_language
max_input_characters
max_context_characters
max_total_characters
default_template_version
estimated_characters_per_token
```

Utilizar valores seguros e documentados.

A configuração não deve depender de OpenAI.

---

# 16. OBSERVABILIDADE

Preparar metadata de observabilidade.

O PromptPackage deverá registrar:

```text
request_id
module
template_id
template_version
estimated_size
fingerprint
created_at
```

Não registrar conteúdo sensível integralmente em logs.

Não criar telemetria externa.

Não adicionar ferramentas de monitoramento nesta Sprint.

---

# 17. INTEGRAÇÃO COM MODULES

Criar uma demonstração mínima ou teste de integração utilizando um módulo placeholder.

Exemplo:

```text
modules/trading
  ↓
cria PromptRequest genérico
  ↓
Prompt Engine
  ↓
PromptPackage
```

Importante:

- não implementar análise de trading;
- não criar prompt de CALL ou PUT;
- não acessar provider;
- não alterar comportamento funcional atual;
- utilizar somente para provar a direção arquitetural.

---

# 18. COMPATIBILIDADE

A implementação deve preservar:

- aplicação atual;
- rotas atuais;
- frontend atual;
- testes atuais;
- Vision existente;
- contratos já utilizados;
- comportamento do sistema;
- build atual.

Não migrar toda a aplicação antiga nesta Sprint.

A adoção do Prompt Engine deverá ser gradual.

---

# 19. TESTES OBRIGATÓRIOS

Criar testes para:

## PromptRequest

- criação válida;
- módulo ausente;
- template ausente;
- language padrão;
- metadata;
- contexto inválido.

## PromptMessage

- roles válidas;
- role inválida;
- conteúdo vazio quando proibido;
- metadata.

## Registry

- registrar template;
- buscar template;
- buscar versão;
- duplicidade;
- template inexistente;
- versão inexistente;
- listagem.

## Prompt Engine

- construir PromptPackage;
- template correto;
- versão correta;
- sanitização;
- metadata;
- fingerprint;
- fingerprint determinístico;
- request ID;
- timestamp;
- estimativa de tamanho;
- limite excedido;
- falha de template.

## Templates

- core.system;
- core.generic_analysis;
- core.structured_response.

## Arquitetura

- módulos não importam providers diretamente;
- Prompt Engine não realiza chamada de rede;
- Prompt Engine não depende de OpenAI;
- nenhum template chama provider.

---

# 20. DOCUMENTAÇÃO

Criar:

```text
docs/JARVIS_PROMPT_ENGINE.md
```

Conteúdo mínimo:

- objetivo;
- arquitetura;
- responsabilidades;
- contratos;
- fluxo;
- exemplos;
- templates;
- versionamento;
- fingerprint;
- sanitização;
- estimativa;
- erros;
- regras de integração;
- limitações da V1;
- roadmap.

Atualizar:

```text
docs/FRIDAY_ARCHITECTURE.md
```

Adicionar o Prompt Engine como primeira engine funcional do J.A.R.V.I.S Core.

Atualizar o README apenas quando necessário e sem transformar o documento em relatório de Sprint.

---

# 21. EXEMPLO ESPERADO

Exemplo conceitual:

```python
request = PromptRequest(
    module="trading",
    template_id="core.generic_analysis",
    template_version="1.0",
    user_input="Analise os dados fornecidos.",
    context={
        "source": "example"
    },
    language="pt-BR",
)

package = prompt_engine.build(request)
```

Resultado conceitual:

```text
PromptPackage
├── request_id
├── module: trading
├── template_id: core.generic_analysis
├── template_version: 1.0
├── messages
│   ├── system
│   └── user
├── metadata
├── estimated_size
├── fingerprint
└── created_at
```

Nenhum provider deverá ser chamado.

---

# 22. CRITÉRIOS DE ACEITAÇÃO

A Sprint será considerada concluída quando:

- Prompt Engine estiver implementado;
- contratos estiverem definidos;
- registry estiver funcional;
- templates iniciais estiverem registrados;
- versionamento estiver funcional;
- fingerprint determinístico estiver funcional;
- sanitização estiver funcional;
- estimativa de tamanho estiver funcional;
- exceções estiverem padronizadas;
- documentação estiver criada;
- arquitetura estiver atualizada;
- testes novos estiverem passando;
- suíte completa estiver passando;
- build do frontend estiver passando;
- nenhuma API externa tiver sido conectada;
- nenhuma funcionalidade de negócio tiver sido adicionada;
- nenhum módulo acessar provider diretamente.

---

# 23. FORA DO ESCOPO

Não realizar:

- integração OpenAI;
- criação de chave de API;
- configuração de billing;
- login no ChatGPT;
- automação de navegador;
- cookies;
- CDP;
- Pocket Option;
- Polarium;
- análise automática de gráficos;
- memória persistente;
- banco de dados;
- RAG;
- embeddings;
- frontend novo;
- chat;
- streaming;
- ferramentas;
- agentes;
- aprendizado automático.

---

# 24. RELATÓRIO FINAL OBRIGATÓRIO

Ao terminar, entregar:

1. resumo da implementação;
2. estrutura criada;
3. arquivos criados;
4. arquivos modificados;
5. contratos implementados;
6. templates implementados;
7. testes adicionados;
8. resultado dos testes específicos;
9. resultado da suíte completa;
10. resultado do build;
11. problemas encontrados;
12. decisões arquiteturais;
13. limitações atuais;
14. recomendações para a Sprint seguinte;
15. confirmação de que nenhuma API externa foi chamada;
16. confirmação de que nenhum módulo acessa providers diretamente.

Não executar:

- git add;
- git commit;
- git push;
- reset;
- checkout;
- limpeza do worktree.