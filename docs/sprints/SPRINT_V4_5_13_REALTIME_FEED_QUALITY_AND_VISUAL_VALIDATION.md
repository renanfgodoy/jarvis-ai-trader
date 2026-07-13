# SPRINT V4.5.13 — REALTIME FEED QUALITY AND VISUAL VALIDATION

## Objetivo

Validar tecnicamente e visualmente a qualidade do realtime candle feed da IQ Option utilizado pelo Friday Trade.

A Sprint V4.5.12 implementou:

- subscription read-only `candle-generated`;
- cache realtime no worker persistente;
- endpoint de realtime candles;
- atualização incremental da vela;
- reconciliação por snapshot;
- classificação `NEAR_REALTIME`, `SNAPSHOT`, `STALE` e `NO_DATA`.

Esta Sprint não deve criar nova arquitetura.

O objetivo agora é provar:

1. quais ativos realmente entregam realtime utilizável;
2. qual é a cadência real;
3. onde existem congelamentos ou jitter;
4. se a vela abre e fecha corretamente;
5. se Friday e corretora apresentam direção e OHLC compatíveis;
6. se o status visual representa corretamente a qualidade do feed.

---

# REGRA PRINCIPAL

Não alterar a arquitetura antes de medir.

Não criar WebSocket ou SSE frontend nesta Sprint.

Não aumentar frequência por impulso.

Não inventar preços.

Não interpolar movimentos.

Não afirmar igualdade com a corretora sem evidência visual e temporal.

Aplicar correção somente se uma falha concreta for comprovada.

---

# PARTE 1 — MÉTRICAS DE QUALIDADE

## 1. Ativos obrigatórios

Auditar os seguintes ativos quando estiverem disponíveis:

### Controles prioritários

```text
EURUSD-OTC
GBPUSD-OTC
USDJPY-OTC
EURJPY-OTC
```

### Ativos adicionais

Usar até seis ativos adicionais compatíveis com candles e classificados como abertos.

Dar preferência a:

```text
AUDCAD-OTC
AUDUSD-OTC
EURGBP-OTC
GBPJPY-OTC
USDCHF-OTC
NZDUSD-OTC
```

Se algum não existir na lista atual, usar outro ativo OTC compatível e registrar a substituição.

### Ativos problemáticos conhecidos

```text
CADCHF
AMAZON
```

### Mercado regular

Usar pelo menos um ativo regular realmente aberto e compatível no horário do teste.

Não classificar mercado fechado como falha técnica.

---

## 2. Duração

Observar cada ativo por no mínimo:

```text
60 segundos
```

Os quatro controles prioritários devem ser observados por:

```text
180 segundos
```

EURUSD-OTC deve possuir também um teste contínuo de:

```text
10 minutos
```

---

## 3. Métricas por ativo

Registrar:

```text
events_read
```

Quantidade de leituras do cache realtime.

```text
ohlc_changes
```

Quantidade de alterações reais em timestamp, close, high ou low.

```text
new_candles
```

Quantidade de novos buckets de vela.

```text
identical_reads
```

Quantidade de leituras sem mudança.

```text
movement_rate_per_second
```

```text
average_movement_interval_ms
```

```text
p50_movement_interval_ms
```

```text
p95_movement_interval_ms
```

```text
maximum_movement_gap_ms
```

```text
average_http_cycle_ms
```

```text
p95_http_cycle_ms
```

```text
stale_transitions
```

```text
stream_restarts
```

```text
errors
```

---

## 4. Jitter

Calcular o jitter dos intervalos entre movimentos reais.

Apresentar:

- média;
- desvio padrão;
- p50;
- p95;
- maior gap;
- quantidade de gaps acima de 2 segundos;
- quantidade de gaps acima de 3 segundos;
- quantidade de gaps acima de 5 segundos.

Separar claramente:

```text
ausência real de movimento de preço
```

de:

```text
falha na chegada dos eventos
```

Quando possível, usar o campo de timestamp/at recebido da IQ Option para diferenciar as duas situações.

---

## 5. Classificação oficial por ativo

Classificar cada ativo em:

### EXCELLENT

- feed recente;
- eventos progressivos;
- p95 de movimento abaixo de 2 segundos;
- sem gaps técnicos superiores a 3 segundos;
- abertura e fechamento de vela corretos.

### GOOD

- feed recente;
- movimento utilizável;
- p95 até 3 segundos;
- poucos gaps;
- sem staleness recorrente.

### LIMITED

- feed recente, mas com poucos movimentos;
- snapshot predominante;
- grandes intervalos;
- adequado apenas para leitura não instantânea.

### STALE

- último candle antigo;
- série imutável;
- não utilizável para análise.

### NO_DATA

- nenhum candle utilizável.

Não atribuir EXCELLENT ou GOOD apenas por quantidade de chamadas HTTP.

---

# PARTE 2 — AUDITORIA DA ABERTURA E FECHAMENTO

## 6. Transição de vela M1

Para pelo menos:

```text
EURUSD-OTC
GBPUSD-OTC
```

observar duas transições completas de vela M1.

Registrar:

1. timestamp da vela anterior;
2. OHLC final antes do fechamento;
3. horário local da virada;
4. horário do primeiro evento do novo bucket;
5. open da nova vela;
6. diferença entre close anterior e open novo;
7. tempo para a nova vela aparecer no Friday;
8. se houve vela duplicada;
9. se houve bucket perdido;
10. se uma resposta atrasada alterou a vela anterior.

---

## 7. M5 e M15

Executar ao menos uma validação por timeframe:

```text
M5
M15
```

Confirmar:

- bucket correto;
- countdown correto;
- histórico correto;
- candle atual correto;
- stream não mistura timeframe;
- troca de timeframe limpa contexto anterior.

Não é necessário esperar o fechamento completo de uma M15 se isso tornar a Sprint excessivamente longa.

Nesse caso, validar o bucket e a atualização da vela aberta.

---

# PARTE 3 — VALIDAÇÃO VISUAL LADO A LADO

## 8. Preparação visual

Abrir simultaneamente:

### Lado esquerdo

Gráfico da IQ Option.

### Lado direito

Friday Trade em:

```text
http://localhost:5173/market-chart
```

Configurar nos dois:

- mesmo ativo;
- mesmo timeframe;
- mesma janela aproximada;
- mesmo período visual quando possível.

Não comparar Friday com Polarium.

---

## 9. Ativos para comparação visual

Obrigatórios:

```text
EURUSD-OTC
GBPUSD-OTC
```

Opcional adicional:

```text
USDJPY-OTC
```

CADCHF deve ser usado somente para comprovar visualmente o estado STALE, caso continue sem feed atual.

---

## 10. Pontos de comparação visual

Comparar:

- direção da vela atual;
- preço de abertura;
- preço atual/close;
- máxima;
- mínima;
- instante de mudança de cor;
- instante de formação de novo high;
- instante de formação de novo low;
- horário de abertura da nova vela;
- cadência aparente;
- gaps visuais;
- tamanho relativo do corpo;
- pavios;
- timestamp do candle.

Não exigir igualdade de escala vertical, zoom ou largura das velas.

---

## 11. Capturas obrigatórias

Produzir evidência visual, quando possível, de:

### Captura A — Feed ativo

IQ Option e Friday mostrando o mesmo ativo e timeframe.

### Captura B — Vela em movimento

Captura durante alteração da vela aberta.

### Captura C — Nova vela

Captura logo após a abertura de uma nova vela.

### Captura D — Feed stale

CADCHF ou outro ativo stale, mostrando:

```text
DADOS ATRASADOS
```

e o histórico preservado.

### Captura E — Indicador visual

Card ou bloco contendo:

- modo da fonte;
- último evento;
- última mudança;
- próxima vela;
- readiness.

Se o FORGE não puder gerar print automaticamente, deve descrever exatamente o roteiro manual para o Renan.

---

# PARTE 4 — INDICADOR VISUAL DE CONFIANÇA

## 12. Revisar o card atual

Auditar se o Friday mostra claramente:

```text
STATUS DO FEED
```

```text
NEAR REALTIME
SNAPSHOT
STALE
NO DATA
CHECKING
```

Também deve exibir, quando disponível:

- último movimento;
- último evento;
- último candle;
- próxima vela;
- frequência recente;
- readiness.

---

## 13. Linguagem visual

Exibir textos em português:

```text
PRÓXIMO DO TEMPO REAL
```

```text
ATUALIZAÇÃO POR SNAPSHOT
```

```text
DADOS ATRASADOS
```

```text
SEM DADOS
```

```text
VERIFICANDO FEED
```

Não depender apenas de termos técnicos em inglês.

Pode exibir o modo técnico em tamanho secundário.

Exemplo:

```text
PRÓXIMO DO TEMPO REAL
NEAR_REALTIME
```

---

## 14. Cadência recente

Mostrar uma métrica simples e compreensível:

```text
Movimentos: 0,9/s
```

ou:

```text
Último movimento: há 1,2s
```

Não mostrar falsas casas decimais.

Não chamar leituras idênticas de movimentos.

---

## 15. Aviso operacional

Regras visuais:

### EXCELLENT ou GOOD

```text
FEED VALIDADO
Análise disponível
```

### LIMITED ou SNAPSHOT

```text
FEED LIMITADO
Evite estratégias de entrada instantânea
```

### STALE

```text
ANÁLISE BLOQUEADA
Não utilize este gráfico
```

### NO_DATA

```text
ANÁLISE BLOQUEADA
Sem candles disponíveis
```

Ainda não gerar CALL ou PUT.

---

# PARTE 5 — TESTE DE ISOLAMENTO

## 16. Troca rápida de ativos

Executar:

```text
EURUSD-OTC
→ GBPUSD-OTC
→ USDJPY-OTC
→ EURUSD-OTC
```

Confirmar:

- stream anterior encerrado;
- somente um contexto ativo;
- nenhum evento do ativo anterior aparece no atual;
- métricas reiniciadas;
- card volta para CHECKING;
- série correta carregada.

---

## 17. Troca de timeframe

Executar:

```text
M1
→ M5
→ M15
→ M1
```

Confirmar:

- subscription correta;
- raw_size correto;
- countdown correto;
- bucket correto;
- nenhuma mistura de candles.

---

## 18. Background e retomada

Com o gráfico aberto:

1. deixar a aba em segundo plano por aproximadamente 30 segundos;
2. retornar;
3. verificar se:
   - o stream continua válido;
   - o frontend reconcilia;
   - não aparecem gaps falsos;
   - não duplica subscriptions;
   - o estado visual é recalculado.

---

# PARTE 6 — TESTES AUTOMATIZADOS

## 19. Worker/provider

Adicionar ou ajustar testes para:

1. stream retorna metadata suficiente para métricas;
2. timestamp do último evento é preservado;
3. leitura idêntica não conta como movimento;
4. mudança de OHLC conta como movimento;
5. novo bucket conta como nova vela;
6. símbolo anterior é isolado;
7. stop anterior ocorre na troca;
8. disconnect limpa stream;
9. nenhuma chamada proibida;
10. estado stale é preservado.

Executar:

```bash
.venv/bin/python -m pytest tests/market/providers tests/market/store -q
```

---

## 20. Frontend

Adicionar ou ajustar testes para:

1. card mostra modo em português;
2. último movimento usa OHLC real;
3. leitura idêntica não atualiza movimento;
4. frequência recente é calculada corretamente;
5. CHECKING aparece na troca;
6. STALE bloqueia análise;
7. SNAPSHOT mostra ressalva;
8. troca de ativo limpa métricas;
9. troca de timeframe limpa métricas;
10. relógio de 1 segundo não realiza fetch;
11. polling realtime continua em 1 segundo;
12. polling de reconciliação continua em 5 segundos.

Executar:

```bash
.venv/bin/python -m pytest tests/frontend -q
```

---

## 21. Suíte e build

```bash
.venv/bin/python -m pytest -q
```

```bash
cd frontend
npm run build
cd ..
```

---

# PARTE 7 — CORREÇÕES PERMITIDAS

## 22. Correção mínima

Somente corrigir se houver evidência de:

- stream não sendo encerrado;
- dados de ativo anterior contaminando o atual;
- polling realtime parando;
- resposta antiga sobrescrevendo nova;
- candle duplicado;
- bucket incorreto;
- card classificando feed incorretamente;
- contador incorreto;
- frontend redesenhando sem mudança;
- atraso local desnecessário.

Não criar WebSocket/SSE frontend nesta Sprint.

Não mudar a frequência de 1 segundo sem prova.

Não fazer animação artificial.

---

# PARTE 8 — ENTREGA ESPERADA

Entregar relatório contendo:

1. ativos testados;
2. duração por ativo;
3. tabela completa das métricas;
4. ranking EXCELLENT/GOOD/LIMITED/STALE/NO_DATA;
5. média, p50, p95 e maior gap;
6. quantidade de gaps acima de 2s, 3s e 5s;
7. resultado do teste de 10 minutos;
8. resultado da transição de vela M1;
9. resultado M5;
10. resultado M15;
11. resultado da troca de ativos;
12. resultado da troca de timeframe;
13. resultado de background/retomada;
14. comparação visual EURUSD-OTC;
15. comparação visual GBPUSD-OTC;
16. comparação visual CADCHF stale;
17. capturas geradas ou roteiro manual exato;
18. diferença visual observada em relação à corretora;
19. qualidade do indicador visual;
20. readiness final;
21. causa de qualquer microcongelamento;
22. correção aplicada, se necessária;
23. arquivos modificados;
24. diff funcional por arquivo;
25. testes worker/provider/store;
26. testes frontend;
27. suíte completa;
28. build;
29. Runtime Guard;
30. limitações;
31. `git status --short`;
32. `git diff --stat`;
33. riscos restantes;
34. sugestão de commit.

Não fazer commit.

Não fazer push.

Não criar arquitetura nova.

Não ocultar ativo ruim ou resultado inconclusivo.