# SPRINT V4.5.9 — IQ OPTION BINARY/TURBO ASSET DISCOVERY

## Objetivo

Substituir exclusivamente o caminho bloqueante de descoberta de ativos da IQ Option por um caminho read-only baseado em `binary/turbo`, já comprovado na Sprint V4.5.8.

A implementação deve permitir que:

- `/assets?market_type=OTC` retorne ativos OTC abertos;
- `/assets?market_type=REGULAR` retorne ativos regulares abertos;
- o frontend deixe de depender apenas do fallback;
- o gráfico e o fluxo de candles permaneçam inalterados.

Não criar nova arquitetura.

---

## Contexto comprovado

A Sprint V4.5.8 comprovou:

- `get_all_open_time()` cria ramificações `binary`, `digital` e `other`;
- os `join()` internos não possuem timeout;
- `digital` pode bloquear;
- `other` pode bloquear;
- a chamada agregada não é segura para o worker persistente;
- `__get_binary_open()` isolado retorna em tempo aceitável;
- o caminho binary/turbo fornece status `open`;
- foram encontrados:
  - 430 símbolos binary/turbo;
  - 334 símbolos abertos;
  - 331 OTC abertos;
  - 3 REGULAR abertos;
- candles OTC e REGULAR continuam funcionando.

O Friday Trade atual trabalha com análise de opções binárias e não precisa descobrir digital, forex, CFD ou cripto nesta fase.

---

## Decisão de escopo

A descoberta oficial de ativos da experiência principal será:

```text
IQ Option binary/turbo
```

Não apresentar essa lista como cobertura total da IQ Option.

Não misturar:

- digital-option;
- forex;
- CFD;
- cripto;
- catálogo sem status open.

---

## Arquitetura preservada

Manter:

```text
Friday backend
→ provider IQ Option
→ worker persistente isolado
→ iqoptionapi 7.1.1
→ JSON sanitizado
→ MarketAsset
→ /assets
→ frontend
```

Não criar novo provider.

Não criar novo endpoint.

Não alterar o contrato público existente, salvo metadado opcional e retrocompatível.

---

## Implementação esperada

### 1. Worker

No comando de listagem de ativos:

- não chamar `client.get_all_open_time()`;
- obter somente a estrutura binary/turbo usando caminho equivalente ao comprovado em `__get_binary_open()`;
- não editar a biblioteca instalada;
- não chamar método privado por name mangling de forma frágil se for possível reproduzir a lógica mínima usando métodos públicos já existentes;
- se a única forma segura for encapsular a lógica equivalente dentro do worker, documentar exatamente o motivo.

A chamada deve continuar protegida pelo timeout externo do worker.

---

### 2. Status open

Usar somente ativos com status real disponível na resposta binary/turbo.

Não inferir `open=True` por:

- presença no catálogo;
- sucesso de candles;
- existência do opcode;
- sufixo do símbolo.

O sufixo `-OTC` deve ser usado somente para classificação de mercado.

---

### 3. Classificação de mercado

Classificar:

```text
símbolo termina em -OTC
→ OTC
```

```text
símbolo não termina em -OTC
→ REGULAR
```

Aplicar também o filtro `open=True`.

Não retornar símbolo fechado como ativo disponível na lista principal.

---

### 4. Normalização

Produzir `MarketAsset` usando o contrato atual.

Preservar campos já utilizados pelo frontend.

Quando possível, manter:

- símbolo técnico;
- nome de exibição;
- provider;
- market_type;
- open;
- tradable ou equivalente, caso já exista no modelo.

Não criar campos obrigatórios novos sem necessidade.

---

### 5. Resposta da API

OTC deve retornar:

```json
{
  "provider": "IQ_OPTION",
  "market_type": "OTC",
  "assets": []
}
```

REGULAR deve retornar:

```json
{
  "provider": "IQ_OPTION",
  "market_type": "REGULAR",
  "assets": []
}
```

As listas não devem ser vazias quando a biblioteca retornar ativos abertos válidos.

Opcionalmente, pode ser incluído metadado retrocompatível, como:

```json
{
  "discovery_scope": "BINARY_TURBO"
}
```

Somente incluir se não quebrar testes ou frontend.

---

## Segurança

Preservar Runtime Guard read-only.

Nunca chamar:

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
- equivalentes de execução ou consulta financeira.

Não alterar conta.

Não consultar saldo.

Não executar ordens.

---

## Frontend

Não alterar `MarketChart.tsx` por padrão.

O frontend já lê:

```ts
response.assets
```

Manter os fallbacks:

```text
EURUSD-OTC
EURUSD
```

Os fallbacks continuam necessários para resiliência.

Somente alterar frontend se houver incompatibilidade concreta comprovada com o contrato atual.

---

## Concorrência e timeout

Garantir que:

- a listagem binary/turbo retorna dentro do timeout do worker;
- nenhuma thread bloqueada da biblioteca permanece impedindo o worker;
- chamadas repetidas não acumulam threads órfãs;
- resposta antiga não contamina mercado diferente;
- erro é sanitizado.

Não aumentar o timeout como solução principal.

---

## Testes obrigatórios

### Testes focados

Adicionar testes para:

1. worker não chama `get_all_open_time()`;
2. binary/turbo é usado;
3. ativos fechados são removidos;
4. ativos `-OTC` são classificados como OTC;
5. símbolos sem `-OTC` são classificados como REGULAR;
6. catálogo sem status open não é usado;
7. resposta OTC respeita o contrato;
8. resposta REGULAR respeita o contrato;
9. falha do caminho binary/turbo retorna erro sanitizado;
10. Runtime Guard permanece ativo.

Executar:

```bash
.venv/bin/python -m pytest tests/market/providers -q
```

### Suíte completa

```bash
.venv/bin/python -m pytest -q
```

### Build

```bash
cd frontend
npm run build
cd ..
```

---

## Validação real obrigatória

Após conectar à IQ Option em PRACTICE e read-only:

### OTC

Validar:

- `/assets?market_type=OTC`;
- HTTP 200;
- `response.assets` presente;
- quantidade maior que zero;
- somente símbolos `-OTC`;
- somente ativos `open=True`;
- pelo menos `EURUSD-OTC`, caso esteja realmente presente e aberto na resposta.

### REGULAR

Validar:

- `/assets?market_type=REGULAR`;
- HTTP 200;
- `response.assets` presente;
- somente símbolos sem `-OTC`;
- somente ativos `open=True`;
- lista pode ser pequena, pois depende do horário real do mercado.

### Candles

Confirmar que continuam funcionando:

- EURUSD-OTC M1;
- EURUSD M1.

### Interface

Confirmar:

- dropdown OTC mostra múltiplos ativos quando disponíveis;
- dropdown REGULAR mostra somente ativos abertos;
- gráfico continua carregando;
- troca de ativo atualiza o gráfico;
- não há chamadas Polarium;
- fallback continua funcionando se `/assets` falhar.

---

## Arquivos permitidos

Alterar somente os arquivos estritamente necessários em:

```text
app/market/providers/iq_option/
tests/market/providers/
```

Alterar rota/modelo compartilhado somente se indispensável e devidamente justificado.

Não alterar:

- CandleStore;
- Chart API;
- RealCandleChart;
- fluxo de polling;
- arquitetura do worker;
- biblioteca instalada;
- Polarium.

---

## Entrega esperada

Entregar relatório contendo:

1. causa raiz anterior;
2. decisão técnica aplicada;
3. método exato usado no lugar de `get_all_open_time()`;
4. arquivos modificados;
5. diff funcional por arquivo;
6. quantidade bruta binary/turbo;
7. quantidade aberta;
8. quantidade OTC aberta;
9. quantidade REGULAR aberta;
10. exemplo sanitizado de até 5 ativos OTC;
11. exemplo sanitizado de até 5 ativos REGULAR;
12. resultado HTTP e contrato de `/assets` OTC;
13. resultado HTTP e contrato de `/assets` REGULAR;
14. confirmação de candles OTC;
15. confirmação de candles REGULAR;
16. testes focados;
17. suíte completa;
18. build;
19. validação visual;
20. auditoria de Runtime Guard;
21. auditoria de threads e timeout;
22. `git status --short`;
23. `git diff --stat`;
24. riscos restantes;
25. sugestão de commit.

Não fazer commit.

Não fazer push.

Não alterar arquivos fora do escopo.

Não ocultar lista vazia, timeout ou mercado fechado.