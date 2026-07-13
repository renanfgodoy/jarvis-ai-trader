# Friday Trade — Sprint V4.5.1

# IQ Option Isolated Worker Bridge

## Status

PLANNED

---

## Objetivo

Permitir que o backend principal do Friday utilize o provider IQ Option sem instalar `iqoptionapi` ou dependências antigas na `.venv` principal.

Arquitetura:

```text
Friday backend (.venv)
→ IQOptionIsolatedWorkerClient
→ subprocesso local
→ .jarvis_cache/iq_option_probe_venv
→ iqoptionapi
→ resposta JSON sanitizada
→ provider
→ CandleStore

Evidência confirmada

Ambiente principal:

.venv/bin/python -m pip show iqoptionapi
→ Package not found

Ambiente isolado:

.jarvis_cache/iq_option_probe_venv/bin/python -m pip show iqoptionapi
→ iqoptionapi 7.1.1

Não instalar a biblioteca na .venv principal.

Escopo

Criar um worker local controlado capaz de:

conectar;
listar ativos OTC;
buscar candles;
buscar atualização curta;
desconectar;
responder somente JSON sanitizado.

O worker deve rodar exclusivamente com:

.jarvis_cache/iq_option_probe_venv/bin/python
Arquitetura sugerida

Criar:

app/market/providers/iq_option/worker/
├── __init__.py
├── protocol.py
├── runner.py
├── client.py
├── models.py
└── errors.py
runner.py

Executado pelo Python isolado.

Responsável por:

carregar credenciais locais;
importar iqoptionapi;
instalar runtime guard;
executar comando solicitado;
devolver JSON em stdout;
nunca imprimir logs livres;
escrever erros somente em formato JSON sanitizado.
client.py

Executado pelo backend principal.

Responsável por:

iniciar subprocesso;
enviar comando;
ler JSON;
aplicar timeout;
matar processo travado;
validar resposta;
nunca acessar iqoptionapi diretamente.
Protocolo permitido

Comandos:

status
connect
list_otc_assets
get_candles
disconnect

Parâmetros permitidos:

symbol
raw_size
limit

Nunca aceitar:

email
password
token
cookie
authorization
ssid
order
amount
direction
expiration

Credenciais vêm somente de:

.jarvis_cache/iq_option/probe.env
Segurança

O worker deve manter:

READ_ONLY

Bloquear métodos:

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
get_positions
get_position
get_orders
get_order

Nenhum endpoint de ordem.

Nenhum endpoint de saldo.

Nenhuma credencial em stdout/stderr.

Comunicação

Formato de entrada:

{
  "command": "get_candles",
  "params": {
    "symbol": "EURUSD-OTC",
    "raw_size": 60,
    "limit": 1000
  }
}

Formato de saída:

{
  "success": true,
  "data": {
    "provider": "IQ_OPTION",
    "symbol": "EURUSD-OTC",
    "raw_size": 60,
    "count": 1000,
    "candles": []
  },
  "error_code": null
}

Sem logs misturados ao stdout.

Lifecycle

Preferir processo persistente por sessão para evitar login a cada request.

Se isso complicar demais, aceitar POC inicial one-shot com documentação de custo.

O processo deve:

iniciar;
conectar;
atender comandos;
encerrar limpo;
não deixar WebSocket órfão.
Integração com provider

O provider atual IQ Option deve usar:

IQOptionIsolatedWorkerClient

em vez de importar iqoptionapi.

O backend principal nunca deve importar:

from iqoptionapi...

Adicionar teste arquitetural garantindo isso.

Endpoints existentes

Manter:

POST /api/v1/market/providers/iq-option/connect
GET /api/v1/market/providers/iq-option/assets
GET /api/v1/market/providers/iq-option/candles
POST /api/v1/market/providers/iq-option/disconnect

Esses endpoints passam pelo worker isolado.

Timeframes

Suportar:

60
300
900
Testes obrigatórios

Criar testes para:

.venv principal sem iqoptionapi;
worker isolado com iqoptionapi;
status;
connect;
list_otc_assets;
get_candles M1;
get_candles M5;
get_candles M15;
disconnect;
timeout;
subprocesso travado;
JSON inválido;
stdout contaminado;
credenciais não expostas;
método proibido bloqueado;
backend não importa iqoptionapi;
Store recebe candles;
Chart API recebe candles;
frontend continua funcionando;
suíte completa e build.
Validação real

Depois:

subir backend com .venv;
conectar pelo endpoint;
confirmar que o subprocesso usa o Python isolado;
listar OTC;
carregar 1000 candles;
abrir gráfico;
trocar M1/M5/M15;
atualizar candle;
desconectar;
confirmar ausência de processos órfãos.
Entrega obrigatória
Objetivo.
Arquitetura.
Arquivos criados.
Arquivos modificados.
Protocolo.
Worker.
Client.
Segurança.
Integração provider.
Resultado connect.
Resultado assets.
Resultado candles.
Resultado Store.
Resultado Chart API.
Resultado frontend.
Testes específicos.
Suíte completa.
Build.
Como testar para o Renan.
Riscos.
git status.
git diff --stat.
Sugestão de commit.

Mensagem sugerida:

feat(iq-option): bridge provider through isolated worker
Regra final

Não fazer commit.

Não fazer push.

Não instalar iqoptionapi na .venv principal.

Não expor credenciais.

Não executar ordens.

Não consultar saldo.