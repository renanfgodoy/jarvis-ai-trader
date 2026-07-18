# Friday AI Platform — V0.24.0

Plataforma modular de inteligência artificial, composta por backend FastAPI e frontend React/Vite.

## Estado atual

- Arquitetura Vision-First e Core modular em evolução.
- Trading permanece como módulo legado/experimental, não como centro da plataforma.
- Integrações de corretoras e provedores antigos permanecem desativadas no runtime principal.
- Execução financeira real não está habilitada.

## Estrutura

```text
app/         Backend FastAPI
core/        J.A.R.V.I.S Core e engines arquiteturais
modules/     Módulos de produto desacoplados de providers
shared/      Contratos e interfaces compartilhadas
frontend/    Dashboard React + TypeScript + Vite
tests/       Testes automatizados
docs/        Histórico técnico das Sprints
tools/       Ferramentas auxiliares de diagnóstico
```

## Documentacao tecnica

- Arquitetura oficial: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Arquitetura Friday AI Platform: [docs/FRIDAY_ARCHITECTURE.md](docs/FRIDAY_ARCHITECTURE.md)
- ADRs: [docs/adr/](docs/adr/)
- Roadmap: [ROADMAP.md](ROADMAP.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md)

## Preparação

Crie o ambiente local sem copiar segredos para o Git:

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Frontend:

```bash
cd frontend
npm install
```

Dependências geradas não são versionadas. Se `frontend/node_modules/` não
existir, reconstrua com `npm install` ou `npm ci` dentro de `frontend/`.

## Executar

Backend:

```bash
cd ~/Desktop/jarvis-ai-trader
source .venv/bin/activate
python -m uvicorn app.main:app --reload
```

Frontend, em outro terminal:

```bash
cd ~/Desktop/jarvis-ai-trader/frontend
npm run dev
```

Dashboard: `http://localhost:5173`

## Testes

```bash
cd ~/Desktop/jarvis-ai-trader
source .venv/bin/activate
python -m pytest -q
```

```bash
cd ~/Desktop/jarvis-ai-trader/frontend
npm run build
```

## Segurança

- Nunca commitar `.env`, tokens, senhas, cookies, SSID ou arquivos HAR.
- Use somente credenciais próprias e integrações autorizadas.
- AutoTrade deve permanecer bloqueado enquanto conta DEMO, saldo, moeda, risco e sessão não estiverem validados.

## Higiene do repositório

- `frontend/node_modules/`, `frontend/dist/`, caches do Vite/Pytest/Python e artefatos de build não pertencem ao Git.
- Arquivos locais como `.DS_Store`, `__pycache__/`, `.pyc`, `.log`, `.env` e `.jarvis_cache/` devem permanecer ignorados.
- Arquivos HAR e qualquer conteúdo com tokens, cookies, bearer, authorization, refresh token, SSID ou credenciais nunca devem ser versionados.
