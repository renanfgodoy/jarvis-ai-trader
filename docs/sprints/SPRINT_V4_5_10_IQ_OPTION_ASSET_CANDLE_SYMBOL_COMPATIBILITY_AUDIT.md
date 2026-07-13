# SPRINT V4.5.10 — IQ OPTION ASSET/CANDLE SYMBOL COMPATIBILITY AUDIT

## Objetivo

Descobrir e corrigir a incompatibilidade entre os símbolos retornados pela descoberta binary/turbo da IQ Option e os símbolos aceitos pelo fluxo real de candles.

Não criar nova arquitetura.

Não desfazer a descoberta de ativos implementada na V4.5.9.

Não alterar o frontend antes de comprovar onde o símbolo é perdido ou transformado incorretamente.

---

## Situação comprovada

Após a Sprint V4.5.9:

- `/assets?market_type=OTC` retorna múltiplos ativos;
- o dropdown OTC é preenchido;
- o usuário consegue selecionar outro ativo;
- o estado da tela muda corretamente;
- `EURUSD-OTC` continua retornando candles;
- ao selecionar `AMAZON-OTC`, a interface recebe 0 candles;
- o CandleStore mostra 0 candles;
- o gráfico permanece vazio;
- o título visual aparece como `AMA/ZON OTC`, indicando que um formatador de par cambial está sendo aplicado a símbolo corporativo.

O problema atual não é mais a listagem de ativos.

---

## Pergunta principal

O símbolo retornado em `response.assets` é realmente o mesmo identificador que deve ser enviado para:

- worker de candles;
- provider de candles;
- CandleStore;
- Chart API?

A resposta deve ser comprovada com payloads e chamadas reais.

---

## Escopo

Auditar a cadeia:

```text
get_all_init_v2()
→ asset_discovery
→ mapper
→ MarketAsset
→ response.assets
→ seleção React
→ requisição de candles
→ provider
→ worker
→ iqoptionapi.get_candles()
→ CandleStore
```

Não alterar:

- arquitetura do worker;
- Runtime Guard;
- polling;
- bootstrap;
- Chart API;
- Polarium;
- `.venv` principal.

---

## Ativos mínimos obrigatórios

Auditar pelo menos:

### Controle funcional

```text
EURUSD-OTC
```

### Ativo que falhou visualmente

```text
AMAZON-OTC
```

### Símbolo especial

```text
AMZN/ALIBABA-OTC
```

Caso algum nome real bruto seja diferente, registrar exatamente:

- chave interna;
- nome bruto;
- nome normalizado;
- nome enviado ao frontend;
- nome enviado ao `get_candles()`.

Não presumir que os nomes acima são os identificadores finais corretos.

---

## Fase 1 — Contrato bruto de assets

Para cada ativo auditado, registrar:

1. active id;
2. chave original em `get_all_init_v2()`;
3. campo `name`;
4. campos `enabled`;
5. campos `is_suspended`;
6. tipo binary/turbo;
7. símbolo bruto;
8. símbolo após `asset_discovery.py`;
9. símbolo após `mapper.py`;
10. objeto JSON enviado em `response.assets`.

Apresentar amostra sanitizada do JSON individual.

---

## Fase 2 — Auditoria da normalização

Localizar todas as funções que:

- removem `-op`;
- adicionam ou removem `-OTC`;
- transformam nomes em uppercase;
- inserem `/`;
- convertem símbolo técnico em display name;
- convertem display name em símbolo técnico;
- deduplicam binary e turbo.

Pesquisar especialmente por lógica equivalente a:

```text
[:3] + "/" + [3:]
```

Essa formatação só pode ser usada para pares cambiais comprovados.

Não deve transformar:

```text
AMAZON → AMA/ZON
```

Separar claramente:

```text
symbol
display_name
provider_symbol
```

Somente criar ou alterar campo se for indispensável e compatível com a arquitetura atual.

---

## Fase 3 — Probe direto de candles

Executar probes read-only diretamente no worker isolado.

Para cada representação possível do ativo que falhou, testar de forma controlada, sem execução de ordens.

Exemplos a verificar conforme os dados reais:

```text
AMAZON-OTC
AMAZON-OTC-op
AMAZON
active id correspondente
```

Não testar combinações inventadas em massa.

As variantes devem vir de campos reais da resposta da biblioteca.

Para cada chamada registrar:

- identificador exato enviado;
- timeframe;
- quantidade solicitada;
- duração;
- quantidade retornada;
- erro ou payload vazio;
- se a biblioteca aceitou o símbolo;
- se candles foram normalizados.

Executar o mesmo controle com:

```text
EURUSD-OTC
```

---

## Fase 4 — Compatibilidade da lista

Determinar se todos os ativos classificados como `open=True` pelo binary/turbo também são compatíveis com o método atual de candles.

Não assumir que:

```text
open para binary/turbo
```

é igual a:

```text
candles disponíveis via get_candles
```

Se existirem ativos abertos sem compatibilidade de candles:

- quantificar;
- explicar a diferença;
- decidir se devem ser removidos da experiência principal;
- não marcar um ativo como gráfico disponível sem prova.

---

## Correção mínima permitida

Aplicar correção somente após comprovar a causa.

Possibilidades aceitáveis:

1. preservar o `provider_symbol` bruto para candles;
2. separar `display_name` de `symbol`;
3. corrigir remoção indevida de `-op`;
4. impedir que nome de exibição seja enviado ao backend;
5. filtrar da lista ativos incompatíveis com a fonte atual de candles, desde que isso seja comprovado e eficiente;
6. corrigir o formatador visual que transforma `AMAZON` em `AMA/ZON`.

Não implementar tentativa sequencial de vários símbolos em toda chamada de polling.

Não mascarar erro retornando candles de outro ativo.

Não substituir o ativo selecionado silenciosamente por EURUSD-OTC.

Não criar catálogo fixo.

---

## Cuidados de desempenho

Não realizar probe de candles para centenas de ativos em toda requisição `/assets`.

Se for necessário construir compatibilidade:

- usar dados estruturais já disponíveis;
- usar normalização determinística comprovada;
- ou cache controlado e explícito;
- nunca gerar centenas de chamadas por polling.

---

## Contrato esperado

O ativo enviado ao frontend deve possuir um identificador técnico estável.

Exemplo conceitual, somente se necessário:

```json
{
  "symbol": "AMAZON-OTC",
  "display_name": "AMAZON OTC",
  "provider_symbol": "IDENTIFICADOR_REAL_DA_IQ_OPTION",
  "market_type": "OTC",
  "is_open": true
}
```

Não adicionar `provider_symbol` ao contrato público se o backend puder manter essa tradução internamente.

Preferir a menor alteração compatível.

---

## Testes obrigatórios

Adicionar testes para:

1. EURUSD ser exibido como EUR/USD;
2. EURUSD-OTC ser exibido como EUR/USD OTC;
3. AMAZON não ser exibido como AMA/ZON;
4. símbolo técnico não ser substituído pelo display name;
5. sufixo `-op` ser tratado conforme a prova real;
6. ativo selecionado ser enviado corretamente ao endpoint de candles;
7. resposta vazia não contaminar candles anteriores;
8. troca de ativo limpar somente a série anterior correta;
9. Runtime Guard continuar bloqueando métodos proibidos;
10. fluxo EURUSD-OTC continuar funcionando.

Executar:

```bash
.venv/bin/python -m pytest tests/market/providers -q
```

Executar testes frontend focados existentes:

```bash
.venv/bin/python -m pytest tests/frontend -q
```

Executar suíte completa:

```bash
.venv/bin/python -m pytest -q
```

Executar build:

```bash
cd frontend
npm run build
cd ..
```

---

## Validação real obrigatória

### EURUSD-OTC

- selecionar no frontend;
- gráfico deve carregar;
- candles maiores que zero.

### AMAZON OTC

- selecionar no frontend;
- registrar símbolo enviado;
- gráfico deve carregar somente se a fonte realmente oferecer candles;
- o nome não pode aparecer como `AMA/ZON`.

### Símbolo especial

Validar um ativo com barra ou nome composto, caso esteja aberto.

### Troca de ativos

Testar:

```text
EURUSD-OTC
→ AMAZON OTC
→ EURUSD-OTC
```

Confirmar:

- série correta;
- sem candles do ativo anterior;
- sem resposta atrasada contaminando o novo ativo;
- sem loading infinito.

### REGULAR

Validar pelo menos um ativo listado como REGULAR e compatível com candles.

---

## Entrega esperada

Entregar relatório contendo:

1. causa raiz comprovada;
2. arquivo e linha onde o símbolo era alterado incorretamente;
3. contrato bruto de EURUSD-OTC;
4. contrato bruto de AMAZON;
5. identificador aceito pelo método de candles;
6. identificadores rejeitados;
7. explicação do sufixo `-op`;
8. explicação da formatação `AMA/ZON`;
9. quantidade de ativos abertos compatíveis com candles;
10. quantidade incompatível;
11. decisão de filtragem ou tradução;
12. arquivos modificados;
13. diff funcional por arquivo;
14. resultado visual EURUSD-OTC;
15. resultado visual AMAZON;
16. resultado visual de retorno para EURUSD-OTC;
17. resultado REGULAR;
18. testes de provider;
19. testes frontend;
20. suíte completa;
21. build;
22. Runtime Guard;
23. `git status --short`;
24. `git diff --stat`;
25. riscos restantes;
26. sugestão de commit.

Não fazer commit.

Não fazer push.

Não alterar arquivos fora do escopo.

Não afirmar que um ativo possui candles sem probe real.