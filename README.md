# J.A.R.V.I.S AI TRADER

Sistema proprietário de apoio à decisão em Trading desenvolvido para Renan Godoy.

> Primeiro proteger a banca. Depois crescer a banca.
> Não buscamos mais operações. Buscamos operações melhores.

## Sprint 1 — Arquitetura do Sistema

Esta Sprint cria a fundação técnica do projeto:

- Backend em FastAPI
- Arquitetura modular
- Separação por responsabilidades
- Health check da API
- Configuração centralizada
- Estrutura preparada para Market Reader, AI Decision Engine, Risk Manager, Journal, Estatísticas, Backtesting e Machine Learning
- Teste inicial automatizado

## Tecnologias desta Sprint

- Python
- FastAPI
- Uvicorn
- Pydantic Settings
- Pytest

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
