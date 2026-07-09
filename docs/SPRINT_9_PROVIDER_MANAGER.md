# Sprint 9 — Multi Provider Engine

## Objetivo

A Sprint 9 cria a arquitetura do **Provider Manager**, responsável por centralizar qual fonte de dados está ativa no sistema.

Antes desta Sprint, o sistema usava diretamente o provider simulado em vários pontos. Agora, módulos como Market Reader, Signal Engine e Asset Scanner passam a depender de uma camada intermediária.

## Arquitetura

```text
Market Reader
      ↓
Provider Manager
      ↓
Active Provider
      ↓
Simulated / TradingView / Quadcode
```

## Providers registrados

### Simulated

Provider ativo nesta Sprint. Retorna múltiplos símbolos simulados e candles determinísticos para desenvolvimento seguro.

### TradingView

Provider estrutural. Criado para integração futura com dados autorizados ou alertas normalizados.

### Quadcode / Polarium

Provider estrutural em modo seguro. Nenhuma conexão real, autenticação real ou ordem real é executada nesta Sprint.

Regra oficial:

> Durante o desenvolvimento, qualquer integração operacional deve usar apenas ambiente DEMO.

## Arquivos criados

```text
app/providers/manager.py
app/providers/tradingview.py
app/providers/quadcode.py
tests/test_provider_manager.py
docs/SPRINT_9_PROVIDER_MANAGER.md
```

## Arquivos alterados

```text
app/providers/base.py
app/providers/simulated.py
app/models/provider.py
app/services/provider_engine.py
app/services/market_reader.py
app/services/asset_scanner.py
app/api/routes/providers.py
app/api/router.py
app/core/config.py
README.md
```

## Endpoints

```text
GET /api/v1/providers/current
GET /api/v1/providers/list
```

## Como testar

### 1. Ativar ambiente

```bash
cd ~/Desktop/jarvis-ai-trader
source .venv/bin/activate
```

### 2. Instalar dependências

```bash
python -m pip install -r requirements.txt
```

### 3. Rodar API

```bash
python -m uvicorn app.main:app --reload
```

### 4. Abrir Swagger

```text
http://127.0.0.1:8000/docs
```

### 5. Testar endpoints

```text
GET /api/v1/providers/current
GET /api/v1/providers/list
GET /api/v1/scanner/top-assets
```

### 6. Rodar testes

```bash
python -m pytest
```

Resultado esperado:

```text
37 passed
```

## Critérios de validação

- Swagger exibe seção Provider Manager.
- `/providers/current` retorna provider `simulated` ativo.
- `/providers/list` retorna `simulated`, `tradingview` e `quadcode`.
- Scanner continua retornando Top 12.
- Todos os testes passam.

## Segurança

Esta Sprint não executa ordens, não autentica em corretoras e não acessa conta real. O adapter Quadcode/Polarium é apenas estrutural e preparado para futura conta DEMO.
