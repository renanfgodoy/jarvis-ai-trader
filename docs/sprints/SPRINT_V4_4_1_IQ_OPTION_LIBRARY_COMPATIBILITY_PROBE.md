# Friday Trade — Sprint V4.4.1

# IQ Option Library Compatibility Probe

## Status

PLANNED

---

## Objetivo

Validar de forma isolada e segura se a biblioteca comunitária IQ Option pode funcionar com o ambiente atual do Friday Trade:

```text
Python 3.11
macOS
conta PRACTICE
modo estritamente read-only
```

Esta Sprint não deve integrar definitivamente a biblioteca ao runtime principal enquanto a compatibilidade não estiver comprovada.

---

## Situação atual

A Sprint V4.4 criou:

```text
provider architecture
models
registry
Store multi-provider
persistência multi-provider
Chart API
frontend
testes fake
```

Porém:

```text
iqoptionapi não está instalada
conexão real não foi executada
ativos OTC reais não foram consultados
candles reais não foram recebidos
```

Portanto, a prova de conceito real ainda está bloqueada.

---

## Regras de segurança

Usar exclusivamente:

```text
conta DEMO / PRACTICE
```

Nunca usar conta real.

Não consultar saldo.

Não executar ordens.

Não importar ou chamar:

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
```

Credenciais somente por variáveis de ambiente locais ignoradas pelo Git.

Nunca imprimir:

```text
email completo
senha
token
cookie
SSID
headers
sessão
```

---

## Fonte da biblioteca

Não usar automaticamente o pacote antigo do PyPI sem análise.

Investigar:

```text
GitHub iqoptionapi/iqoptionapi
PyPI iqoptionapi 0.5
forks ativos relevantes
commits recentes
issues de Python 3.11
dependências
```

Selecionar uma origem pinada:

```text
repository URL
commit SHA
```

Não depender de branch móvel sem registrar commit.

---

## Ambiente isolado obrigatório

Não alterar imediatamente a `.venv` principal.

Criar ambiente temporário:

```text
.jarvis_cache/iq_option_probe_venv
```

ou equivalente ignorado pelo Git.

Nesse ambiente:

1. instalar biblioteca escolhida;
2. instalar dependências;
3. testar import;
4. testar construção do client;
5. verificar conflitos;
6. registrar versões.

Não fazer downgrade da `.venv` principal nesta Sprint.

---

## Diagnóstico de dependências

Registrar:

```text
Python version
pip version
iqoptionapi source
iqoptionapi commit
websocket-client version
requests version
urllib3 version
certifi version
```

Verificar especialmente conflitos com:

```text
websocket
websocket-client
```

Não manter simultaneamente pacotes conflitantes sem justificativa.

---

## Teste 1 — Import

Executar:

```python
from iqoptionapi.stable_api import IQ_Option
```

Resultado:

```text
IMPORT_OK
```

ou erro sanitizado.

---

## Teste 2 — Construção do client

Com credenciais locais:

```python
client = IQ_Option(email, password)
```

Não imprimir o objeto.

Não imprimir credenciais.

Resultado sanitizado:

```text
CLIENT_CREATED
```

---

## Teste 3 — Conexão PRACTICE

Executar conexão somente se:

```text
IQ_OPTION_PROBE_ALLOW_NETWORK=true
```

Confirmar:

```text
connected
reason_code
```

Se a biblioteca tentar selecionar conta real por padrão, interromper.

Selecionar explicitamente:

```text
PRACTICE
```

Não chamar saldo para confirmar modo.

---

## Teste 4 — Ativos OTC

Após conexão autorizada:

```text
get_all_open_time()
```

Extrair somente:

```text
símbolo
categoria
open
```

Filtrar OTC.

Não retornar dados de conta.

Registrar:

```text
otc_assets_count
sample_symbols
```

Máximo de 10 símbolos sanitizados na evidência.

---

## Teste 5 — Candles

Escolher somente um ativo OTC aberto retornado pela própria fonte.

Buscar:

```text
M1 = 60
limit = 20
```

Usar:

```text
get_candles(symbol, 60, 20, current_timestamp)
```

Validar somente:

```text
count
timestamps ordenados
campos OHLC presentes
timestamps distintos
primeiro timestamp
último timestamp
```

Não incluir todos os preços no relatório.

---

## Teste 6 — M5 e M15

Se M1 funcionar:

```text
300
900
```

Buscar até 20 candles em cada timeframe.

Registrar somente contagens e coerência estrutural.

---

## Proibição de execução

Realizar busca estática e runtime monkey-patch defensivo.

Caso qualquer função de ordem seja chamada:

```text
READ_ONLY_VIOLATION
```

Interromper imediatamente.

Não criar ordem de valor zero como teste.

Não chamar payout.

Não consultar posição.

---

## Resultado possível A — compatível

Considerar compatível somente se:

```text
import funciona
conexão PRACTICE funciona
OTC é listado
M1 retorna candles
nenhuma ordem é chamada
nenhuma dependência principal é quebrada
```

---

## Resultado possível B — compatível com patch

Documentar patches mínimos necessários:

```text
arquivo
causa
alteração
risco
```

Não aplicar fork definitivo na `.venv` principal sem aprovação.

---

## Resultado possível C — incompatível

Bloquear integração real caso haja:

```text
falha de login persistente
protocolo obsoleto
dependência incompatível
necessidade de downgrade perigoso
ausência de candles
necessidade de usar conta real
```

Não mascarar incompatibilidade com mocks.

---

## Artefato de diagnóstico

Criar relatório:

```text
docs/iq_option/IQ_OPTION_LIBRARY_COMPATIBILITY_REPORT.md
```

Sem credenciais e sem payloads privados.

---

## Não alterar

Não alterar nesta Sprint:

```text
CandleStore
persistência principal
Chart API
frontend
Polarium
Indicator Engine
sinais
execução
```

Alterar somente o necessário para o probe isolado e documentação.

---

## Testes

Criar testes para:

1. probe desabilitado;
2. network bloqueada por padrão;
3. credenciais ausentes;
4. import fake;
5. erro de import sanitizado;
6. conexão fake;
7. erro de conexão sanitizado;
8. filtro OTC;
9. candles M1;
10. candles M5;
11. candles M15;
12. nenhuma função de ordem chamada;
13. nenhuma credencial em relatório;
14. ambiente temporário ignorado pelo Git;
15. `.venv` principal não modificada.

---

## Entrega obrigatória

1. Objetivo.
2. Origem da biblioteca.
3. Commit pinado.
4. Ambiente isolado criado.
5. Dependências instaladas.
6. Compatibilidade Python 3.11.
7. Resultado do import.
8. Resultado da construção do client.
9. Resultado da conexão PRACTICE.
10. Quantidade de OTC.
11. Símbolos OTC sanitizados.
12. Resultado M1.
13. Resultado M5.
14. Resultado M15.
15. Evidência read-only.
16. Conflitos encontrados.
17. Patches necessários.
18. Pode integrar à `.venv` principal?
19. Arquivos criados.
20. Arquivos modificados.
21. Testes.
22. Resultado da suíte.
23. Build.
24. Como testar para o Renan.
25. Riscos.
26. Próximo passo.
27. git status --short.
28. git diff --stat.

---

## Regra final

Não fazer commit.

Não fazer push.

Não instalar na `.venv` principal antes de comprovar compatibilidade.

Não usar conta real.

Não executar ordens.

Não consultar saldo.