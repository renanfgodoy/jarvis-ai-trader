# SPRINT V5.4 — POLARIUM SESSION CONTEXT ARCHITECTURE

## Objetivo

Eliminar estados duplicados relacionados ao contexto da sessão Polarium.

A Friday deve possuir apenas uma fonte oficial de verdade (Single Source of Truth) para representar o estado vivo da sessão.

Esta Sprint é exclusivamente arquitetural.

Não implementar:

- Scanner
- Estratégias
- IA
- CALL
- PUT
- Entradas automáticas
- Ordens
- Saldo
- Conta
- Portfolio

---

# Problema

Atualmente existem diversos estados independentes.

Exemplos:

- latest_active_id
- latest_symbol
- iqSymbol
- dropdown selecionado
- gráfico
- Strategy Engine
- Feed Quality
- MarketChart

Cada um pode ficar diferente.

Isso gera bugs como:

- gráfico mostra um ativo
- cabeçalho mostra outro
- Strategy analisa outro
- dropdown continua antigo

---

# Nova Arquitetura

Criar um único objeto oficial.

```
PolariumSessionContext
```

Toda a aplicação deverá ler esse contexto.

Nunca manter estado duplicado.

---

# MODELO

Criar:

```ts
interface PolariumSessionContext {

    provider

    websocket_state

    authenticated

    connection_status

    active_id

    symbol

    display_name

    market_type

    raw_size

    timeframe

    latest_price

    feed_status

    last_update

}
```

Adicionar apenas campos realmente necessários.

Não incluir estratégia.

---

# RESPONSABILIDADE

O Session Context será atualizado somente pelo Runtime Polarium.

Nenhum componente visual poderá alterar esse contexto.

---

# FLUXO

```
Market WebSocket

↓

Runtime

↓

Session Context

↓

Frontend
```

Nunca:

```
Runtime

↓

MarketChart

↓

Strategy

↓

Dropdown
```

Tudo passa pelo Session Context.

---

# COMPONENTES QUE DEVEM LER O CONTEXTO

- MarketChart

- RealCandleChart

- Feed Quality

- Header

- Dropdown

- Friday Strategy

- Indicador de conexão

Todos devem consumir o mesmo objeto.

---

# MUDANÇA DE ATIVO

Quando o Runtime detectar:

```
active_id diferente
```

Executar obrigatoriamente:

1.

Atualizar:

```
active_id
```

↓

2.

Resolver:

```
symbol
```

↓

3.

Atualizar:

```
display_name
```

↓

4.

Atualizar:

```
market_type
```

↓

5.

Atualizar:

```
raw_size
```

↓

6.

Atualizar:

```
timeframe
```

↓

7.

Atualizar:

```
latest_price
```

↓

8.

Publicar novo Session Context

Nenhum componente poderá manter o contexto antigo.

---

# REGRA DE SINCRONIZAÇÃO

Todos os componentes deverão responder ao mesmo evento.

Não permitir:

- Header atualizado antes do gráfico

- Strategy atualizada depois

- Dropdown antigo

- Feed antigo

Toda mudança deve acontecer a partir do Session Context.

---

# REGRA PARA SÍMBOLO

Nunca usar fallback:

```
EURUSD
```

Se não resolver:

```
ATIVO NÃO IDENTIFICADO
```

Bloquear:

- análise

- Strategy

- recomendações

---

# REGRA PARA PROVIDER

O Session Context deverá informar claramente:

```
POLARIUM
```

ou

```
IQ OPTION
```

Nunca misturar providers.

---

# REGRA PARA TIMEFRAME

Toda troca:

```
60

↓

300

↓

900
```

deverá atualizar o mesmo Session Context.

Não criar contexto paralelo.

---

# REGRA PARA PREÇO

O último preço observado deverá ficar apenas no Session Context.

Nenhum componente deverá guardar latest_price próprio.

---

# EVENTOS

Criar evento único.

Exemplo:

```
POLARIUM_SESSION_UPDATED
```

Todos os componentes deverão ouvir apenas esse evento.

---

# FRONTEND

Remover estados duplicados quando possível.

O MarketChart deverá consumir apenas o Session Context.

---

# TESTES

Adicionar testes para:

- troca de active_id

- troca de símbolo

- troca de timeframe

- troca de provider

- atualização de preço

- atualização do gráfico

- atualização do Strategy

- atualização do Header

- atualização do Dropdown

- atualização do Feed Quality

- ativo não identificado

- mudança simultânea

---

# BUILD

Executar:

pytest

npm run build

---

# GIT

Não executar:

git add

commit

push

---

# ENTREGA

O Forge deverá informar obrigatoriamente:

1. Arquivos criados

2. Arquivos modificados

3. Arquitetura final

4. Session Context criado

5. Fluxo completo

6. Componentes migrados

7. Estados removidos

8. Testes

9. Build

10. Performance

11. CPU

12. Memória

13. git status

14. git diff

15. Riscos

16. Próximas etapas

Não implementar scanner.

Não implementar IA.

Não implementar estratégia.

Não alterar Runtime IQ.

Não criar estados duplicados.

Não fazer commit.

Não fazer push.