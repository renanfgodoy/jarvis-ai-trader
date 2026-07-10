# FRIDAY TRADE V2.8
# HAR CANDLE EVIDENCE EXTRACTION

## Status

PLANNED

---

# Objetivo

Analisar localmente um HAR produzido por uma sessão autorizada do próprio operador da Polarium e extrair somente evidências sanitizadas relacionadas a dados de mercado.

Arquivo privado de entrada:

```text
.jarvis_cache/evidence/trade.polariumbroker.com.har
```

O HAR bruto:

- não pode ser alterado;
- não pode ser movido para docs;
- não pode ser adicionado ao Git;
- não pode ser citado integralmente no relatório;
- não pode ter seus segredos reproduzidos.

---

# Regras obrigatórias de segurança

Nunca copiar para arquivos rastreáveis:

- cookies;
- Authorization;
- bearer;
- access token;
- refresh token;
- SSID;
- senhas;
- e-mails;
- client_secret;
- code_verifier;
- parâmetros privados de sessão;
- headers completos;
- URLs com credenciais;
- IDs pessoais desnecessários.

Não imprimir esses valores no terminal.

Não incluí-los no relatório final.

Não reconstruir credenciais parcialmente mascaradas.

O HAR deve permanecer somente em:

```text
.jarvis_cache/evidence/
```

---

# Antes de analisar

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

pwd
git rev-parse --show-toplevel
git branch --show-current
git status --short

git check-ignore -v .jarvis_cache/evidence/trade.polariumbroker.com.har

.venv/bin/python -m pytest -q

cd frontend
npm run build
```

Se o HAR não estiver ignorado pelo Git, interromper imediatamente.

---

# Escopo da análise

Analisar somente o necessário para identificar dados de mercado via WebSocket.

Procurar eventos ou estruturas relacionados a:

- candle-generated;
- candles-generated;
- first-candles;
- candles;
- digital-option-client-price-generated;
- timeSync;
- subscribeMessage;
- unsubscribeMessage;
- active_id;
- instrument_id;
- symbol;
- size;
- duration;
- timeframe;
- from;
- to;
- timestamp;
- open;
- high;
- low;
- close;
- min;
- max;
- volume.

Não analisar nem documentar operações, ordens ou execução.

---

# Classificação obrigatória

Cada descoberta deve ser classificada como:

## CONFIRMADO

Existe mensagem real no HAR que comprova o evento ou campo.

## PARCIAL

Existe indício real, mas o significado ou mapeamento ainda não está completamente comprovado.

## NÃO CONFIRMADO

Não existe evidência suficiente no HAR.

Nunca transformar hipótese em confirmação.

---

# Evidência sanitizada

Criar:

```text
docs/ws/POLARIUM_HAR_CANDLE_EVIDENCE_SANITIZED.md
```

Esse documento deve conter somente pequenos trechos necessários para explicar:

- nome do evento;
- direção da mensagem, quando identificável;
- estrutura sanitizada;
- active_id;
- timeframe ou duração;
- timestamp;
- OHLC;
- volume, somente quando presente;
- relação entre evento e contexto visual, quando comprovável.

Redigir ou remover qualquer valor sensível.

Não copiar blocos enormes do HAR.

Não copiar headers.

Não copiar cookies.

Não copiar mensagens de autenticação.

---

# Mapeamento de candle

Para cada payload candidato, verificar se existem campos equivalentes a:

```text
event
active_id
symbol
timeframe
from
to
timestamp
open
high
low
close
volume
```

Considerar possíveis equivalências:

```text
high = max
low = min
timeframe = size ou duration
timestamp inicial = from
timestamp final = to
```

Essas equivalências somente poderão ser marcadas como confirmadas quando sustentadas pela estrutura real observada.

---

# Mapeamento de ativo

Investigar se o HAR permite comprovar:

```text
active_id → símbolo visual
```

Procurar em:

- respostas de catálogo;
- mensagens de ativos;
- requests HTTP;
- subscriptions;
- instrument metadata;
- mensagens associadas à troca de ativo.

Não assumir que IDs conhecidos da IQ Option são iguais aos da Polarium.

---

# Mapeamento de timeframe

Investigar se:

```text
60  → M1
300 → M5
900 → M15
```

Somente marcar como confirmado quando a correlação puder ser demonstrada por mensagens reais ou contexto claro da captura.

---

# Documento técnico

Atualizar:

```text
docs/REAL_MARKET_DATA_REPORT.md
```

Adicionar uma seção:

```text
Sprint V2.8 — Evidência HAR autorizada
```

Incluir:

- eventos confirmados;
- eventos parciais;
- eventos não confirmados;
- estrutura do candle;
- possível subscription;
- mapeamento de ativo;
- mapeamento de timeframe;
- limitações;
- próximo passo recomendado.

Não incluir segredos nem grandes dumps.

---

# Adapter

Atualizar:

```text
app/market/adapters/market_data_adapter.py
```

somente se a evidência real comprovar campos adicionais.

Não integrar o adapter ao runtime.

Não alterar APIs.

Não alterar Connector em produção.

Não criar parser definitivo nesta Sprint.

---

# Não implementar

Não criar:

- indicadores;
- EMA;
- RSI;
- MACD;
- CALL;
- PUT;
- probabilidade;
- sinais;
- IA;
- execução;
- AutoTrade;
- ordens;
- subscriptions automáticas.

---

# Verificação de segurança

Após gerar os documentos, executar:

```bash
grep -RniE \
"access_token|refresh_token|authorization|bearer|cookie|ssid|password|client_secret|code_verifier" \
docs/ws docs/REAL_MARKET_DATA_REPORT.md || true
```

Revisar manualmente qualquer ocorrência.

Executar:

```bash
git status --short
```

Confirmar que o HAR bruto não aparece.

---

# Testes obrigatórios

Backend:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader
.venv/bin/python -m pytest -q
```

Frontend:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run build
```

---

# Entrega obrigatória

1. Objetivo.
2. Confirmação de que o HAR está ignorado.
3. Arquivos criados.
4. Arquivos modificados.
5. Quantidade aproximada de mensagens WS analisadas.
6. Eventos confirmados.
7. Eventos parciais.
8. Eventos não confirmados.
9. Estrutura real do payload de candle.
10. Mapeamento de OHLC.
11. Mapeamento de timeframe.
12. Mapeamento de active_id para símbolo.
13. Subscription encontrada ou não encontrada.
14. Limitações.
15. Atualização ou não do adapter, com justificativa.
16. Verificação de segurança.
17. Resultado do pytest.
18. Resultado do build.
19. `git status --short`.
20. `git diff --stat`.
21. Próxima Sprint recomendada.
22. Sugestão de commit.

Mensagem sugerida, somente se houver evidência sanitizada nova:

```text
docs(market): add sanitized Polarium candle evidence
```

---

# Regra final

NÃO fazer commit.

NÃO fazer push.

Não modificar frontend funcional.

Não modificar backend funcional.

Não expor conteúdo sensível do HAR.

Se não for possível sanitizar com segurança, interromper e entregar somente uma explicação do bloqueio.
