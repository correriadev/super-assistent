#!/usr/bin/env python3
"""
retrieval.py — navegação: dado um query (item.text), achar QUAL seção do documento
responde. É a metade "retrieval" do RAG. NÃO decide verdade — só aponta onde olhar.

Dois ranqueadores, mesma interface:
  - lexical  (grátis, sem modelo): overlap de termos. Erra paráfrase.
  - semantic (embeddings): cosseno de vetores. Pega paráfrase. O modelo de embedding
    entra por INJEÇÃO (`embed_fn`) — este módulo não chama API nenhuma; quem injeta
    decide se é local, API, ou stub de teste.

A fronteira dura: o trecho retornado vira candidato a decompor (extractor), com
excerpt verbatim e grounding exato depois. A imprecisão do retrieval fica em
quarentena aqui — nunca vira fonte de verdade nem de score.
"""

import math
import re

from engine.linking import _terms, _jaccard, item_text


def split_sections(doc_text):
    """Quebra o doc em seções. Tenta marcadores 'Art. N'; senão, parágrafos.
    Retorna lista de {id, text}."""
    if not doc_text:
        return []
    # granularidade primária = parágrafo (funciona em estatuto E em prosa).
    paras = [p.strip() for p in re.split(r"\n\s*\n", doc_text) if p.strip()]
    if len(paras) <= 1:
        # doc num bloco só (sem linhas em branco) — cai pra marcadores 'Art. N'
        paras = [p.strip() for p in re.split(r"(?=Art\.\s*\d+)", doc_text) if p.strip()]
    chunks = []
    for i, p in enumerate(paras):
        m = re.match(r"Art\.\s*(\d+)", p)
        cid = f"art-{m.group(1)}" if m else f"sec-{i}"
        chunks.append({"id": cid, "text": p})
    return chunks


def rank_lexical(query, chunks):
    """Ranqueia por overlap de termos (jaccard). Grátis, determinístico."""
    q = _terms(query)
    scored = [(_jaccard(q, _terms(c["text"])), c) for c in chunks]
    return sorted(scored, key=lambda x: x[0], reverse=True)


def _cosine(a, b):
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def rank_semantic(query, chunks, embed_fn):
    """Ranqueia por similaridade de cosseno entre embeddings. `embed_fn(text)->vetor`
    é injetado (local/API/stub). Pega paráfrase onde o lexical falha."""
    qv = embed_fn(query)
    scored = [(_cosine(qv, embed_fn(c["text"])), c) for c in chunks]
    return sorted(scored, key=lambda x: x[0], reverse=True)


def retrieve(query, doc_text, embed_fn=None, top_k=1):
    """Interface única. Usa semantic se `embed_fn` for dado, senão lexical.
    `query` aceita string ou verification_item objeto. Retorna [(score, chunk), ...]."""
    query = item_text(query)
    chunks = split_sections(doc_text)
    if not chunks:
        return []
    ranked = rank_semantic(query, chunks, embed_fn) if embed_fn else rank_lexical(query, chunks)
    return ranked[:top_k]
