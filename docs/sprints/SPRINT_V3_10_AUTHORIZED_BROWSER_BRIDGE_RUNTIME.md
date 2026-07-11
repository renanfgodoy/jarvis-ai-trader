# Friday Trade V3.10
# Authorized Browser Bridge Runtime

## Status

PLANNED

---

## Objetivo

Transformar o Browser Bridge já existente em uma fonte autorizada, read-only e sanitizada de mensagens reais de mercado.

O Bridge deve observar exclusivamente o WebSocket que a própria aba autenticada da Polarium já abriu.

O Friday Trade não deve autenticar na Polarium nesta Sprint.

Fluxo:

```text
Aba Polarium autenticada pelo operador
→ content-script Browser Bridge
→ filtro e sanitização no navegador
→ endpoint interno protegido
→ MarketPipeline compartilhado
→ CandleStore compartilhado
→ Chart API
→ RealCandleChart
```

---

## Princípio de segurança

O Browser Bridge nunca poderá encaminhar:

- authenticate;
- authenticated com material de sessão;
- token;
- cookie;
- Authorization;
- bearer;
- SSID;
- credenciais;
- headers;
- URL privada;
- dados de conta;
- saldo;
- portfólio;
- ordens;
- posições;
- execução;
- HAR bruto.

Somente eventos de mercado permitidos poderão sair do navegador.

---

## Eventos inicialmente permitidos

Permitir somente:

```text
first-candles
candle-generated
candles-generated
timeSync
```

Opcionalmente registrar apenas metadados de:

```text
subscribeMessage
get-first-candles
```

Não enviar material de autenticação ou payload privado.

---

## Diagnóstico obrigatório inicial

Revisar:

```text
tools/polarium-browser-bridge/content-script.js
tools/polarium-browser-bridge/
app/api/router.py
app/api/routes/
app/market/events/
app/market/pipeline/
app/market/runtime.py
app/market/store/
app/market/chart/
```

Confirmar:

1. Como o content-script intercepta `window.WebSocket`.
2. Se intercepta frames enviados e recebidos.
3. Qual endpoint tenta utilizar.
4. Por que `bridge-message` ainda não existe.
5. Como adicionar o endpoint sem aceitar segredos.
6. Como garantir que somente eventos permitidos chegam ao pipeline.

---

## Backend

Criar uma rota interna semelhante a:

```text
POST /api/v1/polarium/browser-bridge/message
GET  /api/v1/polarium/browser-bridge/status
```

A rota de mensagem deve:

- aceitar somente JSON;
- limitar tamanho de payload;
- rejeitar arrays ou objetos excessivamente profundos;
- rejeitar qualquer campo sensível, inclusive em estruturas aninhadas;
- aceitar somente eventos da allowlist;
- sanitizar antes de encaminhar;
- encaminhar candles ao `market_pipeline` compartilhado;
- nunca registrar payload bruto;
- retornar somente resultado sanitizado.

---

## Proteção do endpoint

O endpoint não deve ficar aberto indiscriminadamente.

Implementar proteção local apropriada, sem utilizar credenciais da Polarium.

Possibilidades permitidas:

- aceitar somente origem/extensão local previamente configurada;
- chave local aleatória gerada no primeiro uso e armazenada apenas em `.jarvis_cache`;
- token local próprio do Friday Trade, diferente de qualquer segredo da Polarium;
- validação de ambiente development/local.

Nunca usar token da Polarium como proteção do Bridge.

Não versionar a chave local.

---

## Content Script

Modificar apenas o necessário para:

1. observar WebSockets já criados pela aba Polarium;
2. decodificar mensagens JSON quando possível;
3. identificar o `name` do evento;
4. aplicar allowlist no navegador;
5. remover qualquer campo sensível;
6. enviar somente eventos permitidos ao endpoint interno;
7. manter contador e status local;
8. não interferir no WebSocket original;
9. não alterar mensagens enviadas pela Polarium;
10. não executar ordens nem ações na página.

---

## Status sanitizado

Expor somente:

```text
connected
bridge_active
last_event_name
last_event_at
received_count
accepted_count
rejected_count
pipeline_success_count
last_error_code
active_ids_seen
raw_sizes_seen
source = POLARIUM_AUTHORIZED_BROWSER
```

Nunca expor conteúdo bruto.

---

## Integração com MarketPipeline

Utilizar exclusivamente:

```text
market_pipeline.process(message)
```

Não escrever diretamente no CandleStore.

Não duplicar parser.

Não duplicar CandleChartService.

---

## Fonte exibida no gráfico

Quando houver eventos reais aceitos, o frontend deverá identificar a fonte como:

```text
POLARIUM AUTHORIZED BROWSER LIVE
```

Quando não houver Bridge ativo:

```text
DISCONNECTED
```

Quando o simulador estiver ativo:

```text
SIMULATED / CONTROLLED DEVELOPMENT DATA
```

Nunca misturar dados simulados e reais na mesma série sem limpar ou separar o Store.

---

## Separação entre modo real e simulador

Adicionar regra explícita:

- iniciar Bridge real deve bloquear/parar o simulador;
- iniciar simulador deve ser impedido enquanto o Bridge real estiver ativo;
- candles simulados e reais não podem compartilhar a mesma série sem reset controlado;
- o status deve informar claramente o modo atual.

---

## Testes obrigatórios

Criar testes para:

- aceitar `candle-generated`;
- aceitar `first-candles`;
- aceitar `timeSync` sem enviar ao CandleStore;
- rejeitar `authenticate`;
- rejeitar `authenticated`;
- rejeitar token aninhado;
- rejeitar cookie aninhado;
- rejeitar Authorization;
- rejeitar bearer;
- rejeitar SSID;
- rejeitar saldo;
- rejeitar portfólio;
- rejeitar ordens;
- rejeitar execução;
- rejeitar evento fora da allowlist;
- rejeitar payload grande;
- proteção local do endpoint;
- MarketPipeline recebe apenas mensagem sanitizada;
- CandleStore recebe candle real;
- Chart API reflete candle;
- status não expõe segredo;
- simulador e Bridge não funcionam simultaneamente;
- erro do Bridge não derruba backend;
- mensagens repetidas seguem deduplicação existente.

---

## Fora do escopo

Não:

- criar login;
- criar OAuth;
- abrir WebSocket no backend;
- receber senha;
- receber cookie da Polarium;
- receber token da Polarium;
- controlar a página;
- clicar;
- executar CALL;
- executar PUT;
- enviar ordens;
- alterar saldo;
- criar AutoTrade;
- criar indicadores;
- criar IA.

---

## Validação visual obrigatória

Após implementação:

1. Abrir o Friday Trade.
2. Abrir a Polarium em uma aba separada.
3. Entrar manualmente na própria conta.
4. Preferir conta DEMO.
5. Ativar o Browser Bridge.
6. Selecionar manualmente um ativo e timeframe na Polarium.
7. Abrir `/market-chart`.
8. Confirmar que o candle muda sem F5.
9. Confirmar que novos candles surgem.
10. Confirmar que a fonte mostra `POLARIUM AUTHORIZED BROWSER LIVE`.
11. Confirmar que o simulador está parado.
12. Abrir o Console e verificar ausência de erros.
13. Conferir status sanitizado do Bridge.

Enviar prints:

- Polarium com ativo e timeframe;
- Friday Trade com candles reais;
- status do Bridge;
- Chart API;
- Console;
- terminal do backend sem dados sensíveis.

---

## Testes e build

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

.venv/bin/python -m pytest -q

cd frontend
npm run build
```

---

## Entrega obrigatória

1. Objetivo.
2. Diagnóstico do Browser Bridge existente.
3. Arquitetura implementada.
4. Arquivos criados.
5. Arquivos modificados.
6. Endpoint criado.
7. Proteção local utilizada.
8. Allowlist de eventos.
9. Política de sanitização.
10. Integração com MarketPipeline.
11. Separação simulador/real.
12. Status sanitizado.
13. Testes criados.
14. Resultado dos testes específicos.
15. Resultado da suíte completa.
16. Resultado do build.
17. Como instalar/ativar o Browser Bridge.
18. Como testar visualmente.
19. Riscos conhecidos.
20. Débitos técnicos.
21. `git status --short`.
22. `git diff --stat`.
23. Sugestão de commit.

Mensagem sugerida:

```text
feat(polarium): add authorized browser bridge market runtime
```

---

## Regra final

Não fazer commit.

Não fazer push.

Se o Bridge exigir copiar token, cookie, SSID ou qualquer segredo da Polarium para o backend, interromper.

O Browser Bridge só poderá encaminhar eventos de mercado sanitizados da sessão que o próprio operador abriu manualmente.