# Friday Trade

# Sprint V4.5

## IQ OPTION OTC READ-ONLY PROVIDER

---

# Objetivo

Transformar a IQ Option no primeiro provider oficial de candles OTC do Friday Trade.

O objetivo desta Sprint NÃO é operar.

O objetivo NÃO é consultar saldo.

O objetivo NÃO é consultar posições.

O objetivo NÃO é descobrir automaticamente se a conta é PRACTICE.

O objetivo é apenas consumir candles OTC em modo somente leitura e alimentar o Friday Trade.

---

# Contexto

Na Sprint V4.4.3 foi comprovado:

- conexão funciona;
- runtime guard funciona;
- nenhuma chamada proibida ocorreu;
- subscriptions observadas são passivas;
- disconnect funciona.

O único bloqueio restante foi:

ACCOUNT_MODE_NOT_SAFELY_CONFIRMED

Esse bloqueio deixa de ser impeditivo.

Ele passa a ser apenas informativo.

---

# Nova política

Após conexão bem sucedida:

permitido:

- listar ativos OTC;
- descobrir quais OTC estão abertos;
- buscar candles;
- normalizar candles;
- alimentar CandleStore;
- atualizar Chart API;
- desconectar.

Proibido:

- buy;
- sell;
- buy_order;
- buy_digital;
- close_position;
- get_balance;
- get_positions;
- portfolio;
- alterar tipo de conta;
- qualquer execução.

---

# Runtime Guard

O guard continua obrigatório.

Toda chamada para métodos proibidos deve levantar:

READ_ONLY_VIOLATION

A execução deve ser imediatamente interrompida.

---

# Fluxo

connect()

↓

listar ativos OTC

↓

selecionar ativo OTC aberto

↓

baixar candles

↓

normalizar

↓

CandleStore

↓

Chart API

↓

disconnect()

---

# Ativos

Prioridade:

EURUSD OTC

Depois:

GBPUSD OTC

USDJPY OTC

AUDCAD OTC

demais OTC disponíveis.

Nunca usar ativo fechado.

---

# Timeframes

Suportar:

M1

M5

M15

---

# Bootstrap

Baixar o maior histórico permitido pela biblioteca.

Não limitar a:

100

200

500

Usar o máximo permitido.

Caso a API permita:

1000

2000

5000

utilizar.

O provider apenas entrega.

O CandleStore controla retenção.

---

# Normalização

Todos os candles devem virar:

NormalizedMarketCandle

provider="IQ_OPTION"

symbol preenchido

active_id=None

raw_size

timestamp

OHLC

volume quando existir.

---

# Integração

Nenhuma alteração na IA.

Nenhuma alteração nos indicadores.

Nenhuma alteração nas estratégias.

Apenas trocar a origem dos candles.

---

# Frontend

Adicionar provider:

IQ OPTION OTC

Quando selecionado:

listar ativos OTC

listar M1

M5

M15

abrir gráfico imediatamente.

Nunca mostrar Active ID.

Sempre mostrar símbolo.

Exemplo:

EURUSD OTC

---

# Critério de sucesso

Conexão:

OK

↓

Ativo OTC encontrado

↓

Candles baixados

↓

Store preenchido

↓

Chart API funcionando

↓

Gráfico Friday funcionando

↓

Disconnect

---

# Critério de falha

Qualquer chamada para:

buy

sell

balance

portfolio

position

change_balance

↓

READ_ONLY_VIOLATION

↓

abortar.

---

# Testes

Criar testes para:

conexão

download OTC

bootstrap

M1

M5

M15

normalização

Store

Chart API

disconnect

guard runtime

ausência de métodos proibidos

frontend provider

---

# Build

Executar:

pytest

build frontend

---

# Entrega

Responder:

1. Objetivo.

2. Fluxo implementado.

3. Ativos OTC encontrados.

4. Timeframes suportados.

5. Quantidade máxima de candles.

6. Resultado do bootstrap.

7. Resultado da normalização.

8. Resultado do Store.

9. Resultado da Chart API.

10. Resultado do gráfico.

11. Runtime Guard.

12. Métodos proibidos chamados.

13. Disconnect.

14. Testes.

15. Build.

16. git status.

17. git diff --stat.

Não fazer commit.

Não fazer push.