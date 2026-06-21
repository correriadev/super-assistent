# Orçamento de token — o recurso escasso

Token é ouro. Antes de qualquer ação que gasta (subagent, modelo real): **estimar, apresentar, esperar OK**. Determinístico/teste é grátis.

**Custos medidos:**
- **gate ≈ 8k tokens/claim** (sonnet — carrega a spec + raciocina). É o gargalo do fan-out.
- extractor / reporter / expander ≈ 4–10k cada (haiku).
- embedder (local) e navegação/score/linking determinístico = **0**.

**Regras (ADR-014):**
- gate devolve **só JSON**; raciocínio interno não volta ao contexto.
- fan-out em **lotes de ≤5**; **avisar se >10 claims** antes de rodar.
- documento grande lido como **texto extraído**, nunca page-images (reenviadas a cada turno).
- **embedder local** (sentence-transformers) em vez de API: grátis offline.
- recon determinístico (grátis) **antes** de decidir gastar (ex: navegar antes de decompor).

**Tiers de agent:** gate/critic = sonnet · extractor/expander/reporter/intake = haiku · orchestrator herda.
