# SPRINT 5 — FRIDAY CONNECTION CENTER

## Status

Planned

---

# Objetivo

Criar a Central Oficial de Conexões do Friday Trade.

Esta Sprint deve reorganizar apenas a experiência do usuário relacionada à conexão com a Polarium.

Não deve criar nova lógica de conexão.

Não deve alterar o backend.

Não deve alterar APIs.

Não deve alterar o Connector.

Não deve alterar providers.

Não deve alterar AI, Risk ou Execution.

O objetivo é transformar a conexão com a Polarium em um fluxo visual, claro, seguro e profissional.

---

# Contexto Atual

Hoje a conexão com a Polarium está distribuída entre vários painéis e ferramentas:

- Polarium Login Panel
- OAuth Lab
- Session Inspector
- WebSocket Recorder
- Diagnostics
- Direct Login Lab
- status de conta
- sincronização
- logout

Esses recursos são úteis para desenvolvimento, mas confundem o operador.

A tela de operação deve mostrar apenas um estado simples:

- Conectado
- Não conectado
- Conta identificada
- Moeda identificada
- Ambiente DEMO ou REAL
- Pronto ou bloqueado para operar

Os detalhes técnicos devem permanecer fora da tela operacional.

---

# Rota Oficial

A Central de Conexões deve continuar em:

```text
/connections/polarium
```

A opção Conexões da Sidebar deve ficar visualmente ativa quando essa página estiver aberta.

---

# Estrutura Visual

A página deve ser dividida em áreas claras.

## 1. Cabeçalho da Conexão

Mostrar:

- Broker: Polarium
- Status geral
- Ambiente da conta
- Conta identificada
- Moeda identificada
- Saldo disponível
- Última sincronização
- Última atualização
- Último erro sanitizado

Nunca mostrar:

- token
- cookie
- bearer
- authorization
- refresh token
- SSID
- headers privados
- HAR
- credenciais
- conteúdo bruto de sessão

---

## 2. Wizard de Conexão

Criar um fluxo visual com as etapas:

```text
OAuth
  ↓
Sessão
  ↓
WebSocket
  ↓
Conta
  ↓
Moeda
  ↓
Market Sync
  ↓
READY
```

Cada etapa deve possuir um estado visual.

Estados permitidos:

- success
- running
- error
- pending
- blocked

Os componentes devem traduzir esses estados para uma apresentação amigável.

Exemplo:

```text
OAuth          Concluído
Sessão         Concluído
WebSocket      Em andamento
Conta          Aguardando
Moeda          Aguardando
Market Sync    Bloqueado
READY          Bloqueado
```

Não criar estado fictício de sucesso.

Os estados devem ser derivados somente de dados já existentes no frontend ou retornados pelas APIs atuais.

Quando não houver informação suficiente, mostrar:

```text
Não verificado
```

e nunca assumir sucesso.

---

## 3. Resumo Operacional

Criar um card com:

- Broker
- Tipo de conta
- Ambiente
- Moeda
- Saldo
- Connector status
- WebSocket status
- Market status
- Operação disponível

A informação “Operação disponível” deve ser apenas visual e derivada do estado atual.

Não alterar a lógica real do AutoTrade Gate.

Não duplicar regras de Risk no frontend.

---

## 4. Ações

Criar uma área de ações com os botões existentes:

- Conectar
- Sincronizar
- Atualizar status
- Desconectar

Reutilizar os endpoints e funções existentes.

Não criar endpoints novos.

Não criar fluxo alternativo de autenticação.

Não disparar execução real.

Os botões devem possuir:

- estado de carregamento;
- bloqueio durante requisição;
- feedback de sucesso;
- feedback de erro sanitizado;
- prevenção de clique duplicado.

---

## 5. Histórico de Tentativas

Criar um histórico visual local da sessão atual da interface.

Pode exibir:

- horário da tentativa;
- ação executada;
- resultado;
- etapa afetada;
- mensagem sanitizada.

Importante:

- não persistir tokens;
- não persistir cookies;
- não registrar payload bruto;
- não registrar headers privados;
- não armazenar segredo em LocalStorage;
- não criar banco de dados;
- não alterar backend.

Esse histórico pode existir apenas em memória durante a sessão do frontend.

---

## 6. Tratamento de Erros

Mensagens técnicas devem ser convertidas em mensagens compreensíveis.

Exemplos:

```text
Falha ao iniciar OAuth.
```

```text
Sessão não encontrada.
```

```text
WebSocket desconectado.
```

```text
Conta ainda não sincronizada.
```

```text
Moeda da conta não identificada.
```

Evitar mostrar traceback, stack trace ou conteúdo sensível.

Pode existir uma área expansível chamada:

```text
Detalhes técnicos sanitizados
```

Somente se os dados já forem seguros.

---

# Componentes

Criar componentes reutilizáveis, preferencialmente dentro de:

```text
frontend/src/components/connections/
```

Estrutura sugerida:

```text
ConnectionWizard/
ConnectionStep/
ConnectionStatusCard/
ConnectionActions/
ConnectionSummary/
ConnectionAttemptHistory/
ConnectionErrorAlert/
ConnectionReadinessBadge/
```

Separar lógica de UI quando necessário.

Criar hooks em:

```text
frontend/src/hooks/
```

Exemplos sugeridos:

```text
usePolariumConnection.ts
useConnectionWizard.ts
useConnectionHistory.ts
```

Não criar hooks vazios apenas para preencher estrutura.

---

# Reutilização

Reutilizar sempre que fizer sentido:

- Card
- Section
- StatusBadge
- ActionButton
- Loading
- EmptyState
- PageContainer
- PageTitle
- PolariumLoginPanel
- hooks de status existentes
- serviços HTTP existentes
- tipos já definidos

Evitar duplicar chamadas de API.

Evitar duplicar tipos.

---

# Separação Entre Operação, Conexão e Laboratório

## Página de Operação

A página `/operation` não deve mostrar:

- OAuth Lab
- Session Inspector
- WS Recorder
- Direct Login Lab
- cookies
- headers
- protocolos
- testes técnicos
- mensagens WebSocket brutas

Ela deve mostrar somente um resumo simples da conexão.

Exemplo:

```text
Polarium
Conectado
Conta DEMO
BRL
Pronto para análise
```

ou:

```text
Polarium não conectada
Ir para Central de Conexões
```

## Página de Conexões

Deve mostrar o fluxo amigável para conexão e sincronização.

## Polarium Lab

A rota `/labs/polarium` continua contendo ferramentas experimentais e técnicas.

Não mover labs para a Central de Conexões.

---

# Preparação para Múltiplos Brokers

A arquitetura visual deve estar preparada para suportar outros brokers no futuro.

Não implementar outro broker agora.

Evitar componentes acoplados exclusivamente ao nome Polarium quando puderem ser genéricos.

Exemplo:

```text
ConnectionWizard
ConnectionStep
ConnectionSummary
```

A página pode continuar sendo específica:

```text
PolariumConnections
```

---

# Branding

Toda referência visual ao produto deve vir do módulo:

```text
frontend/src/branding/
```

Não escrever diretamente em componentes:

- Friday Trade
- Trade Smarter.
- Professional AI Trading Platform
- versão
- nome do operador
- cores oficiais

Usar o módulo de branding existente.

---

# Segurança

Nunca expor na interface:

- tokens
- cookies
- bearer
- refresh token
- authorization
- SSID
- .env
- HAR
- credenciais
- headers sensíveis

Nunca armazenar esses valores em:

- LocalStorage
- SessionStorage
- logs do navegador
- histórico de tentativas
- estado compartilhado sem necessidade

---

# Não Fazer

Não alterar backend.

Não alterar Connector.

Não alterar API.

Não alterar contratos Pydantic.

Não alterar providers.

Não alterar AI.

Não alterar Risk.

Não alterar Execution.

Não alterar dependências.

Não instalar bibliotecas novas.

Não alterar `package-lock.json`.

Não renomear o repositório.

Não remover os laboratórios existentes.

Não fazer commit.

Não fazer push.

---

# Testes Obrigatórios

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run build
```

Também executar os testes do backend para garantir que nenhuma mudança indireta ocorreu:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader
.venv/bin/python -m pytest -q
```

---

# COMO TESTAR A SPRINT

Criar no relatório final uma seção completa ensinando o Renan a testar.

A instrução deve incluir:

## Passo 1

Abrir o VS Code.

## Passo 2

Abrir o Terminal integrado.

## Passo 3

Entrar no projeto:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader
```

## Passo 4

Subir o backend:

```bash
.venv/bin/python -m uvicorn app.main:app --reload
```

## Passo 5

Abrir outro terminal.

## Passo 6

Subir o frontend:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run dev
```

## Passo 7

Abrir:

```text
http://localhost:5173/connections/polarium
```

## Passo 8

Explicar exatamente o que verificar em:

- Header
- Sidebar
- Status geral
- Wizard
- Resumo operacional
- Botões
- Histórico
- Mensagens de erro
- Responsividade

## Passo 9

Explicar quais botões podem ser clicados sem usar credenciais reais.

## Passo 10

Explicar como abrir o DevTools e verificar o Console.

## Passo 11

Explicar o resultado esperado.

## Passo 12

Solicitar prints de:

- página completa;
- Wizard;
- resumo operacional;
- histórico de tentativas;
- Console sem erros;
- testes do backend;
- build do frontend.

---

# Critérios de Aprovação

A Sprint só estará pronta quando:

- a página `/connections/polarium` estiver organizada;
- o Wizard mostrar todas as etapas;
- nenhum sucesso for inventado;
- o status vier de dados existentes;
- a Sidebar destacar Conexões;
- os botões reutilizarem a lógica atual;
- nenhuma API nova for criada;
- nenhum backend for alterado;
- nenhum segredo for exibido;
- o histórico não guardar dados sensíveis;
- o frontend build passar;
- os testes do backend passarem;
- a página de operação continuar sem labs técnicos;
- o Polarium Lab continuar disponível;
- não houver erro vermelho no Console;
- a documentação da Sprint estiver atualizada.

---

# Documentação

Atualizar, se necessário:

```text
docs/ARCHITECTURE.md
ROADMAP.md
CHANGELOG.md
```

Atualizar o próprio documento da Sprint com o status final.

Não modificar documentos sem necessidade real.

---

# Entrega Obrigatória

Ao finalizar, entregar exatamente:

1. Objetivo.
2. Plano executado.
3. Arquitetura implementada.
4. Componentes criados.
5. Componentes reutilizados.
6. Hooks criados ou modificados.
7. Arquivos modificados.
8. APIs e endpoints reutilizados.
9. Regras de segurança aplicadas.
10. Testes executados.
11. Resultado dos testes.
12. Resultado do build.
13. Como testar a Sprint, com passo a passo completo para o Renan.
14. Critérios de aprovação.
15. Riscos conhecidos.
16. Débitos técnicos.
17. Atualizações de documentação.
18. Saída resumida de `git status --short`.
19. Sugestão de mensagem de commit.

Mensagem sugerida:

```text
refactor(frontend): introduce guided Friday Connection Center
```

---

# Regra Final

NÃO faça commit.

NÃO faça push.

Pare após entregar o relatório completo e aguarde a revisão do J.A.R.V.I.S e do Renan Godoy.