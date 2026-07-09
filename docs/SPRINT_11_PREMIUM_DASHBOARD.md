# Sprint 11 — Premium Dashboard V1

## Objetivo

Criar o primeiro frontend profissional do J.A.R.V.I.S AI TRADER, saindo do uso operacional exclusivo do Swagger e iniciando um dashboard premium para monitorar scanner, IA, risco, providers e execução demo.

## Entregas

- Frontend React + TypeScript + Vite.
- TailwindCSS configurado.
- Consumo da API FastAPI com Axios e React Query.
- Dashboard com tema escuro premium.
- Sidebar institucional.
- Header com status de API, IA, provider e execução.
- Cards de métricas.
- Top 12 ativos via Asset Scanner.
- Painel da IA via Signal Engine.
- Card do Risk Manager.
- Card do Execution Engine em modo DEMO/DRY_RUN.
- Gráfico placeholder com Recharts.
- Timeline operacional do J.A.R.V.I.S.
- CORS configurado no backend para o frontend local.

## Como rodar o backend

```bash
cd ~/Desktop/jarvis-ai-trader
source .venv/bin/activate
python -m uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000/docs
```

## Como rodar o frontend

Em outro terminal:

```bash
cd ~/Desktop/jarvis-ai-trader/frontend
npm install
npm run dev
```

Frontend:

```text
http://127.0.0.1:5173
```

## Como testar backend

```bash
cd ~/Desktop/jarvis-ai-trader
source .venv/bin/activate
python -m pytest
```

Resultado esperado nesta Sprint:

```text
43 passed
```

## Critérios de validação

- Backend inicia sem erro.
- Swagger continua funcionando.
- Testes backend continuam passando.
- Frontend abre em `http://127.0.0.1:5173`.
- Dashboard mostra cards principais.
- Dashboard consome pelo menos os endpoints de health, providers, scanner, signal, risk e execution.
- Interface permanece em modo seguro DEMO/DRY_RUN.

## Observação

Esta Sprint ainda não executa ordens reais. A interface mostra o estado dos módulos e prepara o terreno para as próximas telas operacionais.
