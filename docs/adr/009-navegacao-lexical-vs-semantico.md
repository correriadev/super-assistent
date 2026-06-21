# ADR-009 — Navegação: lexical grátis vs semântico injetado

**Status:** aceito, construído (`engine/retrieval.py`, `engine/embed.py`).

**Contexto:** o lazy-decompose precisa achar **qual seção** do documento responde a dúvida. Lexical (jaccard) é grátis mas tem viés a heading curto-e-denso.

**Decisão:** dois ranqueadores, mesma interface: `rank_lexical` (grátis) e `rank_semantic` (cosseno via `embed_fn` injetado). Medição em doc real (760 linhas): lexical navega 11/15 para headings; semântico acerta 15/15 em prosa.

**Consequência:** para documento de porte real o embedder não é opcional. Embedder local (`embed.py`, sentence-transformers) — grátis offline, injetado na borda (ADR-005).
