# SPRINT V4.5.8 — IQ OPTION SAFE ASSET DISCOVERY PATH PROBE

## Objetivo

Encontrar e comprovar o menor caminho read-only capaz de descobrir ativos utilizáveis da IQ Option sem depender da chamada completa:

```python
client.get_all_open_time()
```

A Sprint deve priorizar auditoria e provas reais.

Não modificar o frontend.

Não alterar o fluxo de candles.

Não criar nova arquitetura.

---

## Contexto comprovado

A Sprint V4.5.7 comprovou:

- conexão IQ Option funciona;
- candles OTC e REGULAR funcionam;
- `get_all_open_time()` não retorna dentro do timeout;
- o método trava em threads internas da biblioteca;
- a parte digital tenta acessar dados que retornam tarde ou `None`;
- worker encerra em aproximadamente 6 segundos;
- provider retorna `PROVIDER_REQUEST_FAILED`;
- API responde 502;
- `response.assets` não é produzido;
- `get_all_ACTIVES_OPCODE()` retorna aproximadamente 382 símbolos, mas não informa sozinho se estão abertos ou negociáveis.

---

## Hipótese a investigar

A chamada agregada `get_all_open_time()` pode estar bloqueada apenas por uma de suas ramificações internas, especialmente a descoberta digital.

Pode existir um caminho menor e read-only para obter:

- ativos binários/turbo;
- status de abertura;
- identificação OTC ou REGULAR;
- catálogo necessário para alimentar `response.assets`;

sem aguardar a ramificação digital travada.

Nenhuma hipótese deve ser tratada como fato antes dos testes.

---

## Escopo da auditoria

Inspecionar no ambiente isolado:

```text
.jarvis_cache/iq_option_probe_venv
```

e no código instalado da:

```text
iqoptionapi 7.1.1
```

Localizar a implementação real de:

```python
get_all_open_time()
```

Mapear:

1. threads iniciadas;
2. funções chamadas por cada thread;
3. joins sem timeout;
4. parte binary;
5. parte turbo;
6. parte digital;
7. estruturas internas preenchidas antes do bloqueio;
8. existência de métodos públicos ou internos read-only capazes de consultar cada categoria separadamente.

---

## Regras de segurança

É proibido chamar:

- buy
- buy_multi
- buy_digital_spot
- sell_option
- buy_order
- close_position
- change_balance
- get_balance
- get_positions
- get_orders
- qualquer método de execução ou consulta financeira equivalente.

Subscriptions passivas necessárias para leitura podem ser analisadas, desde que:

- nenhuma ordem seja criada;
- nenhum saldo seja consultado;
- nenhuma posição seja consultada;
- o Runtime Guard permaneça ativo.

Não expor credenciais nos logs ou relatório.

---

## Fase 1 — Inspeção estática

Sem alterar a biblioteca instalada, apresentar:

1. arquivo e linhas de `get_all_open_time()`;
2. funções chamadas internamente;
3. onde são criadas threads;
4. onde ocorre `join()` sem timeout;
5. qual thread acessa `get_digital_underlying_list_data()`;
6. quais estruturas são retornadas para binary, turbo e digital;
7. quais métodos podem ser chamados separadamente.

Não editar arquivos dentro do ambiente isolado.

Não aplicar monkey patch permanente.

---

## Fase 2 — Probes read-only isolados

Executar probes controlados no worker ou em script temporário fora do código de produção.

Cada probe deve possuir timeout externo.

Testar separadamente, quando tecnicamente disponível:

1. descoberta binary;
2. descoberta turbo;
3. descoberta digital;
4. catálogo/opcode;
5. qualquer cache interno já preenchido após conexão;
6. método menor identificado na inspeção estática.

Para cada probe registrar:

- nome exato do método;
- duração;
- retornou ou timeout;
- tipo do payload;
- quantidade de símbolos;
- presença de status open;
- presença de identificação OTC;
- presença de identificação REGULAR;
- amostra sanitizada de até 5 símbolos;
- se depende de subscription passiva.

Não executar probes concorrentes até provar que cada chamada isolada é segura.

---

## Fase 3 — Comparação com candles

Para uma pequena amostra de símbolos encontrados, validar somente leitura:

OTC:

```text
EURUSD-OTC
```

REGULAR:

```text
EURUSD
```

e até três outros símbolos, caso descobertos.

Verificar:

- se o símbolo é aceito pelo endpoint de candles;
- se retorna candles;
- se o mercado atribuído está correto.

Não usar sucesso de candles como substituto automático para status `open`.

Registrar claramente a diferença entre:

- símbolo existente;
- símbolo com candles;
- símbolo oficialmente identificado como aberto.

---

## Critério para uma solução candidata

Uma solução só pode ser recomendada se:

1. retornar dentro do timeout;
2. não chamar métodos proibidos;
3. não depender de alteração na `.venv` principal;
4. não modificar a biblioteca instalada;
5. identificar OTC e REGULAR de forma comprovável;
6. fornecer status de abertura ou declarar claramente que ele não existe;
7. não misturar catálogo com ativos abertos;
8. não interromper o worker persistente;
9. não afetar candles;
10. não exigir alteração no frontend.

---

## Alteração de produção

Por padrão, esta Sprint é de auditoria e probe.

Somente aplicar uma correção de produção se existir um caminho claramente comprovado, mínimo e reversível.

Caso aplique correção:

- alterar somente o worker/provider necessário;
- preservar `get_all_open_time()` como referência ou fallback seguro, se apropriado;
- nunca deixar uma thread interna sem limite bloquear o worker;
- retornar erro sanitizado;
- não retornar catálogo como se fosse lista de ativos abertos;
- não tocar em `MarketChart.tsx`;
- não tocar em `RealCandleChart`;
- não alterar endpoints;
- não criar provider novo.

Se não houver caminho comprovado, não improvisar implementação.

---

## Testes obrigatórios caso haja alteração

Executar testes focados:

```bash
.venv/bin/python -m pytest tests/market/providers -q
```

Executar suíte completa:

```bash
.venv/bin/python -m pytest -q
```

Executar build:

```bash
cd frontend
npm run build
```

Retornar à raiz após o build:

```bash
cd ..
```

Também realizar validação real read-only:

- conexão;
- assets OTC;
- assets REGULAR;
- candles OTC;
- candles REGULAR.

---

## Entrega esperada

Entregar relatório com:

1. causa interna detalhada de `get_all_open_time()`;
2. arquivo e linhas da biblioteca auditada;
3. tabela dos probes realizados;
4. duração de cada probe;
5. quantidade de símbolos retornados;
6. presença ou ausência de status open;
7. presença ou ausência de classificação OTC/REGULAR;
8. solução candidata comprovada ou declaração de que nenhuma foi encontrada;
9. arquivos alterados;
10. explicação exata da correção, caso aplicada;
11. resultado de assets OTC;
12. resultado de assets REGULAR;
13. resultado de candles OTC;
14. resultado de candles REGULAR;
15. testes focados;
16. suíte completa;
17. build;
18. `git status --short`;
19. `git diff --stat`;
20. riscos restantes;
21. sugestão de commit somente se houver arquivos alterados.

Não fazer commit.

Não fazer push.

Não alterar arquivos fora do escopo.

Não ocultar timeout, payload vazio ou resultado inconclusivo.