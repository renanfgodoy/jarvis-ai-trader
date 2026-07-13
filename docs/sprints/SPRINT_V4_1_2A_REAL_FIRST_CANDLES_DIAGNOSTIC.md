# Friday Trade — Sprint V4.1.2A

# Real First-Candles Diagnostic

## Status

PLANNED

---

## Objetivo

Descobrir por que o Friday Trade continua iniciando com zero candles mesmo após a implementação do bootstrap histórico por `first-candles`.

Esta Sprint é de diagnóstico controlado.

Não corrigir por hipótese.

Não inventar envelope.

Não criar candles.

Não solicitar dados de mercado manualmente nesta Sprint.

O objetivo é comprovar:

1. se `first-candles` realmente aparece na sessão atual;
2. em qual direção ele trafega;
3. qual é sua estrutura real;
4. quantos candles contém;
5. se chega antes ou depois do relay estar pronto;
6. em qual etapa ele é perdido.

---

## Problema real confirmado

Com backend, frontend, extensão e Polarium abertos:

```text
CandleStore inicia vazio
→ gráfico inicia zerado
→ apenas candle-generated começa a preencher a série
```

Mesmo após suporte teórico para:

```text
first-candles
msg.body.candles
até 200 itens
```

o histórico real não aparece.

---

## Fluxo a rastrear

```text
Polarium WebSocket
→ page-bridge-main.js
→ content-script.js
→ background.js
→ endpoint Browser Bridge
→ Payload Adapter
→ first-candles parser
→ MarketPipeline
→ CandleStore
→ Chart API
```

Para cada etapa, registrar apenas metadados sanitizados.

---

## Revisão obrigatória

Revisar:

```text
tools/polarium-browser-bridge/manifest.json
tools/polarium-browser-bridge/page-bridge-main.js
tools/polarium-browser-bridge/content-script.js
tools/polarium-browser-bridge/background.js

app/api/routes/polarium_browser_bridge.py
app/market/browser_bridge.py
app/market/browser_bridge_payload_adapter.py
app/market/events/parsers/first_candles.py
app/market/pipeline/
app/market/store/
```

---

## Perguntas obrigatórias

Responder com evidência:

1. O evento `first-candles` foi observado na sessão real atual?
2. Quantas vezes foi observado?
3. Ele é recebido como:
   - objeto;
   - array;
   - string JSON;
   - lista de envelopes;
   - frame binário;
   - formato não decodificado?
4. Qual é o caminho estrutural até a coleção?
5. Qual é o tamanho real da coleção?
6. O nome aparece exatamente como `first-candles`?
7. Existe variação como:
   - `firstCandles`;
   - `candles`;
   - `candles-generated`;
   - `sendMessage`;
   - resposta por `request_id` sem `name`?
8. O evento ocorre antes de `content-script`/relay estar pronto?
9. O MAIN world recebe o evento, mas o relay isolado perde?
10. O backend recebe o evento e rejeita?
11. O adapter aceita?
12. O parser retorna candles?
13. O Pipeline armazena?
14. Quantos candles chegam ao Store?
15. A Chart API enxerga a série?

---

## Instrumentação sanitizada

Adicionar contadores/status, sem payload bruto:

```text
first_candles_seen_main
first_candles_relayed
first_candles_received_backend
first_candles_adapter_accepted
first_candles_parsed
first_candles_stored
first_candles_collection_count
first_candles_last_error_code
```

Adicionar metadados estruturais permitidos:

```text
event_name
direction
top_level_type
top_level_keys
msg_type
msg_keys
body_type
body_keys
candidate_collection_path
candidate_collection_length
received_at
relay_ready_at
websocket_created_at
```

Não incluir valores de candles nesta Sprint.

Não incluir token, cookie, SSID, Authorization, headers ou payload privado.

---

## Diagnóstico de ordem de inicialização

Comprovar a sequência:

```text
page bridge instalado
content relay instalado
WebSocket criado
WebSocket aberto
first-candles recebido
relay enviado
backend recebido
```

Registrar apenas timestamps relativos/sanitizados.

Determinar se:

```text
first-candles ocorre antes de o relay estar pronto
```

Se ocorrer, documentar como causa raiz.

---

## Diagnóstico de direção

O Browser Bridge deve observar:

```text
client → server
server → client
```

Confirmar se o histórico é:

- resposta recebida do servidor;
- resposta correlacionada por `request_id`;
- evento sem campo `name`;
- coleção dentro de outra mensagem.

Não alterar frames.

---

## Endpoint de status

Atualizar somente o status sanitizado existente para expor a seção:

```text
historical_diagnostic
```

Exemplo:

```json
{
  "historical_diagnostic": {
    "first_candles_seen_main": 1,
    "first_candles_relayed": 1,
    "first_candles_received_backend": 1,
    "first_candles_adapter_accepted": 0,
    "first_candles_parsed": 0,
    "first_candles_stored": 0,
    "candidate_collection_path": "msg.candles",
    "candidate_collection_length": 112,
    "last_error_code": "ADAPTER_UNSUPPORTED_ENVELOPE"
  }
}
```

Nunca expor o conteúdo da coleção.

---

## Cenários possíveis

### Cenário A — Evento não aparece no MAIN world

Conclusão:

```text
A Polarium atual não está enviando first-candles nessa interação
```

Não criar correção.

### Cenário B — Evento aparece antes do relay

Conclusão:

```text
race de inicialização da extensão
```

Documentar ponto exato.

### Cenário C — Evento chega ao backend, adapter rejeita

Documentar envelope real por tipos, chaves e caminhos sanitizados.

### Cenário D — Parser retorna zero

Documentar o contrato incompatível.

### Cenário E — Pipeline armazena, Chart API não mostra

Documentar divergência de série/Store.

---

## Não implementar nesta Sprint

Não:

- enviar `get-first-candles`;
- injetar subscription;
- alterar WebSocket da Polarium;
- criar request de histórico;
- criar candles;
- criar fallback sintético;
- criar persistência;
- alterar gráfico;
- alterar seleção;
- alterar IA;
- alterar indicadores;
- enviar ordens.

---

## Testes obrigatórios

Criar testes para:

1. status sanitizado sem payload bruto;
2. contador por etapa;
3. evento visto no MAIN e não relayado;
4. evento relayado e rejeitado pelo adapter;
5. evento parseado com quantidade;
6. nenhuma chave sensível no diagnóstico;
7. ordem temporal das etapas;
8. coleção grande expõe somente comprimento;
9. frame desconhecido não derruba o Bridge;
10. diagnóstico não altera Pipeline ou Store.

---

## Validação real obrigatória

Após implementação:

1. reiniciar backend;
2. recarregar extensão;
3. fechar abas antigas;
4. abrir nova aba Polarium;
5. selecionar ativo/timeframe;
6. aguardar 20 segundos;
7. consultar:

```text
/api/v1/polarium/browser-bridge/status
```

8. copiar apenas:

```text
historical_diagnostic
```

9. não copiar payload bruto.

---

## Testes e build

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

.venv/bin/python -m pytest -q tests/market tests/tools tests/frontend

.venv/bin/python -m pytest -q

cd frontend
npm run build
```

---

## Entrega obrigatória

1. Objetivo.
2. `first-candles` foi observado ou não.
3. Direção do evento.
4. Ordem de inicialização comprovada.
5. Estrutura sanitizada real.
6. Caminho candidato da coleção.
7. Quantidade real encontrada.
8. Etapa exata onde o evento para.
9. Arquivos criados.
10. Arquivos modificados.
11. Instrumentação adicionada.
12. Testes criados.
13. Resultado dos testes específicos.
14. Resultado da suíte completa.
15. Resultado do build.
16. Como testar para o Renan.
17. Dados sanitizados que o Renan deve enviar.
18. Riscos conhecidos.
19. `git status --short`.
20. `git diff --stat`.
21. Próxima correção recomendada, sem implementá-la.
22. Sugestão de commit.

Mensagem sugerida:

```text
chore(market): trace real first-candles bootstrap
```

---

## Regra final

Não fazer commit.

Não fazer push.

Não corrigir por hipótese.

A Sprint deve terminar informando exatamente onde o histórico real desaparece.