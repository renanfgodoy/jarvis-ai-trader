# J.A.R.V.I.S Module SDK

## Objetivo

O Module SDK padroniza como módulos da Friday AI Platform conversam com o Core.
Ele fornece contratos, validação, manifesto, loader, registry e um `BaseModule`.

O SDK não implementa regras de negócio, não monta prompts, não resolve identidade e
não executa providers diretamente. Ele apenas encapsula uma chamada ao
`CoreOrchestrator`.

## Arquitetura

```text
Module
  -> Module SDK
  -> CoreOrchestrator
  -> IdentityEngine
  -> PromptEngine
  -> ProviderEngine
  -> ExecutionResponse
  -> ModuleResponse
```

## Fluxo

1. O módulo recebe um `ModuleRequest`.
2. O SDK valida o request.
3. O SDK cria um `ExecutionRequest` público do Orchestrator.
4. O `CoreOrchestrator` executa o pipeline oficial.
5. O SDK encapsula o resultado em `ModuleResponse`.

## Manifest

Todo módulo possui um `ModuleManifest` com:

- name;
- display_name;
- description;
- version;
- identity;
- provider;
- language;
- permissions;
- core_version;
- enabled.

V1.0 permite apenas `provider="mock"` para impedir uso acidental de provider real.

## Registry

`ModuleRegistry` registra, lista, busca, remove e define módulo padrão sem singleton
oculto.

## Loader

`ModuleLoader` carrega módulos por builders explícitos, valida manifesto e metadata,
e opcionalmente registra ou inicializa o módulo.

## Contracts

- `BaseModule`
- `ModuleManifest`
- `ModuleRequest`
- `ModuleResponse`
- `ModuleMetadata`
- `ModuleConfig`
- `ModuleValidator`
- `ModuleRegistry`
- `ModuleLoader`

## Roadmap

1. Migrar módulos de produto para contratos explícitos.
2. Adicionar catálogo de módulos com permissões por domínio.
3. Integrar auditoria do Core em sprint dedicada.
4. Permitir providers reais somente por configuração segura do Provider Engine.
