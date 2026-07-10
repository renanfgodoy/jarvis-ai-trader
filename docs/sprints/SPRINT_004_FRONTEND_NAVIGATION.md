# SPRINT 4 — FRONTEND FOUNDATION (VERSÃO OFICIAL)

## Status

Planned

---

# Objetivo

Transformar o Frontend em uma arquitetura modular, preparada para crescimento.

Esta Sprint NÃO implementa novas funcionalidades.

Esta Sprint NÃO altera comportamento do Backend.

Esta Sprint NÃO altera APIs.

Esta Sprint NÃO altera Connector.

Esta Sprint reorganiza exclusivamente o Frontend.

---

# Problema Atual

O Dashboard concentra praticamente toda a interface.

Mistura:

- Operação
- Conexões
- OAuth
- Diagnostics
- Labs
- Layout
- Navegação
- Componentes

Isso dificulta manutenção e evolução.

---

# Objetivo Arquitetural

Criar uma arquitetura escalável.

## Estrutura alvo

frontend/src/

pages/

components/

layouts/

hooks/

contexts/

services/

types/

widgets/

assets/

---

# Layout Principal

Criar:

layouts/

MainLayout.tsx

O MainLayout será responsável por:

- Sidebar
- Header
- Área de conteúdo
- Footer (opcional)

Todas as páginas internas deverão utilizar este Layout.

A tela Login NÃO utiliza MainLayout.

---

# Componentes Compartilhados

Criar:

components/

Sidebar/

Header/

PageContainer/

PageTitle/

Card/

StatusBadge/

EmptyState/

Loading/

Section/

ActionButton/

Esses componentes deverão ser reutilizados em todas as páginas.

Evitar duplicação.

---

# Sidebar

Criar Sidebar profissional.

Itens:

🏠 Operação

🔌 Conexões

📊 Diagnósticos

⚙️ Configurações

---

🧪 Desenvolvimento

Polarium Lab

Sidebar fixa.

Responsiva.

Preparada para expansão.

---

# Header

Criar Header reutilizável.

Mostrar:

Nome da plataforma

Status da conexão

Conta

Ambiente

Usuário (placeholder)

---

# Login

Criar apenas layout.

Sem autenticação.

Campos:

Usuário

Senha

Entrar

Texto:

Modo Desenvolvimento

---

# Operation

Nova página principal.

Mover apenas:

Saldo

Conta

Moeda

Scanner

Gráfico

AI

Risk

Orders

AutoTrade

Logs Operacionais

Tudo relacionado à operação.

Remover dessa tela:

OAuth

Diagnostics

WS Recorder

Session Inspector

Labs

Cookies

Ferramentas técnicas

---

# Connections

Criar página dedicada.

Mostrar:

Status

OAuth

Sessão

WebSocket

Conta

Moeda

Ambiente

Última sincronização

Último erro

Fluxo visual:

Não conectado

↓

OAuth

↓

Sessão

↓

WebSocket

↓

Conta

↓

Pronto

Usar endpoints existentes.

Sem alterar Backend.

---

# Diagnostics

Criar página.

Mostrar:

Health

Connector

Backend

Frontend

Latência

Serviços

Logs

Sem alterar APIs.

---

# Labs

Criar:

/labs/polarium

Mover:

OAuth Lab

Direct Login Lab

Session Inspector

WS Recorder

Adicionar aviso grande:

⚠️ AMBIENTE DE DESENVOLVIMENTO

---

# Settings

Criar estrutura.

Sem lógica.

Reservar espaço para:

Perfil

Tema

Broker

API

Preferências

Notificações

---

# Hooks

Criar pasta:

hooks/

Sempre que possível separar lógica da UI.

Evitar componentes gigantes.

---

# Contexts

Criar estrutura:

contexts/

Preparar:

AuthContext

ConnectionContext

ThemeContext

Mesmo que inicialmente contenham apenas estrutura.

---

# Widgets

Criar pasta:

widgets/

Preparar componentes reutilizáveis do Dashboard.

Exemplo:

BalanceWidget

ChartWidget

OrdersWidget

ScannerWidget

AIWidget

RiskWidget

Ainda não mover tudo.

Preparar a estrutura.

---

# Navegação

Criar rotas:

/login

/operation

/connections/polarium

/diagnostics

/labs/polarium

/settings

---

# Compatibilidade

Não remover Dashboard atual imediatamente.

Migrar gradualmente.

Não quebrar imports.

Não apagar componentes.

---

# Testes

Executar:

npm run build

Confirmar:

Build OK

Rotas funcionando

Sidebar funcionando

Sem erros de import

Sem erros TypeScript

---

# Como testar

Explicar passo a passo para o Renan:

1. Subir Backend

2. Subir Frontend

3. Abrir navegador

4. Validar Sidebar

5. Validar Header

6. Validar Login

7. Validar Operation

8. Validar Connections

9. Validar Diagnostics

10. Validar Labs

11. Validar Settings

12. Abrir DevTools

13. Conferir Console

14. Tirar prints

---

# Critérios de Aceitação

MainLayout funcionando.

Sidebar funcionando.

Header funcionando.

Rotas funcionando.

Build passando.

Sem regressão.

Nenhuma alteração Backend.

Nenhuma alteração Connector.

Dashboard preparado para próximas Sprints.

---

# Entrega

Objetivo

Arquitetura

Arquivos criados

Arquivos modificados

Componentes criados

Componentes reutilizados

Build

Resultado

Como testar

Critérios

Riscos

Sugestão de commit

---

# Commit (após aprovação)

refactor(frontend): create modular application layout and navigation foundation
