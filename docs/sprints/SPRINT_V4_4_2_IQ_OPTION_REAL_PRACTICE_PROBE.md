# Friday Trade — Sprint V4.4.2

# IQ Option Real PRACTICE Probe

## Status

PLANNED

---

## Objetivo

Executar automaticamente a validação real e estritamente read-only da biblioteca comunitária IQ Option no ambiente virtual isolado já criado.

A Sprint deve:

- carregar credenciais locais temporárias;
- conectar somente em conta PRACTICE;
- listar ativos OTC reais;
- selecionar automaticamente um ativo OTC aberto;
- buscar candles reais M1, M5 e M15;
- validar estrutura, timestamps e OHLC;
- comprovar ausência de operações;
- preservar a `.venv` principal;
- produzir relatório sanitizado;
- remover variáveis sensíveis da sessão ao terminar.

Não integrar ainda a biblioteca à `.venv` principal.

---

## Ambiente autorizado

Projeto:

```text
/Users/renangodoy/Desktop/jarvis-ai-trader
```

Ambiente isolado:

```text
.jarvis_cache/iq_option_probe_venv
```

Arquivo local temporário de credenciais:

```text
.jarvis_cache/iq_option/probe.env
```

Esse arquivo:

- está autorizado apenas para esta execução;
- deve permanecer ignorado pelo Git;
- não pode ser aberto, impresso ou incluído em relatório;
- não pode ser copiado para outro local;
- não pode ser enviado ao frontend;
- não pode ser adicionado a Markdown;
- não pode ser incluído em logs.

---

## Regras absolutas de segurança

Usar somente:

```text
PRACTICE
```

Não usar conta real.

Nunca chamar:

```text
get_balance
get_balance_mode
buy
buy_multi
buy_digital_spot
buy_digital_spot_v2
sell_option
buy_order
close_position
change_balance
reset_practice_balance
get_position
get_positions
get_order
get_orders
```

Não executar operações de valor zero.

Não consultar payout.

Não consultar portfólio.

Não consultar saldo.

Não registrar:

```text
e-mail completo
senha
token
cookie
SSID
Authorization
headers
sessão bruta
payload bruto
```

---

## Pré-validação obrigatória

Antes de carregar credenciais:

1. confirmar `pwd`;
2. confirmar Git root;
3. confirmar branch;
4. executar `git status --short`;
5. confirmar Python principal;
6. confirmar Python isolado;
7. confirmar que `probe.env` é ignorado pelo Git;
8. confirmar permissão `600`;
9. confirmar que `iqoptionapi` não está instalada na `.venv` principal;
10. confirmar que está instalada somente no venv isolado.

Se o arquivo secreto não estiver ignorado ou estiver com permissão insegura:

```text
INTERROMPER
```

---

## Carregamento seguro

Carregar o arquivo com shell local sem imprimir conteúdo:

```bash
set -a
source .jarvis_cache/iq_option/probe.env
set +a
```

Validar somente presença:

```text
email_configured = true
password_configured = true
account_mode = PRACTICE
network_allowed = true
```

Nunca mostrar valores.

---

## Guard read-only obrigatório

Antes da conexão, instalar proteção defensiva sobre qualquer método perigoso exposto pelo client.

Qualquer chamada a método proibido deve:

```text
levantar READ_ONLY_VIOLATION
interromper o probe
registrar apenas o nome sanitizado do método
```

Não depender apenas de busca estática.

Adicionar também monitoramento de runtime para comprovar que nenhum método proibido foi chamado.

---

## Teste 1 — Import

Usar:

```text
.jarvis_cache/iq_option_probe_venv/bin/python
```

Importar:

```python
from iqoptionapi.stable_api import IQ_Option
```

Esperado:

```text
IMPORT_OK
```

---

## Teste 2 — Construção do client

Criar o client com as credenciais carregadas.

Não imprimir o client.

Não imprimir e-mail.

Esperado:

```text
CLIENT_CREATED
```

---

## Teste 3 — Conexão

Executar conexão real apenas porque:

```text
IQ_OPTION_PROBE_ALLOW_NETWORK=true
```

Aplicar timeout controlado.

Limitar tentativas.

Sugestão:

```text
máximo 2 tentativas
timeout por tentativa
backoff curto
```

Resultado sanitizado:

```text
connected
reason_code
attempts
connection_duration_ms
```

Não registrar resposta bruta.

---

## Teste 4 — Garantia PRACTICE

Selecionar explicitamente:

```text
PRACTICE
```

Não usar `get_balance()` para validar.

Validar somente pelo estado/configuração do client, quando passivamente possível.

Se não for possível confirmar PRACTICE sem consultar saldo:

```text
interromper antes de candles
ACCOUNT_MODE_NOT_SAFELY_CONFIRMED
```

Nunca continuar em modo possivelmente real.

---

## Teste 5 — Ativos OTC reais

Executar:

```python
get_all_open_time()
```

Processar somente:

```text
digital
turbo
binary
```

Extrair:

```text
symbol
category
is_open
```

Filtrar símbolos OTC.

Deduplicar.

Não expor payload bruto.

Resultado:

```text
otc_assets_count
open_otc_assets_count
sample_symbols
```

Máximo de 10 símbolos.

---

## Seleção automática do ativo

Escolher automaticamente o primeiro ativo que:

```text
termine com -OTC
esteja aberto
apareça em categoria suportada
```

Preferência somente quando realmente disponível:

```text
EURUSD-OTC
```

Não hardcodar como obrigatório.

Se não estiver aberto, escolher outro retornado pela fonte.

Registrar somente:

```text
selected_symbol
selected_category
```

---

## Teste 6 — Candles M1

Buscar:

```text
raw_size = 60
limit = 20
```

Validar:

- resposta não vazia;
- timestamps presentes;
- timestamps distintos;
- ordenação;
- open/high/low/close presentes;
- valores finitos;
- valores positivos;
- high >= low;
- open dentro da faixa;
- close dentro da faixa.

Retornar somente:

```text
count
distinct_timestamps
first_timestamp
last_timestamp
valid_count
invalid_count
```

Não imprimir lista de preços.

---

## Teste 7 — Candles M5

Buscar:

```text
raw_size = 300
limit = 20
```

Aplicar as mesmas validações sanitizadas.

---

## Teste 8 — Candles M15

Buscar:

```text
raw_size = 900
limit = 20
```

Aplicar as mesmas validações sanitizadas.

---

## Teste 9 — Atualização curta

Se M1 retornar candles:

1. guardar somente timestamp/hash estrutural do último candle;
2. aguardar intervalo curto;
3. buscar novamente M1;
4. verificar se:
   - candle aberto atualizou;
   - ou novo candle apareceu;
   - ou série permaneceu estável.

Não exigir nascimento de candle novo durante poucos segundos.

Resultado:

```text
UNCHANGED
CURRENT_CANDLE_UPDATED
NEW_CANDLE_APPENDED
```

Não mostrar preços.

---

## Teste 10 — Disconnect

Desconectar de forma limpa, se a biblioteca suportar.

Confirmar:

```text
DISCONNECTED
```

Não deixar threads ou WebSockets órfãos.

---

## Limpeza obrigatória da sessão

Ao final, mesmo em erro:

```bash
unset IQ_OPTION_EMAIL
unset IQ_OPTION_PASSWORD
unset IQ_OPTION_ACCOUNT_MODE
unset IQ_OPTION_PROBE_ALLOW_NETWORK
```

Não apagar automaticamente o arquivo secreto nesta Sprint, pois Renan poderá precisar repetir o teste.

Não modificar o conteúdo.

---

## Relatório sanitizado

Atualizar:

```text
docs/iq_option/IQ_OPTION_REAL_PRACTICE_PROBE_REPORT.md
```

O relatório deve conter somente:

```text
library_source
library_commit
python_version
connected
account_mode
read_only
connection_attempts
otc_assets_count
open_otc_assets_count
sample_symbols
selected_symbol
M1 summary
M5 summary
M15 summary
update_summary
disconnect_status
last_error_code
```

Nunca conter e-mail, senha, token, cookie, SSID ou payload bruto.

---

## Testes automatizados

Criar testes para:

1. arquivo secreto ausente;
2. arquivo secreto fora do Git ignore;
3. permissão insegura;
4. variáveis carregadas sem exposição;
5. e-mail nunca serializado;
6. senha nunca serializada;
7. guard read-only bloqueia `buy`;
8. guard read-only bloqueia `get_balance`;
9. conexão fake;
10. timeout;
11. limite de tentativas;
12. PRACTICE confirmado;
13. PRACTICE não confirmado bloqueia;
14. filtro OTC realista;
15. seleção automática;
16. M1 válido;
17. M5 válido;
18. M15 válido;
19. candle inválido;
20. update curto;
21. disconnect;
22. cleanup de variáveis;
23. relatório sanitizado;
24. `.venv` principal não modificada;
25. nenhuma função de ordem chamada.

---

## Testes de projeto

Após o probe real:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

.venv/bin/python -m pytest -q tests/market/providers

.venv/bin/python -m pytest -q

cd frontend
npm run build
```

---

## Critério de aprovação

A biblioteca poderá seguir para integração principal somente se:

```text
IMPORT_OK
CLIENT_CREATED
connected = true
account_mode = PRACTICE
open_otc_assets_count > 0
M1 valid_count > 0
read_only = true
order_method_calls = 0
balance_method_calls = 0
credentials_exposed = false
main_venv_modified = false
```

M5 e M15 são desejáveis, mas M1 é o requisito mínimo para avançar.

---

## Critério de bloqueio

Bloquear se ocorrer:

```text
login falha repetidamente
PRACTICE não pode ser confirmado
método de saldo é necessário
método de ordem é chamado
credencial aparece em log
nenhum OTC é retornado
M1 não retorna candles
protocolo incompatível
WebSocket não encerra
dependência principal precisa ser rebaixada
```

---

## Entrega obrigatória

1. Objetivo.
2. Pré-validação de segurança.
3. Ambiente isolado.
4. Biblioteca/commit.
5. Resultado do import.
6. Resultado do client.
7. Resultado da conexão.
8. Confirmação PRACTICE.
9. Quantidade OTC.
10. Símbolos sanitizados.
11. Ativo selecionado.
12. Resultado M1.
13. Resultado M5.
14. Resultado M15.
15. Atualização curta.
16. Disconnect.
17. Evidência read-only.
18. Métodos proibidos chamados.
19. Credenciais expostas ou não.
20. `.venv` principal modificada ou não.
21. Arquivos criados.
22. Arquivos modificados.
23. Testes específicos.
24. Suíte completa.
25. Build.
26. Riscos.
27. Pode avançar para integração?
28. Próximo passo.
29. `git status --short`.
30. `git diff --stat`.

---

## Regra final

Não fazer commit.

Não fazer push.

Não usar conta real.

Não consultar saldo.

Não executar ordens.

Não imprimir credenciais.

Executar automaticamente todos os testes permitidos e entregar somente resultados sanitizados.
