"""Suíte pytest da cascade invalidation + event log (propagation.py). Sem LLM."""

import json
from score import compute_scores
from linking import resolve_link, link_claim
from propagation import propagate, log_event, read_events, events_between

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
