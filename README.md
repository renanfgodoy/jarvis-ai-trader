# J.A.R.V.I.S AI TRADER — V0.24.0

Plataforma experimental de apoio à decisão em trading, composta por backend FastAPI e frontend React/Vite.

## Estado atual

- Dashboard profissional com gráfico candlestick.
- Scanner Top 12 e seleção de timeframe M1, M5 e M15.
- AI Decision Engine, Risk Manager e AutoTrade Gate em modo de laboratório.
- Módulos de diagnóstico da integração Polarium: OAuth/PKCE, Session Inspector e WS Session Recorder.
- Execução financeira real não está habilitada.

## Estrutura

```text
app/         Backend FastAPI
frontend/    Dashboard React + TypeScript + Vite
tests/       Testes automatizados
docs/        Histórico técnico das Sprints
tools/       Ferramentas auxiliares de diagnóstico
```

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
