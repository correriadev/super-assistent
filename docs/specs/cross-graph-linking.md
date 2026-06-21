# spec — cross-graph linking (a árvore de decisão)

Orquestra linking + retrieval (`engine/resolution.py:resolve_verification_item`). Implementa ADR-007. Todo caminho volta ao usuário (`system_decided: False`, ADR-002).

```
verification_item (com domain: lei/engenharia/financeiro)
│
1. existe domínio próprio?
│   ├── NÃO → outcome "no-domain"
│   └── SIM ↓
2. procura nos nós (resolve_link, semântico se embed_fn)
│   ├── not-found ↓
│   │     2a. hook on_not_found (lazy-decompose): navega → piso/ledger anti-token
│   │         → decompose_fn (extractor real) → grounding → re-busca
│   │     └── ainda not-found → "not-found"
│   ├── ambiguous → outcome "ambiguous" (+ candidates, ADR-011)
│   └── found → "found-strong" (score>0) | "found-weak" (score≤0)
```

**`make_lazy_decompose(decompose_fn, embed_fn=None, nav_floor=0.16)`** — o hook `on_not_found`; único ponto de LLM (injetado). **`load_domains(mapping)`** monta o registry. Testes: `test_resolution.py`, `test_retrieval.py`.
