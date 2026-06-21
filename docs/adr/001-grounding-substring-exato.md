# ADR-001 — Grounding por substring exato, nunca similaridade

**Status:** aceito, construído (`engine/score.py:is_grounded`).

**Contexto:** um claim do source graph (lei) precisa de uma medida de confiança rastreável. Usar similaridade textual reintroduziria o risco de "parece que diz" sem dizer.

**Decisão:** grounding = o `excerpt` existe **literalmente** no documento (substring normalizado por espaços/caixa). Binário: existe ou não. Excerpt localizável → +10 de peso; inventado → 0.

**Consequência:** qualquer humano clica e confere. Grounding = "o texto diz isto", nunca "isto é verdade". O embedder (ADR-009/010) mudou navegação e matching, **nunca** o grounding.
