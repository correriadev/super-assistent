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


# embed_fn: matching semântico evita o viés do claim genérico curto-e-denso.
# Stub 2-dim por conceito (mechanism, discipline) — sem modelo real.
_MECH = {"segregada", "segregado", "instante", "paga", "pagamento", "momento"}
_DISC = {"disciplinado", "arts", "31", "35", "previsto"}


def _stub_embed(text):
    t = text.lower()
    return [sum(w in t for w in _MECH), sum(w in t for w in _DISC)]


def test_embed_fn_casa_claim_especifico_nao_o_generico():
    claims = [
        {"id": "generico", "content": "o split payment é disciplinado pelos arts 31 a 35",
         "provenance": {"document": "X", "excerpt": "disciplinado pelos arts 31 a 35"}},
        {"id": "mecanismo", "content": "no instante em que o adquirente paga, a parcela do tributo é segregada",
         "provenance": {"document": "X", "excerpt": "a parcela do tributo é segregada"}},
    ]
    scores = {"generico": 10, "mecanismo": 10}
    q = "o tributo é segregado no instante do pagamento?"
    # semântico casa o claim do mecanismo (conceito certo)
    assert resolve_link(q, claims, scores, embed_fn=_stub_embed)["source_claim"] == "mecanismo"


# margin gate: dois claims-fonte quase empatados não são auto-escolhidos.
def _flat_embed(text):
    # embed constante -> cosseno 1.0 para todo claim => empate perfeito
    return [1.0, 1.0]


def test_margin_gate_marca_ambiguo_no_empate():
    claims = [
        {"id": "a", "content": "split na liquidação", "provenance": {"document": "X", "excerpt": "split na liquidação"}},
        {"id": "b", "content": "split proporcional por parcela", "provenance": {"document": "X", "excerpt": "split proporcional por parcela"}},
    ]
    r = resolve_link("split?", claims, {"a": 10, "b": 10}, embed_fn=_flat_embed)
    assert r["result"] == "ambiguous" and r["source_claim"] is None
    assert {c["source_claim"] for c in r["candidates"]} == {"a", "b"}


def test_link_claim_nao_persiste_ambiguo():
    claim = {"id": "idea", "provenance": "human decision"}
    r = {"result": "ambiguous", "candidates": [], "source_claim": None}
    assert link_claim(claim, "q?", r) is None and "links" not in claim


def test_margin_largo_nao_dispara_no_match_claro():
    # top-1 muito acima do top-2 -> escolhe normal, sem ambiguidade
    claims = [
        {"id": "certo", "content": "o tributo é segregado no instante do pagamento",
         "provenance": {"document": "X", "excerpt": "segregado no instante do pagamento"}},
        {"id": "longe", "content": "disciplinado pelos arts 31 a 35",
         "provenance": {"document": "X", "excerpt": "arts 31 a 35"}},
    ]
    r = resolve_link("o tributo é segregado no instante do pagamento?", claims,
                     {"certo": 10, "longe": 10}, embed_fn=_stub_embed)
    assert r["result"] in ("confirms", "refutes") and r["source_claim"] == "certo"
