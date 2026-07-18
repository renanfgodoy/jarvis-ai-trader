# FRIDAY AI TRADER

# SPRINT V5.9C — RUNTIME RECOVERY AND BASELINE

## Status

PLANEJADA

---

## 1. Objetivo

Restaurar e estabilizar o funcionamento básico da Friday após as alterações acumuladas das Sprints V5.8 e V5.9.

Antes desta Sprint, o fluxo básico já funcionava:

```text
Backend
→ Chrome dedicado
→ Polarium /traderoom
→ sessão autenticada
→ Market WebSocket
→ runtime
→ CandleStore
→ Chart API
→ Friday
Após as últimas alterações relacionadas à seleção programática e bootstrap nativo, o comportamento ficou instável:

em algumas execuções a Friday demora vários minutos para abrir;
em outras execuções a Friday não abre;
o espelhamento manual deixou de funcionar de forma confiável;
reinicializações apresentam comportamento inconsistente;
testes manuais sucessivos deixaram o estado difícil de diagnosticar.

Esta Sprint deve restaurar primeiro o baseline funcional.

2. Regra principal

Não continuar a implementação da seleção programática enquanto o fluxo manual básico não estiver novamente estável.

A prioridade absoluta é:

Polarium manual
→ contexto correto
→ candles reais
→ Chart API
→ Friday espelhada
3. Baseline obrigatório

O Forge deverá restaurar e validar:

Backend sobe na porta 8000.
Frontend sobe na porta 5173.
Chrome dedicado abre pela porta CDP 9227.
Polarium abre em:
https://trade.polariumbroker.com/traderoom
Login da Polarium funciona.
Market WebSocket é identificado.
Friday abre em segunda aba.
Friday não demora indefinidamente para abrir.
Seleção manual de ativo na Polarium atualiza a Friday.
Troca manual de timeframe atualiza a Friday.
M1 continua funcional.
M5 continua funcional.
M15 continua funcional.
O histórico manual chega a READY.
Nenhum lock temporário permanece preso após timeout ou erro.
Nenhum bootstrap programático interfere no fluxo manual.
4. Escopo desta Sprint

É permitido auditar e corrigir somente:

inicialização do CDP Live Source;
gerenciamento das abas Polarium e Friday;
condição de abertura da Friday;
lifecycle do runtime Polarium;
locks temporários de bootstrap;
ownership de bootstrap;
cleanup após timeout, erro ou cancelamento;
restauração do bootstrap manual;
integração entre runtime, Chart API e frontend;
regressões introduzidas pelas Sprints V5.8A até V5.9B.
5. Fora de escopo

Não implementar nesta Sprint:

nova seleção programática;
novos requests get-candles;
reprodução adicional de envelope histórico;
scanner;
ranking;
estratégia;
CALL;
PUT;
IA;
backtest;
execução de ordens;
saldo;
portfólio;
OAuth novo;
Browser Bridge;
extensão;
automação visual;
clique por DOM;
Selenium;
Playwright;
alteração de layout.
6. Auditoria obrigatória

Antes de modificar código, auditar todas as alterações relacionadas a:

NativeHistoricalBootstrapOrchestrator
HistoricalBootstrapManager
programmatic bootstrap ownership
temporary bootstrap locks
PolariumCDPLiveSource
DualTabCDPSessionManager
AssetSwitchDiagnostic
GetCandlesEnvelopeDiagnostic
historical request sequence
bootstrap payload trace

Identificar quais alterações podem afetar:

startup;
abertura da Friday;
captura do Market WebSocket;
publicação do Session Context;
bootstrap manual;
Chart API;
encerramento e reinicialização do runtime.
7. Hipóteses prioritárias

Investigar especialmente:

7.1 Lock não liberado

Verificar se o lock por:

(active_id, raw_size)

é sempre liberado em:

sucesso;
timeout;
exceção;
cancelamento;
encerramento do backend;
troca de ativo;
reinicialização do live source.
7.2 Ownership incorreto

Verificar se o NativeHistoricalBootstrapOrchestrator está bloqueando o bootstrap automático mesmo quando não existe uma seleção programática ativa.

O fluxo manual nunca poderá ser bloqueado por ownership programático residual.

7.3 Startup preso

Verificar se a abertura da Friday depende de uma condição que pode nunca ser atingida.

A Friday deverá abrir de forma previsível e mostrar estado de espera, sem ficar vários minutos sem feedback.

7.4 Target incorreto

Confirmar que o runtime usa como target principal:

https://trade.polariumbroker.com/traderoom

e não iframe, service worker, worker ou aba Friday.

7.5 Runtime interrompido

Verificar se alguma task do CDP, polling, target manager ou runtime termina silenciosamente após erro.

8. Estratégia de recuperação

O Forge deverá aplicar o menor patch possível.

Se uma funcionalidade experimental das Sprints V5.8/V5.9 estiver causando regressão, ela deverá ser:

desabilitada por configuração;
isolada do fluxo manual;
ou temporariamente retirada do startup automático.

Não apagar o código de diagnóstico sem necessidade.

O endpoint:

POST /api/dev/select-market

pode permanecer, mas não poderá interferir no funcionamento normal quando não estiver sendo chamado.

9. Configuração segura

A seleção programática e o bootstrap nativo experimental deverão ficar atrás de configuração explícita, se ainda não estiverem.

Exemplo:

POLARIUM_PROGRAMMATIC_SELECTION_ENABLED=false

Valor padrão:

false

Com a configuração desabilitada:

fluxo manual deve funcionar normalmente;
nenhum lock programático deve ser criado;
nenhum bootstrap nativo experimental deve ser iniciado;
nenhum get-candles programático deve ser enviado.

Não usar exatamente esse nome se a arquitetura atual já possuir configuração equivalente.

10. Startup da Friday

A abertura da Friday não deverá depender indefinidamente de READY histórico.

Condição mínima sugerida:

Chrome CDP conectado
+
target Polarium detectado
+
frontend disponível

A Friday pode abrir mostrando:

Aguardando sessão da Polarium

enquanto autenticação e Market WebSocket terminam.

Não abrir abas duplicadas.

Não substituir a aba da Polarium.

11. Cleanup obrigatório

Garantir cleanup em finally ou mecanismo equivalente para:

locks de bootstrap;
ownership programático;
pending requests;
tasks de espera;
timeouts;
subscriptions temporárias;
estados transitórios;
referências ao target anterior.

O backend deve poder ser parado e iniciado novamente sem herdar estado inválido.

12. Testes obrigatórios

Adicionar ou ajustar testes para:

Startup
Chrome dedicado inicia;
target Polarium é encontrado;
Friday abre sem depender de READY histórico;
Friday não duplica;
frontend indisponível não derruba backend;
login pendente não bloqueia indefinidamente.
Runtime manual
seleção manual publica Session Context;
bootstrap manual funciona;
Chart API recebe candles;
M1 chega a READY;
M5 chega a READY;
M15 chega a READY.
Locks
lock programático é liberado em sucesso;
lock programático é liberado em timeout;
lock programático é liberado em exceção;
lock programático é liberado em cancelamento;
fluxo manual não é bloqueado por lock residual;
endpoint não chamado não cria ownership programático.
Reinicialização
runtime pode iniciar, parar e iniciar novamente;
nenhuma task fica presa;
nenhum estado antigo contamina nova sessão.
Regressão
Parser preservado;
CandleStore preservado;
Readiness preservado;
realtime não incrementa histórico;
troca atômica preservada;
Chart API preservada.
13. Testes automatizados

Executar:

cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

python -m pytest tests/market/providers -v
python -m pytest -v

Executar build:

cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run build
14. Validação real obrigatória
Terminal 1 — frontend
cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run dev
Terminal 2 — backend
cd /Users/renangodoy/Desktop/jarvis-ai-trader
source .venv/bin/activate

POLARIUM_CDP_LIVE_ENABLED=true \
.venv/bin/uvicorn app.main:app \
--host 127.0.0.1 \
--port 8000
Resultado esperado
1. Chrome dedicado abre.
2. Polarium abre em /traderoom.
3. Friday abre em segunda aba em tempo previsível.
4. Login funciona.
5. Market WebSocket conecta.
6. Seleção manual na Polarium espelha na Friday.
7. M1 funciona.
8. M5 funciona.
9. M15 funciona.
10. Histórico chega a READY.
11. Reiniciar backend não quebra o fluxo.
12. Nenhum POST /api/dev/select-market é necessário.
15. Critério de aceitação

Esta Sprint somente será considerada concluída quando o baseline manual estiver novamente estável.

Critérios mínimos:

Polarium abre
Friday abre
Market WebSocket conecta
ativo manual espelha
timeframe manual espelha
histórico manual chega a READY
reinicialização funciona

Não declarar sucesso apenas com testes automatizados.

16. Entrega obrigatória

O Forge deverá entregar:

Objetivo;
arquitetura encontrada;
regressão identificada;
causa raiz;
arquivos criados;
arquivos modificados;
patch aplicado;
locks e ownership auditados;
cleanup implementado;
configuração experimental adicionada ou ajustada;
testes adicionados;
resultados dos testes específicos;
resultado de tests/market/providers;
resultado da suíte completa;
resultado do build;
procedimento de validação real;
git status --short;
git diff --stat;
riscos;
próximos passos;
sugestão de commit.
17. Git

Não executar:

git add
git commit
git push

Sem autorização explícita do Renan.

Não apagar alterações pendentes de Sprints anteriores.

Não executar reset, checkout ou clean destrutivo.

18. Sugestão de commit
fix(polarium): restore stable manual CDP market baseline