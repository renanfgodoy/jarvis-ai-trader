# SPRINT V4.8.1 — STABLE CHECKPOINT

## Objetivo

Preparar a Friday para seu primeiro checkpoint estável.

Esta sprint NÃO cria funcionalidades.

Ela existe para garantir que tudo desenvolvido nas Sprints V4.x esteja consistente antes do primeiro commit oficial.

---

# REGRA DE OURO

Esta sprint NÃO deve:

- criar novas telas;
- alterar arquitetura;
- alterar backend;
- alterar IQ Option Runtime;
- alterar Worker;
- alterar Provider;
- alterar CandleStore;
- alterar SSE;
- alterar Polling;
- alterar API;
- alterar Engine;
- alterar Strategy Engine;
- alterar Assets;
- alterar gráficos.

Esta sprint é exclusivamente de:

- auditoria;
- limpeza;
- validação;
- organização;
- estabilidade.

---

# PARTE 1 — LIMPEZA

## Verificar arquivos órfãos

Auditar arquivos como:

```
CandleStore
Chart
IQ
MarketChart
Provider
RealCandleChart
```

Confirmar:

- tamanho;
- origem;
- utilização.

Se forem arquivos acidentais e não utilizados:

NÃO apagar.

Apenas listar no relatório.

---

## Verificar docs temporários

Localizar:

```
*.md~
*.tmp
*.bak
```

Relatar.

Não remover.

---

# PARTE 2 — GIT

Executar apenas consultas.

Permitir:

```
git status --short
git diff --stat
git diff --name-only
git ls-files --others --exclude-standard
```

Não executar:

```
git add
git commit
git push
git restore
git clean
```

---

# PARTE 3 — FRONTEND

Validar:

- gráfico;
- troca de ativo;
- troca de timeframe;
- lista completa de ativos;
- Friday Strategy;
- DEV;
- Operador;
- layout;
- responsividade.

Sem alterar comportamento.

---

# PARTE 4 — BUILD

Executar:

```
cd frontend
npm run build
```

Registrar resultado.

---

# PARTE 5 — TESTES

Executar:

```
.venv/bin/python -m pytest tests/frontend -q
```

Depois:

```
.venv/bin/python -m pytest -q
```

Registrar resultados.

---

# PARTE 6 — VALIDAÇÃO

Confirmar:

- lista de ativos funcional;
- Strategy Engine intacto;
- gráfico funcionando;
- dropdown funcionando;
- SSE preservado;
- polling preservado;
- backend intacto;
- frontend íntegro.

---

# PARTE 7 — RELATÓRIO

Entregar:

1. arquivos órfãos encontrados;
2. arquivos temporários;
3. git status;
4. git diff;
5. build;
6. testes frontend;
7. suíte completa;
8. lista de ativos;
9. troca de ativos;
10. troca de timeframe;
11. responsividade;
12. riscos restantes;
13. recomendação para commit.

---

## IMPORTANTE

Não executar:

- git add
- git commit
- git push

Apenas preparar o checkpoint.