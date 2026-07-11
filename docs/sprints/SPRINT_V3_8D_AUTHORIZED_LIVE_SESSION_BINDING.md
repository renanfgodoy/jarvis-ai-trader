# Sprint V3.8D — Authorized Session Bridge

## Objetivo

Implementar uma ponte segura (Bridge) entre a sessão autenticada existente e o PolariumLiveSessionManager.

Esta Sprint NÃO implementa mercado ao vivo.

Ela apenas verifica se existe uma sessão autenticada reutilizável e cria uma abstração segura para entregá-la ao runtime, sem exposição de credenciais.

---

## Escopo

Criar apenas a camada:

OAuth Lab
↓
Authorized Session Bridge
↓
Live Session Manager

Sem alterar:

- OAuth Lab
- Connector
- MarketPipeline
- CandleStore
- Chart API
- Frontend
- IA
- Indicadores

---

## Regras

Nunca:

- aceitar Token
- aceitar Cookie
- aceitar Bearer
- aceitar Authorization
- aceitar HAR
- aceitar SSID

Nunca:

- serializar segredo
- logar segredo
- expor segredo
- retornar segredo

Se não existir uma sessão reutilizável segura, interromper a Sprint documentando exatamente o motivo.

---

## Critério de sucesso

A Sprint será considerada concluída apenas se ocorrer um dos cenários:

### Cenário A

Existe uma abstração segura que entrega uma sessão autenticada reutilizável ao LiveSessionManager.

### Cenário B

A abstração não existe e isso é comprovado tecnicamente, documentando o bloqueio sem criar soluções paralelas.

Nenhuma implementação baseada em hipótese é permitida.