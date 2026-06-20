#!/usr/bin/env python3
"""embed.py — embed_fn real (local) p/ navegação semântica do retrieval.

Modelo multilíngue simétrico (query e passage embedam igual), serve a interface
embed_fn(text)->vetor que `retrieval.rank_semantic` espera. Roda offline depois do
primeiro download. ponytail: lazy-load do modelo; sem cache de vetores até um
profiler pedir.
"""

from sentence_transformers import SentenceTransformer

_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
_model = None


def embed_fn(text):
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model.encode(text, normalize_embeddings=True).tolist()
