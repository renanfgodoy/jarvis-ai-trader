# SPRINT V4.5.17A — ASSET LIST REGRESSION HOTFIX

## Objetivo

Auditar e corrigir a regressão que fez a lista de ativos da IQ Option deixar de exibir os ativos disponíveis no dropdown do `/market-chart`.

Sintoma observado manualmente:

- o gráfico de `EURUSD-OTC` continua carregando;
- o ativo fallback continua selecionado;
- o dropdown mostra apenas `EUR/USD OTC`;
- aparece a mensagem:

```text
Nenhum ativo OTC disponível
```

- a lista completa de ativos não aparece;
- o gráfico e os candles continuam funcionando;
- o bug surgiu após as Sprints recentes de UI.

Esta Sprint é um hotfix cirúrgico.

Não criar nova arquitetura.

Não alterar componentes fora do necessário.

---

## Regra principal

Não assumir que o problema está no React sem auditar a resposta real da API.

Primeiro comprovar onde a lista desaparece:

```text
API
→ parsing
→ state
→ filtro
→ options
→ dropdown
```

A correção deve ocorrer no primeiro ponto comprovadamente incorreto.

---

# PARTE 1 — AUDITORIA DA API

## 1. Validar o endpoint de assets

Com backend atual rodando, testar:

```text
GET /api/v1/market/providers/iq-option/assets?market_type=OTC
```

Registrar:

- HTTP status;
- quantidade de ativos;
- presença de `response.assets`;
- exemplo sanitizado de até 5 ativos;
- se a lista contém mais de um ativo;
- se inclui ativos como:
  - EURUSD-OTC;
  - GBPUSD-OTC;
  - USDJPY-OTC;
  - EURJPY-OTC;
  - ou equivalentes atuais.

Também testar:

```text
GET /api/v1/market/providers/iq-option/assets?market_type=REGULAR
```

Não alterar backend se a API estiver correta.

---

## 2. Contrato esperado

OTC:

```json
{
  "provider": "IQ_OPTION",
  "market_type": "OTC",
  "assets": []
}
```

REGULAR:

```json
{
  "provider": "IQ_OPTION",
  "market_type": "REGULAR",
  "assets": []
}
```

O frontend deve ler:

```ts
response.assets
```

Não ler:

```ts
response.data
```

sem comprovação do contrato real.

---

# PARTE 2 — AUDITORIA DO FRONTEND

## 3. Cadeia obrigatória

Auditar em:

```text
frontend/src/pages/MarketChart.tsx
```

a cadeia:

```text
fetch assets
→ parseIqAssetsResponse
→ setIqAssets
→ filtro por mercado
→ ativo selecionado
→ options do select
→ dropdown
```

Registrar o tamanho em cada etapa:

```text
response.assets.length
parsedAssets.length
iqAssets.length
filteredAssets.length
assetOptions.length
```

Não deixar logs permanentes desnecessários após a correção.

---

## 4. Efeito de carregamento

Auditar o `useEffect` responsável pelos assets.

Confirmar:

- dependências;
- AbortController;
- cleanup;
- Strict Mode;
- retry key;
- troca de mercado;
- falha da conexão;
- resposta atrasada;
- qualquer `setIqAssets([])`;
- qualquer retorno antecipado;
- qualquer fallback que substitua a lista por apenas um item.

Localizar exatamente se existe lógica equivalente a:

```ts
setIqAssets([])
```

após uma resposta válida.

---

## 5. Parsing

Auditar:

```ts
parseIqAssetsResponse()
```

Confirmar que:

- lê `response.assets`;
- preserva todos os itens válidos;
- não retorna apenas o símbolo selecionado;
- não filtra por `symbol === iqSymbol`;
- não elimina ativos por display name;
- não confunde `symbol`, `display_name` e `market_type`.

---

## 6. Filtro de mercado

Confirmar que:

```text
OTC
→ ativos OTC
```

```text
REGULAR
→ ativos REGULAR
```

Não filtrar novamente por sufixo se o backend já devolve `market_type` correto, salvo regra comprovada.

Auditar especialmente:

- símbolos OTC traduzidos, como `AMAZON`;
- display name `AMAZON OTC`;
- símbolos sem `-OTC` usados internamente para candles;
- market type preservado separadamente.

Não usar apenas o sufixo do símbolo técnico para decidir o mercado.

---

## 7. Seleção automática

A seleção deve funcionar assim:

```text
lista válida contém o símbolo atual
→ preservar seleção
```

```text
símbolo atual não existe
→ escolher primeiro ativo válido
```

```text
assets falham
→ manter fallback
```

O fallback não pode substituir a lista completa.

Não construir:

```ts
[selectedAsset]
```

como fonte das opções quando `iqAssets` possui vários itens.

---

## 8. Dropdown

Auditar o JSX do seletor.

Confirmar que as opções vêm de:

```text
assetOptions.map(...)
```

ou equivalente baseado na lista completa.

Não renderizar apenas:

```text
iqSymbol
```

Não mostrar simultaneamente:

```text
ativo selecionado
+
Nenhum ativo disponível
```

quando `assetOptions.length > 0`.

A mensagem de vazio só pode aparecer quando a lista realmente estiver vazia.

---

# PARTE 3 — ERROS 408 E SSE

## 9. Separar os problemas

Os prints mostraram:

```text
HTTP_408
realtime_request_failed
```

e requisições realtime canceladas.

Esses erros não devem ser confundidos automaticamente com a lista de ativos.

Auditar se:

- timeout realtime limpa assets indevidamente;
- fallback polling chama `setIqAssets([])`;
- mudança de feed state dispara reload de assets;
- SSE failure altera o state da lista.

A lista de ativos deve ser independente do estado realtime do candle.

Não corrigir realtime nesta Sprint, salvo se for comprovado que ele limpa a lista.

---

# PARTE 4 — CORREÇÃO MÍNIMA

## 10. Correções permitidas

Aplicar somente o necessário, por exemplo:

- restaurar parsing de `response.assets`;
- impedir `setIqAssets([])` tardio;
- separar fallback selecionado da lista;
- corrigir filtro por `market_type`;
- restaurar `.map()` sobre todos os assets;
- impedir resposta atrasada de sobrescrever lista válida;
- corrigir mensagem de lista vazia;
- preservar assets durante erro realtime.

Não alterar:

- IQ worker;
- provider;
- runtime;
- CandleStore;
- Chart API;
- SSE;
- polling;
- status bar;
- HUD;
- backend;

salvo causa comprovada diretamente ligada à regressão.

---

# PARTE 5 — TESTES OBRIGATÓRIOS

## 11. Testes frontend

Adicionar ou ajustar testes para:

1. `response.assets` com múltiplos ativos gera múltiplas opções;
2. ativo selecionado não reduz a lista;
3. fallback não substitui assets válidos;
4. mensagem “Nenhum ativo OTC disponível” não aparece quando há opções;
5. erro realtime não limpa assets;
6. resposta atrasada não sobrescreve lista mais nova;
7. troca de OTC para REGULAR carrega lista correta;
8. troca de REGULAR para OTC restaura lista OTC;
9. símbolo técnico `AMAZON` com `market_type=OTC` aparece como `AMAZON OTC`;
10. seleção de outro ativo mantém a lista completa;
11. Strict Mode não apaga a lista;
12. AbortController de candles não afeta assets.

Executar:

```bash
.venv/bin/python -m pytest tests/frontend -q
```

---

## 12. Testes completos

Executar:

```bash
.venv/bin/python -m pytest -q
```

Build:

```bash
cd frontend
npm run build
cd ..
```

---

# PARTE 6 — VALIDAÇÃO REAL

## 13. OTC

Abrir:

```text
http://localhost:5173/market-chart
```

Selecionar:

```text
Mercado: OTC
```

Confirmar:

- dropdown possui vários ativos;
- não mostra “Nenhum ativo OTC disponível”;
- EURUSD OTC continua disponível;
- selecionar GBPUSD OTC funciona;
- selecionar USDJPY OTC funciona;
- após selecionar outro ativo, a lista continua completa.

---

## 14. REGULAR

Trocar para:

```text
Mercado: Aberto
```

Confirmar:

- lista REGULAR aparece quando houver ativos;
- lista pode ser pequena conforme horário;
- fallback não contamina OTC;
- voltar para OTC restaura ativos OTC.

---

## 15. Regressões

Confirmar:

- gráfico continua carregando;
- status bar premium permanece;
- SSE/fallback continuam funcionando;
- HUD permanece;
- nenhuma alteração visual regressiva;
- candles não misturam ativos.

---

# PARTE 7 — GIT

## 16. Não executar

Não executar:

```bash
git add .
```

Não executar staging.

Não fazer commit.

Não fazer push.

---

# ENTREGA ESPERADA

Entregar relatório com:

1. causa raiz comprovada;
2. status e payload de `/assets` OTC;
3. status e payload de `/assets` REGULAR;
4. quantidade em cada etapa do frontend;
5. arquivo e linha onde a lista era perdida;
6. relação ou ausência de relação com os erros 408;
7. correção mínima aplicada;
8. arquivos modificados;
9. diff funcional por arquivo;
10. quantidade de ativos OTC após correção;
11. quantidade de ativos REGULAR após correção;
12. validação de troca de ativo;
13. validação de troca de mercado;
14. testes frontend;
15. suíte completa;
16. build;
17. confirmação de ausência de regressão em status bar/SSE/HUD;
18. `git status --short`;
19. `git diff --stat`;
20. sugestão de commit;
21. confirmação de que não fez commit;
22. confirmação de que não fez push.

Não ocultar endpoint vazio.

Não culpar React sem validar API.

Não alterar arquitetura.

Não corrigir apenas adicionando fallback visual.