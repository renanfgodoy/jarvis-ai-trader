# Changelog

Todas as mudancas relevantes do J.A.R.V.I.S AI Trader devem ser documentadas neste arquivo.

## Sprint 8 - Market Data Engine

- Criada a camada `frontend/src/market-data/` como fonte compartilhada de contexto de mercado.
- Criada a pagina `/markets/data` para resumo, snapshot, contexto, fonte, disponibilidade e timeline.
- Criados contratos internos passivos em `app/market/data/`, sem endpoints novos e sem alterar comportamento do backend.
- Operation passou a consumir o mesmo contexto de ativo/timeframe usado pelas areas de mercado.

## Sprint 2 - Architecture Documentation

- Criada a documentacao oficial de arquitetura em `docs/ARCHITECTURE.md`.
- Criada a ADR 0001 definindo isolamento completo do Connector.
- Criado o roadmap oficial das proximas sprints.
- README atualizado com links para arquitetura, roadmap e changelog.

## Sprint 1 - Repository Hygiene

- Politica de higiene do repositorio documentada.
- Dependencias geradas e artefatos locais definidos como fora do Git.
