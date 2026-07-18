# FRIDAY AI TRADER

# SPRINT V5.8A — PROGRAMMATIC MARKET SELECTION

## Status

PLANEJADA

---

# 1. Objetivo

Validar se a Friday consegue selecionar programaticamente um ativo utilizando exclusivamente o protocolo oficial já observado da Polarium.

Não utilizar CDP para clicar.

Não utilizar automação visual.

Não utilizar DOM.

Não utilizar JavaScript injetado.

A troca deverá ocorrer apenas pelo protocolo de mercado.

---

# 2. Evidências

Já comprovamos:

- WebSocket funcionando.
- subscribeMessage funcionando.
- get-first-candles funcionando.
- bootstrap funcionando.
- troca manual funcionando.
- Session Context funcionando.

Agora queremos descobrir se a própria Friday consegue iniciar a troca.

---

# 3. Escopo

Criar um endpoint temporário de desenvolvimento.

Exemplo:

POST

/api/dev/select-market

Payload:

{
    "active_id": 76,
    "raw_size": 300
}

O endpoint deverá reutilizar exclusivamente componentes existentes.

Não criar um segundo fluxo.

---

# 4. Fluxo esperado

Receber:

active_id

↓

validar

↓

emitir subscribeMessage

↓

emitir get-first-candles

↓

aguardar first-candles

↓

atualizar Session Context

↓

Chart API

↓

Frontend

---

# 5. Fora de escopo

Não alterar:

Parser

CandleStore

Runtime Guard

Readiness

Chart API

Frontend

Scanner

Ranking

Estratégia

IA

Layout

CDP

---

# 6. Regras

Nunca clicar na interface.

Nunca usar DOM.

Nunca usar querySelector.

Nunca usar Playwright.

Nunca usar Selenium.

Nunca usar Browser Bridge.

Toda seleção deverá ocorrer pelo mesmo protocolo utilizado naturalmente pela Polarium.

---

# 7. Testes

Adicionar testes para:

active_id válido

active_id inexistente

subscribe enviado

bootstrap enviado

Session Context atualizado

gráfico atualizado

M1

M5

M15

---

# 8. Validação real

Com a Polarium aberta:

POST

/api/dev/select-market

active_id=76

↓

confirmar gráfico EURUSD

Depois:

active_id=1857

↓

confirmar gráfico XAUUSD

Depois:

active_id=2270

↓

confirmar gráfico BTCUSD

Sem clicar na Polarium.

---

# 9. Critério de sucesso

A Sprint será considerada concluída quando o gráfico da Friday trocar de ativo utilizando apenas mensagens do protocolo da Polarium.

Não é necessário que a interface visual da Polarium mude.

---

# 10. Git

Não executar:

git add

git commit

git push

---

# Sugestão de commit

feat(polarium): support programmatic market selection