# Roadmap

Este roadmap define a sequencia planejada de evolucao arquitetural do J.A.R.V.I.S AI Trader. As sprints devem permanecer pequenas, revisaveis e sem misturar objetivos.

## Sprint 3 - Connector Boundary

Isolar o Connector como dominio proprio, preparando `app/connector/polarium` para OAuth, PKCE, session, WebSocket, parser e diagnostics tecnicos.

## Sprint 4 - Diagnostics Boundary

Separar laboratorios, sniffers, logs e gravacao WS do fluxo operacional. Diagnostics deve observar, nunca decidir ou executar.

## Sprint 5 - Market Domain

Organizar candles, ticks, assets, historico, scanner e providers em um dominio Market coeso.

## Sprint 6 - Risk Domain

Isolar gerenciamento da banca, regras operacionais e AutoTrade Gate. Risk deve ser a fronteira obrigatoria antes de qualquer execucao.

## Sprint 7 - Execution Domain

Organizar ordens, replay e modo DEMO/DRY_RUN. Execucao real permanece bloqueada ate validacao futura.

## Sprint 8 - Frontend Hooks

Separar chamadas de API, estado remoto e regras de tela em hooks dedicados por dominio.

## Sprint 9 - Dashboard Modular

Dividir o Dashboard em areas funcionais: Scanner, Chart, Orders, HUD, Replay, Settings, Assets, Balance, AI e Logs.

## Sprint 10 - Shared Contracts

Reduzir divergencia entre contratos Pydantic e TypeScript, eliminando tipos duplicados e usos de `any` onde houver contrato formal.
