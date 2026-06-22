"""Suíte pytest da cascade invalidation + event log (propagation.py). Sem LLM."""

import json
from engine.score import compute_scores
from engine.linking import resolve_link, link_claim
from engine.propagation import propagate, log_event, read_events, events_between, referenced_by

DOC = open("ideias/pub_780677977.txt", encoding="utf-8").read()
SOURCE = json.load(
    open("projetos/02-simulador-caixa-split/dados/claims-source.json", encoding="utf-8")
)
SCORES = compute_scores(SOURCE, [], doc_text=DOC)


def _dep():
    return {"id": "comparacao-credito", "content": "trata crédito condicionado",
            "rationale": "produto", "binding": "vinculante", "provenance": "human decision"}


def _linked_dep():
    c = _dep()
    q = "O art. 47 condiciona o direito ao crédito do adquirente à extinção do tributo?"
    link_claim(c, q, resolve_link(q, SOURCE, SCORES))
    return c


def test_invalidacao_marca_stale_e_derruba_score(tmp_path):
    log = tmp_path / "events.jsonl"
    claim = _linked_dep()
    claims, verdicts = [claim], [{"id": "comparacao-credito"}]
    assert compute_scores(claims, verdicts)["comparacao-credito"] == 10

    afetados, v2 = propagate("art-47-condicao-extincao-tributo", claims, verdicts, str(log))
    assert afetados == ["comparacao-credito"]
    assert claim["stale"]["state"] == "review"
    assert claim["links"][0]["state"] == "review"
    assert compute_scores(claims, v2)["comparacao-credito"] == 9
    assert len(read_events(str(log))) == 1


def test_propagacao_nunca_reescreve_resposta(tmp_path):
    log = tmp_path / "events.jsonl"
    claim = _linked_dep()
    antes = {k: claim[k] for k in ("content", "rationale", "binding")}
    propagate("art-47-condicao-extincao-tributo", [claim], [{"id": "comparacao-credito"}], str(log))
    assert {k: claim[k] for k in ("content", "rationale", "binding")} == antes


def test_claim_sem_link_nao_e_afetado(tmp_path):
    log = tmp_path / "events.jsonl"
    outro = {"id": "nome", "content": "Split", "provenance": "human decision"}
    afetados, _ = propagate("art-47-condicao-extincao-tributo", [outro], [{"id": "nome"}], str(log))
    assert afetados == [] and "stale" not in outro and read_events(str(log)) == []


def test_log_append_only_e_diff_por_eventos(tmp_path):
    log = tmp_path / "events.jsonl"
    log_event(str(log), "mark", "M0", None, ts="2026-01-01T00:00:00")
    log_event(str(log), "cascade-invalidation", "c1", "src-x", ts="2026-02-01T00:00:00")
    log_event(str(log), "cascade-invalidation", "c2", "src-y", ts="2026-03-01T00:00:00")
    assert len(read_events(str(log))) == 3
    diff = events_between(str(log), since="2026-01-15T00:00:00", until="2026-02-15T00:00:00")
    assert [e["claim"] for e in diff] == ["c1"]


def test_referenced_by_constroi_indice_reverso():
    """referenced_by mapeia cada ref_id para a lista de ids que apontam para ele."""
    nos = [
        {"id": "filho-a", "parent": "raiz", "links": [{"ref": "externo-x"}]},
        {"id": "filho-b", "parent": "raiz", "links": []},
        {"id": "filho-c", "parent": None, "links": [{"ref": "externo-x"}, {"ref": "externo-y"}]},
        {"id": "legado", "provenance": {"ref": "externo-y"}},
    ]
    idx = referenced_by(nos)
    assert sorted(idx["raiz"]) == ["filho-a", "filho-b"]
    assert sorted(idx["externo-x"]) == ["filho-a", "filho-c"]
    assert sorted(idx["externo-y"]) == ["filho-c", "legado"]


def test_propagate_cross_domain_cicatriz_cruza_fronteira(tmp_path):
    """Cicatriz cruza domínio: invalidar aws-gateway marca stale o nó do simulador
    que o linka — mesmo sendo de domínios distintos. O índice reverso resolve.
    A propagação NUNCA reescreve content/rationale/binding (invariante dura)."""
    log = tmp_path / "events.jsonl"

    gateway = {
        "id": "aws-gateway",
        "domain": "aws",
        "exposed": True,
        "content": "API Gateway AWS exposto",
        "rationale": "infra",
        "binding": "vinculante",
        "links": [],
        "provenance": {"document": "aws-arch", "excerpt": "gateway principal"},
    }
    simulador = {
        "id": "simulador-precisa-gateway",
        "domain": "simulador",
        "content": "simulador depende do gateway",
        "rationale": "integracao",
        "binding": "vinculante",
        "links": [{"domain": "aws", "ref": "aws-gateway", "result": "confirms", "confidence": 8}],
        "provenance": "human decision",
    }

    todos_nos = [gateway, simulador]
    verdicts = [{"id": "aws-gateway"}, {"id": "simulador-precisa-gateway"}]

    antes = {k: simulador[k] for k in ("content", "rationale", "binding")}

    afetados, v2 = propagate("aws-gateway", todos_nos, verdicts, str(log))

    # nó do simulador foi marcado stale pelo índice reverso cruzando domínio
    assert "simulador-precisa-gateway" in afetados
    assert simulador["stale"]["state"] == "review"
    assert simulador["stale"]["source"] == "aws-gateway"

    # link dentro do simulador aponta state=review
    assert simulador["links"][0]["state"] == "review"

    # invariante dura: propagação não reescreve resposta
    assert {k: simulador[k] for k in ("content", "rationale", "binding")} == antes

    # evento logado
    evs = read_events(str(log))
    assert any(e["claim"] == "simulador-precisa-gateway" and e["cause"] == "aws-gateway" for e in evs)

    # gateway em si NÃO vira stale (não foi quem referenciou a fonte)
    assert "stale" not in gateway
