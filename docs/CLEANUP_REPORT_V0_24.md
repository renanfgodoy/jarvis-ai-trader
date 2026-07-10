# Relatório de limpeza — V0.24.0

## Removido
- Cópias numeradas de arquivos (`arquivo 2`, `arquivo 3`, etc.).
- Duplicatas idênticas em `tests/`, `docs/` e configurações do frontend.
- `.venv`, `node_modules`, caches Python/Vite/Pytest e metadados do macOS.
- `.env`, arquivos HAR e caches locais com potencial conteúdo sensível.
- Metadados `.git` do pacote de distribuição.

## Consolidado
- Um único `README.md`.
- Um único `requirements.txt`.
- Um único conjunto de arquivos `package.json`, TypeScript, Vite, Tailwind e PostCSS.
- Um único `.env.example`, sem senha e sem token.
- Um único teste por módulo.

## Mantido
- Código funcional mais recente do backend e frontend.
- Documentação histórica não duplicada.
- Módulos atuais de diagnóstico Polarium.
