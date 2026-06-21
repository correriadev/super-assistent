"""Navegação (retrieval.py) lexical + semântica + lazy decompose. Stubs, sem LLM/API."""

from engine.retrieval import split_sections, rank_lexical, rank_semantic, retrieve
from engine.resolution import make_lazy_decompose, resolve_verification_item

DOC = (
    "Art. 31. Os prestadores devem segregar e recolher o IBS e a CBS no momento da "
    "liquidação financeira da operação.\n\n"
    "Art. 47. O direito ao crédito do adquirente somente pode ser exercido quando "
    "ocorrida a extinção do tributo."
)


def test_split_sections_acha_artigos():
    secs = split_sections(DOC)
    ids = [s["id"] for s in secs]
    assert ids == ["art-31", "art-47"]


def test_lexical_acerta_com_palavras_iguais():
    q = "recolhe o IBS e a CBS na liquidação financeira?"
    top = rank_lexical(q, split_sections(DOC))[0]
    assert top[1]["id"] == "art-31" and top[0] > 0


# stub de embedding: 2 dimensões conceituais (settlement, credit) por presença de gatilhos
_SETTLE = {"liquidação", "liquidacao", "recolher", "segregar", "some", "cair", "conta", "antes", "momento", "financeira"}
_CREDIT = {"crédito", "credito", "adquirente", "extinção", "extincao", "direito"}


def _stub_embed(text):
    t = text.lower()
    return [sum(w in t for w in _SETTLE), sum(w in t for w in _CREDIT)]


def test_semantico_pega_parafrase_onde_lexical_falha():
    q = "o dinheiro do imposto some antes de cair na minha conta?"  # sem palavra do Art.31
    secs = split_sections(DOC)
    # lexical falha: nenhum overlap relevante
    assert rank_lexical(q, secs)[0][0] == 0.0
    # semântico acerta: mesmo conceito (settlement)
    top = rank_semantic(q, secs, _stub_embed)[0]
    assert top[1]["id"] == "art-31" and top[0] > 0.9


def test_retrieve_despacha_lexical_vs_semantico():
    q = "imposto some antes de cair na conta?"
    assert retrieve(q, DOC)[0][1]["id"] in ("art-31", "art-47")          # lexical (default)
    assert retrieve(q, DOC, embed_fn=_stub_embed)[0][1]["id"] == "art-31"  # semântico


def _fake_decompose(section_text):
    # simula o extractor: gera 1 claim-fonte com excerpt verbatim do doc
    return [{
        "id": "art31-recolhe-liquidacao",
        "content": "o texto manda recolher o IBS e a CBS na liquidação financeira",
        "provenance": {"document": "LC 214", "excerpt": "recolher o IBS e a CBS no momento da liquidação financeira"},
    }]


def _entry():
    return {"claims": [], "scores": {}, "doc_text": DOC, "decomposed": []}


def test_lazy_decompose_resolve_not_found():
    hook = make_lazy_decompose(_fake_decompose)  # lexical, sem embed
    entry = _entry()
    item = {"text": "recolhe o IBS e a CBS na liquidação financeira?", "domain": "lei", "critical": True}
    r = hook(item, entry)
    assert r is not None and r["result"] == "confirms"
    assert "art-31" in entry["decomposed"]          # ledger marcou
    assert entry["claims"]                            # grafo cresceu


def test_lazy_ledger_nao_re_decompoe():
    chamadas = []
    def counting(sec): chamadas.append(sec); return _fake_decompose(sec)
    hook = make_lazy_decompose(counting)
    entry = _entry()
    item = {"text": "recolhe o IBS e a CBS na liquidação financeira?", "domain": "lei", "critical": True}
    hook(item, entry)
    hook(item, entry)  # 2ª vez: art-31 já no ledger
    assert len(chamadas) == 1  # decompôs só uma vez


def test_lazy_nav_fraca_nao_decompoe():
    chamadas = []
    def counting(sec): chamadas.append(sec); return _fake_decompose(sec)
    hook = make_lazy_decompose(counting, nav_floor=0.16)
    item = {"text": "qual a paleta de cores da interface?", "domain": "lei", "critical": False}
    assert hook(item, _entry()) is None and chamadas == []  # não gastou a chamada


def test_integracao_resolve_com_hook():
    hook = make_lazy_decompose(_fake_decompose)
    domains = {"lei": _entry()}
    item = {"text": "recolhe o IBS e a CBS na liquidação financeira?", "domain": "lei", "critical": True}
    r = resolve_verification_item(item, domains, on_not_found=hook)
    assert r["outcome"] == "found-strong" and r["system_decided"] is False
