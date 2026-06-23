"""E2E: cicatriz composição + cadeia determinística. Sem LLM."""

from engine.descent import is_resolved, refresh_provisional


def test_cicatriz_e2e_reabrir_pai_recicatriza_filhos():
    # pai resolvido -> filho desce limpo (sem marca provisional)
    def _v(id_, status, **kw):
        return {"id": id_, "status": status, **kw}

    filhos = [{"id": "f", "parent": "pai"}]

    # pai com status PASSA é resolvido -> lista de pais abertos vazia
    abertos_antes = [pid for pid in ["pai"] if not is_resolved(_v(pid, "PASSA"))]
    assert refresh_provisional(filhos, abertos_antes) == []
    assert "provisional" not in filhos[0]

    # reabre o pai (PRECISA-JUSTIFICAR não é resolvido)
    abertos_depois = [pid for pid in ["pai"] if not is_resolved(_v(pid, "PRECISA-JUSTIFICAR"))]
    assert refresh_provisional(filhos, abertos_depois) == ["f"]
    assert filhos[0]["provisional"]["state"] == "review"


def test_chain_deterministica_nao_quebra():
    from engine.contract import validate_claims, validate_verdicts

    claims = [{"id": "a", "content": "c", "binding": "vinculante",
               "provenance": "human decision", "parent": None, "links": []}]
    verds = [{"id": "a", "status": "PASSA", "structural_gaps": [], "verification_items": [],
              "elicitation_question": None, "contradiction": None}]
    validate_claims(claims)
    validate_verdicts(verds)
