# Sprint 14 — Chart Workspace Pro

## Objetivo

Transformar o dashboard em uma mesa operacional mais próxima de um terminal de trading profissional, priorizando o gráfico Candlestick como área principal do sistema.

## Entregas

- Layout principal reorganizado em três colunas:
  - Scanner Top 12 à esquerda.
  - Gráfico Candlestick Pro no centro.
  - IA, Risk Manager e Execution à direita.
- Clique no ativo do Scanner sincroniza:
  - gráfico;
  - leitura do workspace;
  - painel de IA.
- Gráfico com mais altura e área útil.
- Painéis laterais compactados.
- Regra mantida: gráfico de preço sempre em Candlestick.

## Como testar

Backend:

```bash
cd ~/Desktop/jarvis-ai-trader
source .venv/bin/activate
python -m pytest
python -m uvicorn app.main:app --reload
```

Frontend:

```bash
cd ~/Desktop/jarvis-ai-trader/frontend
npm install
npm run dev
```

Abrir:

```text
http://localhost:5173
```

## Critérios de validação

- O dashboard abre sem erro.
- O gráfico ocupa a área principal da tela.
- O Scanner Top 12 aparece em formato compacto.
- Ao clicar em outro ativo, o gráfico muda para o ativo selecionado.
- IA e dados do workspace acompanham o ativo selecionado.
- `python -m pytest` retorna todos os testes passando.

## Commit sugerido

```bash
git add .
git commit -m "feat(sprint-14): chart workspace pro layout"
git push origin main
```
