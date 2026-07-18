# FRIDAY AI TRADER

# SPRINT V5.7A — ATOMIC ASSET SWITCH

## Status

PLANEJADA

---

# 1. Objetivo

Eliminar a condição de corrida observada durante a troca de ativos da Polarium, garantindo que a Friday publique uma nova seleção apenas quando o contexto do ativo estiver completo.

Esta é a primeira Sprint de correção funcional baseada em evidências reais.

---

# 2. Evidências comprovadas

Validação real demonstrou que:

- Parser funciona.
- Bootstrap funciona.
- CandleStore funciona.
- History Count funciona.
- Readiness funciona.
- Chart API funciona.
- Frontend recebe atualização.

O diagnóstico identificou repetidamente:

```
RACE_CONDITION

Historical response did not match current visible context.
```

Também foi observado que existem estados transitórios contendo:

```
active_id válido
raw_size = None
bucket = None
```

Esses estados geram seleções intermediárias que posteriormente são descartadas.

---

# 3. Objetivo técnico

Transformar a troca de ativo em uma operação atômica.

O runtime somente poderá publicar uma nova seleção quando existir um contexto consistente contendo:

- active_id
- symbol
- raw_size
- bucket correspondente

Todos válidos.

---

# 4. Arquitetura desejada

Atual:

```
active_id
↓

publica seleção

↓

raw_size chega depois

↓

bootstrap

↓

race
```

Novo fluxo:

```
active_id

+

raw_size

+

bucket

↓

contexto completo

↓

publicar seleção

↓

bootstrap

↓

chart
```

---

# 5. Escopo permitido

Modificar apenas a orquestração da troca de ativo.

É permitido alterar:

- runtime Polarium
- Session Context
- Asset Switch

Somente para tornar a troca atômica.

---

# 6. Fora de escopo

Não alterar:

- Parser
- CandleStore
- BootstrapRequestFactory
- HistoricalBootstrapManager
- Readiness
- Chart API
- Frontend
- Scanner
- Ranking
- IA
- Estratégia
- CALL
- PUT
- Backtest
- Layout
- CDP

---

# 7. Regras obrigatórias

Nunca publicar seleção quando:

- active_id ausente
- raw_size ausente
- bucket inexistente

Não iniciar bootstrap em contexto parcial.

Não gerar seleção intermediária.

Não substituir bucket válido por bucket nulo.

---

# 8. URL oficial

Utilizar como URL oficial da Polarium:

```
https://trade.polariumbroker.com/traderoom
```

Substituir referências antigas ao domínio raiz quando aplicável ao CDP.

---

# 9. Testes obrigatórios

Adicionar testes para:

- troca normal de ativo;
- troca rápida entre ativos;
- resposta atrasada;
- raw_size chegando depois;
- ausência de race condition;
- bootstrap iniciado apenas após contexto completo;
- bucket nunca regressa para None;
- regressão M1 inexistente;
- regressão M5 inexistente;
- regressão M15 inexistente.

---

# 10. Validação automatizada

Executar:

python -m pytest tests/market/providers -v

Depois:

python -m pytest -v

Executar:

npm run build

---

# 11. Validação real

Backend CDP

Frontend

Trocar repetidamente:

EURUSD-OTC

↓

XAUUSD-OTC

↓

BTCUSD-OTC

↓

EURUSD-OTC

Confirmar:

- nenhuma categoria RACE_CONDITION;
- nenhuma seleção com raw_size=None;
- bootstrap sempre iniciado após contexto completo;
- gráfico atualizado corretamente.

---

# 12. Critério de conclusão

A Sprint somente poderá ser concluída quando:

- RACE_CONDITION desaparecer dos relatórios;
- bucket nunca voltar para None durante troca válida;
- bootstrap ocorrer apenas uma vez por seleção;
- gráfico permanecer consistente.

---

# 13. Entrega obrigatória

Objetivo

Arquitetura alterada

Arquivos modificados

Causa raiz

Correção aplicada

Testes adicionados

Resultado dos testes

Resultado da suíte completa

Resultado do build

Validação real

git status

git diff

Riscos

Próximos passos

Sugestão de commit

---

# 14. Git

Não executar:

git add

git commit

git push

sem autorização explícita do Renan.

---

# 15. Sugestão de commit

fix(polarium): make asset switch atomic before bootstrap