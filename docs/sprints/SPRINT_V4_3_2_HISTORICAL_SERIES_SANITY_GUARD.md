# Friday Trade — Sprint V4.3.2

# Historical Series Sanity Guard

## Status

PLANNED

---

## Objetivo

Implementar uma camada de diagnóstico e proteção semântica para impedir que candles órfãos, antigos, artificiais ou incompatíveis com a série sejam carregados no gráfico ou persistidos futuramente.

A auditoria V4.3.1 confirmou que a série:

```text
active_id = 76
raw_size = 60
```

possui:

```text
count = 206
first_timestamp = 100
last_timestamp = 1783731940
price_min = 1.0
price_max = 1.3
```

Os candles passam nas regras matemáticas:

```text
low <= open <= high
low <= close <= high
high >= low
```

Porém são semanticamente incompatíveis com a série atual.

Esses candles antigos e fora de contexto distorcem a escala do Lightweight Charts e produzem velas gigantes.

---

## Evidência confirmada

Dados reais da auditoria:

```text
series_count = 4
total_candles = 224
valid_candles = 224
invalid_candles = 0
```

Série problemática:

```text
active_id = 76
raw_size = 60
count = 206
first_timestamp = 100
last_timestamp = 1783731940
price_min = 1.0
price_max = 1.3
low_min = 1.0
high_max = 1.3
open_min = 1.1
open_max = 1.201705
close_min = 1.162145
close_max = 1.201425
```

Conclusão:

```text
candles estruturalmente válidos
mas semanticamente órfãos ou pertencentes a teste/contexto antigo
```

---

## Objetivos da Sprint

1. Detectar candles semanticamente suspeitos.
2. Descobrir a origem provável.
3. Impedir novos registros suspeitos.
4. Impedir restauração de candles suspeitos.
5. Não apagar automaticamente nenhum candle existente.
6. Expor diagnóstico sanitizado.
7. Preparar futura limpeza controlada.

---

## Não apagar dados nesta Sprint

Esta Sprint não deve remover registros existentes do SQLite.

Não deve executar `DELETE`.

Não deve limpar séries automaticamente.

Não deve modificar candles persistidos.

A limpeza ficará para Sprint própria:

```text
V4.3.3 — Controlled Candle Repair
```

---

## Revisão obrigatória

Revisar:

```text
app/market/store/candle_store.py
app/market/persistence/
app/market/runtime.py
app/market/runtime_feed.py
app/market/runtime_simulator.py
app/market/browser_bridge.py
app/market/pipeline/
tests/market/
```

Procurar qualquer origem de candles com:

```text
start_timestamp = 100
timestamps pequenos
preços 1.0 / 1.1 / 1.2 / 1.3
fixtures
mocks
simuladores
dados de teste
bootstrap manual
runtime feed
seed
snapshot sanitizado
```

Executar também buscas no repositório:

```bash
grep -R "start_timestamp.*100" -n app tests docs frontend tools
grep -R "\"from\".*100" -n app tests docs frontend tools
grep -R "1\.3" -n tests app docs
grep -R "1\.0" -n tests app docs
```

Não alterar arquivos apenas por coincidência; comprovar a origem.

---

## Regras de sanity

Criar um serviço ou política explícita:

```text
CandleSanityGuard
```

ou nome equivalente.

A camada deve receber um candle normalizado e o contexto da série.

---

## Regra 1 — Timestamp mínimo absoluto

Por padrão, candle de mercado real não deve possuir timestamp Unix extremamente baixo.

Criar configuração segura:

```text
market_candle_min_timestamp
```

Sugestão inicial:

```text
1500000000
```

equivalente aproximadamente a 2017.

Candles abaixo do limite devem ser classificados como:

```text
TIMESTAMP_BELOW_MINIMUM
```

Não usar data atual hardcoded em testes.

---

## Regra 2 — Timestamp futuro

Rejeitar ou marcar candle com timestamp muito à frente do relógio atual.

Criar tolerância configurável:

```text
market_candle_future_tolerance_seconds
```

Sugestão:

```text
300
```

Código:

```text
TIMESTAMP_IN_FUTURE
```

---

## Regra 3 — Distância temporal da série

Quando a série já possuir candles, detectar candle muito distante do conjunto atual.

Exemplo:

```text
últimos candles em 2026
novo candle em 1970
```

Código:

```text
TEMPORAL_ORPHAN
```

A regra deve considerar:

```text
raw_size
último timestamp
diferença máxima aceitável
```

Não rejeitar gaps normais de mercado.

Usar limite configurável e conservador.

---

## Regra 4 — Faixa de preço contextual

Para uma série já existente, calcular contexto robusto usando candles recentes:

```text
mediana de close
mediana de range
```

Detectar candle extremamente distante do contexto.

Não usar apenas média simples.

Não rejeitar volatilidade legítima com regra agressiva.

Código:

```text
PRICE_CONTEXT_OUTLIER
```

Essa regra deve ser conservadora e configurável.

Preferir diagnóstico antes de rejeição automática.

---

## Regra 5 — Range extremo

Detectar candle cujo range:

```text
high - low
```

seja desproporcional à mediana dos ranges recentes.

Código:

```text
EXTREME_RANGE_OUTLIER
```

Não usar percentual fixo universal sem contexto.

---

## Regra 6 — Estrutura matemática

Manter regras já existentes:

```text
high >= low
low <= open <= high
low <= close <= high
valores finitos
valores positivos
```

Códigos:

```text
HIGH_BELOW_LOW
OPEN_OUTSIDE_RANGE
CLOSE_OUTSIDE_RANGE
NON_FINITE_VALUE
NON_POSITIVE_PRICE
```

---

## Classificação

Cada avaliação deve retornar:

```text
accepted
suspicious
rejected
reasons
```

Estados:

```text
ACCEPTED
SUSPICIOUS
REJECTED
```

Política inicial:

### Rejeição obrigatória

```text
TIMESTAMP_BELOW_MINIMUM
TIMESTAMP_IN_FUTURE
HIGH_BELOW_LOW
OPEN_OUTSIDE_RANGE
CLOSE_OUTSIDE_RANGE
NON_FINITE_VALUE
NON_POSITIVE_PRICE
```

### Apenas suspeito inicialmente

```text
TEMPORAL_ORPHAN
PRICE_CONTEXT_OUTLIER
EXTREME_RANGE_OUTLIER
```

Candles suspeitos não devem entrar no gráfico até revisão, mas também não devem ser apagados do SQLite existente nesta Sprint.

---

## Integração com escrita

Antes de persistir novo candle:

```text
MarketPipeline
→ CandleStore
→ CandleSanityGuard
→ Persistence
```

Ou arquitetura equivalente que preserve o contrato atual.

Regras:

- candle rejeitado não deve ser persistido;
- candle rejeitado não deve alterar série;
- candle suspeito deve ser bloqueado do gráfico/runtime;
- registrar somente diagnóstico sanitizado;
- não expor OHLC completos em status.

Não escrever diretamente a partir do Browser Bridge.

---

## Integração com restore

Durante startup:

```text
SQLite
→ CandleSanityGuard
→ CandleStore
```

Candles rejeitados ou suspeitos devem:

- permanecer no SQLite nesta Sprint;
- não ser restaurados para o CandleStore;
- ser contabilizados;
- aparecer no relatório sanitizado.

Isso deve impedir que as velas gigantes voltem após restart.

---

## Status sanitizado

Criar:

```text
GET /api/v1/market/persistence/sanity-status
```

ou ampliar status existente com:

```text
market_candle_sanity
```

Campos:

```text
enabled
checked_on_restore
accepted_on_restore
suspicious_on_restore
rejected_on_restore

checked_on_write
accepted_on_write
suspicious_on_write
rejected_on_write

last_reason_code
last_active_id
last_raw_size
last_timestamp
last_checked_at

min_timestamp
future_tolerance_seconds
last_error_code
```

Não retornar OHLC completos.

---

## Endpoint de auditoria aprimorado

A auditoria existente deve passar a identificar:

```text
TIMESTAMP_BELOW_MINIMUM
TEMPORAL_ORPHAN
PRICE_CONTEXT_OUTLIER
EXTREME_RANGE_OUTLIER
```

Para cada registro suspeito retornar somente:

```text
active_id
raw_size
timestamp
reason
classification
```

Não retornar preços completos.

---

## Descoberta da origem

A Sprint deve entregar resposta objetiva:

```text
O candle timestamp=100 foi criado por:
- teste;
- simulador;
- runtime feed;
- fixture;
- seed;
- restore antigo;
- origem não confirmada.
```

Caso não seja possível provar, informar:

```text
ORIGIN_NOT_CONFIRMED
```

Não inventar a origem.

---

## Não alterar

Não alterar:

- Browser Bridge;
- Payload Adapter;
- frontend;
- RealCandleChart;
- Chart API pública;
- Indicator Engine;
- IA;
- execução;
- AutoTrade;
- Connector;
- OAuth.

---

## Não implementar

Não implementar:

- limpeza automática;
- delete no SQLite;
- reparo de OHLC;
- interpolação;
- candles sintéticos;
- troca de preços;
- fallback externo;
- mapeamento de ativo;
- nome do ativo nesta Sprint;
- sinais;
- CALL;
- PUT.

O nome real do ativo será tratado em Sprint própria após a sanidade dos dados.

---

## Testes obrigatórios

Criar testes para:

1. timestamp `100` rejeitado;
2. timestamp abaixo do mínimo;
3. timestamp atual aceito;
4. timestamp futuro rejeitado;
5. candle matematicamente inválido;
6. candle com preço zero;
7. candle com NaN;
8. candle com infinito;
9. temporal orphan;
10. price context outlier;
11. extreme range outlier;
12. candle normal aceito;
13. write rejeitado não persiste;
14. write rejeitado não entra no Store;
15. restore rejeitado não entra no Store;
16. restore válido entra no Store;
17. SQLite existente não é apagado;
18. múltiplas séries;
19. status sanitizado;
20. auditoria retorna timestamp e razão;
21. auditoria não retorna OHLC completo;
22. configuração de timestamp mínimo;
23. configuração de tolerância futura;
24. restart sem restaurar candle órfão;
25. Chart API não recebe candle órfão;
26. gráfico não recebe série contaminada;
27. pipeline continua funcionando com candle válido;
28. persistência continua funcionando;
29. suíte completa sem regressão;
30. build frontend aprovado.

---

## Validação real obrigatória

Após implementação:

1. manter o SQLite atual, sem apagá-lo;
2. reiniciar backend;
3. consultar auditoria;
4. confirmar que timestamp `100` aparece como suspeito/rejeitado;
5. abrir `/market/chart/series`;
6. confirmar que a série restaurada não inclui candles órfãos;
7. abrir `/market-chart`;
8. confirmar que as velas verdes gigantes desapareceram;
9. abrir Polarium;
10. confirmar atualizações reais;
11. confirmar que candles válidos continuam sendo salvos.

Não limpar o banco nesta Sprint.

---

## Testes e build

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

.venv/bin/python -m pytest -q tests/market/persistence tests/market/store tests/market/pipeline

.venv/bin/python -m pytest -q

cd frontend
npm run build
```

---

## Entrega obrigatória

1. Objetivo.
2. Causa comprovada.
3. Origem do candle timestamp 100.
4. Arquitetura do Sanity Guard.
5. Regras implementadas.
6. Classificações.
7. Arquivos criados.
8. Arquivos modificados.
9. Integração com escrita.
10. Integração com restore.
11. Status sanitizado.
12. Auditoria aprimorada.
13. Candles bloqueados na restauração.
14. Candles bloqueados na escrita.
15. Segurança.
16. Testes criados.
17. Resultado dos testes específicos.
18. Resultado da suíte completa.
19. Resultado do build.
20. Como testar para o Renan.
21. Validação visual necessária.
22. Riscos conhecidos.
23. Débitos técnicos.
24. `git status --short`.
25. `git diff --stat`.
26. Sugestão de commit.

Mensagem sugerida:

```text
fix(market): guard candle series against semantic outliers
```

---

## Regra final

Não fazer commit.

Não fazer push.

Não apagar o SQLite.

Não corrigir valores automaticamente.

Não inventar origem.

Bloquear candles comprovadamente incompatíveis do runtime e da restauração.