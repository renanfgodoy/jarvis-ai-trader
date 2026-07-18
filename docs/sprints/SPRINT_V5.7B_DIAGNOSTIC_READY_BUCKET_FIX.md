# FRIDAY AI TRADER

# SPRINT V5.7B — DIAGNOSTIC READY BUCKET FIX

## Status

PLANEJADA

---

## 1. Objetivo

Corrigir exclusivamente a classificação do `AssetSwitchDiagnostic` para que buckets já carregados e em estado `READY` não sejam classificados incorretamente como `BUCKET_NOT_UPDATED` apenas porque o tamanho do bucket não cresceu durante uma troca de ativo.

Esta Sprint não altera o funcionamento do mercado, bootstrap, CandleStore, Chart API ou frontend.

---

## 2. Evidência real

A validação real da Sprint V5.7A mostrou trocas corretas com:

- bucket correto;
- bootstrap finalizado;
- `discarded=False`;
- Chart API atualizada;
- frontend atualizado;
- Readiness em `READY`.

Mesmo assim, o diagnóstico classificou como:

`BUCKET_NOT_UPDATED`

porque:

`bucket_size_before == bucket_size_after`

Exemplo:

```text
bucket_size: 315 -> 315
bootstrap: started=True finished=True discarded=False
chart updated=True
frontend_updated=True
readiness=READY
Esse comportamento é válido quando o bucket já possui histórico suficiente e está pronto.

3. Causa

A regra atual assume que toda troca válida deve necessariamente aumentar o tamanho do bucket.

Essa premissa é incorreta para buckets previamente carregados.

4. Correção permitida

Alterar somente a lógica de classificação do AssetSwitchDiagnostic.

Quando todas as condições abaixo forem verdadeiras:

bucket final existe;
bucket final corresponde ao active_id e raw_size atuais;
Readiness está READY;
bootstrap não foi descartado;
Chart API aponta para o bucket correto;
frontend foi atualizado;
bucket possui candles;

a classificação deverá ser de sucesso, mesmo que:

bucket_size_before == bucket_size_after

Não exigir crescimento do bucket quando ele já estava carregado.

5. Fora de escopo

Não alterar:

runtime de mercado;
parser;
CandleStore;
HistoricalBootstrapManager;
BootstrapRequestFactory;
Readiness;
Chart API;
frontend;
Session Context;
CDP;
layout;
estratégia;
scanner;
ranking;
IA.
6. Comportamento esperado
Bucket novo
bucket_size: 0 -> 200
resultado: sucesso
Bucket existente e READY
bucket_size: 315 -> 315
chart updated=True
frontend_updated=True
resultado: sucesso
Bucket ausente ou incorreto
bucket final inexistente
ou bucket incompatível
resultado: BUCKET_NOT_UPDATED
7. Testes obrigatórios

Adicionar testes para:

bucket existente, READY e sem crescimento não gera BUCKET_NOT_UPDATED;
bucket existente com Chart API correta é sucesso;
bucket existente com frontend atualizado é sucesso;
bucket ausente continua gerando BUCKET_NOT_UPDATED;
bucket incorreto continua gerando falha;
resposta descartada não é considerada sucesso;
nenhuma regressão nas categorias existentes.
8. Validação automatizada

Executar:

python -m pytest tests/market/providers/test_polarium_asset_switch_diagnostic.py -v
python -m pytest tests/market/providers -v
python -m pytest -v

Executar:

cd frontend
npm run build
9. Validação real

Repetir:

EURUSD-OTC
XAUUSD-OTC
BTCUSD-OTC
EURUSD-OTC

Esperado:

nenhuma RACE_CONDITION;
nenhum falso BUCKET_NOT_UPDATED para bucket READY já carregado;
trocas corretas classificadas como sucesso;
Chart API e frontend atualizados.
10. Entrega obrigatória
Objetivo;
causa;
arquivo modificado;
regra anterior;
regra nova;
testes adicionados;
resultados;
build;
validação real;
git status;
git diff;
riscos;
sugestão de commit.
11. Git

Não executar:

git add
git commit
git push

sem autorização explícita do Renan.

12. Sugestão de commit
fix(diagnostics): accept unchanged ready asset buckets