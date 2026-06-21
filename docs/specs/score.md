# spec — score (`engine/score.py`)

Mede quão **resolvido** um claim está. Determinístico (ADR-004).

**`compute_scores(claims, verdicts, doc_text=None) -> {id: score}`**
`score = base + herança + fechadas − abertas`.
- base: idea graph = 10; source graph = 0, +10 se `is_grounded` (ADR-001).
- herança: soma do score dos pais em `derives_from` (topológico, detecta ciclo).
- abertas: `structural_gaps` + `verification_items` reais (ignora "(non-blocking)").
- fechadas: `resolved_gaps` + `verified_items`.

**CLI:** `python3 engine/score.py claims.json verdicts.json scores.json [--doc texto]`.

**Invariantes:** nunca LLM; "(non-blocking)" não derruba; recalcular a cada mudança. Testes: `test_score.py`, `test_domain.py`.
