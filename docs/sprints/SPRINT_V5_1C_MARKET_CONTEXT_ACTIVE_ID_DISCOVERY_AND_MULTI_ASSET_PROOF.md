# SPRINT V5.1C — MARKET CONTEXT ACTIVE ID DISCOVERY AND MULTI-ASSET PROOF

## Objetivo

Colocar a sessão dedicada da Polarium em estado real de mercado, identificar sanitizadamente active_ids válidos da sessão atual e concluir a prova com dois ativos simultâneos.

A V5.1B comprovou:

- Chrome dedicado sem extensão;
- login manual legítimo;
- CDP local;
- authenticated;
- timeSync;
- classificação PAGE_NATIVE / FRIDAY_PROBE / SERVER_INBOUND;
- friday_probe_forbidden_calls vazio.

O bloqueio atual é:

```text
BLOCKED_NO_TWO_VALID_ACTIVE_IDS
```

Não implementar scanner.

Não integrar ao runtime principal.

---

# PARTE 1 — ABA E CONTEXTO CORRETOS

## 1. Uma aba da plataforma

A probe deve:

1. iniciar o Chrome dedicado;
2. abrir a Polarium oficial;
3. permitir login manual;
4. navegar até o terminal/gráfico de negociação;
5. manter somente uma aba relevante da Polarium;
6. listar sanitizadamente as abas abertas;
7. não registrar URLs com tokens ou parâmetros sensíveis.

Não prosseguir enquanto a tela real de mercado não estiver carregada.

---

## 2. Confirmação de estado de mercado

Considerar o terminal carregado somente após observar pelo menos um dos seguintes sinais:

```text
underlying-list
initialization-data
first-candles
candles
candle-generated
get-first-candles
```

`authenticated` e `timeSync` sozinhos não são suficientes.

Status esperado:

```text
MARKET_CONTEXT_READY
```

Caso contrário:

```text
BLOCKED_MARKET_CONTEXT_NOT_READY
```

---

# PARTE 2 — IDENTIFICAÇÃO DO WEBSOCKET DE MERCADO

## 3. Classificar os WebSockets

Para cada WebSocket observado, registrar somente:

- índice sanitizado;
- host;
- quantidade de frames;
- authenticated presente;
- timeSync presente;
- candle-generated presente;
- first-candles presente;
- mensagens de mercado presentes.

Não registrar payload completo.

Escolher como MARKET_WEBSOCKET aquele que contém eventos de mercado.

Não assumir que o primeiro WebSocket é o correto.

---

## 4. Reconexões

Se um WebSocket antigo fechar e outro substituir:

- atualizar a referência;
- não contar sockets encerrados como ativos;
- não enviar subscription em socket fechado;
- registrar somente contagem sanitizada de reconexões.

Resultado esperado:

```text
active_market_websocket_count = 1
```

Se existirem dois WebSockets de mercado ativos simultaneamente:

```text
BLOCKED_AMBIGUOUS_MARKET_WEBSOCKET
```

---

# PARTE 3 — DESCOBERTA PASSIVA DE ACTIVE IDS

## 5. Primeiro ativo

Solicitar ao usuário na própria execução:

```text
Abra um ativo OTC em M1 e aguarde.
```

Observar passivamente:

- outgoing get-first-candles;
- outgoing subscribeMessage candle-generated;
- incoming first-candles;
- incoming candle-generated.

Extrair somente:

```text
active_id
size
```

Símbolo pode ser registrado apenas se vier de estrutura pública de instrumentos e não contiver dado sensível.

Resultado:

```text
ACTIVE_CONTEXT_A_VALIDATED
```

---

## 6. Segundo ativo

Depois solicitar:

```text
Troque manualmente para outro ativo OTC em M1 e aguarde.
```

Capturar outro `active_id + size`.

Requisitos:

- active_id diferente;
- size igual a 60;
- contexto observado na sessão atual;
- nenhum ID vindo apenas de HAR antigo.

Resultado:

```text
ACTIVE_CONTEXT_B_VALIDATED
```

---

## 7. Não confundir mudança visual com encerramento

Registrar passivamente se a página:

- faz unsubscribe do ativo anterior;
- mantém a subscription anterior;
- cria nova subscription;
- reutiliza request_id;
- troca somente get-first-candles.

Isso ajudará a entender o comportamento nativo.

---

# PARTE 4 — RUNTIME GUARD

Manter as três origens:

```text
PAGE_NATIVE
FRIDAY_PROBE
SERVER_INBOUND
```

## FRIDAY_PROBE permitida

Somente:

```text
subscribeMessage -> candle-generated
unsubscribeMessage -> candle-generated
sendMessage -> get-first-candles
```

Qualquer outra mensagem criada pela Friday:

```text
ABORT
```

## PAGE_NATIVE

Observar passivamente e descartar domínios não relacionados ao mercado.

Não persistir payload.

## SERVER_INBOUND

Processar apenas:

```text
authenticated
timeSync
first-candles
candles
candle-generated
```

---

# PARTE 5 — PROVA COM DOIS ATIVOS

## 8. Preparação

Após validar A e B na sessão atual:

- garantir um único WebSocket de mercado ativo;
- manter a interface Polarium visível apenas no ativo B;
- enviar subscription Friday para A M1;
- enviar subscription Friday para B M1;
- usar request_ids exclusivos com prefixo `friday_probe_`.

---

## 9. Janela de observação

Observar por 60 segundos.

Comprovar:

- eventos de A;
- eventos de B;
- eventos intercalados;
- pelo menos 30 segundos de sobreposição;
- ativo A continua recebendo mesmo sem estar visível;
- stores independentes por `active_id + size`;
- zero forbidden calls da Friday.

---

# PARTE 6 — MESMO ATIVO M1 E M5

Somente após sucesso com A e B em M1:

- manter A size 60;
- criar A size 300;
- observar por 60 segundos.

Comprovar:

- eventos M1;
- eventos M5;
- stores separados;
- nenhum cruzamento de candles.

---

# PARTE 7 — UNSUBSCRIBE

Primeiro observar o envelope nativo real de:

```text
unsubscribeMessage -> candle-generated
```

Se comprovado, cancelar somente B M1.

Confirmar:

- B para;
- A M1 continua;
- A M5 continua, quando aplicável;
- WebSocket permanece aberto.

Não inventar envelope.

---

# PARTE 8 — MÉTRICAS

Registrar por contexto:

- active_id;
- size;
- origem da validação;
- subscription_at;
- first_event_at;
- event_count;
- OHLC changes;
- average interval;
- p50;
- p95;
- maximum gap;
- last_event_at;
- events_after_unsubscribe.

Global:

- active WebSockets;
- reconnects;
- CPU;
- memória;
- Chrome processes;
- page_native_discarded_count;
- server_inbound_discarded_count;
- friday_probe_forbidden_calls;
- cleanup duration.

---

# PARTE 9 — CLEANUP

Ao finalizar:

- cancelar subscriptions Friday quando envelope estiver comprovado;
- caso contrário, fechar o navegador dedicado;
- encerrar conexões CDP;
- confirmar zero processos da probe;
- não reutilizar perfil autenticado fora da probe;
- não exportar cookie/token/storage.

---

# ENTREGA ESPERADA

Entregar:

1. motivo de active_ids não aparecerem na V5.1B;
2. estado MARKET_CONTEXT_READY;
3. quantidade total e ativa de WebSockets;
4. identificação do MARKET_WEBSOCKET;
5. contexto A validado;
6. contexto B validado;
7. comportamento nativo ao trocar ativo;
8. envelopes sanitizados observados;
9. subscriptions Friday enviadas;
10. eventos de A;
11. eventos de B;
12. intercalamento;
13. ativo não visível;
14. resultado M1 + M5;
15. unsubscribe;
16. CPU e memória;
17. cleanup;
18. friday_probe_forbidden_calls;
19. page_native_discarded_count;
20. server_inbound_discarded_count;
21. arquivos modificados;
22. testes;
23. git status;
24. git diff;
25. riscos;
26. recomendação para V5.2.

Não implementar scanner.

Não alterar runtime principal.

Não alterar MarketChart.

Não usar extensão.

Não fazer commit.

Não fazer push.