# J.A.R.V.I.S Polarium Bridge — V0.20.0

Extensão local e somente leitura para testes de sincronização real da conta DEMO.

Ela roda na aba `https://trade.polariumbroker.com/*`, escuta mensagens WebSocket já recebidas pela sua sessão logada e encaminha eventos relevantes para o backend local do J.A.R.V.I.S.

## Segurança

- Não salva senha.
- Não salva cookie.
- Não salva token.
- Não envia ordem.
- Não clica em nada.
- Não opera conta real.
- Apenas encaminha eventos de leitura como `marginal-balance` para `http://127.0.0.1:8000`.

## Instalação no Chrome

1. Abra `chrome://extensions`.
2. Ative **Modo do desenvolvedor**.
3. Clique em **Carregar sem compactação**.
4. Selecione a pasta:
   `jarvis-ai-trader/tools/polarium-browser-bridge`
5. Deixe o backend J.A.R.V.I.S rodando.
6. Abra a Polarium e faça login normalmente.
7. Entre na Traderoom DEMO.
8. O dashboard do J.A.R.V.I.S deve atualizar saldo/moeda automaticamente quando chegar `marginal-balance`.
