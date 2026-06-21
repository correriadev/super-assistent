# spec — retrieval (`engine/retrieval.py`)

Navegação: dado a dúvida, achar **qual seção** do documento responde. Metade "retrieval" do RAG; quarentena de imprecisão — nunca vira fonte de verdade nem score (ADR-009).

**`split_sections(doc_text)`** — quebra por parágrafo (cai pra marcadores `Art. N` se for bloco único).
**`rank_lexical(query, chunks)`** — jaccard. Grátis. Viés a heading.
**`rank_semantic(query, chunks, embed_fn)`** — cosseno via `embed_fn` injetado.
**`retrieve(query, doc_text, embed_fn=None, top_k=1)`** — despacha semântico se houver `embed_fn`, senão lexical.

**Embedder:** `engine/embed.py` (sentence-transformers local, grátis offline, ADR-005). Testes: `test_retrieval.py` (stubs).
