# SPRINT V5.1 — AUTHORIZED MULTI-ASSET SESSION PROBE

## Objetivo

Comprovar, em uma sessão Polarium legítima do próprio usuário, se um único WebSocket autenticado consegue manter subscriptions read-only simultâneas para múltiplos ativos e timeframes.

A prova deve ocorrer sem extensão instalada, sem exportação manual de cookies, sem reutilização de HAR e sem automação de ordens.

Esta Sprint é uma probe isolada.

Não é implementação de produção.

---

# CONTEXTO COMPROVADO

A auditoria V5.0 encontrou evidências compatíveis com:

```text
1 WebSocket
→ N subscriptions
→ eventos identificados por active_id + size
```

Foram observados:

- `subscribeMessage`;
- `unsubscribeMessage`;
- `get-first-candles`;
- `first-candles`;
- `candle-generated`;
- múltiplos `active_id`;
- campo `size`;
- `timeSync`.

Ainda falta provar simultaneidade real e unsubscribe isolado.

---

# REGRA PRINCIPAL

Usar somente uma sessão legítima iniciada pelo próprio usuário.

Não:

- ler senha;
- armazenar senha;
- exportar cookie;
- exportar token;
- copiar SSID;
- reutilizar HAR;
- imprimir material de autenticação;
- executar ordem;
- consultar saldo;
- consultar posições;
- consultar portfolio;
- alterar conta.

Todo material sensível deve permanecer dentro do contexto autenticado original.

---

# PARTE 1 — SESSÃO LOCAL SEM EXTENSÃO

## 1. Navegador dedicado

Criar somente uma probe local capaz de:

1. iniciar um navegador/perfil dedicado;
2. abrir a página oficial da Polarium;
3. permitir que o usuário faça login manualmente;
4. detectar que a sessão foi autenticada;
5. observar o WebSocket existente da sessão;
6. nunca capturar ou persistir credenciais.

Não exigir instalação de extensão.

Não exigir DevTools manual.

Não alterar o perfil principal do Chrome do usuário.

---

## 2. Isolamento

Usar perfil temporário ou perfil específico da Friday.

Ao encerrar:

- fechar a conexão;
- limpar referências em memória;
- não exportar cookies;
- não copiar storage;
- não escrever tokens em log;
- não reutilizar a sessão em outro processo.

---

# PARTE 2 — RUNTIME GUARD

## 3. Allowlist de saída

Permitir somente mensagens estritamente necessárias para:

- autenticação já realizada pelo contexto original;
- subscription de candles;
- unsubscribe de candles;
- solicitação de histórico `first-candles`;
- heartbeat técnico, se necessário.

Bloquear qualquer saída relacionada a:

- order;
- buy;
- sell;
- position;
- portfolio;
- balance;
- account;
- payment;
- deposit;
- withdrawal;
- change-balance.

A probe deve abortar se uma mensagem fora da allowlist for solicitada.

---

## 4. Allowlist de entrada

Processar somente:

- `authenticated`;
- `timeSync`;
- `first-candles`;
- `candles`;
- `candle-generated`;
- confirmação técnica de subscribe/unsubscribe, quando houver.

Ignorar e descartar eventos financeiros ou de conta.

Não persistir payloads sensíveis.

---

# PARTE 3 — PROVA MULTIATIVOS

## 5. Teste inicial

Usar somente 2 ativos distintos no mesmo timeframe.

Exemplo conceitual:

```text
Ativo A + M1
Ativo B + M1
```

Não fixar IDs sem validá-los na sessão atual.

Confirmar:

- uma única sessão;
- um único WebSocket;
- duas subscriptions ativas;
- eventos recebidos para os dois `active_id`;
- eventos identificáveis sem mistura;
- CandleStores separados.

Janela mínima sugerida:

```text
60 segundos
```

---

## 6. Teste com 3 ativos

Somente se o teste com 2 ativos for estável:

```text
Ativo A + M1
Ativo B + M1
Ativo C + M1
```

Medir:

- eventos por ativo;
- erros;
- mensagens perdidas;
- maior intervalo;
- consumo de CPU;
- consumo de memória;
- estabilidade da sessão.

Não avançar para dezenas de ativos nesta Sprint.

---

# PARTE 4 — MULTITIMEFRAME

## 7. Mesmo ativo em tamanhos diferentes

Testar:

```text
Ativo A + M1
Ativo A + M5
```

Confirmar:

- eventos separados por `active_id + size`;
- nenhuma contaminação entre séries;
- CandleStore M1 independente do M5.

---

## 8. Combinação final

Somente após os testes anteriores:

```text
Ativo A + M1
Ativo A + M5
Ativo B + M1
```

Não ultrapassar três contextos simultâneos nesta Sprint.

---

# PARTE 5 — UNSUBSCRIBE

## 9. Cancelamento isolado

Cancelar apenas:

```text
Ativo B + M1
```

Confirmar:

- Ativo B deixa de receber eventos;
- Ativo A M1 continua;
- Ativo A M5 continua;
- WebSocket permanece aberto;
- nenhum contexto incorreto é encerrado.

---

## 10. Cleanup

Ao terminar:

- cancelar todas as subscriptions criadas pela probe;
- fechar listeners;
- encerrar navegador dedicado;
- confirmar zero assinantes órfãos;
- confirmar zero processos órfãos.

---

# PARTE 6 — MÉTRICAS

## 11. Registrar por contexto

Para cada `active_id + size`:

- subscription iniciada;
- primeiro evento;
- quantidade de eventos;
- quantidade de mudanças OHLC;
- último evento;
- intervalo médio;
- p50;
- p95;
- maior gap;
- erros;
- eventos após unsubscribe;
- tempo de cleanup.

Não registrar preço ou payload completo quando desnecessário.

---

# PARTE 7 — RESULTADO

Responder objetivamente:

## Um WebSocket aceita 2 ativos simultâneos?

```text
SIM / NÃO / INCONCLUSIVO
```

## Um WebSocket aceita 3 ativos simultâneos?

```text
SIM / NÃO / NÃO TESTADO
```

## Mesmo ativo aceita M1 e M5 simultaneamente?

```text
SIM / NÃO / INCONCLUSIVO
```

## Unsubscribe é isolado?

```text
SIM / NÃO / INCONCLUSIVO
```

## O gráfico principal precisa estar no ativo medido?

```text
SIM / NÃO / INCONCLUSIVO
```

## É possível criar scanner multiativos?

```text
SIM / PARCIALMENTE / NÃO
```

---

# PARTE 8 — LIMITES

Não transformar sucesso com três contextos em alegação de suporte a 72 ativos.

Caso a prova funcione, recomendar crescimento gradual:

```text
3
→ 5
→ 10
→ lotes rotativos
```

Não criar scanner em massa nesta Sprint.

---

# PARTE 9 — ARQUIVOS

Preferir probe isolada em:

```text
.jarvis_cache/polarium_multi_asset_probe/
```

ou diretório de ferramenta experimental já ignorado pelo Git.

Não conectar a probe ao runtime principal.

Não alterar MarketChart.

Não alterar Strategy Engine.

Não alterar IQ Option.

---

# PARTE 10 — TESTES

Se houver código reutilizável, criar testes para:

1. allowlist de saída;
2. bloqueio de mensagens proibidas;
3. chave `active_id + size`;
4. roteamento para stores independentes;
5. unsubscribe isolado;
6. cleanup;
7. sanitização de logs;
8. ausência de segredos persistidos.

Executar somente os testes pertinentes.

Não executar build frontend se o frontend não for alterado.

---

# ENTREGA ESPERADA

Entregar relatório com:

1. arquitetura da sessão local;
2. confirmação de ausência de extensão;
3. confirmação de ausência de exportação de cookie/token;
4. quantidade de WebSockets;
5. resultado com 2 ativos;
6. resultado com 3 ativos;
7. resultado M1 + M5;
8. resultado do unsubscribe;
9. eventos por contexto;
10. p50, p95 e maior gap;
11. CPU e memória;
12. cleanup;
13. Runtime Guard;
14. forbidden_calls;
15. arquivos criados/modificados;
16. testes;
17. git status;
18. git diff;
19. riscos;
20. recomendação para V5.2.

Não implementar scanner.

Não executar ordens.

Não consultar saldo.

Não fazer commit.

Não fazer push.