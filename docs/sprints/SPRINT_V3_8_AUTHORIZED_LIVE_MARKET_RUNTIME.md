# FRIDAY TRADE V3.8

# AUTHORIZED LIVE MARKET RUNTIME

Status

PLANNED

---

# Objetivo

Criar o primeiro runtime somente leitura capaz de receber mensagens reais de mercado provenientes de uma sessão autorizada da Polarium e encaminhá-las para a arquitetura interna do Friday Trade.

Fluxo desejado:

```text
Sessão Polarium autorizada
→ WebSocket existente
→ filtro de eventos de mercado
→ sanitização
→ MarketPipeline compartilhado
→ CandleStore compartilhado
→ Chart API
→ RealCandleChart
```

Esta Sprint não envia ordens.

Esta Sprint não automatiza entradas.

Esta Sprint não executa CALL ou PUT.

Esta Sprint não altera saldos, posições ou ordens.

---

# Regra principal

O runtime real deve ser exclusivamente:

```text
READ ONLY
```

Somente eventos de mercado podem entrar no pipeline.

Eventos de autenticação, saldo, portfólio, ordens e dados privados não devem ser encaminhados ao MarketPipeline.

---

# Antes de começar

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

pwd
git rev-parse --show-toplevel
git branch --show-current
git status --short
.venv/bin/python --version

.venv/bin/python -m pytest -q

cd frontend
npm run build
```

O arquivo Markdown da Sprint atual pode estar não rastreado e, sozinho, não bloqueia a execução.

Qualquer outra alteração pendente deve bloquear a Sprint.

---

# Evidências permitidas

Usar somente os eventos reais já confirmados e documentados:

```text
first-candles
candle-generated
candles-generated
timeSync
subscribeMessage
unsubscribeMessage
```

Para a primeira integração runtime, priorizar:

```text
candle-generated
first-candles
```

Não assumir contratos não comprovados.

---

# Eventos proibidos no MarketPipeline

Não encaminhar:

```text
authenticate
authenticated
marginal-balance
balances
subscription-balance-changed
portfolio
orders
positions
execution
```

Esses eventos devem ser ignorados ou classificados fora do pipeline de mercado.

---

# Arquitetura

Criar uma fronteira semelhante a:

```text
app/market/live/
    __init__.py
    runtime.py
    event_filter.py
    models.py
    status.py
```

Responsabilidades:

## event_filter.py

Receber mensagens já decodificadas.

Permitir somente eventos de mercado autorizados.

Rejeitar qualquer mensagem com campos sensíveis.

Não registrar payload bruto.

## runtime.py

Receber mensagens da camada de Connector já existente.

Encaminhar somente mensagens permitidas ao:

```text
market_pipeline
```

Não abrir uma segunda conexão WebSocket desnecessária.

Reutilizar a sessão e a infraestrutura autorizada existente quando possível.

## status.py

Expor estado interno sanitizado:

```text
running
connected
last_event_name
last_event_at
processed_count
rejected_count
last_error
active_ids_seen
raw_sizes_seen
```

Nunca expor tokens, cookies, SSID ou headers.

---

# Integração com Connector

Antes de alterar qualquer Connector:

1. Mapear onde as mensagens WebSocket reais já entram.
2. Identificar o ponto mais seguro para adicionar um listener somente leitura.
3. Evitar duplicar parser, sessão ou conexão.
4. Não alterar autenticação.
5. Não alterar reconnect existente sem necessidade comprovada.
6. Não alterar fluxo de saldo.
7. Não alterar fluxo de ordens.

A integração deve ser mínima e reversível.

---

# Mapeamentos

Manter:

```text
symbol = None
timeframe = None
mapping_verified = False
```

Enquanto os vínculos visuais não estiverem comprovados.

Preservar:

```text
active_id
raw_size
start_timestamp
end_timestamp
open
close
low_candidate
high_candidate
volume
```

---

# Fonte e transparência

O frontend e a API devem distinguir claramente:

```text
SIMULATED
CONTROLLED
POLARIUM AUTHORIZED LIVE
DISCONNECTED
```

Nunca mostrar “ao vivo” enquanto o runtime real não estiver conectado e recebendo eventos.

---

# Endpoints internos

Criar somente endpoints de controle e status se realmente necessários.

Sugestão:

```text
POST /api/v1/market/live/start
POST /api/v1/market/live/stop
GET  /api/v1/market/live/status
```

Requisitos:

- não aceitar credenciais no body;
- não aceitar cookies;
- não aceitar bearer;
- não aceitar HAR;
- utilizar apenas sessão autorizada previamente estabelecida;
- retornar erro claro se não houver sessão válida;
- nunca iniciar execução de ordem.

Não expor endpoint em produção sem proteção explícita e revisão de segurança.

---

# Gráfico

Não alterar `RealCandleChart` além do estritamente necessário.

O gráfico deve continuar lendo:

```text
GET /api/v1/market/chart
```

Quando o runtime real alimentar o Store, o polling já existente deverá atualizar:

- candle aberto;
- novo candle;
- contador;
- escala.

---

# Testes obrigatórios

Criar testes para:

- aceitar `candle-generated`;
- aceitar `first-candles`;
- rejeitar evento de saldo;
- rejeitar evento de portfólio;
- rejeitar evento de ordem;
- rejeitar Authorization;
- rejeitar cookie;
- rejeitar token;
- ausência de sessão autorizada;
- start idempotente;
- stop idempotente;
- mensagem real sanitizada chegando ao MarketPipeline;
- CandleStore sendo atualizado;
- Chart API refletindo o candle;
- status sanitizado;
- erro do Connector sem derrubar aplicação;
- nenhum dado privado em logs ou respostas.

---

# Segurança

Nunca persistir:

```text
token
access_token
refresh_token
authorization
bearer
cookie
ssid
password
email
client_secret
code_verifier
headers privados
```

Não imprimir mensagens completas recebidas da sessão.

Logs permitidos:

```text
event_name
active_id
raw_size
timestamp
processing_status
```

---

# Fora do escopo

Não criar:

- AutoTrade;
- Execution;
- CALL;
- PUT;
- ordens;
- cliques automáticos;
- IA;
- Probability Engine;
- indicadores novos;
- mapeamento inventado de símbolo;
- mapeamento inventado de timeframe;
- scraping visual;
- iframe da Polarium.

---

# Critérios de aprovação

- Runtime somente leitura.
- Sessão autorizada reutilizada.
- Nenhuma credencial recebida por endpoint.
- Somente eventos de mercado chegam ao pipeline.
- CandleStore recebe candles reais.
- Chart API expõe candles reais.
- Gráfico atualiza sem F5.
- Fonte marcada como `POLARIUM AUTHORIZED LIVE`.
- Simulador permanece separado.
- Connector não envia ordens.
- Suíte completa passando.
- Build passando.

---

# Validação visual obrigatória

Após a implementação:

1. Abrir uma sessão autorizada da Polarium.
2. Selecionar manualmente um ativo.
3. Selecionar manualmente o timeframe.
4. Iniciar o runtime somente leitura.
5. Abrir `/market-chart`.
6. Confirmar que o candle atual muda automaticamente.
7. Confirmar que novos candles surgem.
8. Confirmar que o contador aumenta.
9. Confirmar que o simulador está parado.
10. Confirmar que a origem aparece como:

```text
POLARIUM AUTHORIZED LIVE
```

Enviar prints de:

- Polarium com ativo/timeframe visíveis;
- Friday Trade;
- status do runtime;
- Chart API;
- Console do navegador;
- terminal backend sem segredos.

---

# Entrega obrigatória

1. Objetivo.
2. Arquitetura implementada.
3. Ponto de integração com o Connector.
4. Arquivos criados.
5. Arquivos modificados.
6. Eventos aceitos.
7. Eventos rejeitados.
8. Política de sanitização.
9. Endpoints criados.
10. Exemplo de status sanitizado.
11. Integração com MarketPipeline.
12. Integração com CandleStore.
13. Integração com Chart API.
14. Testes criados.
15. Resultado dos testes específicos.
16. Resultado da suíte completa.
17. Resultado do build.
18. Como testar.
19. Verificação visual necessária.
20. Riscos conhecidos.
21. Débitos técnicos.
22. `git status --short`.
23. `git diff --stat`.
24. Sugestão de commit.

Mensagem sugerida:

```text
feat(market): add authorized read-only live market runtime
```

---

# Regra final

Não fazer commit.

Não fazer push.

Se a integração exigir credenciais no código, copiar sessão privada ou reconstruir autenticação, interromper e relatar.

Se não for possível reutilizar a sessão autorizada existente com segurança, não criar conexão alternativa por hipótese.