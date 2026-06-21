"""Forma A: verification_item com endereço de domínio. Sem LLM."""

from engine.score import compute_scores, item_text
from engine.linking import resolve_link, domain_of


def test_score_conta_item_objeto():
    claims = [{"id": "c"}]
    verdicts = [{"id": "c", "verification_items": [
        {"text": "a lei exige X?", "domain": "lei", "critical": True},
        {"text": "viável em tempo real?", "domain": "engenharia", "critical": False},
    ]}]
    assert compute_scores(claims, verdicts)["c"] == 8  # 10 - 2 issues objeto


def test_item_objeto_non_blocking_nao_conta():
    claims = [{"id": "c"}]
    verdicts = [{"id": "c", "verification_items": [
        {"text": "real issue", "domain": None, "critical": False},
        {"text": "(non-blocking) cosmético", "domain": None, "critical": False},
    ]}]
    assert compute_scores(claims, verdicts)["c"] == 9  # só 1 conta


def test_compat_string_legada_ainda_conta():
    claims = [{"id": "c"}]
    verdicts = [{"id": "c", "verification_items": ["[CRÍTICO] fato antigo", "(non-blocking) ruído"]}]
    assert compute_scores(claims, verdicts)["c"] == 9  # string legada: 1 real, nonblock ignorado


def test_domain_of_extrai():
    assert domain_of({"text": "x", "domain": "lei", "critical": True}) == "lei"
    assert domain_of({"text": "x", "domain": None}) is None
    assert domain_of("string legada") is None  # legado não tem domínio


def test_item_text_normaliza():
    assert item_text({"text": "abc", "domain": "lei"}) == "abc"
    assert item_text("abc") == "abc"


def test_resolve_link_aceita_item_objeto():
    source = [{"id": "art47", "content": "o art. 47 condiciona o crédito do adquirente à extinção do tributo",
               "provenance": {"document": "LC 214", "excerpt": "o crédito do adquirente à extinção do tributo"}}]
    scores = {"art47": 10}
    item = {"text": "o art. 47 condiciona o crédito do adquirente à extinção do tributo?", "domain": "lei", "critical": True}
    r = resolve_link(item, source, scores)
    assert r["result"] == "confirms" and r["source_claim"] == "art47"
