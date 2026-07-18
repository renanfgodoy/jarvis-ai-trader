# SPRINT V4.8.2A — ASSET RANKING VISIBILITY HOTFIX

## Objetivo

Corrigir a regressão da lista de ativos causada pelo ranking de qualidade da Sprint V4.8.2.

Sintoma real observado:

- o dropdown mostra apenas o ativo selecionado;
- ao marcar “Mostrar todos os ativos”, a lista continua sem exibir corretamente os demais ativos;
- nenhum ativo aparece como bom no início da sessão;
- ativos não medidos ficam escondidos;
- a experiência impede navegar pelos pares para que sejam classificados.

A Sprint deve corrigir a visibilidade da lista sem remover o ranking dinâmico.

---

# Regra principal

O ranking deve:

```text
ordenar
→ agrupar
→ destacar
```

e não:

```text
eliminar todos os ativos ainda não medidos
```

Todos os ativos abertos retornados pela API devem continuar acessíveis.

---

# PARTE 1 — AUDITORIA

## 1. Validar assets reais

Confirmar:

```text
response.assets.length
```

para OTC e REGULAR.

Registrar:

- total recebido;
- total parsed;
- total presente em `iqAssets`;
- total com qualidade conhecida;
- total CHECKING;
- total EXCELLENT;
- total GOOD;
- total LIMITED;
- total STALE;
- total NO_DATA.

---

## 2. Auditar cadeia frontend

Auditar:

```text
iqAssets
→ feedQualityByContext
→ rankedAssets
→ recommendedAssets
→ checkingAssets
→ limitedAssets
→ unavailableAssets
→ visibleAssets
→ select options
```

Registrar o tamanho de cada grupo.

---

## 3. Auditar “Mostrar todos”

Confirmar que:

```text
showAllAssets = false
```

mostra:

- EXCELLENT;
- GOOD;
- ativo atual;
- CHECKING em seção secundária acessível, caso ainda não existam recomendados suficientes.

Confirmar que:

```text
showAllAssets = true
```

mostra todos os ativos da API, incluindo:

- CHECKING;
- LIMITED;
- STALE;
- NO_DATA.

Não permitir que `showAllAssets=true` resulte em lista vazia se `iqAssets.length > 0`.

---

# PARTE 2 — NOVA REGRA DE VISIBILIDADE

## 4. Lista padrão

No início da sessão, enquanto poucos ativos foram medidos:

### Se existem EXCELLENT/GOOD

Mostrar primeiro:

```text
RECOMENDADOS
```

Depois:

```text
AINDA NÃO AVALIADOS
```

com ativos CHECKING.

### Se não existem EXCELLENT/GOOD

Mostrar:

```text
AINDA NÃO AVALIADOS
```

com todos os ativos CHECKING.

Nunca mostrar apenas o ativo atual quando existem outros ativos abertos.

---

## 5. Mostrar todos

Ao ativar:

```text
Mostrar todos os ativos
```

mostrar grupos:

```text
RECOMENDADOS
```

```text
AINDA NÃO AVALIADOS
```

```text
LIMITADOS
```

```text
INDISPONÍVEIS
```

Todos os ativos devem continuar selecionáveis, exceto se houver motivo técnico explícito para desabilitar.

---

## 6. Ativo atual

O ativo selecionado deve sempre permanecer visível.

Mas ele não deve ser a única opção quando `iqAssets.length > 1`.

---

# PARTE 3 — CLASSIFICAÇÃO INICIAL

## 7. CHECKING

Ativos nunca visitados devem receber:

```text
CHECKING
```

e não:

```text
NO_DATA
```

Não considerar ausência de métrica como feed ruim.

---

## 8. Sem ranking conhecido

A ausência de métricas não pode reduzir a lista principal a zero.

Usar rótulo humano:

```text
Verificando
```

ou:

```text
Ainda não avaliado
```

---

# PARTE 4 — PRODUTO

## 9. Ranking como ordenação

A lista deve ordenar por:

1. EXCELLENT;
2. GOOD;
3. CHECKING;
4. LIMITED;
5. STALE;
6. NO_DATA.

Não excluir CHECKING por padrão quando isso impedir a navegação.

---

## 10. Recomendação

A Friday pode sugerir os melhores já medidos, mas deve permitir explorar os demais para construir o ranking da sessão.

Exemplo:

```text
2 recomendados
70 ainda não avaliados
```

---

# PARTE 5 — TESTES

## 11. Frontend

Adicionar testes para:

1. 72 assets + zero métricas não produz lista com 1 item;
2. zero EXCELLENT/GOOD mostra CHECKING;
3. ativo atual permanece visível;
4. `showAllAssets=false` mantém navegação possível;
5. `showAllAssets=true` mostra todos os assets;
6. CHECKING não vira NO_DATA;
7. grupos aparecem na ordem correta;
8. selecionar ativo CHECKING funciona;
9. após medir um ativo, ele muda de grupo;
10. qualidade de um ativo não remove os demais;
11. troca de timeframe usa ranking independente;
12. lista REGULAR permanece funcional.

Executar:

```bash
.venv/bin/python -m pytest tests/frontend -q
```

---

## 12. Suíte completa e build

```bash
.venv/bin/python -m pytest -q
```

```bash
cd frontend
npm run build
cd ..
```

---

# PARTE 6 — VALIDAÇÃO REAL

## 13. Sessão fria

Após reload:

- OTC deve mostrar vários ativos;
- a maioria pode aparecer como “Verificando”;
- o ativo atual deve estar selecionado;
- não pode existir somente uma opção.

---

## 14. Após medição

Visitar:

```text
EURUSD-OTC
USDJPY-OTC
EURJPY-OTC
```

Aguardar janela mínima.

Confirmar:

- ativos medidos mudam de grupo;
- demais continuam visíveis como CHECKING;
- lista recomendada cresce;
- nenhum ativo desaparece sem motivo.

---

## 15. Mostrar todos

Confirmar que a quantidade visível se aproxima do total retornado pela API.

---

# ENTREGA ESPERADA

Entregar:

1. causa raiz;
2. total de assets da API;
3. tamanho de cada grupo antes;
4. ponto onde ativos eram descartados;
5. correção aplicada;
6. nova regra de visibilidade;
7. comportamento sem recomendados;
8. comportamento com recomendados;
9. comportamento de Mostrar todos;
10. arquivos modificados;
11. testes frontend;
12. suíte completa;
13. build;
14. validação OTC;
15. validação REGULAR;
16. git status;
17. git diff stat;
18. sugestão de commit.

Não alterar backend sem causa comprovada.

Não remover FeedQualityTracker.

Não criar scanner em massa.

Não fazer commit.

Não fazer push.