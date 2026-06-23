"""test_embed.py — cobre engine/embed.py sem precisar de sentence_transformers real.

embed_fn(text) → list[float], lazy-carrega SentenceTransformer na primeira chamada.

Estratégia: sentence_transformers pode não estar instalado. Shimamos o módulo em
sys.modules antes de importar engine.embed, depois substituímos _model em cada teste
para controlar o retorno sem tocar na rede.
"""

import importlib
import sys
import types
from unittest.mock import MagicMock

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# shim sentence_transformers se ausente (executado no momento do import do test)
# ---------------------------------------------------------------------------

_ST_REAL = "sentence_transformers" in sys.modules

if not _ST_REAL:
    _shim = types.ModuleType("sentence_transformers")
    _shim.SentenceTransformer = MagicMock  # classe substituta mínima
    sys.modules["sentence_transformers"] = _shim

# agora podemos importar engine.embed com segurança
import engine.embed as _embed_mod  # noqa: E402

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_fake_model():
    """Retorna mock de SentenceTransformer com encode determinístico por seed."""

    model = MagicMock()

    def fake_encode(text, normalize_embeddings=False):
        seed = sum(ord(c) for c in text)
        rng = np.random.default_rng(seed)
        arr = rng.random(384, dtype=np.float32)
        return arr  # .tolist() é chamado pelo caller (embed_fn)

    model.encode.side_effect = fake_encode
    return model


# ---------------------------------------------------------------------------
# testes (executam sempre)
# ---------------------------------------------------------------------------

def test_embed_retorna_lista_de_floats():
    """embed_fn deve devolver list[float], nunca ndarray ou outro tipo."""
    _embed_mod._model = _make_fake_model()

    result = _embed_mod.embed_fn("qualquer texto")

    assert isinstance(result, list), "embed_fn deve retornar list"
    assert len(result) > 0, "lista não pode ser vazia"
    assert all(isinstance(x, float) for x in result), "todos os elementos devem ser float"


def test_embed_deterministico():
    """Mesma entrada → mesmo vetor (sem estado externo)."""
    _embed_mod._model = _make_fake_model()

    v1 = _embed_mod.embed_fn("imposto sobre serviços")
    v2 = _embed_mod.embed_fn("imposto sobre serviços")

    assert v1 == v2, "embed_fn deve ser determinístico para a mesma entrada"


def test_embed_discrimina_entradas_distintas():
    """Entradas diferentes → vetores diferentes."""
    _embed_mod._model = _make_fake_model()

    v_gato = _embed_mod.embed_fn("gato")
    v_aviao = _embed_mod.embed_fn("avião")

    assert v_gato != v_aviao, "embed_fn deve produzir vetores distintos para textos distintos"


# ---------------------------------------------------------------------------
# teste de integração real (skip se sentence_transformers ausente)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not _ST_REAL,
    reason="sentence_transformers não instalado; teste de integração ignorado",
)
def test_embed_integracao_real():
    """Integração real: modelo local produz vetores de 384 dims normalizados."""
    _embed_mod._model = None  # force lazy-load limpo

    v = _embed_mod.embed_fn("reforma tributária")

    assert isinstance(v, list)
    assert len(v) == 384, f"esperado 384 dims, obteve {len(v)}"
    norm = sum(x * x for x in v) ** 0.5
    assert abs(norm - 1.0) < 1e-4, f"vetor não normalizado: norma={norm}"
