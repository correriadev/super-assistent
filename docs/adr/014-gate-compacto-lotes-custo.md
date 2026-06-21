# ADR-014 — Gate compacto, fan-out em lotes, custo

**Status:** aceito.

**Contexto:** uma rodada estourou o orçamento de tokens: gate devolvendo ensaio por claim + fan-out ilimitado (1 subagent caro por claim) + PDF como imagens.

**Decisão:** o gate devolve **só o JSON estruturado** (raciocínio interno). Fan-out em **lotes de ≤5**; avisar o humano se >10 claims. PDF/documento grande lido como **texto extraído**, nunca page-images.

**Consequência:** custo medido ≈ **8k tokens/gate** (sonnet, carrega a spec + raciocina) — é o gargalo do fan-out; pesar antes de rodar N claims. Ver [quality/token-budget](../quality/token-budget.md).
