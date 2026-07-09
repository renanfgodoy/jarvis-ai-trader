# Sprint 10 — Quadcode / Polarium DEMO Adapter

## Objetivo

Criar uma base segura para futura integração com a Polarium via arquitetura Quadcode, sempre respeitando a regra oficial do projeto:

> Desenvolvimento somente em conta DEMO/DRY_RUN. Nenhuma ordem real será enviada.

## O que foi implementado

- Modelos Pydantic para contratos Quadcode/Polarium.
- Provider `QuadcodePolariumProvider` em modo seguro.
- Catálogo inicial de ativos OTC para discovery.
- Endpoints de status, conexão demo, desconexão, símbolos e ordem dry-run.
- Testes automatizados garantindo que ordens reais estejam bloqueadas.

## Endpoints

### GET `/api/v1/quadcode/status`

Retorna o estado seguro do adapter.

### POST `/api/v1/quadcode/demo/connect`

Prepara o adapter em modo DEMO/DRY_RUN.

### POST `/api/v1/quadcode/demo/disconnect`

Desconecta o adapter do modo demo.

### GET `/api/v1/quadcode/symbols`

Lista o universo inicial de ativos OTC.

### POST `/api/v1/quadcode/demo/order`

Recebe uma ordem em DRY_RUN e confirma que nada foi executado.

## Como testar

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Abrir:

```text
http://127.0.0.1:8000/docs
```

Executar os testes:

```bash
python -m pytest
```

Resultado esperado:

```text
43 passed
```

## Critérios de validação

- Swagger mostra a seção `Quadcode / Polarium Demo`.
- `/quadcode/status` retorna `canTrade=false`.
- `/quadcode/demo/order` retorna `executed=false`.
- Todos os testes passam.

## Segurança

Esta Sprint não faz scraping, não captura credenciais e não envia ordens. Ela prepara somente a camada de contrato e segurança para uma futura integração autorizada em conta DEMO.
