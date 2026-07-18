# FRIDAY AI TRADER

# SPRINT V5.9A — REPRODUCE NATIVE HISTORICAL SEQUENCE

## Status

PLANEJADA

---

## 1. Objetivo

Implementar a reprodução da sequência histórica nativa utilizada pela Polarium após a seleção de um ativo.

A reprodução deve reutilizar exclusivamente mensagens comprovadas pela captura da sessão real.

Não criar protocolo novo.

Não inventar parâmetros.

Não criar paginação artificial.

---

## 2. Evidências comprovadas

Já foi comprovado:

- seleção programática funciona;
- subscribeMessage funciona;
- get-first-candles funciona;
- parser funciona;
- CandleStore funciona;
- Readiness funciona.

Também foi comprovado que:

o fluxo manual envia:

get-first-candles

↓

get-first-candles

↓

subscribeMessage

↓

get-candles

↓

get-candles

↓

get-candles

Enquanto o fluxo Friday envia apenas:

subscribeMessage

↓

get-first-candles

---

## 3. Objetivo técnico

Reproduzir exatamente a sequência outbound manual utilizando o mesmo mecanismo CDP já existente.

Não criar um novo cliente WebSocket.

Não alterar Runtime.

Não alterar Session Context.

Não alterar Parser.

---

## 4. Implementação permitida

Somente:

- reutilizar CDP;
- reutilizar WebSocket já capturado;
- reutilizar Runtime.evaluate existente;
- reutilizar sendMessage.

Criar apenas um orquestrador de bootstrap histórico.

---

## 5. Ordem obrigatória

Para cada ativo:

1. subscribeMessage (candles-generated)

2. get-first-candles

3. aguardar resposta

4. enviar os get-candles comprovados

5. aguardar READY

Se algum passo falhar:

parar.

Não continuar.

---

## 6. bootstrap_ready

bootstrap_ready somente pode ser verdadeiro quando:

history_state == READY

history_count >= history_required

bootstrap_complete == true

Nunca baseado apenas em chart_count.

---

## 7. Instrumentação

Registrar:

sequência enviada

resposta

history_count

readiness

tempo entre mensagens

quantidade de candles recebidos

---

## 8. Relatório

Gerar:

.jarvis_cache/diagnostics/native_bootstrap_sequence_report.json

.jarvis_cache/diagnostics/native_bootstrap_sequence_report.txt

Registrar:

PASSO

↓

REQUEST

↓

RESPONSE

↓

HISTORY

↓

READINESS

---

## 9. Testes

Adicionar testes para:

M1

M5

M15

READY

timeout

interrupção

duplicidade

reexecução

troca rápida de ativo

---

## 10. Build

Executar:

python -m pytest tests/market/providers -v

python -m pytest -v

cd frontend

npm run build

---

## 11. Validação real

Subir backend.

Subir frontend.

Abrir Polarium.

Executar:

```bash
curl -sS -X POST http://127.0.0.1:8000/api/dev/select-market \
  -H "Content-Type: application/json" \
  -d '{"active_id":1857,"raw_size":300}' | python -m json.tool
```

Esperado:

history_count >= 50

history_state = READY

analysis_blocked = false

bootstrap_complete = true

---

## 12. Critério de aceitação

A Sprint somente será considerada concluída quando:

XAUUSD atingir READY sem clique manual.

Depois repetir para BTCUSD.

---

## 13. Entrega

Objetivo

Arquitetura

Arquivos criados

Arquivos modificados

Sequência implementada

Testes

Resultados

Build

Validação real

git status

git diff

Riscos

Próximos passos

Sugestão de commit

---

## 14. Git

Não executar:

git add

git commit

git push

sem autorização do Renan.

---

## 15. Sugestão de commit

fix(polarium): reproduce native historical bootstrap sequence