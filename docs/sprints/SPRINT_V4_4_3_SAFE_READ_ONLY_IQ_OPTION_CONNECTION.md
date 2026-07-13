# Friday Trade — Sprint V4.4.3

# Safe Read-Only IQ Option Connection

## Status

PLANNED

---

## Objetivo

Executar a conexão real da conta IQ Option PRACTICE no ambiente isolado, permitindo subscriptions passivas necessárias ao lifecycle da biblioteca, mas bloqueando de forma absoluta qualquer chamada efetiva de:

- compra;
- venda;
- saldo;
- posição;
- portfólio consultado ativamente;
- execução;
- alteração de conta.

A Sprint deve distinguir:

```text
subscription passiva
```

de:

```text
ação de trading ou consulta proibida
```

Não bloquear a conexão apenas porque o código interno registra canais de eventos.

---

## Evidência da Sprint anterior

A V4.4.2 bloqueou com:

```text
CONNECT_USES_PORTFOLIO_OR_ORDER_SUBSCRIPTIONS
```

Nenhum método proibido foi realmente chamado:

```text
methods_called = []
```

Conclusão:

```text
bloqueio estático excessivamente conservador
```

A próxima execução deve usar proteção real de runtime, não somente inspeção textual do método `connect()`.

---

## Ambiente obrigatório

Usar exclusivamente:

```text
.jarvis_cache/iq_option_probe_venv
```

Credenciais:

```text
.jarvis_cache/iq_option/probe.env
```

Requisitos:

- arquivo ignorado pelo Git;
- permissão 600;
- nunca imprimir conteúdo;
- nunca copiar para Markdown;
- nunca enviar ao frontend;
- conta PRACTICE exclusivamente.

Não instalar nada na `.venv` principal.

---

## Política read-only

### Permitido

Permitir somente operações necessárias para:

```text
conectar
autenticar
manter sessão
receber eventos
listar horários/ativos
buscar candles
desconectar
```

Subscriptions passivas internas são permitidas quando não executarem mutações.

### Proibido

Bloquear efetivamente qualquer chamada a:

```text
buy
buy_multi
buy_digital_spot
buy_digital_spot_v2
sell_option
buy_order
close_position
change_balance
reset_practice_balance
get_balance
get_balance_mode
get_position
get_positions
get_order
get_orders
get_portfolio
```

Também bloquear aliases ou métodos semanticamente equivalentes encontrados na biblioteca.

---

## Guard de runtime

Criar:

```text
IQOptionReadOnlyRuntimeGuard
```

ou equivalente.

Antes da conexão:

1. localizar métodos proibidos no objeto client;
2. substituir temporariamente cada método por função que levante:

```text
READ_ONLY_VIOLATION
```

3. registrar apenas o nome sanitizado do método;
4. contar chamadas;
5. restaurar os métodos originais no encerramento, caso necessário;
6. nunca executar o corpo original.

O guard deve funcionar durante toda a probe.

---

## Subscriptions passivas

Não bloquear por nome de canal apenas.

Registrar somente:

```text
subscription_count
subscription_names_sanitized
```

Máximo de nomes sanitizados.

Não registrar payloads.

Classificar:

```text
PASSIVE_SUBSCRIPTION
```

Somente bloquear se a subscription provocar chamada real a método proibido.

---

## Confirmação PRACTICE

O arquivo de ambiente define:

```text
IQ_OPTION_ACCOUNT_MODE=PRACTICE
```

Após conexão:

- solicitar explicitamente mudança para PRACTICE apenas se o método não consultar saldo;
- não chamar `get_balance`;
- não chamar `get_balance_mode` se estiver na lista proibida;
- não usar existência de saldo como confirmação.

Se a biblioteca não permitir selecionar PRACTICE sem chamada proibida:

```text
ACCOUNT_MODE_NOT_SAFELY_CONFIRMED
```

e interromper antes de buscar candles.

---

## Sequência real

### 1. Pré-validação

Confirmar:

```text
probe.env seguro
venv isolado
biblioteca importável
conta PRACTICE configurada
network true
```

### 2. Import

```python
from iqoptionapi.stable_api import IQ_Option
```

### 3. Client

Criar o client sem imprimir credenciais.

### 4. Instalar guard

Bloquear métodos proibidos em runtime.

### 5. Conectar

Máximo de duas tentativas, com timeout e backoff curto.

Não bloquear apenas por subscriptions passivas.

### 6. Confirmar PRACTICE

Somente por mecanismo seguro.

### 7. Ativos OTC

Usar:

```text
get_all_open_time()
```

Filtrar símbolos:

```text
*-OTC
```

Categorias:

```text
digital
turbo
binary
```

Deduplicar.

### 8. Selecionar ativo

Preferência:

```text
EURUSD-OTC
```

somente se estiver aberto.

Caso contrário, primeiro OTC aberto retornado.

### 9. Candles

Buscar:

```text
M1 = 60
M5 = 300
M15 = 900
limit = 20
```

Validar:

- timestamps;
- ordenação;
- OHLC estrutural;
- valores finitos;
- valores positivos;
- high >= low;
- open/close dentro da faixa.

Não imprimir preços.

### 10. Atualização curta

Buscar M1 novamente após pequena espera e classificar:

```text
UNCHANGED
CURRENT_CANDLE_UPDATED
NEW_CANDLE_APPENDED
```

### 11. Disconnect

Encerrar conexão e verificar ausência de threads órfãs quando possível.

---

## Diagnóstico de subscriptions

Entregar:

```text
passive_subscriptions_observed
passive_subscription_count
read_only_method_calls
read_only_violations
```

Não retornar mensagens completas.

---

## Critério de sucesso

A Sprint passa se:

```text
connected = true
account_mode = PRACTICE
open_otc_assets_count > 0
M1 valid_count > 0
read_only_method_calls = []
read_only_violations = 0
credentials_exposed = false
main_venv_modified = false
```

M5 e M15 são desejáveis, mas M1 é o mínimo.

---

## Critério de bloqueio

Interromper se:

```text
qualquer método proibido for chamado
PRACTICE não puder ser confirmado com segurança
credencial aparecer em log
login falhar após duas tentativas
nenhum OTC aberto existir
M1 não retornar candles
disconnect falhar de forma crítica
```

Não bloquear apenas por nomes de subscriptions.

---

## Relatório

Atualizar:

```text
docs/iq_option/IQ_OPTION_REAL_PRACTICE_PROBE_REPORT.md
```

Incluir apenas:

```text
connected
account_mode
connection_attempts
passive_subscription_count
open_otc_assets_count
sample_symbols
selected_symbol
M1 summary
M5 summary
M15 summary
update_summary
read_only_method_calls
read_only_violations
disconnect_status
last_error_code
```

Nunca incluir credenciais ou payloads.

---

## Testes obrigatórios

Criar testes para:

1. subscription passiva não bloqueia;
2. método buy bloqueado;
3. método get_balance bloqueado;
4. método get_positions bloqueado;
5. método change_balance bloqueado;
6. métodos originais não executados;
7. guard permanece ativo durante conexão;
8. conexão fake com subscriptions;
9. PRACTICE confirmado;
10. ativos OTC;
11. M1;
12. M5;
13. M15;
14. update curto;
15. disconnect;
16. relatório sanitizado;
17. credenciais não expostas;
18. `.venv` principal intacta.

---

## Testes do projeto

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

.venv/bin/python -m pytest -q tests/market/providers

.venv/bin/python -m pytest -q

cd frontend
npm run build
```

---

## Entrega obrigatória

1. Objetivo.
2. Por que o bloqueio anterior era excessivo.
3. Guard runtime implementado.
4. Subscriptions passivas observadas.
5. Métodos proibidos chamados.
6. Resultado do import.
7. Resultado do client.
8. Resultado da conexão.
9. Confirmação PRACTICE.
10. Quantidade OTC.
11. Símbolos sanitizados.
12. Ativo selecionado.
13. Resultado M1.
14. Resultado M5.
15. Resultado M15.
16. Atualização curta.
17. Disconnect.
18. Credenciais expostas ou não.
19. `.venv` principal alterada ou não.
20. Arquivos criados.
21. Arquivos modificados.
22. Testes específicos.
23. Suíte completa.
24. Build.
25. Pode avançar para integração?
26. Riscos.
27. Próximo passo.
28. git status --short.
29. git diff --stat.

---

## Regra final

Não fazer commit.

Não fazer push.

Não usar conta real.

Não consultar saldo.

Não executar ordens.

Não bloquear conexão somente por subscriptions passivas.

Bloquear qualquer chamada efetiva a métodos proibidos.