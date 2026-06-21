# spec — descent (`engine/descent.py`)

Gate parametrizável de descida entre níveis + marca provisional (ADR-012).

**`descent_gate(claims, verdicts, policy, min_fraction=0.6, accepted=()) -> {allowed, blocked_by, provisional_parents, resolved_fraction, reason}`**
- `policy`: `strict` | `vinculante_only` | `threshold` | `provisional` | `force`.
- resolvido = status `PASSA` ou aceite humano. Gate por **status**, não score.
- chão absoluto: `CONTRADIZ-NIVEL-ACIMA` bloqueia em qualquer política, nem aceite libera.

**`mark_provisional(child, provisional_parents)`** — carimba se `derives_from` cai em pai aberto.
**`refresh_provisional(children, provisional_parents)`** — **transitivo**: filho é provisional se algum ancestral é aberto OU provisional. Reabre/limpa conforme estado atual dos pais.

Testes: `test_descent.py`.
