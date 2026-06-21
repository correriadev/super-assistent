# Estratégia de teste

**Determinístico = pytest, grátis (ADR-004/005).** Peso, propagação, herança, navegação, matching, descida são aritmética/lógica → testáveis sem LLM. Testá-los via LLM é desperdício de token (causa real de queda de produtividade).

- **LLM nunca nos testes.** O que usa LLM é injetado (`decompose_fn`, `embed_fn`) e nos testes entra como **stub** (ex: `_stub_embed`, `_fake_decompose`). Sem API, sem rede.
- **Uma checagem por lógica não-trivial.** Cada ramo/loop/parser deixa o menor teste que falha se a lógica quebrar.
- **Dados reais como fixture leve.** Alguns testes leem `projetos/02/.../claims-source.json` e `ideias/*.txt` (rodar pytest da raiz; `pyproject.toml` fixa `pythonpath` e `testpaths`).

**Suíte atual: 56 testes.** `tests/test_{score,domain,linking,retrieval,resolution,propagation,descent}.py`.
