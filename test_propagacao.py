"""Suíte pytest da propagação cross-constelação + log de eventos. Sem LLM."""

from peso import compute_pesos
from propagacao import (
    propagar,
    abrir_cicatriz,
    registrar_evento,
    ler_eventos,
    eventos_entre,
)


def _dep():
    """Claim-ideia que ancorou sua dúvida num claim-lei (fonte.ref)."""
    return {
        "id": "comparacao-credito",
        "content": "o simulador trata o crédito condicionado conforme o art. 47",
        "justificativa": "decisão de produto",
        "binding": "vinculante",
        "fonte": {"tipo": "lei", "ref": "art-47-condicao-extincao-tributo"},
    }


def test_reflutuacao_abre_cicatriz_e_derruba_peso(tmp_path):
    log = tmp_path / "eventos.jsonl"
    claims = [_dep()]
    vereditos = [{"id": "comparacao-credito"}]  # sem dúvida -> peso 10

    assert compute_pesos(claims, vereditos)["comparacao-credito"] == 10

    afetados, vers = propagar(
        "art-47-condicao-extincao-tributo", claims, vereditos, str(log)
    )

    assert afetados == ["comparacao-credito"]
    assert claims[0]["cicatriz"]["estado"] == "reveja"
    assert compute_pesos(claims, vers)["comparacao-credito"] == 9  # reabriu 1 dúvida
    assert len(ler_eventos(str(log))) == 1


def test_propagacao_nunca_reescreve_resposta(tmp_path):
    log = tmp_path / "eventos.jsonl"
    claims = [_dep()]
    antes = dict(claims[0])
    propagar("art-47-condicao-extincao-tributo", claims, [{"id": "comparacao-credito"}], str(log))
    # content/justificativa/binding intactos; só ganhou cicatriz (marca, não resposta)
    assert claims[0]["content"] == antes["content"]
    assert claims[0]["justificativa"] == antes["justificativa"]
    assert claims[0]["binding"] == antes["binding"]


def test_claim_sem_fonte_apontando_nao_e_afetado(tmp_path):
    log = tmp_path / "eventos.jsonl"
    outro = {"id": "nome", "content": "Split", "fonte": "decisão humana"}
    afetados, _ = propagar("art-47-condicao-extincao-tributo", [outro], [{"id": "nome"}], str(log))
    assert afetados == []
    assert "cicatriz" not in outro
    assert ler_eventos(str(log)) == []  # nada logado


def test_log_append_only_e_diff_por_eventos(tmp_path):
    log = tmp_path / "eventos.jsonl"
    registrar_evento(str(log), "marco", "M0", None, ts="2026-01-01T00:00:00")
    registrar_evento(str(log), "reflutuacao-propagada", "c1", "lei-x", ts="2026-02-01T00:00:00")
    registrar_evento(str(log), "reflutuacao-propagada", "c2", "lei-y", ts="2026-03-01T00:00:00")

    todos = ler_eventos(str(log))
    assert len(todos) == 3  # append-only: nada sobrescrito

    # "diff" entre dois marcos = eventos no intervalo
    diff = eventos_entre(str(log), desde="2026-01-15T00:00:00", ate="2026-02-15T00:00:00")
    assert [e["claim"] for e in diff] == ["c1"]
