import pytest
from engine.contract import (
    SIX_STATUS, validate_claim, validate_verdict, validate_claims, validate_verdicts,
    ContractError,
)

def test_six_status_fechado():
    assert SIX_STATUS == {
        "CONTRADIZ-NIVEL-ACIMA", "PRECISA-JUSTIFICAR", "INCOMPLETO",
        "PENDENTE-VERIFICAÇÃO", "CONTESTADO", "PASSA",
    }

def test_verdict_status_invalido_falha():
    with pytest.raises(ContractError, match="status"):
        validate_verdict({"id": "x", "status": "INVENTADO", "structural_gaps": [],
                          "verification_items": [], "elicitation_question": None,
                          "contradiction": None})

def test_verdict_valido_passa():
    v = {"id": "x", "status": "PASSA", "structural_gaps": [],
         "verification_items": [], "elicitation_question": None, "contradiction": None}
    assert validate_verdict(v) == v

def test_verification_item_domain_invalido_falha():
    v = {"id": "x", "status": "PENDENTE-VERIFICAÇÃO", "structural_gaps": [],
         "verification_items": [{"text": "q?", "domain": "astrologia", "critical": True}],
         "elicitation_question": None, "contradiction": None}
    with pytest.raises(ContractError, match="domain"):
        validate_verdict(v)

def test_elicitation_obrigatoria_quando_precisa_justificar():
    v = {"id": "x", "status": "PRECISA-JUSTIFICAR", "structural_gaps": [],
         "verification_items": [], "elicitation_question": None, "contradiction": None}
    with pytest.raises(ContractError, match="elicitation"):
        validate_verdict(v)

def test_claim_binding_invalido_falha():
    with pytest.raises(ContractError, match="binding"):
        validate_claim({"id": "x", "content": "c", "binding": "talvez",
                        "provenance": "human decision", "parent": None, "links": []})

def test_claim_id_ausente_falha():
    with pytest.raises(ContractError, match="id"):
        validate_claim({"content": "c", "binding": "vinculante",
                        "provenance": "human decision", "parent": None, "links": []})

def test_validate_lista_acumula_erros():
    bad = [{"id": "a", "status": "PASSA", "structural_gaps": [], "verification_items": [],
            "elicitation_question": None, "contradiction": None},
           {"id": "b", "status": "NOPE", "structural_gaps": [], "verification_items": [],
            "elicitation_question": None, "contradiction": None}]
    with pytest.raises(ContractError, match="b"):
        validate_verdicts(bad)

def test_verification_item_candidates_valido():
    v = {"id": "x", "status": "PENDENTE-VERIFICAÇÃO", "structural_gaps": [],
         "verification_items": [{"text": "q?", "domain": "lei", "critical": True,
             "candidates": [{"source_claim": "s1", "excerpt": "...", "confidence": 10}]}],
         "elicitation_question": None, "contradiction": None}
    assert validate_verdict(v) == v

def test_candidate_confidence_nao_numerica_falha():
    v = {"id": "x", "status": "PENDENTE-VERIFICAÇÃO", "structural_gaps": [],
         "verification_items": [{"text": "q?", "domain": "lei", "critical": True,
             "candidates": [{"source_claim": "s1", "excerpt": "...", "confidence": "alta"}]}],
         "elicitation_question": None, "contradiction": None}
    with pytest.raises(ContractError, match="confidence"):
        validate_verdict(v)
