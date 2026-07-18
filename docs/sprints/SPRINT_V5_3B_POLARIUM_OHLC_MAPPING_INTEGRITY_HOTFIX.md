# SPRINT V5.3B — POLARIUM OHLC MAPPING INTEGRITY HOTFIX

## Objetivo

Corrigir os candles anômalos exibidos pela Friday ao consumir o canal `candles-generated` da Polarium.

Sintoma visual confirmado:

- aproximadamente 200 candles grandes e praticamente idênticos;
- corpos e pavios incompatíveis com o mercado real;
- preço atual próximo de 1.136, mas candles ocupando aproximadamente 1.05 até 1.30;
- o array recebido pelo gráfico não estava vazio.

Portanto, o problema não é placeholder no RealCandleChart.

A causa deve ser encontrada no mapeamento:

```text
candles-generated
→ parser
→ modelo Polarium
→ adapter
→ NormalizedMarketCandle
→ CandleStore
→ Chart API
```

---

# REGRA PRINCIPAL

Não modificar novamente o RealCandleChart antes de provar que o OHLC que chega ao componente está correto.

Não esconder o problema visual.

Não filtrar candles apenas porque parecem grandes.

Não criar clamps arbitrários.

Não inventar preços.

Corrigir o contrato na origem.

---

# PARTE 1 — CONTRATO REAL DO EVENTO PLURAL

Auditar o contrato `candles-generated`.

Estrutura esperada observada:

```json
{
  "name": "candles-generated",
  "msg": {
    "active_id": 85,
    "at": 1783907961000000000,
    "ask": 161.5014,
    "bid": 161.5013,
    "value": 161.50135,
    "candles": {
      "60": {
        "from": 1783907940,
        "to": 1783908000,
        "open": 161.51515,
        "min": 161.50135,
        "max": 161.51515,
        "volume": 0
      }
    }
  }
}
```

Confirmar os nomes reais:

```text
open
min
max
value
from
to
```

Não assumir presença de:

```text
close
low
high
```

---

# PARTE 2 — REGRA OHLC

Para cada timeframe presente no evento plural:

```text
open = candle.open
high = candle.max
low = candle.min
close = preço atual compatível com a vela
```

Para a vela aberta recebida em `candles-generated`, usar como close:

```text
event.msg.value
```

somente quando o evento corresponde ao mesmo active_id e à vela atual daquele timeframe.

Nunca usar:

- valor fixo;
- zero;
- fallback genérico;
- preço de outro ativo;
- preço de outro timeframe;
- campo inexistente convertido silenciosamente.

Validar:

```text
low <= open <= high
low <= close <= high
```

Como o preço atual pode estabelecer uma nova máxima ou mínima no mesmo evento, normalizar defensivamente:

```text
high = max(candle.max, candle.open, close)
low = min(candle.min, candle.open, close)
```

Isso utiliza somente valores reais presentes no evento.

---

# PARTE 3 — TIMESTAMP

Confirmar que:

```text
time = candle.from
```

em segundos Unix.

Não usar:

```text
event.at
```

como timestamp de abertura da vela.

`event.at` pode estar em nanossegundos e representa o instante da cotação, não necessariamente o início da vela.

Não multiplicar ou dividir incorretamente `from`.

Validar:

- M1 avança em blocos de 60 segundos;
- M5 avança em blocos de 300 segundos;
- M15 avança em blocos de 900 segundos;
- candles da mesma janela atualizam o mesmo timestamp;
- nova janela cria novo timestamp.

---

# PARTE 4 — TIPOS E DEFAULTS

Auditar:

- `models.py`
- `parser.py`
- `market_router.py`
- `market_store_adapter.py`
- `CandleStore`
- serialização da Chart API.

Proibir defaults silenciosos para OHLC.

Se algum campo obrigatório estiver ausente ou não for numérico:

```text
DROP_INVALID_MARKET_CANDLE
```

Registrar somente:

- active_id;
- raw_size;
- motivo sanitizado.

Não criar candle incompleto.

---

# PARTE 5 — AUDITORIA DE VALORES

Adicionar diagnóstico DEV sanitizado para uma pequena amostra, sem persistir preços indefinidamente:

```text
RAW:
open, min, max, value, from

NORMALIZED:
open, high, low, close, time
```

Limitar a no máximo 5 eventos em memória/teste.

Confirmar que não ocorre transformação como:

```text
1.136 → 1.20
1.136 → 1.30
1.136 → 1.05
```

---

# PARTE 6 — INTEGRIDADE DO CANDLESTORE

Garantir que o CandleStore:

- atualiza a vela existente quando o timestamp é igual;
- não duplica a vela aberta a cada tick;
- não propaga OHLC de um ativo para outro;
- não propaga M1 para M5/M15;
- não mistura IQ Option com Polarium;
- mantém chave por provider + active_id + raw_size.

---

# PARTE 7 — HISTÓRICO

Auditar de onde vieram os 200 candles mostrados.

Responder claramente:

- vieram do fluxo Polarium atual?
- vieram de persistência antiga?
- vieram da IQ Option?
- vieram de série selecionada incorretamente?
- foram criados pela normalização plural?
- possuem timestamps diferentes ou repetidos?

Quando a fonte Polarium for selecionada:

- não mostrar série de outro provider;
- não restaurar candles incompatíveis pelo símbolo;
- exigir chave correta do provider e active_id;
- limpar série visual ao trocar de provider/ativo.

Não apagar persistência global sem causa comprovada.

---

# PARTE 8 — TESTES

Adicionar testes para:

1. `min` vira `low`;
2. `max` vira `high`;
3. `value` vira `close` da vela aberta;
4. `from` vira timestamp da vela;
5. nanossegundos de `at` não viram tempo do candle;
6. mesmo timestamp atualiza a vela;
7. nova janela cria nova vela;
8. M1/M5/M15 permanecem independentes;
9. ativos diferentes permanecem independentes;
10. campo ausente causa drop, não default;
11. OHLC respeita low <= open/close <= high;
12. série IQ não aparece como Polarium;
13. série antiga incompatível não é renderizada;
14. nenhuma vela artificial é criada.

Executar:

```bash
.venv/bin/python -m pytest -q tests/market/providers/test_polarium_market_feed_runtime.py
.venv/bin/python -m pytest -q tests/market/providers/test_polarium_cdp_live_source.py
.venv/bin/python -m pytest -q tests/market/store tests/market/chart
.venv/bin/python -m pytest -q tests/frontend
.venv/bin/python -m pytest -q
```

Depois:

```bash
cd frontend
npm run build
cd ..
```

---

# PARTE 9 — VALIDAÇÃO VISUAL

Com sessão real Polarium:

1. abrir um ativo OTC M1;
2. aguardar pelo menos 10 candles reais ou carregar histórico real;
3. comparar lado a lado;
4. confirmar escala de preço coerente;
5. confirmar corpos e pavios naturais;
6. confirmar vela aberta atualizando;
7. confirmar ausência dos blocos gigantes idênticos;
8. trocar para M5;
9. trocar para M15;
10. trocar de ativo.

Se não houver candles reais suficientes:

```text
Aguardando dados do mercado...
```

Não preencher visualmente.

---

# ENTREGA ESPERADA

Entregar:

1. causa raiz comprovada;
2. origem dos 200 candles anômalos;
3. contrato raw encontrado;
4. mapeamento anterior;
5. mapeamento corrigido;
6. regra do close;
7. regra do timestamp;
8. arquivos modificados;
9. testes adicionados;
10. testes específicos;
11. suíte completa;
12. build;
13. amostra raw versus normalizada;
14. validação M1;
15. validação M5;
16. validação M15;
17. troca de ativo;
18. screenshot ou orientação para validação manual;
19. git status;
20. git diff;
21. riscos restantes;
22. sugestão de commit.

Não alterar estratégia.

Não implementar scanner.

Não criar candles sintéticos.

Não fazer commit.

Não fazer push.