# Friday Trade — Sprint V4.5.3

# IQ Option Series Integrity

## Status

PLANNED

---

## Objetivo

Corrigir a integridade da série IQ Option exibida no gráfico do Friday Trade.

A conexão, listagem de ativos, bootstrap e polling já funcionam.

O problema atual é visual e de consistência da série:

```text
EURUSD-OTC M1
→ 504 candles
→ dois grupos de preço muito distantes
→ gráfico comprimido e distorcido
```

No print real, parte da série aparece próxima de:

```text
0.98
```

e outra parte próxima de:

```text
1.12
```

Isso não deve ocorrer dentro da mesma série contínua sem validação explícita.

---

## Escopo

Investigar e corrigir somente:

- identidade da série;
- ordenação;
- deduplicação;
- mistura entre histórico/polling;
- mistura entre providers;
- mistura entre símbolos;
- mistura entre timeframes;
- persistência/restore incorreto;
- contexto visual da UI.

Não alterar:

- conexão IQ Option;
- worker isolado;
- credenciais;
- Runtime Guard;
- endpoints de ordem;
- sinais;
- IA;
- indicadores;
- estratégias.

---

## Evidência atual

Frontend:

```text
provider = IQ_OPTION
symbol = EURUSD-OTC
raw_size = 60
candles = 504
```

Problemas observados:

1. dois blocos de preço incompatíveis;
2. gráfico comprimido;
3. texto `504 de 100`;
4. botão `Seguir Polarium` ainda visível;
5. painel já está em seleção manual IQ Option.

---

## Diagnóstico obrigatório

Antes de corrigir, identificar a origem exata dos candles incompatíveis.

Verificar separadamente:

```text
worker response
provider normalization
CandleStore
SQLite restore
Chart API
frontend merge
RealCandleChart input
```

Para a série:

```text
provider = IQ_OPTION
symbol = EURUSD-OTC
raw_size = 60
```

Calcular:

```text
count
first_timestamp
last_timestamp
distinct_timestamps
duplicate_timestamps
timestamps_out_of_order
price_min
price_max
largest_candle_range
largest_price_gap_between_consecutive_closes
distinct_providers
distinct_symbols
distinct_raw_sizes
```

---

## Não assumir a causa

Não concluir automaticamente que é:

- SQLite;
- Polarium;
- frontend;
- worker;
- polling.

Comprovar a etapa onde ocorre a contaminação.

---

## Identidade obrigatória da série

Toda operação de Store, persistência, Chart API e frontend deve usar:

```text
provider + symbol + raw_size
```

Para cada candle:

```text
provider = IQ_OPTION
symbol = EURUSD-OTC
raw_size = 60
```

Nunca misturar com:

```text
POLARIUM + active_id 76
```

Nunca usar apenas:

```text
raw_size
timestamp
active_id
```

como identidade suficiente para IQ Option.

---

## Chave de candle

Deduplicação deve considerar:

```text
provider + symbol + raw_size + start_timestamp
```

Candles com o mesmo timestamp dentro da mesma série:

- atualizam o registro existente;
- não criam duplicata.

Candles com mesmo timestamp de provider/símbolo diferente:

- permanecem em séries separadas.

---

## Ordenação

Antes de devolver candles na Chart API:

```text
ordenar por start_timestamp crescente
```

Antes de renderizar no frontend:

```text
ordenar por time crescente
```

Não permitir timestamps fora de ordem.

---

## Bootstrap e polling

Bootstrap:

```text
até 500/1000 candles
```

Polling:

```text
últimos 5 candles
```

Merge:

```text
histórico atual
+
resposta curta
→ merge por time
→ deduplica
→ ordena
→ limita somente no final
```

O polling nunca deve:

- substituir histórico por 5 candles;
- adicionar candle de outra série;
- adicionar candle antigo fora da janela;
- reintroduzir série persistida incorreta;
- reduzir a contagem.

---

## Validação de contexto no frontend

Antes de aplicar resposta:

```text
provider da resposta == provider selecionado
symbol da resposta == symbol selecionado
raw_size da resposta == timeframe selecionado
```

Caso contrário:

```text
descartar resposta
```

Implementar proteção contra respostas atrasadas de:

- outro ativo;
- outro timeframe;
- outro provider.

---

## Integridade de preço

Criar diagnóstico contextual conservador.

Para a mesma série:

1. calcular mediana dos closes recentes;
2. calcular mediana dos ranges recentes;
3. identificar clusters de preço incompatíveis;
4. detectar salto extremo entre candles consecutivos.

Não apagar ou corrigir automaticamente dados sem comprovação.

Classificações sugeridas:

```text
SERIES_CONTEXT_MISMATCH
PRICE_CLUSTER_SPLIT
EXTREME_CONSECUTIVE_GAP
PROVIDER_MISMATCH
SYMBOL_MISMATCH
TIMEFRAME_MISMATCH
DUPLICATE_TIMESTAMP
OUT_OF_ORDER_TIMESTAMP
```

---

## Persistência

Revisar schema e restore.

Confirmar que registros IQ Option persistem com:

```text
provider
symbol
active_id = NULL
raw_size
timestamp
```

Confirmar que registros antigos Polarium não são restaurados na série IQ Option.

Não apagar SQLite nesta Sprint.

Se houver registros contaminados:

- identificá-los;
- bloquear sua restauração;
- não deletar automaticamente;
- preparar futura limpeza controlada.

---

## Endpoint diagnóstico

Criar ou ampliar endpoint read-only:

```text
GET /api/v1/market/providers/iq-option/series-integrity
```

Parâmetros:

```text
symbol
raw_size
```

Resposta sanitizada:

```text
provider
symbol
raw_size
count
first_timestamp
last_timestamp
distinct_timestamps
duplicate_timestamps
timestamps_out_of_order
price_min
price_max
largest_range
largest_consecutive_gap
distinct_providers
distinct_symbols
distinct_raw_sizes
integrity_status
reason_codes
```

Não retornar todos os candles.

Não retornar credenciais.

---

## Correção do contador

Hoje aparece:

```text
504 de 100
```

Corrigir para algo coerente.

Opções aceitáveis:

```text
504 candles
```

ou:

```text
504 de 500
```

ou:

```text
504 carregados
```

Não manter limite antigo fixo de 100.

---

## Seguir Polarium

Quando:

```text
provider = IQ_OPTION
```

o controle:

```text
Seguir Polarium
```

deve:

- ficar oculto; ou
- ficar desabilitado com explicação clara.

Preferência:

```text
ocultar completamente
```

Também remover qualquer texto lateral:

```text
Seguindo Polarium
```

quando IQ Option estiver selecionada.

Modo correto:

```text
Seleção manual
```

---

## UI de contexto

Para IQ Option exibir:

```text
Provider: IQ Option
Ativo: EUR/USD OTC
Timeframe: M1
Candles: quantidade real
Fonte: IQ OPTION — READ ONLY
```

Nunca mostrar Active ID.

---

## RealCandleChart

Garantir:

- `setData()` apenas no bootstrap/troca real de série;
- `series.update()` em polling normal;
- escala baseada apenas na série selecionada;
- zoom/pan preservados;
- nenhum candle de contexto anterior permanece.

Em troca de símbolo/provider/timeframe:

```text
reset controlado
→ setData da nova série
```

---

## Testes obrigatórios

Criar testes para:

1. IQ Option e Polarium não colidem;
2. símbolos IQ Option não colidem;
3. timeframes não colidem;
4. timestamps ordenados;
5. timestamp duplicado atualizado;
6. resposta atrasada descartada;
7. provider errado descartado;
8. símbolo errado descartado;
9. timeframe errado descartado;
10. bootstrap + polling monotônico;
11. histórico não encolhe;
12. série não mistura dois clusters;
13. restore IQ Option separado;
14. restore Polarium separado;
15. diagnóstico de integridade;
16. endpoint sanitizado;
17. contador sem `de 100`;
18. ocultar Seguir Polarium;
19. contexto mostra seleção manual;
20. nome do ativo correto;
21. M1;
22. M5;
23. M15;
24. troca de ativo;
25. troca de provider;
26. zoom/pan preservados;
27. suíte completa;
28. build.

---

## Validação real

Após implementação:

1. subir backend;
2. subir frontend;
3. selecionar IQ Option OTC;
4. selecionar EUR/USD OTC;
5. selecionar M1;
6. abrir endpoint de integridade;
7. confirmar:
   - uma série;
   - um provider;
   - um símbolo;
   - um raw_size;
   - timestamps ordenados;
   - sem duplicatas;
8. confirmar gráfico sem dois blocos de preço;
9. observar polling;
10. confirmar candle atual atualizando;
11. trocar M5 e M15;
12. voltar M1;
13. confirmar que a série permanece limpa;
14. trocar para outro ativo;
15. confirmar ausência de mistura;
16. confirmar que Seguir Polarium não aparece.

---

## Critério de sucesso

A Sprint passa se:

```text
provider = IQ_OPTION
symbol = EURUSD-OTC
raw_size = 60
```

retornar e exibir:

- somente uma série;
- timestamps crescentes;
- sem duplicatas;
- sem candles Polarium;
- sem clusters incompatíveis;
- gráfico visualmente contínuo;
- contador correto;
- Seguir Polarium oculto;
- polling funcionando.

---

## Entrega obrigatória

1. Objetivo.
2. Causa raiz comprovada.
3. Etapa onde ocorreu a contaminação.
4. Arquitetura corrigida.
5. Identidade da série.
6. Deduplicação.
7. Ordenação.
8. Bootstrap/polling.
9. Persistência/restore.
10. Endpoint de integridade.
11. Correção visual.
12. Correção do contador.
13. Remoção do Seguir Polarium.
14. Arquivos criados.
15. Arquivos modificados.
16. Testes específicos.
17. Suíte completa.
18. Build.
19. Como testar.
20. Riscos.
21. Débitos técnicos.
22. `git status --short`.
23. `git diff --stat`.
24. Sugestão de commit.

Mensagem sugerida:

```text
fix(iq-option): enforce provider series integrity
```

---

## Regra final

Não fazer commit.

Não fazer push.

Não apagar SQLite automaticamente.

Não alterar conexão IQ Option.

Não instalar iqoptionapi na `.venv` principal.

Não consultar saldo.

Não executar ordens.

Comprovar a causa antes de remover ou bloquear dados.