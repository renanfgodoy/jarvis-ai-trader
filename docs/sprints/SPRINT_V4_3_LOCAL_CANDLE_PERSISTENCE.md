# Friday Trade — Sprint V4.3

# Local Candle Persistence

## Status

PLANNED

---

## Objetivo

Implementar persistência local dos candles reais recebidos pelo fluxo oficial da Polarium.

O objetivo é impedir que o gráfico volte a iniciar totalmente vazio após o backend ser reiniciado.

Fluxo atual:

```text
backend reinicia
→ CandleStore em memória é zerado
→ gráfico começa vazio
→ candles voltam a aparecer lentamente
```

Fluxo desejado:

```text
backend inicia
→ candles locais são restaurados
→ CandleStore é preenchido
→ gráfico abre com histórico já capturado
→ Browser Bridge continua atualizando em tempo real
```

A persistência deve armazenar exclusivamente candles reais já normalizados.

Não armazenar payload bruto.

Não armazenar credenciais.

Não armazenar eventos privados.

---

## Escopo

Implementar:

- persistência local de candles normalizados;
- restauração automática ao iniciar o backend;
- merge com candles recebidos em tempo real;
- separação por `active_id + raw_size`;
- deduplicação;
- atualização de candle existente;
- retenção limitada;
- limpeza controlada;
- status sanitizado;
- testes de segurança e consistência.

---

## Fluxo oficial

```text
Polarium
→ Browser Bridge
→ Payload Adapter
→ MarketPipeline
→ CandleStore
→ Local Candle Repository
→ Chart API
→ RealCandleChart
```

Ao iniciar o backend:

```text
Local Candle Repository
→ restaura candles
→ CandleStore compartilhado
→ Chart API
```

Não criar outra fonte de mercado.

Não criar outro CandleStore.

---

## Decisão tecnológica

Utilizar banco local:

```text
SQLite
```

Preferencialmente por biblioteca já disponível no Python padrão:

```text
sqlite3
```

Não adicionar dependência externa se não for necessário.

O banco deve ficar em:

```text
.jarvis_cache/market/candles.sqlite3
```

ou caminho equivalente dentro de `.jarvis_cache`.

O arquivo deve permanecer ignorado pelo Git.

---

## Segurança

Nunca persistir:

```text
token
cookie
Authorization
bearer
SSID
password
credentials
headers
request_id privado
payload bruto
HAR
saldo
conta
ordens
posições
execução
```

Persistir somente campos normalizados necessários:

```text
active_id
raw_size
start_timestamp
end_timestamp
open
close
low_candidate
high_candidate
volume
mapping_verified
created_at
updated_at
```

Preservar:

```text
symbol = None
timeframe = None
mapping_verified = False
```

Enquanto não houver evidência oficial de mapeamento.

---

## Arquitetura sugerida

Criar camada:

```text
app/market/persistence/
```

Arquivos sugeridos:

```text
__init__.py
models.py
repository.py
sqlite_repository.py
service.py
```

Responsabilidades:

### `models.py`

Contratos de persistência e status.

### `repository.py`

Interface/protocolo abstrato de repositório.

### `sqlite_repository.py`

Implementação SQLite local.

### `service.py`

Coordenação entre persistência e CandleStore.

Não colocar SQL dentro de rota API.

Não misturar persistência com parser.

Não misturar persistência com Browser Bridge.

---

## Schema SQLite

Tabela sugerida:

```text
market_candles
```

Campos:

```text
active_id INTEGER NOT NULL
raw_size INTEGER NOT NULL
start_timestamp INTEGER NOT NULL
end_timestamp INTEGER
open REAL NOT NULL
close REAL NOT NULL
low_candidate REAL NOT NULL
high_candidate REAL NOT NULL
volume REAL
mapping_verified INTEGER NOT NULL DEFAULT 0
created_at TEXT NOT NULL
updated_at TEXT NOT NULL
```

Chave única:

```text
active_id + raw_size + start_timestamp
```

Criar índice para:

```text
active_id + raw_size + start_timestamp
```

---

## Política de escrita

Quando o CandleStore recebe candle válido:

### Candle novo

```text
INSERT
```

### Mesmo timestamp e mesmos dados

```text
IGNORE
```

### Mesmo timestamp e dados diferentes

```text
UPDATE
```

A persistência deve refletir as mesmas regras do CandleStore.

Não duplicar regra de negócio de forma divergente.

---

## Integração com CandleStore

O `CandleStore` compartilhado continua sendo a fonte em memória para runtime e Chart API.

A persistência funciona como apoio:

```text
Pipeline
→ CandleStore
→ Persistence Service
```

ou por mecanismo equivalente seguro.

Não criar escrita direta no SQLite a partir do Browser Bridge.

Não pular o MarketPipeline.

---

## Restauração no startup

Ao iniciar o backend:

1. inicializar o SQLite;
2. criar schema se necessário;
3. carregar candles persistidos;
4. ordenar por timestamp;
5. preencher o mesmo `market_candle_store` compartilhado;
6. iniciar API;
7. continuar aceitando eventos ao vivo.

A restauração deve ocorrer uma única vez por processo.

Não duplicar candles em restart.

---

## Retenção

Manter limite por série.

Sugestão inicial:

```text
1000 candles por active_id + raw_size
```

Quando ultrapassar:

- remover somente candles mais antigos;
- preservar os mais recentes;
- nunca apagar candle atual;
- executar retenção de forma controlada.

A retenção deve ser configurável em código/configuração segura.

---

## Chart API

A Chart API existente deve continuar funcionando sem mudança de contrato.

Depois do startup:

```text
GET /api/v1/market/chart/series
```

deve listar séries restauradas.

```text
GET /api/v1/market/chart
```

deve retornar candles persistidos imediatamente.

Não criar endpoint paralelo para leitura.

---

## Status sanitizado

Adicionar status read-only:

```text
market_persistence
```

Pode ficar em endpoint próprio ou status técnico existente.

Campos:

```text
enabled
database_ready
restored_series_count
restored_candles_count
persisted_series_count
persisted_candles_count
last_write_at
last_restore_at
last_cleanup_at
retention_per_series
database_path_sanitized
last_error_code
```

Nunca retornar caminho absoluto completo contendo dados pessoais.

Exemplo sanitizado:

```text
.jarvis_cache/market/candles.sqlite3
```

---

## Endpoint de limpeza controlada

Criar somente se necessário:

```text
DELETE /api/v1/market/persistence/candles
```

ou endpoint equivalente.

Requisitos:

- desenvolvimento/local only;
- não aceitar credenciais;
- confirmação explícita no request;
- limpar SQLite e CandleStore;
- retornar contagem removida;
- não afetar outras configurações;
- não apagar tokens/OAuth/cache de sessão.

Caso não seja necessário nesta Sprint, documentar método administrativo seguro em código/teste.

---

## Comportamento visual esperado

### Primeiro uso

```text
sem histórico persistido
→ gráfico começa com poucos candles
→ histórico cresce
→ candles são salvos
```

### Segundo uso

```text
backend reinicia
→ candles restaurados
→ gráfico abre imediatamente com histórico capturado
→ stream real continua atualizando
```

### Troca de ativo

```text
ativo já conhecido
→ histórico restaurado imediatamente

ativo novo
→ começa com dados disponíveis
→ cresce e passa a ser persistido
```

---

## Não alterar

Não alterar:

- Browser Bridge funcional;
- Payload Adapter;
- Market Event Engine;
- MarketPipeline;
- formato dos candles normalizados;
- Chart API pública;
- frontend, salvo indicador visual mínimo de persistência se estritamente necessário;
- OAuth;
- Connector;
- execução;
- AutoTrade;
- IA;
- indicadores.

---

## Não implementar

Não implementar:

- histórico externo;
- API pública de terceiros;
- candles sintéticos;
- interpolação;
- mapeamento falso de ativos;
- sinais;
- CALL;
- PUT;
- IA;
- EMA;
- RSI;
- MACD;
- execução automática.

---

## Migração e compatibilidade

O banco deve:

- ser criado automaticamente;
- aceitar banco vazio;
- não quebrar em arquivo inexistente;
- lidar com banco corrompido com erro sanitizado;
- não apagar dados automaticamente em erro;
- permitir evolução futura de schema.

Adicionar versão de schema:

```text
schema_version
```

ou mecanismo simples equivalente.

---

## Testes obrigatórios

Criar testes para:

1. criação do banco;
2. criação do schema;
3. insert de candle;
4. ignore de duplicado idêntico;
5. update de candle existente;
6. separação por `active_id`;
7. separação por `raw_size`;
8. ordenação por timestamp;
9. restauração no startup;
10. restauração no mesmo CandleStore compartilhado;
11. restart não duplica candles;
12. retenção por série;
13. retenção remove somente os mais antigos;
14. múltiplas séries;
15. banco vazio;
16. arquivo inexistente;
17. erro SQLite sanitizado;
18. nenhuma credencial persistida;
19. nenhum payload bruto persistido;
20. `symbol=None` preservado;
21. `timeframe=None` preservado;
22. `mapping_verified=False` preservado;
23. Chart API retorna dados restaurados;
24. Browser Bridge continua atualizando após restore;
25. limpeza controlada;
26. status sanitizado;
27. banco permanece dentro de `.jarvis_cache`;
28. arquivo SQLite ignorado pelo Git;
29. suíte completa sem regressão;
30. build frontend aprovado.

---

## Validação real obrigatória

Após implementação:

### Etapa 1 — Captura inicial

1. iniciar backend;
2. iniciar frontend;
3. abrir Polarium;
4. deixar candles reais serem capturados;
5. confirmar gráfico com alguns candles;
6. verificar status de persistência;
7. anotar quantidade.

### Etapa 2 — Reinício

1. parar backend;
2. manter frontend ou reabrir depois;
3. iniciar backend novamente;
4. não depender de novos candles;
5. abrir `/market-chart`;
6. confirmar histórico restaurado imediatamente;
7. confirmar mesma quantidade ou quantidade próxima;
8. confirmar stream real retomando atualizações.

### Etapa 3 — Git

Confirmar:

```bash
git status --short
```

O arquivo:

```text
.jarvis_cache/market/candles.sqlite3
```

não pode aparecer.

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
2. Arquitetura implementada.
3. Tecnologia escolhida.
4. Caminho do banco.
5. Schema.
6. Arquivos criados.
7. Arquivos modificados.
8. Integração com CandleStore.
9. Integração com MarketPipeline.
10. Política de insert/update/ignore.
11. Restauração no startup.
12. Retenção.
13. Status sanitizado.
14. Limpeza controlada.
15. Segurança.
16. Testes criados.
17. Resultado dos testes específicos.
18. Resultado da suíte completa.
19. Resultado do build.
20. Como testar para o Renan.
21. Validação real necessária.
22. Riscos conhecidos.
23. Débitos técnicos.
24. `git status --short`.
25. `git diff --stat`.
26. Sugestão de commit.

Mensagem sugerida:

```text
feat(market): persist real candle history locally
```

---

## Regra final

Não fazer commit.

Não fazer push.

Não persistir credenciais.

Não persistir payload bruto.

Não criar candles sintéticos.

A persistência deve armazenar somente candles reais normalizados já recebidos pelo fluxo oficial.