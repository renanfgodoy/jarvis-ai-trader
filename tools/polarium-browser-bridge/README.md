# J.A.R.V.I.S Polarium Bridge — V0.20.0

Extensão local e somente leitura para testes de sincronização real de candles da conta DEMO.

Ela roda na aba `https://trade.polariumbroker.com/*`, injeta um script no contexto principal da página para observar mensagens WebSocket já recebidas pela sua sessão logada e encaminha somente eventos de mercado sanitizados para o backend local do Friday Trade.

## Segurança

- Não salva senha.
- Não salva cookie.
- Não salva token.
- Não envia ordem.
- Não clica em nada.
- Não opera conta real.
- Apenas encaminha eventos de mercado permitidos: `first-candles`, `candle-generated`, `candles-generated` e `timeSync`.
- O envio ao backend usa somente o endpoint local `http://127.0.0.1:8000/api/v1/polarium/browser-bridge/message`.

## Instalação no Chrome

1. Abra `chrome://extensions`.
2. Ative **Modo do desenvolvedor**.
3. Clique em **Carregar sem compactação**.
4. Selecione a pasta:
   `jarvis-ai-trader/tools/polarium-browser-bridge`
5. Se a extensão já estava instalada, clique em **Atualizar** ou remova e carregue novamente.
6. Deixe o backend J.A.R.V.I.S rodando.
7. Feche abas antigas da Polarium abertas antes da atualização da extensão.
8. Abra uma nova aba da Polarium depois de atualizar a extensão.
9. Faça login normalmente.
10. Entre na Traderoom DEMO.
11. O status local pode ser inspecionado no console da Polarium:

   ```js
   window.__FRIDAY_TRADE_POLARIUM_BRIDGE__.status()
   window.__FRIDAY_TRADE_POLARIUM_BRIDGE_CONTENT__.status()
   ```

12. O Friday Trade deve receber candles pelo endpoint local e expor status sanitizado em:

   `http://127.0.0.1:8000/api/v1/polarium/browser-bridge/status`

Se aparecer `EXTENSION_CONTEXT_INVALIDATED`, a aba antiga ainda está usando um contexto de extensão invalidado. Feche a aba da Polarium e abra uma nova após recarregar a extensão.
