# FRIDAY TRADE V3.3
# INDICATOR ENGINE FOUNDATION

Status

PLANNED

---

# Objetivo

Criar a fundação do Indicator Engine do Friday Trade.

O Indicator Engine será responsável por executar indicadores técnicos sobre séries de candles normalizados armazenados no Candle Store.

Esta Sprint NÃO implementa EMA.

Esta Sprint NÃO implementa RSI.

Esta Sprint NÃO implementa MACD.

Esta Sprint NÃO implementa sinais.

Esta Sprint NÃO implementa IA.

Esta Sprint NÃO implementa Probability Engine.

Esta Sprint NÃO altera frontend.

Esta Sprint NÃO abre WebSocket.

Esta Sprint NÃO altera Connector.

Esta Sprint NÃO altera APIs.

---

# Arquitetura alvo

Criar:

```text
app/indicators/
    __init__.py
    engine.py
    registry.py
    models.py
    base.py
    errors.py