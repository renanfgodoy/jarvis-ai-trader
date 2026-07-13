# Friday Trade — Sprint V4.4

# IQ Option Read-Only OTC Market Data Provider

## Status

PLANNED

---

## Objetivo

Implementar a primeira prova de conceito de um provedor externo de dados de mercado no Friday Trade, utilizando a API comunitária da IQ Option exclusivamente para:

- autenticação local em conta DEMO;
- listar ativos OTC disponíveis;
- selecionar ativo pelo nome;
- carregar candles históricos;
- fornecer candles para M1, M5 e M15;
- atualizar a série continuamente;
- alimentar o gráfico nativo do Friday;
- preservar o nome real do ativo;
- operar em modo estritamente read-only.

Esta Sprint não deve:

- gerar sinal;
- executar ordens;
- consultar ou exibir saldo;
- alterar conta;
- acessar portfólio;
- vender opção;
- comprar opção;
- automatizar entrada.

---

## Decisão de produto

O Friday Trade passará a ser uma plataforma independente de corretora.

Fluxo:

```text
IQ Option OTC
→ IQOptionMarketDataProvider
→ normalização Friday
→ CandleStore
→ persistência local
→ Chart API
→ RealCandleChart
```

O operador poderá analisar no Friday e executar manualmente na corretora de opções binárias que escolher.

A fonte deve ser exibida claramente:

```text
IQ OPTION — COMMUNITY API — READ ONLY
```

Não apresentar esses candles como sendo da Polarium.

---

## Escopo inicial

Mercado:

```text
OTC
```

Timeframes:

```text
M1  = 60 segundos
M5  = 300 segundos
M15 = 900 segundos
```

Ativos:

- todos os ativos OTC realmente retornados como disponíveis pela fonte;
- sem lista inventada;
- sem ativo hardcoded como única opção;
- nomes reais, por exemplo `EURUSD-OTC`, somente quando retornados pela API.

Quantidade inicial:

```text
até 200 candles
```

Caso a API retorne menos:

- aceitar a quantidade real;
- não completar artificialmente;
- não criar candles sintéticos.

---

## API comunitária

Referência técnica atual:

```text
iqoptionapi/iqoptionapi
```

A biblioteca é não oficial e mantida pela comunidade.

Antes de instalar ou importar:

1. revisar o repositório;
2. revisar compatibilidade com Python 3.11;
3. revisar dependências;
4. verificar se o projeto já possui dependência semelhante;
5. não instalar versão arbitrária sem documentar origem;
6. não importar módulos de execução no runtime do Friday.

A Sprint pode:

- instalar de maneira isolada no ambiente virtual;
- usar fork ou commit fixado, se necessário;
- criar adapter próprio em volta da biblioteca;
- documentar incompatibilidades.

Não copiar credenciais para código-fonte.

---

## Segurança obrigatória

Usar somente conta:

```text
DEMO / PRACTICE
```

Nunca usar conta real nesta prova de conceito.

Credenciais devem ficar somente no Mac do operador.

Fontes permitidas:

```text
variáveis de ambiente locais
arquivo local ignorado pelo Git
secret store já existente no projeto
```

Exemplo de nomes:

```text
IQ_OPTION_EMAIL
IQ_OPTION_PASSWORD
IQ_OPTION_ACCOUNT_MODE=PRACTICE
```

Nunca:

- adicionar credenciais ao Git;
- adicionar credenciais ao Markdown;
- devolver credenciais por endpoint;
- registrar senha em log;
- registrar e-mail completo em log;
- enviar credenciais ao frontend;
- armazenar senha no SQLite de candles;
- expor cookies;
- expor SSID;
- expor headers privados;
- expor tokens de sessão.

---

## Bloqueio arquitetural de execução

O provider deve ser incapaz de executar ordens pelo contrato público.

Não expor métodos como:

```text
buy
buy_digital_spot
buy_digital_spot_v2
sell_option
close_position
change_balance
reset_practice_balance
```

Criar proteção explícita:

```text
READ_ONLY_PROVIDER
```

O runtime da Sprint não pode importar, chamar ou registrar rotas para funções de compra, venda ou saldo.

Adicionar testes estáticos ou arquiteturais garantindo ausência de execução.

---

## Arquitetura de providers

Criar camada genérica:

```text
app/market/providers/
```

Estrutura sugerida:

```text
app/market/providers/
├── __init__.py
├── base.py
├── errors.py
├── models.py
├── registry.py
└── iq_option/
    ├── __init__.py
    ├── client.py
    ├── config.py
    ├── mapper.py
    ├── provider.py
    ├── runtime.py
    └── status.py
```

Não criar a camada diretamente dentro do Connector Polarium.

IQ Option deve ser um provider independente.

---

## Contrato base

Criar protocolo ou classe abstrata semelhante a:

```python
class MarketDataProvider:
    provider_name: str

    def connection_status(self): ...
    def list_assets(self, market_type: str): ...
    def get_candles(
        self,
        symbol: str,
        raw_size: int,
        limit: int,
    ): ...
```

Streaming pode ser adicionado com contrato seguro nesta Sprint somente se a biblioteca demonstrar suporte estável.

Caso contrário:

```text
histórico + polling controlado
```

é aceitável para a prova de conceito.

---

## Modelos internos

Criar modelos claros para:

```text
MarketProviderStatus
MarketAsset
MarketCandleRequest
MarketCandleBatch
ProviderCandle
ProviderError
```

O candle normalizado do provider deve conter:

```text
provider
market_type
symbol
raw_size
start_timestamp
end_timestamp
open
high
low
close
volume
is_otc
source_verified
```

Para esta fonte:

```text
provider = IQ_OPTION
market_type = OTC
is_otc = true
```

---

## Identidade da série

Não usar `active_id` da Polarium para identificar séries IQ Option.

A identidade correta passa a ser:

```text
provider + symbol + raw_size
```

Exemplo:

```text
IQ_OPTION + EURUSD-OTC + 60
```

O `active_id` pode permanecer `None` para providers baseados em símbolo, desde que a nova arquitetura suporte isso corretamente.

Não fabricar `active_id`.

---

## Compatibilidade com CandleStore

O CandleStore atual foi construído originalmente em torno de:

```text
active_id + raw_size
```

A Sprint deve revisar essa limitação antes de integrar IQ Option.

Implementar uma evolução compatível que suporte:

```text
provider + symbol + raw_size
```

sem quebrar as séries Polarium existentes.

Possíveis abordagens:

### Opção recomendada

Criar identidade tipada:

```text
MarketSeriesKey
```

Com:

```text
provider
symbol
active_id
raw_size
```

Regras:

- Polarium usa `active_id`;
- IQ Option usa `symbol`;
- nunca misturar fontes;
- manter compatibilidade com chamadas antigas.

Não substituir silenciosamente o contrato atual sem testes de regressão.

---

## Persistência

A persistência SQLite deve separar séries por:

```text
provider + symbol + active_id + raw_size + start_timestamp
```

Para IQ Option:

```text
provider = IQ_OPTION
symbol = EURUSD-OTC
active_id = NULL
```

Para Polarium:

```text
provider = POLARIUM
symbol = NULL ou nome confirmado
active_id = 76
```

Não permitir colisão entre:

```text
IQ_OPTION / EURUSD-OTC
POLARIUM / active_id 76
```

Criar migração segura do schema existente.

Não apagar o SQLite atual.

Não perder candles Polarium já salvos.

---

## Migração do SQLite

A Sprint deve:

1. detectar schema existente;
2. criar versão nova;
3. adicionar campos necessários;
4. preservar dados antigos;
5. preencher provider antigo como `POLARIUM`, quando comprovadamente originado do fluxo atual;
6. manter `symbol=NULL` nos registros sem nome confirmado;
7. testar restart;
8. testar banco vazio;
9. testar banco existente.

Não utilizar `DROP TABLE` destrutivo sem migração segura.

---

## Client IQ Option

Criar wrapper isolado:

```text
IQOptionReadOnlyClient
```

Responsabilidades:

- carregar credenciais locais;
- conectar;
- verificar conexão;
- selecionar conta PRACTICE quando necessário;
- listar ativos;
- buscar candles;
- reconectar com limite;
- sanitizar erros;
- desconectar de forma limpa.

Não expor objeto bruto da biblioteca fora do adapter.

---

## Ativos OTC

Listar ativos usando somente dados retornados pela API.

Filtrar:

```text
symbol termina com -OTC
```

ou metadado oficial retornado pela biblioteca.

Categorias candidatas:

```text
digital
turbo
binary
```

Não duplicar o mesmo símbolo.

Resposta interna:

```text
symbol
display_name
market_type
is_otc
is_open
provider
```

Display inicial aceitável:

```text
EURUSD-OTC → EUR/USD OTC
GBPJPY-OTC → GBP/JPY OTC
```

A transformação visual deve ser determinística e não alterar o símbolo técnico.

---

## Histórico

Usar a funcionalidade de candles da biblioteca, por meio do wrapper.

Timeframes:

```text
60
300
900
```

Quantidade padrão:

```text
200
```

Regras:

- ordenar por timestamp;
- deduplicar;
- validar OHLC;
- validar timestamp;
- aplicar Candle Sanity Guard;
- não inventar volume;
- preservar volume real quando fornecido;
- aceitar volume nulo quando não fornecido;
- não gerar candle faltante.

---

## Atualização em tempo real

A prova de conceito deve manter o gráfico atualizado.

Estratégia preferencial:

1. verificar se existe streaming de candles confiável na biblioteca;
2. usar streaming read-only quando comprovado;
3. caso contrário, usar polling leve e controlado.

Polling sugerido:

```text
1 segundo para candle atual
```

Regras:

- uma única rotina por série ativa;
- impedir requests sobrepostos;
- cancelar rotina anterior ao trocar ativo;
- cancelar rotina anterior ao trocar timeframe;
- reconexão limitada;
- não bloquear thread principal;
- não criar centenas de requests;
- respeitar resposta da fonte.

---

## Bootstrap do gráfico

Ao selecionar ativo e timeframe:

```text
listar/selecionar ativo
→ solicitar histórico
→ normalizar candles
→ alimentar Store
→ exibir gráfico
→ iniciar atualização
```

O gráfico deve começar com todos os candles reais retornados, limitado ao máximo configurado.

Não começar zerado se a API retornar histórico.

---

## APIs internas read-only

Criar endpoints semelhantes a:

```text
GET  /api/v1/market/providers
GET  /api/v1/market/providers/iq-option/status
GET  /api/v1/market/providers/iq-option/assets?market_type=OTC
GET  /api/v1/market/providers/iq-option/candles
POST /api/v1/market/providers/iq-option/connect
POST /api/v1/market/providers/iq-option/disconnect
```

Parâmetros para candles:

```text
symbol
raw_size
limit
```

Não aceitar e-mail ou senha no body.

As credenciais vêm somente da configuração local segura.

Não criar endpoint de ordem.

Não criar endpoint de saldo.

---

## Status sanitizado

Retornar somente:

```text
provider
enabled
configured
connected
account_mode
read_only
last_connected_at
last_candle_at
last_symbol
last_raw_size
last_batch_count
reconnect_count
last_error_code
library_source
library_version
```

Não retornar:

```text
email completo
senha
saldo
token
cookie
ssid
headers
objeto da sessão
```

O e-mail pode ser:

```text
configured = true
```

Nunca retornar o valor.

---

## Frontend

Atualizar `/market-chart` para oferecer:

```text
PROVEDOR
IQ Option

MERCADO
OTC

ATIVO
EUR/USD OTC

TIMEFRAME
M1 / M5 / M15
```

Requisitos:

- selecionar provider;
- listar ativos reais;
- selecionar símbolo;
- selecionar timeframe;
- carregar histórico;
- mostrar loading;
- mostrar erro sanitizado;
- mostrar fonte;
- mostrar status da conexão;
- mostrar quantidade de candles;
- preservar layout compacto para MacBook de 13 polegadas.

Não mostrar `Active ID 76` para séries IQ Option.

Pode mostrar:

```text
EUR/USD OTC
IQ OPTION — READ ONLY
M1
```

---

## Separação Polarium/IQ Option

A interface deve permitir identificar claramente:

```text
Fonte Polarium
Fonte IQ Option
```

Não misturar candles.

Não fazer merge cruzado.

Não usar histórico IQ Option dentro de uma série Polarium existente.

Não alterar automaticamente o provider sem ação do usuário.

---

## Polarium nesta Sprint

A integração atual da Polarium deve permanecer disponível, mas não deve bloquear o provider IQ Option.

Não remover Browser Bridge.

Não apagar histórico Polarium.

Não alterar engenharia reversa nesta Sprint, salvo compatibilidade de identidade/persistência.

---

## M1, M5 e M15

Mapeamento:

```text
M1  = 60
M5  = 300
M15 = 900
```

A UI deve trabalhar com nomes amigáveis, mas o provider deve usar segundos.

Não adicionar outros timeframes ainda.

---

## Sanity Guard

Todo candle IQ Option deve passar por:

```text
CandleSanityGuard
```

Validar:

```text
timestamp
open
high
low
close
valores finitos
valores positivos
high >= low
open dentro da faixa
close dentro da faixa
```

As regras contextuais não podem bloquear volatilidade legítima de OTC de maneira agressiva.

Candles rejeitados devem gerar somente erro sanitizado.

---

## Observabilidade

Adicionar contadores:

```text
connections
connection_failures
asset_requests
candle_requests
candle_batches
candles_received
candles_accepted
candles_rejected
poll_cycles
poll_failures
reconnects
```

Sem payload bruto.

---

## Compatibilidade Python

O projeto usa Python 3.11.

A API comunitária pode ter sido criada originalmente para versões anteriores.

Antes de implementar:

1. instalar em ambiente isolado;
2. verificar import;
3. verificar conexão;
4. executar teste mínimo;
5. documentar patches necessários;
6. não alterar globalmente dependências sem revisar regressões;
7. evitar downgrade global de bibliotecas críticas.

Se houver incompatibilidade séria:

```text
bloquear integração real
```

e entregar diagnóstico claro, sem criar código falso.

---

## Feature flag

Adicionar configuração:

```text
iq_option_provider_enabled
```

Padrão recomendado:

```text
false
```

Ativar localmente somente após configuração.

Adicionar também:

```text
iq_option_read_only = true
iq_option_account_mode = PRACTICE
iq_option_default_candle_limit = 200
iq_option_poll_interval_seconds = 1
```

Em produção, manter desabilitado até revisão.

---

## Testes obrigatórios

Criar testes para:

1. provider desabilitado;
2. credenciais ausentes;
3. status sanitizado;
4. nenhuma senha exposta;
5. nenhum e-mail exposto;
6. conexão fake bem-sucedida;
7. falha de conexão;
8. reconexão limitada;
9. conta PRACTICE;
10. listagem OTC;
11. filtro OTC;
12. deduplicação de símbolos;
13. nome amigável;
14. M1;
15. M5;
16. M15;
17. timeframe inválido;
18. histórico com 2 candles;
19. histórico com 200 candles;
20. ordenação;
21. deduplicação por timestamp;
22. normalização OHLC;
23. candle inválido rejeitado;
24. Store por provider/symbol/raw_size;
25. Polarium e IQ Option não colidem;
26. persistência separada;
27. migração segura;
28. restore IQ Option;
29. restore Polarium existente;
30. polling atualiza candle aberto;
31. polling acrescenta candle novo;
32. requests sobrepostos bloqueados;
33. troca de ativo cancela polling anterior;
34. troca de timeframe cancela polling anterior;
35. disconnect limpo;
36. API assets;
37. API candles;
38. endpoint não aceita credenciais;
39. ausência de endpoints de ordem;
40. ausência de import/uso de funções `buy`;
41. frontend mostra símbolo;
42. frontend mostra provider;
43. frontend mostra M1/M5/M15;
44. layout compacto;
45. suíte completa sem regressão;
46. build aprovado.

---

## Prova de conceito real

A validação real deve utilizar conta DEMO.

Etapa 1:

```text
configurar credenciais localmente
ativar feature flag
subir backend
consultar status
conectar
```

Etapa 2:

```text
listar ativos OTC
selecionar EURUSD-OTC ou outro ativo disponível
buscar 200 candles M1
confirmar gráfico preenchido
```

Etapa 3:

```text
trocar para M5
confirmar novo histórico
trocar para M15
confirmar novo histórico
```

Etapa 4:

```text
observar atualização do candle atual
aguardar candle novo
confirmar append sem reset
```

Etapa 5:

```text
reiniciar backend
confirmar persistência
confirmar provider reconecta somente de forma controlada
```

---

## Não implementar nesta Sprint

Não implementar:

- sinais;
- CALL;
- PUT;
- AGUARDAR calculado;
- IA;
- indicadores reais;
- análise multitemporal;
- execução;
- ordens;
- saldo;
- payout;
- gestão;
- martingale;
- copy trading;
- conta real;
- Forex normal;
- cripto;
- índices;
- outros providers.

Esses itens serão tratados em Sprints futuras.

---

## Entrega obrigatória

1. Objetivo.
2. Diagnóstico de compatibilidade da biblioteca.
3. Origem/versão da biblioteca.
4. Arquitetura do provider.
5. Arquivos criados.
6. Arquivos modificados.
7. Configuração local.
8. Política de credenciais.
9. Status sanitizado.
10. Ativos OTC disponíveis.
11. Contrato dos candles.
12. Normalização.
13. M1/M5/M15.
14. Bootstrap histórico.
15. Atualização contínua.
16. Integração com Store.
17. Evolução da identidade da série.
18. Migração da persistência.
19. Integração frontend.
20. Separação entre providers.
21. Sanity Guard.
22. Segurança read-only.
23. Evidência de ausência de execução.
24. Testes criados.
25. Resultado dos testes específicos.
26. Resultado da suíte completa.
27. Resultado do build.
28. Como testar para o Renan.
29. Validação real necessária.
30. Riscos conhecidos.
31. Débitos técnicos.
32. `git status --short`.
33. `git diff --stat`.
34. Sugestão de commit.

Mensagem sugerida:

```text
feat(market): add read-only IQ Option OTC provider
```

---

## Regra final

Não fazer commit.

Não fazer push.

Não utilizar conta real.

Não executar ordens.

Não consultar saldo.

Não expor credenciais.

Não misturar IQ Option com Polarium.

A Sprint termina com gráfico OTC da IQ Option funcionando em modo somente leitura para M1, M5 e M15, ou com bloqueio técnico comprovado e documentado caso a biblioteca seja incompatível.