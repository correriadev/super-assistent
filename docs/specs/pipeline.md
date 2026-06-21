# spec — pipeline (orchestrator + agents)

O fluxo multi-nível. Agents em `.claude/agents/`; tiers em [quality/token-budget](../quality/token-budget.md). O orchestrator coordena, não decompõe nem avalia.

**Ciclo de um nível:**
1. **extractor** (haiku) → `claims.json` (binding null, ADR-013).
2. **Modalidade em lote** (humano) → seta binding.
3. **gate** (sonnet, lotes ≤5, ADR-014) → JSON por claim, um dos 6 status.
4. Consolida `verdicts.json`.
5. **score** (código) → `scores.json`.
6. **reporter** (haiku) → alerta sóbrio (revela, não sugere).
7. **Resolver** (humano) → fecha issues (move p/ verified/resolved).

**Source graph + linking:** extractor modo legal → `claims-source.json`; score com `--doc` (grounding); `resolve_link`/`link_claim`; `propagate` na emenda.

**Descida (sob comando):** 8. `descent_gate` (política). 9. **expander** (haiku) → `claims-nivel-N.json` + `refresh_provisional`. 10. revisão humana (`[Especulativo]`). 11. roda o ciclo no novo nível.
