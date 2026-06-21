# ADR-005 — LLM só na borda, injetado

**Status:** aceito, construído.

**Contexto:** o motor (peso, propagação, grounding, navegação) é determinístico. O LLM serve só para julgamento (o gate discrimina; o extractor ancora o trecho) e é caro.

**Decisão:** todo ponto que usa LLM é **injetado na borda**: `decompose_fn` (extractor real) e `embed_fn` (embedder real). Os módulos não chamam API nenhuma; quem injeta decide (local/API/stub de teste).

**Consequência:** testes rodam com stubs, grátis. Trocar de modelo não toca o motor. O único ponto de LLM no linking é o lazy-decompose (passo 2a). Ver ADR-009.
