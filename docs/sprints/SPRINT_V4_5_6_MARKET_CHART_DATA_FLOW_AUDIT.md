# Friday Trade — Sprint V4.5.6

# Market Chart IQ Option Data Flow Audit

## Status

PLANNED

---

## Objetivo

Auditar e corrigir o fluxo real de dados da tela `/market-chart`.

Não adicionar novas funcionalidades.

Não alterar a conexão IQ Option, o worker isolado, o runtime guard ou a persistência sem comprovar que a causa está nessas camadas.

Problema real:

```text
IQ Option é o único provider da experiência principal.
OTC não carrega ativos nem gráfico.
Mercado regular não carrega ativos nem gráfico.
A tela permanece em loading ou com zero candles.
```

O backend e endpoints já demonstraram capacidade de retornar ativos e candles em execuções anteriores.

A Sprint deve localizar exatamente onde os dados deixam de avançar entre:

```text
API
→ fetch
→ parsing
→ state React
→ seleção de símbolo
→ bootstrap
→ candles state
→ RealCandleChart
```

---

## Regra principal

Primeiro comprovar a causa.

Depois aplicar a menor correção possível.

Não criar outro worker.

Não criar outro provider.

Não criar outro endpoint sem necessidade comprovada.

Não adicionar novos retries, caches ou camadas antes de entender o fluxo atual.

---

## Escopo

Auditar:

```text
frontend/src/pages/MarketChart.tsx
frontend/src/components/chart/RealCandleChart
frontend/src/components/chart/RealCandleChart/sync.ts
API client usado pela tela
endpoints IQ Option já existentes
```

Revisar também somente quando necessário:

```text
app/api/routes/market_providers.py
runtime do provider IQ Option
worker persistente
```

---

## Evidência atual

Após a V4.5.5:

- Polarium foi retirada da experiência principal;
- IQ Option aparece como provider;
- seletor de mercado possui OTC e regular/aberto;
- nenhum dos dois mercados termina de carregar;
- nenhum ativo é exibido;
- nenhum gráfico é exibido.

Possíveis estados vistos:

```text
Carregando ativos...
Conectando à fonte...
0 candles
Ativo não identificado
```

A auditoria não deve assumir que o problema é somente backend ou frontend.

---

## Auditoria de ciclo completo

Criar rastreamento temporário e sanitizado para uma única execução da tela.

Usar prefixo:

```text
[IQ_FLOW]
```

Registrar apenas metadados, nunca candles completos ou credenciais.

Exemplo:

```text
[IQ_FLOW] page_mounted
[IQ_FLOW] market_selected OTC
[IQ_FLOW] status_request_started
[IQ_FLOW] status_request_finished 200
[IQ_FLOW] connect_started
[IQ_FLOW] connect_finished
[IQ_FLOW] assets_request_started
[IQ_FLOW] assets_request_finished count=14
[IQ_FLOW] assets_state_applied count=14
[IQ_FLOW] symbol_selected EURUSD-OTC
[IQ_FLOW] bootstrap_started
[IQ_FLOW] bootstrap_finished count=500
[IQ_FLOW] candles_state_applied count=500
[IQ_FLOW] chart_props count=500
```

Não registrar:

```text
e-mail
senha
token
cookie
headers
SSID
OHLC completo
payload bruto
```

Os logs temporários devem ser removidos ou condicionados a modo development antes da entrega final.

---

## Auditoria dos assets

Para OTC e REGULAR, verificar:

1. efeito responsável por carregar assets;
2. dependências do `useEffect`;
3. quantidade de vezes que executa;
4. criação do `AbortController`;
5. momento em que o controller é abortado;
6. status HTTP recebido;
7. corpo parseado;
8. propriedade usada para extrair assets;
9. chamada de `setAssets`;
10. qualquer `setAssets([])` posterior;
11. estado final do loading;
12. estado final do erro;
13. seleção automática do símbolo.

Contrato real esperado:

```json
{
  "provider": "IQ_OPTION",
  "market_type": "OTC",
  "assets": []
}
```

O frontend deve ler:

```text
response.assets
```

Não assumir:

```text
response.data.assets
```

sem compatibilidade explícita.

---

## Auditoria do mercado regular

Validar qual valor o backend aceita:

```text
REGULAR
OPEN
REAL
```

Não deixar divergência entre frontend e backend.

Escolher um contrato canônico, preferencialmente:

```text
OTC
REGULAR
```

O frontend e backend devem usar exatamente o mesmo valor.

Se não houver ativos regulares abertos:

```text
loading = false
assets = []
mensagem = Mercado regular fechado no momento.
```

Nunca manter loading infinito.

---

## Auditoria da conexão

Verificar se a tela entra em ciclo:

```text
status
→ connect
→ status
→ connect
```

Confirmar:

- somente uma promise de conexão;
- nenhuma conexão duplicada;
- assets aguardam conexão somente quando necessário;
- falha de assets não reinicia conexão indefinidamente;
- timeout encerra loading;
- worker persistente não é reiniciado em cada render.

---

## Auditoria de efeitos React

Mapear todos os `useEffect` da página.

Para cada um, documentar:

```text
responsabilidade
dependências
estado alterado
cleanup
requests iniciadas
```

Investigar:

- dependência instável criada a cada render;
- função não memorizada nas dependências;
- efeito cancelando a própria request;
- efeito resetando assets após sucesso;
- efeito resetando símbolo;
- efeito resetando candles;
- race condition entre mercado, símbolo e timeframe;
- Strict Mode executando lifecycle duplicado em desenvolvimento.

---

## AbortController

Verificar se o controller está sendo abortado prematuramente.

Regras:

- um controller por ciclo real;
- cleanup apenas quando contexto mudar ou componente desmontar;
- não abortar assets enquanto status/connect ainda está concluindo;
- não reutilizar controller já abortado;
- diferenciar abort esperado de erro real;
- abort não deve deixar loading infinito.

---

## Seleção automática do ativo

Depois de receber assets:

```text
preservar símbolo atual se válido
senão preferir EURUSD-OTC no OTC
senão selecionar primeiro ativo aberto
```

Para mercado regular:

```text
preservar símbolo atual se válido
senão selecionar primeiro ativo aberto
```

Após selecionar:

```text
selectedSymbol != vazio
bootstrap deve iniciar
```

Verificar se `chooseIqSymbol()` retorna o tipo esperado:

```text
string
```

e não o objeto completo.

---

## Auditoria do bootstrap

Quando houver:

```text
marketType
selectedSymbol
rawSize
```

o frontend deve executar exatamente uma carga inicial.

Verificar:

1. URL formada;
2. parâmetros;
3. status;
4. estrutura da resposta;
5. extração de candles;
6. quantidade;
7. normalização;
8. ordenação;
9. `setCandles`;
10. props recebidas pelo gráfico.

Contrato real observado anteriormente:

```json
{
  "provider": "IQ_OPTION",
  "market_type": "OTC",
  "symbol": "EURUSD-OTC",
  "raw_size": 60,
  "load": {},
  "chart": {
    "count": 500,
    "candles": []
  }
}
```

O frontend deve ler:

```text
response.chart.candles
response.chart.count
```

Não apenas:

```text
response.candles
```

---

## Auditoria do RealCandleChart

Confirmar que:

- componente é renderizado quando candles > 0;
- recebe array não vazio;
- `setData()` é chamado no bootstrap;
- `series.update()` é usado no polling;
- nenhum efeito posterior chama `setData([])`;
- nenhuma chave React força desmontagem contínua;
- tamanho do container não é zero;
- erro do Lightweight Charts não está sendo ocultado.

---

## Estado explícito da máquina

Simplificar o fluxo para estados claros:

```text
IDLE
CONNECTING
LOADING_ASSETS
ASSETS_READY
LOADING_CANDLES
CHART_READY
ERROR
MARKET_CLOSED
```

Não permitir combinações incoerentes como:

```text
loading assets = true
erro final definido
assets disponíveis
```

Se não for necessário criar reducer, manter estados atuais, mas garantir transições determinísticas.

---

## Timeout e recuperação

Toda operação deve terminar em:

```text
sucesso
erro
abort controlado
```

Nunca ficar pendente indefinidamente.

Tempos máximos sugeridos:

```text
status: 3s
connect: 8s
assets: 8s
candles: 10s
```

Ao atingir timeout:

```text
loading = false
erro sanitizado
botão Tentar novamente
```

Não recomeçar automaticamente em loop infinito.

---

## Correção mínima

Após encontrar a causa, corrigir somente os pontos comprovados.

Exemplos aceitáveis:

- corrigir parsing `response.assets`;
- corrigir parsing `response.chart.candles`;
- corrigir dependências de `useEffect`;
- corrigir controller abortado;
- corrigir contrato `REGULAR`;
- impedir reset posterior;
- corrigir seleção automática;
- corrigir loading infinito.

Não reescrever toda a página sem necessidade.

---

## Testes reais de frontend

Os testes atuais são majoritariamente estáticos.

Adicionar testes executáveis para a lógica pura extraída, quando possível:

```text
parseIqAssetsResponse
parseIqCandlesResponse
chooseIqSymbol
market type mapping
state transitions
```

Se o projeto ainda não tiver Vitest, criar funções puras testáveis pelos testes existentes ou configurar a menor estrutura necessária, justificando.

---

## Testes obrigatórios

Criar testes para:

1. parse de assets no nível principal;
2. parse opcional de `data.assets`;
3. assets OTC;
4. assets REGULAR;
5. mercado regular vazio encerra loading;
6. símbolo atual preservado;
7. EURUSD-OTC preferido;
8. primeiro ativo como fallback;
9. bootstrap somente após símbolo;
10. parse de `chart.candles`;
11. count vindo de `chart.count`;
12. candles aplicados ao state;
13. resposta vazia encerra loading;
14. erro encerra loading;
15. abort encerra loading corretamente;
16. nenhum `setAssets([])` após sucesso;
17. nenhum `setCandles([])` após sucesso;
18. Strict Mode não cria ciclo infinito;
19. status/connect não duplicados;
20. worker não reinicia por render;
21. timeout não deixa loading infinito;
22. RealCandleChart recebe candles;
23. OTC completo;
24. REGULAR completo;
25. suíte completa;
26. build.

---

## Validação manual obrigatória do FORGE

Antes de encerrar, executar aplicação e comprovar com navegador automatizado quando disponível:

### OTC

```text
mercado = OTC
assets count > 0
selectedSymbol preenchido
candles count > 0
gráfico renderizado
```

### REGULAR

Se houver ativo aberto:

```text
assets count > 0
selectedSymbol preenchido
candles count > 0
gráfico renderizado
```

Se estiver fechado:

```text
loading finalizado
mensagem de mercado fechado
```

Não declarar sucesso baseado somente em mocks.

Se navegador automatizado não estiver disponível, executar endpoints reais e documentar claramente que a validação visual ainda depende do Renan.

---

## Diagnóstico final obrigatório

Entregar a cadeia com resultado real:

```text
API assets:
Parsing assets:
React assets state:
Selected symbol:
API candles:
Parsing candles:
React candles state:
RealCandleChart props:
Render final:
```

Para cada etapa:

```text
OK
FAILED
```

Informar arquivo e linha onde o dado era perdido.

---

## Entrega obrigatória

1. Objetivo.
2. Causa raiz comprovada.
3. Linha/efeito onde assets eram perdidos.
4. Linha/efeito onde candles eram perdidos.
5. Auditoria dos `useEffect`.
6. Auditoria do AbortController.
7. Contrato OTC.
8. Contrato REGULAR.
9. Parsing de assets.
10. Seleção automática.
11. Parsing de candles.
12. Bootstrap.
13. RealCandleChart.
14. Correção mínima aplicada.
15. Arquivos criados.
16. Arquivos modificados.
17. Testes específicos.
18. Suíte completa.
19. Build.
20. Validação real OTC.
21. Validação real REGULAR.
22. Como testar para o Renan.
23. Riscos.
24. `git status --short`.
25. `git diff --stat`.
26. Sugestão de commit.

Mensagem sugerida:

```text
fix(market-chart): repair IQ Option data flow and rendering
```

---

## Regra final

Não fazer commit.

Não fazer push.

Não adicionar funcionalidade nova.

Não alterar credenciais.

Não instalar iqoptionapi na `.venv` principal.

Não consultar saldo.

Não executar ordens.

Não afirmar que resolveu sem comprovar toda a cadeia API → gráfico.