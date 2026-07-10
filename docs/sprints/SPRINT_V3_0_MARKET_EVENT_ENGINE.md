# FRIDAY TRADE V3.0
# MARKET EVENT ENGINE

## Status

PLANNED

---

# Objetivo

Criar o primeiro núcleo de código responsável por receber mensagens WebSocket sanitizadas da Polarium, identificar o tipo de evento e normalizar eventos de candle em contratos internos do Friday Trade.

Esta Sprint NÃO conecta automaticamente ao WebSocket real.

Esta Sprint NÃO altera o Connector em produção.

Esta Sprint NÃO altera frontend.

Esta Sprint NÃO cria indicadores.

Esta Sprint NÃO cria IA.

Esta Sprint NÃO cria sinais.

Esta Sprint NÃO executa ordens.

O objetivo é construir uma camada passiva, testável e baseada apenas nos eventos reais já documentados.

---

# Contexto confirmado

A investigação autorizada confirmou eventos reais:

- `first-candles`
- `candle-generated`
- `candles-generated`
- `digital-option-client-price-generated`
- `timeSync`
- `subscribeMessage`
- `unsubscribeMessage`

Campos reais confirmados em eventos de candle:

- `active_id`
- `size`
- `from`
- `to`
- `open`
- `close`
- `min`
- `max`
- `volume`

Mapeamentos ainda parciais:

- `min → low`
- `max → high`
- `size=60 → M1`
- `size=300 → M5`
- `size=900 → M15`
- `active_id → símbolo visual`

Esses pontos devem continuar explicitamente classificados como parciais.

---

# Antes de começar

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

pwd
git rev-parse --show-toplevel
git branch --show-current
git status --short

.venv/bin/python -m pytest -q

cd frontend
npm run build
```

Se o working tree não estiver limpo, interromper e relatar.

---

# Arquitetura alvo

Criar:

```text
app/market/events/
    __init__.py
    event_types.py
    router.py
    models.py
    parsers/
        __init__.py
        candle_generated.py
        first_candles.py
```

Responsabilidades:

## event_types.py

Centralizar nomes de eventos suportados.

Exemplo:

- `candle-generated`
- `first-candles`
- `candles-generated`
- `timeSync`

Não espalhar strings pelo código.

## router.py

Receber uma mensagem já decodificada como `dict`.

Identificar o campo do evento.

Encaminhar para o parser apropriado.

Eventos desconhecidos devem retornar resultado controlado.

Nunca lançar exceção por evento não suportado sem contexto.

## models.py

Definir contratos internos fortemente tipados para:

- evento bruto sanitizado;
- resultado de roteamento;
- candle normalizado;
- erro de parsing;
- metadados de origem.

Reutilizar `MarketDataCandle` existente quando fizer sentido.

Evitar duplicar modelos.

## parsers/candle_generated.py

Normalizar um único evento `candle-generated`.

Mapeamento permitido:

```text
active_id → active_id
size → raw_size
from → start_timestamp
to → end_timestamp
open → open
close → close
min → low_candidate
max → high_candidate
volume → volume
```

Não promover `min` e `max` a `low` e `high` como confirmação definitiva sem preservar metadado de evidência.

## parsers/first_candles.py

Normalizar coleção inicial de candles quando a estrutura real permitir.

Deve aceitar payloads parciais e retornar erros estruturados por item inválido.

Não descartar silenciosamente problemas.

---

# Fonte de dados para testes

Usar apenas fixtures sanitizadas derivadas de:

```text
docs/ws/POLARIUM_HAR_CANDLE_EVIDENCE_SANITIZED.md
docs/ws/POLARIUM_DIRECTED_CORRELATION.md
```

Não ler o HAR bruto durante os testes.

Não versionar HAR.

Não copiar segredos.

Não criar fixtures sintéticas que contradigam os payloads reais documentados.

---

# Testes obrigatórios

Criar testes para:

- evento `candle-generated` válido;
- evento sem `name`;
- evento desconhecido;
- payload sem `msg`;
- candle com campo obrigatório ausente;
- tipos numéricos inválidos;
- `first-candles` com lista válida;
- `first-candles` com um item inválido;
- preservação de `active_id`;
- preservação de `size`;
- preservação de timestamps;
- preservação de volume;
- nenhum símbolo inventado;
- nenhum timeframe visual inventado.

Estrutura sugerida:

```text
tests/market/events/
```

---

# Regras de normalização

O parser deve produzir um contrato honesto.

Exemplo conceitual:

```text
active_id: 76
symbol: None
raw_size: 60
timeframe: None
start_timestamp: ...
end_timestamp: ...
open: ...
high: ...
low: ...
close: ...
volume: ...
source: "polarium"
source_verified: True
mapping_verified: False
```

Não inventar `symbol`.

Não inventar `M1`.

Não afirmar que `min/max` são definitivos sem registrar a natureza do mapeamento.

---

# Segurança

Nunca incluir em logs ou fixtures:

- token
- cookie
- Authorization
- bearer
- refresh token
- SSID
- e-mail
- senha
- headers privados
- dados de sessão

Nenhum fixture deve vir diretamente do HAR bruto sem sanitização.

---

# Fora do escopo

Não integrar ao Connector.

Não abrir WebSocket.

Não alterar rotas.

Não criar endpoint.

Não alterar frontend.

Não criar Candle Store.

Não criar indicadores.

Não criar IA.

Não criar Probability Engine.

Não criar Replay automático.

Não executar ordem.

---

# Documentação

Atualizar apenas se necessário:

```text
docs/ARCHITECTURE.md
docs/REAL_MARKET_DATA_REPORT.md
CHANGELOG.md
ROADMAP.md
```

Registrar claramente:

- Market Event Engine ainda passivo;
- sem runtime;
- sem conexão automática;
- baseado em fixtures sanitizadas;
- próximo passo: integração controlada ou Candle Store.

---

# Como testar

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

.venv/bin/python -m pytest -q
```

Executar build:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend

npm run build
```

Executar testes específicos, se criados:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

.venv/bin/python -m pytest -q tests/market/events
```

---

# Critérios de aprovação

- Event Router criado.
- Eventos suportados centralizados.
- `candle-generated` normalizado.
- `first-candles` normalizado quando possível.
- Eventos desconhecidos tratados com segurança.
- Nenhum símbolo inventado.
- Nenhum timeframe visual inventado.
- Nenhum runtime alterado.
- Nenhuma API alterada.
- Connector inalterado.
- Fixtures sanitizadas.
- Testes novos passando.
- Suíte completa passando.
- Frontend build passando.

---

# Entrega obrigatória

1. Objetivo.
2. Arquitetura implementada.
3. Arquivos criados.
4. Arquivos modificados.
5. Eventos suportados.
6. Contratos criados ou reutilizados.
7. Mapeamento aplicado.
8. Mapeamentos mantidos como parciais.
9. Fixtures utilizadas.
10. Testes criados.
11. Resultado dos testes específicos.
12. Resultado completo do pytest.
13. Resultado do build.
14. Como testar.
15. Riscos conhecidos.
16. Débitos técnicos.
17. Documentação atualizada.
18. `git status --short`.
19. `git diff --stat`.
20. Sugestão de commit.

Mensagem sugerida:

```text
feat(market): introduce passive Polarium Market Event Engine
```

---

# Regra final

NÃO faça commit.

NÃO faça push.

Se a estrutura real dos payloads sanitizados não for suficiente para implementar algum parser com segurança, implemente apenas a parte comprovada e documente a limitação.