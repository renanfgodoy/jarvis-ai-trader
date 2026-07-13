# Friday Trade — Sprint V4.1.2

# Historical Candle Bootstrap

## Status

PLANNED

---

## Objetivo

Fazer o gráfico real do Friday Trade iniciar com um histórico de candles reais, em vez de começar vazio e acumular candles somente após a abertura do sistema.

Comportamento atual:

```text
CandleStore vazio
→ recebe candle-generated
→ começa com 1 ou 2 candles
→ histórico cresce lentamente
```

Comportamento desejado:

```text
ativo/timeframe detectado
→ first-candles recebido
→ 100 a 200 candles históricos normalizados
→ CandleStore preenchido
→ gráfico aparece completo
→ candle-generated atualiza em tempo real
```

A Sprint deve utilizar somente dados reais observados na sessão autorizada da Polarium.

Não inventar candles.

Não criar dados sintéticos.

Não preencher lacunas artificialmente.

---

## Fluxo oficial

```text
Aba Polarium autenticada
→ Browser Bridge
→ first-candles
→ Payload Adapter
→ Market Event Engine
→ CandleStore
→ Chart API
→ RealCandleChart

candle-generated
→ atualização do candle aberto
→ append de candle novo
```

---

## Evidências existentes

Já foram confirmados nas evidências sanitizadas:

```text
get-first-candles
first-candles
candle-generated
```

Estrutura observada de candle:

```text
active_id
size
from
to
open
close
min
max
volume
```

Preservar:

```text
symbol = None
timeframe = None
mapping_verified = False
```

Não inventar nome visual do ativo.

---

## Diagnóstico obrigatório

Revisar:

```text
tools/polarium-browser-bridge/page-bridge-main.js
tools/polarium-browser-bridge/content-script.js
app/market/browser_bridge.py
app/market/browser_bridge_payload_adapter.py
app/market/events/
app/market/pipeline/
app/market/store/
app/market/chart/
app/api/routes/market_chart.py
```

Responder:

1. O Browser Bridge já encaminha `first-candles`?
2. Qual estrutura real chega no backend?
3. O Payload Adapter suporta coleções históricas?
4. O parser `first-candles` atual normaliza todos os itens?
5. Quantos candles aparecem no evento real?
6. Existe limite aplicado no navegador, backend ou Pipeline?
7. O CandleStore recebe a coleção inteira?
8. A Chart API retorna os candles históricos na ordem correta?
9. O frontend faz carga inicial usando todo o histórico?
10. Existe risco de `candle-generated` sobrescrever ou reduzir o histórico?

---

## Allowlist

Continuar permitindo:

```text
first-candles
candle-generated
candles-generated
timeSync
```

Priorizar nesta Sprint:

```text
first-candles
candle-generated
```

Não permitir eventos privados.

Não permitir eventos de saldo, conta, portfólio, ordens, posições ou execução.

---

## Browser Bridge

O Bridge deve:

- observar `first-candles`;
- encaminhar somente o payload sanitizado;
- preservar a coleção de candles;
- não limitar para apenas 1 ou 2 itens;
- não enviar token, cookie, Authorization, bearer ou SSID;
- não registrar payload bruto;
- não modificar o WebSocket original;
- não solicitar ordens;
- não controlar a página.

Não criar outra extensão.

Não criar outro WebSocket.

---

## Payload Adapter

O adapter deve reconhecer estruturas reais como:

```text
msg
msg.body
payload
payload.msg
payload.msg.body
data
params
```

Para `first-candles`, localizar a coleção real sem inventar caminhos.

Normalizar para o formato aceito pelo Market Event Engine.

Exemplo canônico:

```json
{
  "name": "first-candles",
  "msg": {
    "body": {
      "candles": [
        {
          "active_id": 76,
          "size": 60,
          "from": 1783721940,
          "to": 1783722000,
          "open": 1.16227,
          "close": 1.16231,
          "min": 1.16220,
          "max": 1.16235,
          "volume": 0
        }
      ]
    }
  }
}
```

Usar apenas formato comprovado pelo payload real.

Não inventar campo `candles` se o parser atual utilizar outra estrutura canônica. Adaptar ao contrato já existente.

---

## Market Event Engine

Reutilizar o parser existente:

```text
first-candles
```

Revisar se ele:

- aceita coleção completa;
- ignora apenas itens inválidos;
- não derruba toda a coleção por um item ruim;
- preserva ordenação;
- preserva `active_id`;
- preserva `raw_size`;
- preserva timestamps;
- mantém `symbol=None`;
- mantém `timeframe=None`;
- mantém `mapping_verified=False`.

Não duplicar parser.

---

## CandleStore

Ao receber `first-candles`:

- armazenar toda a coleção válida;
- deduplicar por `start_timestamp`;
- ordenar cronologicamente;
- separar por `active_id + raw_size`;
- atualizar candles duplicados com payload mais recente;
- respeitar limite por série;
- manter preferencialmente entre 100 e 200 candles recentes.

O Store não deve ser substituído.

Não criar segundo Store.

---

## Quantidade mínima

Objetivo visual:

```text
100 candles ou mais
```

Quando o evento real fornecer menos:

- usar somente a quantidade real;
- não completar artificialmente;
- mostrar a quantidade recebida;
- marcar readiness como parcial se abaixo de 100.

Quando fornecer mais de 200:

- manter os 200 mais recentes;
- remover apenas os mais antigos.

---

## Merge histórico + tempo real

Após o bootstrap:

```text
first-candles
→ histórico inicial

candle-generated
→ atualiza último candle
ou
→ acrescenta novo candle
```

Regras:

- não duplicar candle;
- não reduzir histórico;
- não substituir 100 candles por 1 ou 2;
- não limpar a série em polling vazio;
- não misturar séries diferentes;
- tratar `active_id + raw_size` como par atômico.

---

## Chart API

A API deve retornar:

```text
active_id
raw_size
count
candles
```

Com:

- ordem cronológica;
- até 200 candles;
- sem duplicatas;
- candles reais;
- janela estável;
- histórico completo disponível no Store.

Não criar endpoint paralelo se o endpoint atual já suportar isso.

---

## Frontend

Ao selecionar uma série:

1. Buscar o histórico completo.
2. Renderizar com `setData()` somente na carga inicial.
3. Depois usar `series.update()` para atualizações e novos candles.
4. Não recriar o gráfico.
5. Não executar `fitContent()` em cada polling.
6. Preservar zoom e pan.
7. Mostrar a quantidade real de candles.

A tela deve abrir já com histórico quando o Store estiver preenchido.

---

## Seleção de ativo

Quando o operador selecionar ativo/timeframe na Polarium:

- detectar o par real;
- aguardar `first-candles`;
- preencher a série;
- exibir o gráfico completo;
- continuar acompanhando `candle-generated`.

Com `Seguir Polarium` desligado:

- manter a série selecionada;
- usar histórico já disponível no Store.

---

## Reinício do backend

Nesta Sprint, o CandleStore continua em memória.

Ao reiniciar backend:

```text
histórico é perdido
```

Isso permanece aceito temporariamente.

A persistência local será tratada em Sprint própria.

Entretanto, após a Polarium ser aberta e o evento `first-candles` chegar novamente, o gráfico deve repopular automaticamente.

---

## Não alterar

Não alterar:

- OAuth;
- Connector;
- execução;
- AutoTrade;
- IA;
- Indicator Engine;
- regras de segurança;
- origem autorizada dos dados;
- estrutura geral do CandleStore;
- Chart API pública além do necessário;
- Browser Bridge fora do suporte a `first-candles`.

---

## Não implementar

Não implementar:

- banco de dados;
- SQLite;
- persistência;
- candles sintéticos;
- interpolação;
- sinais;
- CALL;
- PUT;
- IA;
- EMA;
- RSI;
- MACD;
- Probability Engine;
- execução automática.

---

## Testes obrigatórios

Criar testes para:

1. `first-candles` com 100 itens.
2. `first-candles` com 200 itens.
3. Coleção parcialmente inválida.
4. Deduplicação por timestamp.
5. Ordenação cronológica.
6. Separação por `active_id`.
7. Separação por `raw_size`.
8. Limite mantém os candles mais recentes.
9. Histórico inicial aparece na Chart API.
10. `candle-generated` atualiza o último candle.
11. `candle-generated` acrescenta novo candle.
12. Histórico não diminui após evento em tempo real.
13. Payload Adapter suporta envelope real.
14. Payload sensível é rejeitado.
15. Bridge não encaminha eventos privados.
16. Frontend carrega histórico completo.
17. Frontend não começa vazio quando há série disponível.
18. Readiness usa a quantidade real.
19. Troca de série não mistura históricos.
20. Reinício do Store não cria dados artificiais.

---

## Validação visual obrigatória

Após implementação:

1. Reiniciar backend.
2. Abrir Polarium.
3. Selecionar ativo em M1.
4. Aguardar o evento `first-candles`.
5. Abrir `/market-chart`.
6. Confirmar que o gráfico aparece com histórico.
7. Confirmar quantidade próxima de 100 ou mais, caso fornecida pela Polarium.
8. Confirmar candle atual mudando em tempo real.
9. Aguardar candle novo.
10. Confirmar histórico preservado.
11. Trocar ativo.
12. Confirmar novo histórico carregado.
13. Trocar timeframe.
14. Confirmar histórico correspondente.
15. Confirmar zoom e pan preservados durante atualização.

---

## Testes e build

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

.venv/bin/python -m pytest -q tests/market tests/frontend

.venv/bin/python -m pytest -q

cd frontend
npm run build
```

---

## Entrega obrigatória

1. Objetivo.
2. Causa atual do gráfico começar vazio.
3. Estrutura real de `first-candles`.
4. Arquivos criados.
5. Arquivos modificados.
6. Alterações no Browser Bridge.
7. Alterações no Payload Adapter.
8. Alterações no parser.
9. Alterações no CandleStore.
10. Quantidade de candles suportada.
11. Estratégia de bootstrap.
12. Estratégia de merge com tempo real.
13. Chart API.
14. Frontend.
15. Testes criados.
16. Resultado dos testes específicos.
17. Resultado da suíte completa.
18. Resultado do build.
19. Como testar para o Renan.
20. Validação visual necessária.
21. Riscos conhecidos.
22. Débitos técnicos.
23. `git status --short`.
24. `git diff --stat`.
25. Sugestão de commit.

Mensagem sugerida:

```text
feat(chart): bootstrap real historical candle series
```

---

## Regra final

Não fazer commit.

Não fazer push.

Não inventar candles.

Não usar dados simulados.

O histórico deve vir exclusivamente do evento real `first-candles` observado na sessão autorizada da Polarium.