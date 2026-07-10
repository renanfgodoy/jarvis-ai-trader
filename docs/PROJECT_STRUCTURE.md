# Estrutura oficial do projeto

## Backend
- `app/api/routes/`: endpoints HTTP.
- `app/core/`: configurações globais.
- `app/models/`: modelos de entrada e saída.
- `app/services/`: regras de negócio e integrações.
- `app/providers/`: provedores de mercado.
- `app/execution/`: execução em ambiente de demonstração.

## Frontend
- `frontend/src/components/`: componentes reutilizáveis.
- `frontend/src/pages/`: páginas e workspace principal.
- `frontend/src/services/`: cliente HTTP.
- `frontend/src/types/`: contratos TypeScript.

## Diagnóstico Polarium
Os módulos `polarium_diagnostics`, `polarium_session_inspector` e `polarium_ws_recorder` são ferramentas de laboratório. Eles não devem armazenar credenciais em código ou no Git.
