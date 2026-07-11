# FRIDAY TRADE V3.2

# MARKET PIPELINE FOUNDATION

Status

PLANNED

---

# Objetivo

Criar o primeiro Pipeline interno do Friday Trade.

O Pipeline será responsável por receber uma mensagem WebSocket já sanitizada, enviá-la ao Market Event Engine, normalizar os candles e armazená-los automaticamente no Candle Store.

Esta Sprint NÃO abre WebSocket.

Esta Sprint NÃO altera o Connector.

Esta Sprint NÃO altera APIs.

Esta Sprint NÃO altera frontend.

Esta Sprint NÃO cria indicadores.

Esta Sprint NÃO cria IA.

Esta Sprint NÃO cria sinais.

Esta Sprint NÃO cria execução.

---

# Arquitetura

Criar:

app/market/pipeline/

    __init__.py

    pipeline.py

    models.py

    processor.py

O pipeline deverá utilizar exclusivamente:

app/market/events/

app/market/store/

Não duplicar lógica.

---

# Fluxo

Mensagem sanitizada

↓

Router

↓

Parser

↓

Normalized Candle

↓

Candle Store

↓

Resultado

---

# Processor

Criar um Processor responsável por:

receber dict

↓

chamar router

↓

executar parser

↓

armazenar candle(s)

↓

retornar relatório

---

# Resultado

Criar um contrato semelhante a:

PipelineResult

com:

success

processed

ignored

updated

unsupported

errors

stored

---

# Eventos suportados

Implementar:

- candle-generated

- first-candles

Eventos desconhecidos:

não derrubar pipeline

retornar unsupported

---

# Integração

O Pipeline deve utilizar o Candle Store criado na Sprint V3.1.

Nenhuma estrutura duplicada.

---

# Não fazer

Não abrir WebSocket.

Não criar runtime.

Não criar Connector.

Não criar endpoint.

Não criar frontend.

Não criar EMA.

Não criar RSI.

Não criar MACD.

Não criar IA.

Não criar Probability Engine.

---

# Testes obrigatórios

Adicionar testes para:

- candle-generated válido

- first-candles válido

- coleção parcialmente inválida

- evento desconhecido

- evento sem name

- candle duplicado

- candle atualizado

- múltiplos candles

- pipeline vazio

- store atualizado corretamente

---

# Segurança

Nunca utilizar HAR bruto.

Utilizar apenas fixtures sanitizadas.

Nunca imprimir:

Authorization

cookie

token

bearer

SSID

credenciais

---

# Critérios

Pipeline totalmente passivo.

Sem runtime.

Sem frontend.

Sem APIs.

Sem Connector.

100% testável.

---

# Como testar

Backend:

.venv/bin/python -m pytest -q

Testes específicos:

.venv/bin/python -m pytest -q tests/market

Frontend:

cd frontend

npm run build

---

# Entrega

1. Objetivo

2. Arquitetura

3. Arquivos criados

4. Arquivos modificados

5. Fluxo implementado

6. Processor

7. PipelineResult

8. Integração com Candle Store

9. Testes criados

10. Resultado dos testes

11. Resultado do build

12. Como testar

13. Riscos

14. Débitos técnicos

15. git status --short

16. git diff --stat

17. Sugestão de commit

Mensagem sugerida:

feat(market): introduce passive market pipeline

---

Não fazer commit.

Não fazer push.