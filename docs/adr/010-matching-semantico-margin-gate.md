# ADR-010 — Matching semântico + margin gate

**Status:** aceito, construído (`engine/linking.py:resolve_link`).

**Contexto:** mesmo achando a seção, casar dúvida↔claim por jaccard preferia o claim genérico curto. E nenhum matcher acerta sempre.

**Decisão:** `resolve_link(..., embed_fn=)` casa por cosseno. **Margin gate:** se top-1 − top-2 < `margin` (0.05) e ambos acima do piso, devolve `result: "ambiguous"` + candidatos e **não escolhe**.

**Consequência:** duas falhas distintas — empate (margin gate pega) vs pick confiante-errado (só embedder melhor ou humano pega). O sistema expõe a incerteza em vez de chutar. Ver ADR-011.
