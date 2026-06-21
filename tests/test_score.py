"""Suíte pytest do score determinístico (score.py). Sem LLM."""

from engine.score import compute_scores, SCORE_BASE, grounding_report


def test_pass_so_non_blocking_fica_positivo():
    claims = [{"id": "nome-split"}]
    verdicts = [{
        "id": "nome-split",
        "structural_gaps": [],
        "verification_items": [
            "(non-blocking) 'Split' disponível como marca no INPI?",
            "(não bloqueante) 'Split' é distintivo demais?",
        ],
    }]
    assert compute_scores(claims, verdicts)["nome-split"] == SCORE_BASE


def test_seis_issues_reais_da_quatro():
    claims = [{"id": "c"}]
    verdicts = [{"id": "c", "structural_gaps": ["l1", "l2", "l3"],
                 "verification_items": ["v1", "v2", "v3"]}]
    assert compute_scores(claims, verdicts)["c"] == 4


def test_resolver_issue_sobe_score():
    claims = [{"id": "c"}]
    antes = compute_scores(claims, [{"id": "c", "verification_items": ["v1", "v2", "v3"]}])
    depois = compute_scores(
        claims, [{"id": "c", "verification_items": ["v1", "v2"], "verified_items": ["v3"]}]
    )
    assert antes["c"] == 7 and depois["c"] == 9 and depois["c"] > antes["c"]


def test_filho_herda_pai_e_propaga_queda():
    claims = [{"id": "P"}, {"id": "C", "derives_from": ["P"]}]
    base = compute_scores(claims, [{"id": "P"}, {"id": "C"}])
    assert base["P"] == 10 and base["C"] == 20
    com = compute_scores(claims, [{"id": "P", "verification_items": ["fato"]}, {"id": "C"}])
    assert com["P"] == 9 and com["C"] == 19


def test_guarda_de_ciclo():
    import pytest
    with pytest.raises(ValueError):
        compute_scores(
            [{"id": "A", "derives_from": ["B"]}, {"id": "B", "derives_from": ["A"]}],
            [{"id": "A"}, {"id": "B"}],
        )


# ── source graph / grounding ──
DOC = (
    "Art. 31. Os prestadores de serviços de pagamento devem segregar e recolher "
    "o IBS e a CBS no momento da liquidação financeira da operação. "
    "Art. 47. O direito ao crédito do adquirente somente pode ser exercido quando "
    "ocorrida a extinção do tributo por qualquer das modalidades do art. 27."
)


def test_source_nasce_leve_sem_grounding():
    claims = [{"id": "x", "provenance": {"document": "LC 214/2025", "excerpt": "o split é facultativo"}}]
    assert compute_scores(claims, [{"id": "x"}], doc_text=DOC)["x"] == 0


def test_source_ganha_score_por_grounding():
    claims = [{"id": "g", "provenance": {
        "document": "LC 214/2025",
        "excerpt": "segregar e recolher o IBS e a CBS no momento da liquidação financeira",
    }}]
    assert compute_scores(claims, [{"id": "g"}], doc_text=DOC)["g"] == 10
    assert grounding_report(claims, DOC)["g"] is True


def test_grounding_e_rastreabilidade_nao_verdade():
    claims = [{"id": "g", "provenance": {
        "document": "LC 214/2025",
        "excerpt": "O direito ao crédito do adquirente somente pode ser exercido quando ocorrida a extinção do tributo",
    }}]
    verdicts = [{"id": "g", "verification_items": ["O art. 47 é constitucional?"]}]
    assert grounding_report(claims, DOC)["g"] is True
    assert compute_scores(claims, verdicts, doc_text=DOC)["g"] == 9


def test_idea_provenance_human_decision_base_10():
    claims = [{"id": "p", "provenance": "human decision"}]
    assert compute_scores(claims, [{"id": "p"}])["p"] == 10
