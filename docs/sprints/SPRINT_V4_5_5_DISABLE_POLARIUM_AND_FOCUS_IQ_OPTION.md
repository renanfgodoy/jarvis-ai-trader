# Friday Trade — Sprint V4.5.5

# Disable Polarium and Focus IQ Option

## Status

PLANNED

---

## Objetivo

Retirar temporariamente a Polarium do runtime e da interface principal do Friday Trade.

A IQ Option OTC passa a ser o único provider de mercado disponível na tela `/market-chart`.

O código e os documentos da Polarium devem ser preservados no repositório para possível retomada futura, mas não devem:

- aparecer no seletor;
- iniciar polling;
- carregar séries;
- influenciar contexto;
- exibir dados antigos;
- interferir no gráfico IQ Option.

---

## Evidência real

A IQ Option já comprovou:

```text
conexão read-only
ativos OTC
candles M1/M5/M15
bootstrap histórico
polling
worker isolado
Store
Chart API
frontend
```

A Polarium permanece com problemas:

```text
ativo não identificado
dados antigos inválidos
velas gigantes artificiais
Browser Bridge desconectado
séries contaminadas persistidas
contexto confuso
```

Manter os dois providers visíveis está prejudicando a experiência e o desenvolvimento da análise.

---

## Decisão arquitetural

Provider ativo oficial atual:

```text
IQ_OPTION
```

Provider temporariamente desativado:

```text
POLARIUM
```

Não apagar arquivos Polarium.

Não remover testes históricos necessários.

Não destruir documentação.

Apenas impedir uso no runtime principal.

---

## Frontend

Na tela `/market-chart`:

- remover o seletor de provider, caso só exista IQ Option;
- ou manter o campo fixo e desabilitado mostrando `IQ Option OTC`;
- iniciar sempre com `providerMode = IQ_OPTION`;
- nunca permitir seleção Polarium;
- remover `Seguir Polarium`;
- remover textos de Browser Bridge;
- remover instruções para abrir Polarium;
- remover Active ID;
- exibir apenas símbolos IQ Option;
- exibir apenas M1, M5 e M15.

Preferência visual:

```text
Fonte: IQ OPTION — READ ONLY
Ativo: EUR/USD OTC
Timeframe: M1
```

---

## Runtime frontend

Não montar ou executar:

```text
useRealCandles
Polarium status polling
Polarium series polling
Polarium chart polling
Follow Polarium
Browser Bridge state
```

O hook pode permanecer no código, mas deve ficar fora do fluxo da página principal.

Não fazer qualquer chamada para:

```text
/api/v1/polarium/browser-bridge/status
/api/v1/market/chart/series com contexto Polarium
/api/v1/market/chart?active_id=
```

durante uso normal da tela.

---

## Estado inicial

Ao abrir `/market-chart`:

1. provider definido como `IQ_OPTION`;
2. consultar status IQ;
3. conectar se necessário;
4. buscar ativos OTC;
5. selecionar automaticamente `EURUSD-OTC` quando disponível;
6. carregar M1;
7. iniciar bootstrap;
8. iniciar polling.

A tela não deve abrir vazia aguardando seleção manual.

---

## Dados Polarium antigos

Não apagar automaticamente SQLite.

Porém, impedir que séries Polarium sejam lidas ou exibidas pela página IQ Option.

O frontend e a API da tela devem filtrar estritamente:

```text
provider = IQ_OPTION
```

Se existir cache Polarium:

- ignorar no modo principal;
- não usar como fallback;
- não mostrar no seletor;
- não misturar no gráfico.

---

## Backend

Manter endpoints Polarium existentes, mas eles não devem ser chamados pelo frontend principal.

Opcionalmente adicionar feature flag:

```text
POLARIUM_PROVIDER_ENABLED=false
```

Padrão atual:

```text
false
```

O runtime Polarium deve permanecer desligado quando a flag for falsa.

---

## Feature flags

Criar ou revisar:

```text
IQ_OPTION_PROVIDER_ENABLED=true
POLARIUM_PROVIDER_ENABLED=false
```

A UI deve refletir apenas providers habilitados.

Se futuramente Polarium voltar:

```text
POLARIUM_PROVIDER_ENABLED=true
```

poderá reativar o provider após nova validação.

---

## Navegação

Revisar itens relacionados:

- `Polarium Lab`;
- `Connections`;
- provider Polarium;
- Browser Bridge.

Preferência:

- ocultar `Polarium Lab` do menu principal enquanto desativado;
- manter código e rota acessíveis apenas em ambiente developer, se necessário;
- não misturar com experiência normal do usuário.

---

## Contexto visual

Remover completamente no fluxo IQ:

```text
Seguindo Polarium
Ativo não identificado
Active ID
Browser Bridge
Abra a Polarium autenticada
Aguardando séries reais da Polarium
```

Exibir:

```text
Modo: IQ Option Read Only
Provider: IQ Option
Ativo: EUR/USD OTC
Timeframe: M1
Candles: quantidade real
Última atualização
```

---

## Gráfico

Ao abrir a tela:

- zerar qualquer contexto visual Polarium anterior;
- não reutilizar candles Polarium;
- carregar apenas série IQ Option;
- reset controlado ao trocar símbolo/timeframe;
- preservar polling IQ;
- preservar zoom e pan;
- evitar flash de dados Polarium.

---

## Persistência

A leitura da página IQ Option deve usar somente:

```text
provider = IQ_OPTION
symbol
raw_size
```

Não usar:

```text
active_id
```

Não restaurar séries Polarium como fallback.

---

## Testes obrigatórios

Criar testes para:

1. provider inicial é IQ Option;
2. Polarium não aparece no seletor;
3. seletor pode ser removido quando houver apenas um provider;
4. `useRealCandles` Polarium não é iniciado;
5. zero chamadas Browser Bridge;
6. zero chamadas chart com `active_id`;
7. zero chamada series Polarium;
8. Follow Polarium não aparece;
9. Active ID não aparece;
10. Polarium Lab oculto quando desativado;
11. IQ status executa;
12. connect IQ executa;
13. assets IQ executa;
14. EURUSD-OTC selecionado automaticamente;
15. bootstrap M1 inicia automaticamente;
16. polling IQ inicia;
17. séries Polarium são ignoradas;
18. cache Polarium não aparece;
19. gráfico inicia sem flash Polarium;
20. M1/M5/M15;
21. troca de ativo;
22. suíte completa;
23. build.

---

## Validação real

1. subir backend;
2. subir frontend;
3. abrir `/market-chart`;
4. confirmar que não existe opção Polarium;
5. confirmar que IQ Option já está selecionada;
6. confirmar ativos carregados;
7. confirmar EUR/USD OTC selecionado;
8. confirmar M1 carregado;
9. abrir Network;
10. confirmar somente chamadas IQ Option;
11. confirmar zero chamadas Polarium;
12. confirmar gráfico sem velas artificiais Polarium;
13. confirmar polling IQ;
14. trocar ativo;
15. trocar timeframe.

---

## Critério de sucesso

Ao abrir `/market-chart`:

```text
IQ Option OTC ativa
ativos carregados
EURUSD-OTC selecionado
M1 carregado
gráfico exibido
polling ativo
zero chamadas Polarium
zero dados Polarium
```

---

---

## Performance obrigatória

O carregamento atual pode ultrapassar um minuto porque o worker IQ Option é iniciado em modo one-shot e pode realizar novo login em cada chamada.

Esse comportamento deve ser substituído por um worker persistente e controlado.

Arquitetura desejada:

```text
Backend Friday
→ IQOptionPersistentWorkerManager
→ um subprocesso isolado
→ uma conexão IQ Option read-only
→ cache de ativos
→ cache de séries
→ comandos rápidos
```

Não criar subprocesso/login novo para cada:

```text
status
assets
candles
polling
```

---

## Worker persistente

O worker deve suportar lifecycle:

```text
start
connect
status
list_assets
get_candles
get_recent_candles
disconnect
stop
restart
```

Requisitos:

- somente um processo ativo;
- somente uma conexão IQ Option;
- fila de comandos;
- uma operação de biblioteca por vez;
- timeout controlado;
- heartbeat;
- reconexão automática limitada;
- encerramento limpo;
- nenhuma thread ou processo órfão;
- Runtime Guard read-only durante todo o lifecycle.

A `.venv` principal continua sem `iqoptionapi`.

O processo deve continuar usando exclusivamente:

```text
.jarvis_cache/iq_option_probe_venv/bin/python
```

---

## Protocolo persistente

Preferir comunicação local por:

```text
stdin/stdout JSON Lines
```

ou socket local restrito a localhost.

Cada comando deve possuir:

```text
request_id sanitizado
command
params permitidos
```

Cada resposta:

```text
request_id sanitizado
success
data sanitizada
error_code
duration_ms
```

Não misturar logs no stdout do protocolo.

---

## Cache de ativos

Após conectar, carregar automaticamente os ativos disponíveis.

Manter cache backend com:

```text
provider
market_type
symbol
display_name
is_open
last_checked_at
```

Categorias desejadas:

```text
OTC
REGULAR
```

O endpoint de assets deve responder primeiro pelo cache.

Atualização do cache:

```text
background refresh controlado
```

Sugestão:

```text
a cada 30–60 segundos
```

Falha temporária não deve apagar a última lista válida.

Usar estratégia:

```text
stale-while-revalidate
```

Ou seja:

1. devolver cache imediatamente;
2. atualizar em background;
3. substituir apenas quando houver resposta válida.

---

## Mercado OTC e mercado aberto

A experiência principal deve permitir:

```text
Mercado OTC
Mercado aberto
```

Mercado OTC:

```text
símbolos terminados em -OTC
```

Mercado aberto/regular:

```text
símbolos sem -OTC
somente quando is_open = true
```

Não inventar disponibilidade.

Não classificar ativo como aberto apenas pelo nome.

Usar evidência read-only real da biblioteca ou candle recente válido.

---

## Seletor de mercado

Adicionar na tela:

```text
MERCADO
[OTC] [ABERTO]
```

Ou seletor equivalente:

```text
IQ Option OTC
IQ Option Mercado Aberto
```

Preferência visual:

```text
Provider: IQ Option
Mercado: OTC
Ativo: EUR/USD OTC
Timeframe: M1
```

Ao selecionar mercado aberto:

```text
Provider: IQ Option
Mercado: Aberto
Ativo: EUR/USD
Timeframe: M1
```

---

## Estado de mercado fechado

Quando não houver ativos regulares abertos:

```text
Mercado regular fechado no momento.
Os ativos OTC continuam disponíveis.
```

Não deixar loading infinito.

Não trocar automaticamente para OTC sem informar o operador.

---

## Bootstrap antecipado

Depois de carregar os ativos, pré-carregar em background:

```text
EURUSD-OTC M1
```

quando disponível.

Também pré-carregar, sem bloquear a UI:

```text
M5
M15
```

Para mercado regular, pré-carregar o primeiro ativo aberto ou o último escolhido pelo usuário.

Prioridade:

```text
1. ativo/timeframe selecionado;
2. último contexto usado;
3. EURUSD-OTC M1;
4. demais timeframes do ativo atual.
```

---

## Cache de candles

Manter cache por:

```text
provider + market_type + symbol + raw_size
```

Cada cache deve conter:

```text
histórico
último candle
last_updated_at
is_stale
```

Ao abrir o gráfico:

1. devolver cache imediatamente;
2. renderizar histórico;
3. atualizar últimos candles em background;
4. fazer merge;
5. nunca apagar histórico em falha temporária.

---

## Persistência e abertura instantânea

Usar o SQLite já existente para restaurar candles no startup.

Ao iniciar backend:

```text
SQLite
→ CandleStore
→ Chart API disponível imediatamente
```

A conexão IQ Option atualiza os candles depois, sem impedir a primeira renderização.

Nunca mostrar dados Polarium.

---

## Polling eficiente

Com worker persistente:

```text
intervalo sugerido = 1 segundo
```

Buscar somente:

```text
1 a 3 candles recentes
```

Não buscar 500/1000 candles em cada ciclo.

Regras:

- apenas uma requisição em voo;
- atualizar candle atual por timestamp;
- acrescentar novo candle;
- preservar histórico;
- backoff em erro;
- não iniciar novo login.

---

## Metas de desempenho

Instrumentar:

```text
worker_start_duration_ms
connection_duration_ms
assets_cache_duration_ms
assets_response_duration_ms
bootstrap_duration_ms
chart_first_render_ms
poll_duration_ms
```

Metas:

```text
assets com cache: < 500 ms
Chart API com cache: < 500 ms
primeiro gráfico com histórico local: < 1 segundo
cold start completo: preferencialmente < 8 segundos
troca entre séries em cache: < 500 ms
polling: não sobreposto
```

Se não atingir, relatar valores reais e gargalo comprovado.

---

## Estado de carregamento

Substituir loading genérico por etapas curtas:

```text
Iniciando fonte...
Conectando...
Carregando ativos...
Restaurando histórico...
Atualizando mercado...
```

Quando houver cache, mostrar gráfico imediatamente com badge:

```text
ATUALIZANDO
```

e depois:

```text
LIVE
```

---

## Preferências locais

Persistir localmente, sem dados sensíveis:

```text
último mercado
último símbolo
último timeframe
```

Ao reabrir:

```text
restaurar seleção
mostrar cache
atualizar em background
```

---

## Endpoints sugeridos

Manter os endpoints existentes e ampliar o contrato:

```text
GET /api/v1/market/providers/iq-option/assets?market_type=OTC
GET /api/v1/market/providers/iq-option/assets?market_type=REGULAR
GET /api/v1/market/providers/iq-option/candles
GET /api/v1/market/providers/iq-option/runtime/status
POST /api/v1/market/providers/iq-option/runtime/restart
```

O restart deve ser permitido apenas localmente e em desenvolvimento.

---

## Segurança do worker persistente

Continuar bloqueando:

```text
buy
sell
get_balance
get_positions
change_balance
close_position
ordens e equivalentes
```

Não persistir credenciais no cache.

Não enviar credenciais ao frontend.

Não incluir credenciais no protocolo JSON.

---

## Testes adicionais obrigatórios

Criar testes para:

1. somente um worker persistente;
2. somente uma conexão;
3. assets não fazem novo login;
4. polling não faz novo login;
5. fila serializa comandos;
6. timeout reinicia worker controladamente;
7. heartbeat detecta worker morto;
8. reconexão limitada;
9. processo órfão inexistente;
10. assets OTC;
11. assets regulares;
12. somente regulares abertos;
13. mercado regular fechado;
14. cache stale-while-revalidate;
15. falha não apaga assets em cache;
16. bootstrap antecipado;
17. cache por market_type/symbol/raw_size;
18. SQLite abre gráfico antes da rede;
19. troca de ativo em cache rápida;
20. polling de 1–3 candles;
21. uma request em voo;
22. métricas sanitizadas;
23. nenhum método proibido;
24. frontend OTC;
25. frontend mercado aberto;
26. suíte completa;
27. build.

---

## Validação real adicional

1. iniciar backend do zero;
2. medir tempo até conexão;
3. medir tempo até ativos;
4. abrir `/market-chart`;
5. medir tempo até primeiro gráfico;
6. confirmar worker único;
7. confirmar ausência de novo login por polling;
8. alternar OTC e mercado aberto;
9. confirmar lista correta em cada mercado;
10. trocar M1/M5/M15;
11. reabrir página;
12. confirmar renderização imediata pelo cache;
13. desconectar rede brevemente;
14. confirmar histórico preservado;
15. restaurar rede;
16. confirmar atualização automática.

## Entrega obrigatória

1. Objetivo.
2. Decisão arquitetural.
3. Polarium removida da UI.
4. Polarium desativada no runtime.
5. Feature flags.
6. Estado inicial IQ Option.
7. Filtro de dados.
8. Navegação.
9. Contexto visual.
10. Arquivos criados.
11. Arquivos modificados.
12. Testes específicos.
13. Suíte completa.
14. Build.
15. Como testar.
16. Riscos.
17. Débitos técnicos.
18. `git status --short`.
19. `git diff --stat`.
20. Sugestão de commit.

Mensagem sugerida:

```text
refactor(market): disable Polarium and focus IQ Option provider
```

---

## Regra final

Não fazer commit.

Não fazer push.

Não apagar código Polarium.

Não apagar SQLite automaticamente.

Não alterar worker IQ Option.

Não instalar iqoptionapi na `.venv` principal.

Não consultar saldo.

Não executar ordens.

Polarium deve ficar completamente fora da experiência principal enquanto estiver desativada.