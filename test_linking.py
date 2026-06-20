"""Suíte pytest do cross-graph link resolution (linking.py) + persistência. Sem LLM."""

import json
from score import compute_scores
from linking import resolve_link, link_claim

DOC = open("ideias/pub_780677977.txt", encoding="utf-8").read()
SOURCE = json.load(
    open("projetos/02-simulador-caixa-split/dados/claims-source.json", encoding="utf-8")
)
SCORES = compute_scores(SOURCE, [], doc_text=DOC)


def test_confirms_com_fonte_grounded():
    q = "O art. 47 condiciona o direito ao crédito do adquirente à extinção do tributo?"
    r = resolve_link(q, SOURCE, SCORES)
    assert r["result"] == "confirms"
    assert r["source_claim"] == "art-47-condicao-extincao-tributo"
    assert r["confidence"] == 10 and r["reliable"] is True and r["excerpt"]


def test_refutes_quando_negacao_desalinha():
    claims = [{"id": "src-credito-independe", "content": "o texto diz que o crédito não depende da conduta do fornecedor",
               "provenance": {"document": "X", "excerpt": "o crédito não depende da conduta do fornecedor"}}]
    r = resolve_link("o crédito depende da conduta do fornecedor?", claims, {"src-credito-independe": 10})
    assert r["result"] == "refutes"


def test_not_found_quando_source_nao_enderaca():
    r = resolve_link("Qual a paleta de cores da interface?", SOURCE, SCORES)
    assert r["result"] == "not-found" and r["source_claim"] is None and r["reliable"] is False


def test_fonte_leve_responde_nao_confie():
    claims = [{"id": "leve", "content": "o art. 47 condiciona o crédito do adquirente à extinção do tributo",
               "provenance": {"document": "X", "excerpt": "inexistente-no-doc"}}]
    r = resolve_link("o art. 47 condiciona o crédito do adquirente à extinção do tributo?", claims, {"leve": 0})
    assert r["source_claim"] == "leve" and r["reliable"] is False and "não confie ainda" in r["note"]


def test_link_claim_persiste_e_idempotente():
    claim = {"id": "comparacao", "provenance": "human decision"}
    q = "O art. 47 condiciona o direito ao crédito do adquirente à extinção do tributo?"
    r = resolve_link(q, SOURCE, SCORES)
    link_claim(claim, q, r)
    link_claim(claim, q, r)
    assert len(claim["links"]) == 1
    assert claim["links"][0]["ref"] == "art-47-condicao-extincao-tributo"
    assert claim["provenance"] == "human decision"  # origem intocada


def test_not_found_nao_cria_link():
    claim = {"id": "x", "provenance": "human decision"}
    r = resolve_link("qual a cor da interface?", SOURCE, SCORES)
    assert link_claim(claim, "qual a cor?", r) is None and "links" not in claim
