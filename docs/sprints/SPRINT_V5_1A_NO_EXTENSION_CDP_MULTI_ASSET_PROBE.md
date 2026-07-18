# SPRINT V5.1A — NO-EXTENSION CDP MULTI-ASSET PROBE

## Objetivo

Comprovar em sessão Polarium legítima, aberta pelo próprio usuário, que a Friday consegue acompanhar múltiplos ativos simultaneamente sem extensão instalada.

A probe deve usar navegador Chrome/Chromium dedicado e CDP local.

Não implementar scanner de produção.

Não executar ordens.

Não consultar saldo, posições, portfolio ou conta.

---

# EVIDÊNCIA JÁ COMPROVADA

O HAR do TradeAutoPilot contém o envelope real:

```json
{
  "name": "subscribeMessage",
  "request_id": "<id crescente>",
  "msg": {
    "name": "candle-generated",
    "version": "1.0",
    "params": {
      "routingFilters": {
        "active_id": 79,
        "size": 60
      }
    }
  }
}
```

Foram observadas subscriptions no mesmo WebSocket para:

```text
79:60
2289:60
2289:300
2090:300
2280:300
2159:300
1941:300
1941:60
```

Portanto:

- o envelope não deve ser reinventado;
- `active_id` e `size` são filtros comprovados;
- múltiplos contextos no mesmo WebSocket são suportados pelas evidências;
- o mesmo ativo pode ter mais de um timeframe inscrito.

---

# PARTE 1 — NAVEGADOR SEM EXTENSÃO

Criar probe local isolada que:

1. inicia Chrome/Chromium com remote debugging;
2. utiliza perfil exclusivo da Friday;
3. abre a Polarium oficial;
4. permite login manual do usuário;
5. não lê senha;
6. não imprime cookies;
7. não exporta tokens;
8. não reutiliza HAR;
9. não exige extensão;
10. não exige DevTools manual.

Preferir código experimental dentro de:

```text
.jarvis_cache/polarium_cdp_probe/
```

Não integrar ao runtime principal.

---

# PARTE 2 — LOCALIZAÇÃO DO WEBSOCKET

Detectar o WebSocket:

```text
wss://ws.trade.polariumbroker.com/echo/websocket
```

Confirmar:

- quantidade de WebSockets;
- sessão autenticada;
- recebimento de `timeSync`;
- recebimento de eventos existentes;
- nenhuma credencial exposta.

A probe deve observar frames enviados e recebidos via CDP.

---

# PARTE 3 — RUNTIME GUARD

## Saída permitida

Permitir exclusivamente:

```text
subscribeMessage → candle-generated
unsubscribeMessage → candle-generated
sendMessage → get-first-candles
```

e mensagens técnicas indispensáveis já emitidas pela página.

## Saída proibida

Bloquear imediatamente qualquer tentativa contendo:

```text
order
buy
sell
position
portfolio
balance
account
payment
deposit
withdrawal
change-balance
```

Não utilizar busca ingênua que bloqueie `active_id` por conter texto incidental.

Validar o nome e a estrutura da mensagem.

---

# PARTE 4 — DESCOBERTA DE ACTIVE IDS

Não usar IDs arbitrários sem contexto.

Obter IDs por uma destas fontes sanitizadas da própria sessão:

- eventos de ativos já recebidos;
- underlying list;
- actives facade;
- payloads de candles existentes;
- IDs já confirmados no HAR, somente após comprovar que continuam válidos na sessão atual.

Registrar somente:

```text
active_id
símbolo sanitizado
market_type
```

Não registrar dados de conta.

---

# PARTE 5 — TESTE COM DOIS ATIVOS

Escolher dois ativos OTC válidos na sessão atual.

Enviar duas subscriptions:

```json
{
  "name": "subscribeMessage",
  "request_id": "<id único>",
  "msg": {
    "name": "candle-generated",
    "version": "1.0",
    "params": {
      "routingFilters": {
        "active_id": "<ATIVO_A>",
        "size": 60
      }
    }
  }
}
```

```json
{
  "name": "subscribeMessage",
  "request_id": "<id único>",
  "msg": {
    "name": "candle-generated",
    "version": "1.0",
    "params": {
      "routingFilters": {
        "active_id": "<ATIVO_B>",
        "size": 60
      }
    }
  }
}
```

Observar por 60 segundos.

Comprovar:

- um único WebSocket;
- eventos para A;
- eventos para B;
- eventos intercalados;
- nenhum vazamento entre stores;
- gráfico aberto na Polarium não precisa estar em ambos os ativos;
- nenhuma chamada proibida.

---

# PARTE 6 — MESMO ATIVO EM M1 E M5

Somente após sucesso com dois ativos:

```text
Ativo A + size 60
Ativo A + size 300
```

Comprovar:

- eventos separados;
- séries independentes;
- chave `active_id + size`;
- nenhum candle M1 armazenado em M5;
- nenhum candle M5 armazenado em M1.

---

# PARTE 7 — UNSUBSCRIBE

Primeiro localizar no HAR ou observar passivamente o envelope real de unsubscribe.

Não inventar envelope.

Após confirmação, cancelar somente:

```text
Ativo B + size 60
```

Comprovar:

- B deixa de receber eventos;
- A continua;
- WebSocket permanece aberto;
- M5 continua, quando estiver ativo;
- nenhuma outra subscription é encerrada.

Se o envelope de unsubscribe não for encontrado:

- não enviar;
- encerrar navegador para cleanup;
- relatar especificamente apenas o unsubscribe como inconclusivo.

---

# PARTE 8 — MÉTRICAS

Para cada contexto:

- active_id;
- size;
- início da subscription;
- primeiro evento;
- eventos recebidos;
- mudanças OHLC;
- último evento;
- intervalo médio;
- p50;
- p95;
- maior gap;
- erros;
- eventos após unsubscribe;
- cleanup.

Também medir:

- CPU;
- memória;
- quantidade de processos;
- quantidade de WebSockets;
- mensagens por segundo.

---

# PARTE 9 — CRITÉRIOS DE SUCESSO

## Dois ativos simultâneos

Sucesso se:

- ambos receberem `candle-generated`;
- mesma conexão;
- pelo menos 30 segundos de sobreposição;
- zero chamadas proibidas.

## Mesmo ativo M1 e M5

Sucesso se:

- `size=60` e `size=300` receberem eventos;
- stores independentes;
- zero mistura de série.

## Independência do gráfico aberto

Sucesso se um ativo não visível na tela continuar recebendo eventos.

---

# PARTE 10 — ENTREGA

Entregar:

1. arquitetura da probe;
2. Chrome iniciado sem extensão;
3. WebSocket encontrado;
4. estado authenticated;
5. origem dos active_ids;
6. envelope exato enviado;
7. resultado com dois ativos;
8. resultado M1 + M5;
9. eventos por contexto;
10. prova de intercalamento;
11. dependência ou não do ativo visível;
12. unsubscribe;
13. CPU e memória;
14. Runtime Guard;
15. forbidden_calls;
16. arquivos temporários criados;
17. arquivos rastreados modificados;
18. testes;
19. git status;
20. git diff;
21. riscos;
22. recomendação para scanner V5.2.

Não integrar ao runtime.

Não alterar MarketChart.

Não usar extensão.

Não fazer commit.

Não fazer push.