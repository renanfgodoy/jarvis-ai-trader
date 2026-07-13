SPRINT V4.5.17 — PREMIUM STATUS BAR UX REFACTOR
Objetivo

Refatorar completamente a barra superior do /market-chart, substituindo os cards atuais por um componente compacto, premium e totalmente responsivo.

Não alterar:

IQ Option Runtime
Worker
CandleStore
SSE
Polling
Backend
Arquitetura de mercado

Esta Sprint é exclusivamente de UX/UI.

Contexto

Após a Sprint V4.5.16 foi eliminado o problema de sobreposição.

Entretanto surgiu um novo problema:

Os cards ficaram estreitos demais.

Resultado observado:

textos cortados;
utilização de ...;
leitura ruim;
excesso de informação para pouco espaço.

Exemplo:

F...
I...

Q...
S...

E...
S...

F...
F...

Embora tecnicamente correto, visualmente ficou pior que a versão anterior.

PARTE 1 — NOVA FILOSOFIA

A barra superior deixa de ser um painel técnico.

Ela passa a ser apenas um indicador rápido do estado do sistema.

A leitura deve acontecer em menos de 1 segundo.

PARTE 2 — NOVA ESTRUTURA

Remover completamente os títulos:

FONTE
MODO
ENTREGA
FEED

O ícone já identifica o significado.

Cada item terá apenas:

Ícone

Valor principal

Exemplo:

📡
IQ OPTION
⚡
TEMPO REAL
📶
SSE
✅
FEED OK

Nada além disso.

PARTE 3 — REMOVER TEXTO DESNECESSÁRIO

Eliminar da barra superior:

READ ONLY
Fluxo saudável
Latência local
Última resposta
Heartbeat
Countdown
Último evento
Média
p95
Reconexões

Essas informações continuam exclusivamente no HUD DEV.

PARTE 4 — SEM TRUNCAMENTO

Não aceitar:

F...
S...
Q...
TEM...

Também não usar:

text-overflow: ellipsis;

para esconder estados importantes.

Se faltar espaço:

reorganizar o layout;
nunca esconder informação.
PARTE 5 — RESPONSIVIDADE
Tela grande

Uma linha:

📡 IQ OPTION
⚡ TEMPO REAL
📶 SSE
✅ FEED OK
Janela dividida

Duas linhas:

📡 IQ OPTION
⚡ TEMPO REAL

📶 SSE
✅ FEED OK
Tela pequena

Uma coluna:

📡 IQ OPTION

⚡ TEMPO REAL

📶 SSE

✅ FEED OK

Nunca reduzir fonte exageradamente.

PARTE 6 — ESTILO

Visual premium.

Mais espaço interno.

Mais respiro.

Menos informação.

Os indicadores devem parecer parte de uma plataforma profissional.

PARTE 7 — TIPOGRAFIA

Valores:

Peso:

600

ou

700

Texto centralizado.

Ícone acima.

Sem subtítulo.

PARTE 8 — CORES

Continuar usando a identidade atual.

Exemplo:

IQ OPTION

Verde.

TEMPO REAL

Amarelo.

SSE

Azul/verde.

FEED OK

Verde.

Estados de erro continuam utilizando as cores atuais.

PARTE 9 — HUD DEV

Não remover.

Apenas garantir:

Recolhido:

DIAGNÓSTICO DEV

Expandido:

Todas as métricas técnicas.

Nada muda.

PARTE 10 — TESTES

Executar:

.venv/bin/python -m pytest tests/frontend -q

Depois:

.venv/bin/python -m pytest -q

Depois:

cd frontend
npm run build
PARTE 11 — VALIDAÇÃO VISUAL

Validar:

Tela cheia.

Janela dividida.

Largura média.

Largura pequena.

Critérios:

sem ...;
sem sobreposição;
sem quebra de palavra;
leitura imediata;
aparência premium.
PARTE 12 — GIT

Não executar:

git add

Não fazer:

git commit

Não fazer:

git push
ENTREGA ESPERADA

O FORGE deve entregar um relatório contendo:

causa da má legibilidade;
nova estrutura da barra;
componentes removidos;
componentes mantidos;
regras de responsividade aplicadas;
arquivos modificados;
diff funcional;
testes frontend;
suíte completa;
build;
validação visual em tela cheia;
validação visual em janela dividida;
confirmação de ausência de ...;
confirmação de ausência de sobreposição;
git status --short;
git diff --stat;
confirmação de que não houve commit;
confirmação de que não houve push.