# ADR-007 — Cross-graph linking sob demanda

**Status:** aceito, construído (`engine/resolution.py`, `engine/linking.py`).

**Contexto:** um `verification_item` com domínio pode buscar resposta no source graph daquele domínio. Decompor a lei inteira antes seria caro e dispersivo.

**Decisão:** árvore — (1) existe domínio? (2) procura nos nós (`resolve_link`); (2a) se not-found, **lazy-decompose dirigido pela dúvida** (navega → decompõe só a seção → grounding → re-busca); todo caminho volta ao usuário. RAG entra só no passo 2a, como navegação, nunca como fonte de verdade. Ver [spec](../specs/cross-graph-linking.md).

**Consequência:** o grafo cresce só onde a dúvida pede. Ledger anti-token nunca re-decompõe a mesma seção.
