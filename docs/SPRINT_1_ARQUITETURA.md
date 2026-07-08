# Sprint 1 — Arquitetura do Sistema

## Objetivo

Criar a fundação técnica do J.A.R.V.I.S AI TRADER com backend FastAPI, estrutura modular e base preparada para evolução em Sprints.

## Entrega

A Sprint 1 entrega:

- Estrutura inicial do projeto
- API FastAPI funcional
- Rota raiz
- Rota de health check
- Rota de visão arquitetural
- Configuração centralizada
- Módulos base separados
- Teste automatizado inicial
- Documentação inicial

## Arquitetura Inicial

Fluxo oficial:

Dashboard → API → AI Decision Engine → Market Reader → Banco de Dados → Machine Learning → Backtesting

## Módulos criados

- Market Reader
- AI Decision Engine
- Risk Manager
- Trade Journal
- Statistics Engine
- Backtesting
- Machine Learning Engine

## Arquivos criados

- README.md
- requirements.txt
- .gitignore
- .env.example
- app/main.py
- app/core/config.py
- app/core/constants.py
- app/api/router.py
- app/api/routes/health.py
- app/api/routes/system.py
- app/modules/*/service.py
- tests/test_health.py
- docs/SPRINT_1_ARQUITETURA.md

## Como testar

1. Criar ambiente virtual:

```bash
python -m venv .venv
```

2. Ativar ambiente no macOS:

```bash
source .venv/bin/activate
```

3. Instalar dependências:

```bash
pip install -r requirements.txt
```

4. Rodar API:

```bash
uvicorn app.main:app --reload
```

5. Abrir no navegador:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/v1/health
http://127.0.0.1:8000/api/v1/system/architecture
```

6. Rodar testes:

```bash
pytest
```

## Critérios de validação

A Sprint 1 está validada quando:

- A API sobe sem erro.
- `/` retorna mensagem de sistema online.
- `/docs` abre a documentação automática do FastAPI.
- `/api/v1/health` retorna status online.
- `/api/v1/system/architecture` retorna fluxo e módulos.
- `pytest` passa sem falhas.

## Commit recomendado

Depois de testar tudo, fazer commit com:

```bash
git add .
git commit -m "feat: create sprint 1 base architecture"
```

## Push recomendado

Depois do commit local estar correto:

```bash
git push origin main
```
