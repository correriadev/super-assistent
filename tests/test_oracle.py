from engine.oracle import oracle_of, oracle_mix, WORLDLY, STRUCTURAL, DECISION

def _v(id, status="PASSA", items=None, gaps=None):
    return {"id": id, "status": status, "structural_gaps": gaps or [],
            "verification_items": items or [], "elicitation_question": None, "contradiction": None}

def test_decision_humano_assentado():
    c = {"id": "a", "provenance": "human decision"}
    assert oracle_of(c, _v("a")) == DECISION

def test_worldly_quando_tem_verification_items():
    c = {"id": "a", "provenance": "human decision"}
    v = _v("a", status="PENDENTE-VERIFICAÇÃO", items=[{"text": "q?", "domain": "lei", "critical": True}])
    assert oracle_of(c, v) == WORLDLY

def test_structural_quando_status_nao_passa():
    c = {"id": "a", "provenance": "human decision"}
    assert oracle_of(c, _v("a", status="INCOMPLETO")) == STRUCTURAL

def test_structural_quando_tem_structural_gaps():
    c = {"id": "a", "provenance": "human decision"}
    assert oracle_of(c, _v("a", status="PASSA", gaps=["vago"])) == STRUCTURAL

def test_source_claim_assentado_e_structural_nao_decision():
    c = {"id": "s", "provenance": {"document": "lei", "excerpt": "..."}}
    assert oracle_of(c, _v("s")) == STRUCTURAL

def test_worldly_vence_structural():
    c = {"id": "a", "provenance": "human decision"}
    v = _v("a", status="INCOMPLETO", items=[{"text": "q?", "domain": "lei", "critical": True}])
    assert oracle_of(c, v) == WORLDLY

def test_oracle_mix_conta_por_id():
    claims = [{"id": "a", "provenance": "human decision"},
              {"id": "b", "provenance": "human decision"}]
    verds = [_v("a"), _v("b", status="INCOMPLETO")]
    assert oracle_mix(claims, verds) == {WORLDLY: 0, STRUCTURAL: 1, DECISION: 1}
