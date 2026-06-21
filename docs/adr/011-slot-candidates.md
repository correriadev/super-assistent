# ADR-011 — Slot candidates no verification_item

**Status:** aceito, construído (`engine/resolution.py:attach_candidates`).

**Contexto:** um match ambíguo (ADR-010) precisa de superfície humana para escolher entre os trechos em conflito.

**Decisão:** carimbar `candidates: [{source_claim, excerpt, confidence}]` **no próprio verification_item** (não array no veredito). O item **segue aberto** (score conta a dúvida); `link_claim` recusa persistir ambíguo; o reporter renderiza a escolha.

**Consequência:** a ambiguidade viaja com a dúvida. Quando o humano escolhe, o item vira `verified_item` + link persistido. `candidates` ≠ `[Especulativo]` (eixos distintos).
