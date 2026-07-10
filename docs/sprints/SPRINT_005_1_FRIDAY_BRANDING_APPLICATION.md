# SPRINT 5.1 — FRIDAY TRADE BRANDING APPLICATION

## Status

Planned

## Objetivo

Aplicar oficialmente a identidade visual Friday Trade em todo o frontend.

O módulo de branding já existe, mas a marca ainda não foi consolidada visualmente na plataforma.

Esta Sprint deve:

- oficializar o nome Friday Trade;
- aplicar o slogan Trade Smarter.;
- criar uma logo vetorial definitiva;
- criar favicon;
- eliminar referências visuais antigas a J.A.R.V.I.S;
- garantir que toda identidade seja consumida pelo módulo de branding.

Não alterar backend, Connector, APIs, regras de trading ou dependências.

---

## Identidade oficial

Nome:

Friday Trade

Nome curto:

Friday

Slogan:

Trade Smarter.

Descrição:

Professional AI Trading Platform

Operador:

Renan Godoy

---

## Logo oficial

Criar uma logo original em SVG dentro de:

```text
frontend/src/branding/assets/
```

Arquivos esperados:

```text
friday-trade-logo.svg
friday-trade-symbol.svg
friday-trade-favicon.svg
```

Características:

- símbolo baseado na letra F;
- composição minimalista;
- detalhe sutil inspirado em candle ou movimento de mercado;
- aparência premium;
- moderna;
- tecnológica;
- profissional;
- boa leitura em tamanhos pequenos;
- fundo transparente;
- sem robô;
- sem cérebro;
- sem referência à Marvel;
- sem copiar marcas de terceiros.

Paleta:

- fundo principal: preto/grafite;
- símbolo principal: branco;
- destaque: azul elétrico;
- verde somente para sucesso/WIN;
- vermelho somente para erro/LOSS.

A logo deve funcionar em:

- Sidebar;
- Login;
- Header;
- favicon;
- cards institucionais;
- fundo escuro;
- fundo claro, quando aplicável.

Não usar emoji como logo.

---

## Módulo de branding

Revisar:

```text
frontend/src/branding/brand.ts
```

Ele deve ser a única fonte oficial para:

- nome;
- nome curto;
- slogan;
- descrição;
- versão;
- operador;
- caminhos da logo;
- favicon;
- cores oficiais.

Exemplo conceitual:

```ts
export const BRAND = {
  name: "Friday Trade",
  shortName: "Friday",
  tagline: "Trade Smarter.",
  descriptor: "Professional AI Trading Platform",
  operator: "Renan Godoy",
  assets: {
    logo: "...",
    symbol: "...",
    favicon: "...",
  },
};
```

Adaptar ao padrão TypeScript existente.

---

## Aplicação visual obrigatória

Aplicar a identidade em:

- tela de Login;
- Sidebar;
- Header;
- página de Operation;
- Central de Conexões;
- Diagnostics;
- Settings;
- Polarium Lab;
- Brand Center;
- estados vazios institucionais;
- título da aba do navegador;
- favicon;
- tela inicial da aplicação.

O usuário não deve mais encontrar visualmente:

- J.A.R.V.I.S AI Trader;
- JARVIS IA;
- Jarvis Trader;
- logo antiga;
- textos antigos de branding.

O nome técnico do repositório pode continuar:

```text
jarvis-ai-trader
```

Não renomear:

- repositório;
- diretórios;
- imports;
- pacotes Python;
- módulos backend;
- variáveis técnicas internas sem necessidade.

---

## Tela de Login

Transformar a tela em uma apresentação profissional da marca.

Mostrar:

- logo Friday Trade;
- nome;
- slogan;
- descrição;
- formulário visual de acesso;
- aviso Modo Desenvolvimento;
- versão da aplicação;
- status simples da plataforma.

Não implementar autenticação real nesta Sprint.

Não apresentar o formulário como autenticação segura já concluída.

---

## Sidebar

No topo da Sidebar mostrar:

- símbolo da marca;
- Friday Trade;
- Trade Smarter.

Quando recolhida, mostrar apenas o símbolo oficial.

---

## Header

Mostrar de forma discreta:

- Friday Trade;
- broker;
- conta;
- ambiente;
- moeda;
- status da conexão.

Não repetir slogan excessivamente em todas as telas.

---

## Central de Conexões

Aplicar a identidade Friday Trade na página criada na Sprint 5.

Não alterar sua lógica.

Manter:

- Wizard;
- resumo;
- ações;
- histórico;
- sanitização;
- status conservador.

---

## Brand Center

Renomear a rota e a interface de Branding para:

```text
/developer/brand-center
```

Nome exibido:

```text
Brand Center
```

A página deve mostrar:

- logo principal;
- símbolo;
- favicon;
- paleta;
- tipografia;
- nome;
- slogan;
- descrição;
- exemplos de aplicação.

Remover sugestões de outros nomes, pois Friday Trade foi escolhido oficialmente.

Manter redirecionamento ou compatibilidade com `/branding`, caso necessário, para não quebrar navegação existente.

---

## Regra permanente

Nenhum texto fixo relacionado à marca pode ficar espalhado pelo frontend.

Buscar referências antigas com comandos equivalentes a:

```bash
grep -RniE "J\.?A\.?R\.?V\.?I\.?S|Jarvis|JARVIS|AI Trader" frontend/src frontend/index.html
```

Cada ocorrência deve ser classificada:

1. branding visual antigo: substituir;
2. nome técnico necessário: preservar;
3. comentário ou conteúdo histórico: avaliar.

Não executar substituição global cega.

---

## Acessibilidade

A logo deve possuir:

- `alt` adequado;
- contraste;
- versão compacta;
- foco visível quando usada em links;
- dimensões estáveis para evitar layout shift.

SVGs não devem conter scripts ou conteúdo externo.

---

## Segurança

Não incluir no SVG:

- scripts;
- links externos;
- dados embutidos desnecessários;
- metadados pessoais;
- tokens;
- comentários com caminhos locais.

---

## Fora do escopo

Não alterar backend.

Não alterar Connector.

Não alterar endpoints.

Não alterar contratos.

Não alterar Risk.

Não alterar AI.

Não alterar Execution.

Não instalar dependências.

Não alterar `package.json`.

Não alterar `package-lock.json`.

Não fazer commit.

Não fazer push.

---

## Testes obrigatórios

Frontend:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend
npm run build
```

Backend:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader
.venv/bin/python -m pytest -q
```

Verificar referências visuais antigas:

```bash
grep -RniE "J\.?A\.?R\.?V\.?I\.?S|Jarvis|JARVIS|AI Trader" frontend/src frontend/index.html || true
```

Explicar qualquer ocorrência que precise permanecer.

---

# COMO TESTAR A SPRINT

O relatório final deve ensinar o Renan passo a passo a:

1. subir backend;
2. subir frontend;
3. abrir `/login`;
4. conferir logo, nome, slogan e favicon;
5. abrir `/operation`;
6. abrir `/connections/polarium`;
7. conferir Sidebar e Header;
8. abrir `/diagnostics`;
9. abrir `/labs/polarium`;
10. abrir `/developer/brand-center`;
11. verificar ausência do nome visual antigo;
12. verificar o Console;
13. conferir responsividade;
14. enviar prints ao J.A.R.V.I.S.

Prints obrigatórios:

- Login;
- Sidebar;
- Header;
- Operation;
- Connection Center;
- Brand Center;
- aba do navegador com favicon;
- Console sem erros;
- build;
- pytest.

---

## Critérios de aprovação

- Friday Trade aplicado visualmente em toda a plataforma;
- logo original em SVG criada;
- favicon aplicado;
- slogan oficial aplicado;
- nenhuma referência visual antiga relevante;
- identidade centralizada;
- Login atualizado;
- Sidebar atualizada;
- Header atualizado;
- Connection Center preservado;
- build aprovado;
- testes backend aprovados;
- nenhuma dependência modificada;
- nenhum código backend alterado;
- nenhum segredo exposto.

---

## Entrega obrigatória

1. Objetivo.
2. Plano executado.
3. Identidade aplicada.
4. Logo e arquivos criados.
5. Arquivos modificados.
6. Referências antigas encontradas.
7. Referências substituídas.
8. Referências técnicas preservadas e justificativa.
9. Aplicações da logo.
10. Testes executados.
11. Resultado dos testes.
12. Resultado do build.
13. Como testar passo a passo.
14. Riscos conhecidos.
15. Débitos técnicos.
16. `git status --short`.
17. Sugestão de commit.

Mensagem sugerida:

```text
feat(branding): apply official Friday Trade identity across frontend
```

NÃO faça commit.

NÃO faça push.

Aguarde a revisão do J.A.R.V.I.S e do Renan Godoy.
