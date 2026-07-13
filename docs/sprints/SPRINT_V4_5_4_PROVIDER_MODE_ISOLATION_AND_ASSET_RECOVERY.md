# Friday Trade — Sprint V4.5.4

# Provider Mode Isolation and IQ Option Asset Recovery

## Status

PLANNED

---

## Objetivo

Corrigir a troca de provider na tela `/market-chart`, garantindo isolamento completo entre Polarium e IQ Option.

Evidência real observada:

```text
provider selecionado = IQ Option OTC
/assets?market_type=OTC = 502
lista de ativos = vazia
```

Ao mesmo tempo, o frontend continua executando chamadas Polarium:

```text
/browser-bridge/status
/market/chart/series
/market/chart?active_id=76...
```

Portanto, os dois modos continuam ativos simultaneamente.

---

## Causa comprovada

O frontend mantém o hook/polling Polarium ativo mesmo quando:

```text
providerMode = IQ_OPTION
```

Além disso, uma falha temporária `502` no endpoint de ativos IQ Option deixa a lista vazia permanentemente, sem retry ou recuperação automática.

---

## Fluxo desejado

### Polarium selecionada

```text
ativar hook Polarium
ativar Follow Polarium
buscar status/series/chart Polarium
desativar IQ polling
```

### IQ Option selecionada

```text
desativar hook/polling Polarium
limpar contexto Polarium
conectar IQ Option
buscar assets OTC
retry controlado em falha temporária
selecionar primeiro ativo aberto
buscar bootstrap
iniciar polling IQ
```

Nunca executar os dois fluxos simultaneamente.

---

## Isolamento obrigatório

Quando:

```text
providerMode === "IQ_OPTION"
```

não executar chamadas para:

```text
polarium/browser-bridge/status
market/chart/series Polarium
market/chart?active_id=
```

Quando:

```text
providerMode === "POLARIUM"
```

não executar chamadas para:

```text
iq-option/assets
iq-option/candles
```

salvo conexão/status explicitamente necessários.

---

## Hook Polarium

Revisar:

```text
useRealCandles
```

Adicionar parâmetro de ativação:

```ts
enabled: boolean
```

Quando `enabled=false`:

- não criar intervalo;
- não fazer fetch;
- cancelar request em andamento;
- não alterar candles;
- não atualizar contexto;
- não selecionar active_id;
- limpar timers no cleanup.

Uso esperado:

```ts
useRealCandles({
  enabled: providerMode === "POLARIUM"
})
```

---

## IQ Option Assets

Fluxo:

1. provider muda para IQ Option;
2. cancelar contexto Polarium;
3. consultar status IQ;
4. conectar se necessário;
5. consultar `/assets?market_type=OTC`;
6. popular lista;
7. selecionar automaticamente primeiro ativo aberto quando não houver seleção válida;
8. carregar candles.

---

## Recuperação de erro 502

O endpoint de assets pode falhar temporariamente por conexão one-shot.

Implementar retry controlado:

```text
máximo 3 tentativas
backoff: 1s, 2s, 4s
uma request por vez
```

Retry apenas para erros temporários:

```text
502
503
504
PROVIDER_CONNECTION_FAILED
WORKER_TIMEOUT
```

Não fazer retry infinito.

Em sucesso:

- limpar erro;
- preencher ativos;
- selecionar primeiro ativo válido;
- iniciar bootstrap.

Em falha final:

- mostrar botão `Tentar novamente`;
- preservar provider selecionado;
- não iniciar Polarium automaticamente;
- não mostrar mensagem de abrir Polarium.

---

## Connect antes dos assets

Verificar se o provider está conectado.

Quando necessário:

```text
POST /iq-option/connect
```

antes de:

```text
GET /iq-option/assets
```

Evitar chamadas simultâneas de connect/assets.

Adicionar lock ou promise compartilhada:

```text
iqConnectPromise
```

para impedir múltiplos connects concorrentes.

---

## Seleção automática

Após assets carregados:

- preservar símbolo atual se ainda existir e estiver aberto;
- caso contrário, preferir `EURUSD-OTC` quando realmente disponível;
- caso contrário, selecionar o primeiro OTC aberto.

Não deixar:

```text
Nenhum ativo OTC disponível
```

se a API retornou ativos válidos.

---

## Contexto visual

No modo IQ Option:

- ocultar `Seguir Polarium`;
- não mostrar textos sobre Browser Bridge;
- não mostrar `Aguardando séries reais no CandleStore` com instrução de abrir Polarium;
- mostrar loading específico:

```text
Conectando à fonte IQ Option...
Carregando ativos OTC...
Carregando candles...
```

Em erro:

```text
Não foi possível carregar os ativos IQ Option.
[Tentar novamente]
```

---

## Estado ao trocar provider

### Polarium → IQ Option

- abortar requests Polarium;
- limpar timers Polarium;
- limpar active_id;
- limpar Follow Polarium;
- carregar IQ assets;
- selecionar símbolo;
- carregar candles IQ.

### IQ Option → Polarium

- abortar requests IQ;
- limpar timers IQ;
- limpar symbol IQ;
- ativar hook Polarium;
- restaurar contexto Polarium real.

---

## Controle de concorrência

Implementar:

```text
AbortController
request sequence
provider context token
in-flight lock
```

Resposta deve ser descartada quando o provider atual não corresponder ao provider que iniciou a requisição.

---

## Backend

Revisar se `/assets` pode garantir conexão internamente.

Comportamento aceitável:

```text
assets request
→ provider desconectado
→ connect controlado
→ list assets
```

Ou manter connect separado, desde que o frontend faça a sequência corretamente.

Não criar múltiplos subprocessos concorrentes.

---

## Testes obrigatórios

Criar testes para:

1. IQ selecionada desativa polling Polarium;
2. Polarium selecionada desativa polling IQ;
3. troca de provider cancela requests anteriores;
4. 502 de assets gera retry;
5. retry máximo de três;
6. backoff controlado;
7. sucesso na segunda tentativa;
8. ativos populam seletor;
9. EURUSD-OTC é selecionado quando disponível;
10. primeiro ativo aberto é fallback;
11. erro final mostra retry manual;
12. erro IQ não ativa Polarium;
13. texto Browser Bridge não aparece em IQ;
14. Seguir Polarium oculto em IQ;
15. connect não ocorre em duplicidade;
16. assets não ocorre em duplicidade;
17. resposta atrasada Polarium descartada;
18. resposta atrasada IQ descartada;
19. bootstrap começa após ativo selecionado;
20. polling IQ começa depois do bootstrap;
21. M1/M5/M15;
22. suíte completa;
23. build.

---

## Validação real

1. subir backend;
2. subir frontend;
3. abrir Network;
4. selecionar IQ Option;
5. confirmar que chamadas Polarium param;
6. confirmar connect IQ;
7. confirmar assets;
8. se ocorrer 502, confirmar retry;
9. confirmar lista com 14 ativos;
10. confirmar seleção automática;
11. confirmar bootstrap;
12. confirmar polling IQ;
13. trocar para Polarium;
14. confirmar IQ polling cancelado;
15. voltar para IQ;
16. confirmar recuperação completa.

---

## Critério de sucesso

No modo IQ Option:

```text
zero chamadas Polarium
assets recuperados após erro temporário
ativo selecionado
candles carregados
polling IQ ativo
```

No modo Polarium:

```text
zero polling IQ
hook Polarium ativo
```

---

## Entrega obrigatória

1. Objetivo.
2. Causa raiz.
3. Isolamento implementado.
4. Hook Polarium condicionado.
5. Fluxo IQ Option.
6. Connect controlado.
7. Retry de assets.
8. Seleção automática.
9. Cancelamento de requests.
10. Contexto visual.
11. Arquivos criados.
12. Arquivos modificados.
13. Testes específicos.
14. Suíte completa.
15. Build.
16. Como testar.
17. Riscos.
18. git status.
19. git diff --stat.
20. Sugestão de commit.

Mensagem sugerida:

```text
fix(market-chart): isolate providers and recover IQ assets
```

---

## Regra final

Não fazer commit.

Não fazer push.

Não alterar credenciais.

Não instalar iqoptionapi na .venv principal.

Não consultar saldo.

Não executar ordens.

Não manter Polarium e IQ Option ativos simultaneamente.