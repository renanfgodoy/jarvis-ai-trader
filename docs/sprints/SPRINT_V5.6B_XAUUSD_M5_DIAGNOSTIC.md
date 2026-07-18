# FRIDAY AI TRADER

# SPRINT V5.6B — ASSET BOOTSTRAP AUDIT

## Status

PLANEJADA

---

# 1. Objetivo

Investigar por que alguns ativos carregam corretamente o bootstrap histórico M5 enquanto outros permanecem em `0/50`, preservando integralmente a arquitetura já implementada nas Sprints V5.6A e V5.7.

Esta Sprint é exclusivamente de auditoria baseada em evidências.

Não implementar correções especulativas.

---

# 2. Evidência atual

Validação real confirmou:

EURUSD

- Bootstrap M5 funcionando.

XAUUSD

- Bootstrap M5 permanece em 0/50.

Isso comprova que:

- raw_size=300 funciona.
- parser histórico funciona para alguns ativos.
- correlação funciona para alguns ativos.

A divergência ocorre somente para determinados instrumentos.

---

# 3. Objetivo técnico

Auditar completamente o fluxo:

Session Context

↓

BootstrapRequestFactory

↓

Pending Requests

↓

sendMessage

↓

get-first-candles

↓

Resposta

↓

Parser

↓

Correlação

↓

Validação temporal

↓

CandleStore

↓

History Count

↓

Readiness

para descobrir exatamente em qual etapa ocorre a divergência entre ativos.

---

# 4. Escopo permitido

Adicionar somente instrumentação.

Registrar automaticamente:

- request_id
- active_id
- symbol
- display_name
- market_type
- raw_size solicitado
- raw_size resolvido
- envio do request
- resposta recebida
- formato da resposta
- quantidade de candles encontrados
- quantidade aceita
- quantidade rejeitada
- motivo da rejeição
- history_count antes/depois
- readiness antes/depois
- timeout
- request expirado
- etapa exata da falha

---

# 5. Fora de escopo

Não alterar:

- parser histórico
- CandleStore
- HistoricalBootstrapManager
- BootstrapRequestFactory
- Readiness
- Runtime Guard
- Strategy Engine
- Scanner
- Ranking
- IA
- CALL
- PUT
- Backtest
- Layout
- OAuth
- Browser Bridge
- CDP
- Seleção de ativo

---

# 6. Diagnóstico automático

Criar um componente dedicado, por exemplo:

HistoricalBootstrapDiagnostic

Esse componente apenas observa o pipeline existente.

Não criar um segundo bootstrap.

---

# 7. Relatório automático

Gerar automaticamente um arquivo:

.jarvis_cache/diagnostics/bootstrap_report.json

e também:

.jarvis_cache/diagnostics/bootstrap_report.txt

O relatório deverá conter uma comparação direta entre todos os ativos analisados.

Exemplo:

EURUSD

request enviado
resposta recebida
candles aceitos
history_count
readiness

XAUUSD

request enviado
resposta recebida
candles aceitos
history_count
readiness

Diferença detectada:

...

---

# 8. Classificação das falhas

O relatório deverá identificar uma categoria única para cada bootstrap.

Valores aceitos:

REQUEST_NOT_SENT

NO_RESPONSE

WRONG_ACTIVE_ID

RAW_SIZE_NOT_RESOLVED

UNSUPPORTED_PAYLOAD

NO_CANDLES_FOUND

TIMESTAMP_REJECTED

STORE_KEY_MISMATCH

HISTORY_NOT_INCREMENTED

READINESS_NOT_UPDATED

REALTIME_ONLY

UNKNOWN

---

# 9. Segurança

Nunca registrar:

- cookies
- tokens
- credenciais
- payloads OAuth
- headers

---

# 10. Testes

Adicionar testes cobrindo:

- request auditado
- resposta auditada
- request_id preservado
- relatório gerado
- relatório sem dados sensíveis
- categoria correta
- realtime não contado como histórico
- regressão M1 inexistente
- regressão M5 inexistente
- regressão M15 inexistente

---

# 11. Validação automatizada

Executar:

python -m pytest tests/market/providers -v

Depois:

python -m pytest -v

Executar:

npm run build

---

# 12. Validação real

Subir frontend.

Subir backend com:

POLARIUM_CDP_LIVE_ENABLED=true

Abrir ativos diferentes em M5.

Ao finalizar, executar:

cat .jarvis_cache/diagnostics/bootstrap_report.txt

O relatório deverá identificar automaticamente a etapa onde cada ativo falhou.

---

# 13. Critério de conclusão

Esta Sprint não corrige o problema.

Ela apenas produz evidências suficientes para comprovar a causa raiz.

Nenhuma correção deverá ser implementada sem essa comprovação.

---

# 14. Entrega obrigatória

Objetivo

Arquitetura auditada

Arquivos criados

Arquivos modificados

Instrumentação adicionada

Testes adicionados

Resultado dos testes

Resultado da suíte completa

Resultado do build

Exemplo do relatório

git status

git diff

Riscos

Próximos passos

Sugestão de commit

---

# 15. Git

Não executar:

git add

git commit

git push

sem autorização explícita do Renan.

---

# 16. Sugestão de commit

chore(polarium): add bootstrap diagnostic audit