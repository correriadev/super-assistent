"""engine.domains — registry de domínios + checagem D4 (exposição cross-domínio). Sem LLM."""

import pytest
from engine.domains import registry, node_index, is_exposed
from engine.integrity import verify_integrity


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _node(id_, domain, *, parent=None, links=None, exposed=None, provenance=None):
    n = {"id": id_, "domain": domain}
    if parent is not None:
        n["parent"] = parent
    if links is not None:
        n["links"] = links
    if exposed is not None:
        n["exposed"] = exposed
    if provenance is not None:
        n["provenance"] = provenance
    return n


# ---------------------------------------------------------------------------
# Task 1 — registry, node_index, is_exposed
# ---------------------------------------------------------------------------

def test_registry_agrupa_por_dominio():
    nodes = [
        _node("a", "simulador"),
        _node("b", "simulador"),
        _node("c", "lei"),
    ]
    r = registry(nodes)
    assert set(r.keys()) == {"simulador", "lei"}
    assert {n["id"] for n in r["simulador"]} == {"a", "b"}
    assert {n["id"] for n in r["lei"]} == {"c"}


def test_registry_dominio_ausente_vira_chave_none():
    nodes = [_node("x", "simulador"), {"id": "y"}]  # sem 'domain'
    r = registry(nodes)
    assert "simulador" in r
    assert None in r


def test_node_index_mapeia_id_para_no():
    nodes = [_node("a", "d1"), _node("b", "d2")]
    idx = node_index(nodes)
    assert idx["a"]["domain"] == "d1"
    assert idx["b"]["domain"] == "d2"


def test_is_exposed_true_quando_campo_true():
    assert is_exposed({"id": "x", "exposed": True}) is True


def test_is_exposed_false_quando_ausente():
    assert is_exposed({"id": "x"}) is False


def test_is_exposed_false_quando_false():
    assert is_exposed({"id": "x", "exposed": False}) is False


def test_is_exposed_false_quando_truthy_nao_bool():
    # Só `True` booleano vale; strings ou inteiros não devem contar
    assert is_exposed({"id": "x", "exposed": 1}) is False
    assert is_exposed({"id": "x", "exposed": "true"}) is False


# ---------------------------------------------------------------------------
# Task 2 — verify_integrity com checagem D4 (unexposed_xref)
# ---------------------------------------------------------------------------

def test_cross_domain_para_alvo_nao_exposto_falha(tmp_path):
    """Link cross-domínio mirando nó sem exposed:true -> unexposed_xref, ok=False."""
    nodes = [
        _node("sim-a", "simulador", links=[{"domain": "lei", "ref": "lei-x", "kind": "grounding"}]),
        _node("lei-x", "lei"),  # NÃO exposto
    ]
    r = verify_integrity(nodes, str(tmp_path))
    assert r["ok"] is False
    assert ("sim-a", "lei-x") in r["unexposed_xref"]


def test_cross_domain_para_alvo_exposto_ok(tmp_path):
    """Link cross-domínio mirando nó com exposed:true -> ok, sem unexposed_xref."""
    nodes = [
        _node("sim-a", "simulador", links=[{"domain": "lei", "ref": "lei-x", "kind": "grounding"}]),
        _node("lei-x", "lei", exposed=True),
    ]
    r = verify_integrity(nodes, str(tmp_path))
    assert r["unexposed_xref"] == []
    # ok pode ainda ser True se não houver outras violações (sem artefatos)
    assert r["ok"] is True


def test_intra_dominio_sem_exposed_ok(tmp_path):
    """Link INTRA-domínio para alvo não-exposto -> não gateia D4, ok."""
    nodes = [
        _node("sim-a", "simulador", links=[{"domain": "simulador", "ref": "sim-b", "kind": "derivation"}]),
        _node("sim-b", "simulador"),  # mesma domain, não precisa de exposed
    ]
    r = verify_integrity(nodes, str(tmp_path))
    assert r["unexposed_xref"] == []
    assert r["ok"] is True


def test_cross_domain_via_graph_source_alvo_nao_exposto_falha(tmp_path):
    """Link com graph:source (sem domain no link) que resolve para domínio diferente -> D4."""
    nodes = [
        _node("sim-a", "simulador", links=[{"graph": "source", "ref": "lei-y", "kind": "grounding"}]),
        _node("lei-y", "lei"),  # não exposto
    ]
    r = verify_integrity(nodes, str(tmp_path))
    assert r["ok"] is False
    assert ("sim-a", "lei-y") in r["unexposed_xref"]


def test_cross_domain_via_graph_source_alvo_exposto_ok(tmp_path):
    """Link com graph:source que resolve para nó exposto -> ok."""
    nodes = [
        _node("sim-a", "simulador", links=[{"graph": "source", "ref": "lei-y", "kind": "grounding"}]),
        _node("lei-y", "lei", exposed=True),
    ]
    r = verify_integrity(nodes, str(tmp_path))
    assert r["unexposed_xref"] == []
    assert r["ok"] is True


def test_checagens_existentes_nao_quebram(tmp_path):
    """D4 não interfere com orphan/ungrounded/red/missing_parent_ref existentes."""
    f = tmp_path / "a.js"
    f.write_text("function f(){}", encoding="utf-8")
    nodes = [
        _node("art", "simulador", parent="fantasma",
              provenance={"file": "a.js", "symbol": "f"}),
    ]
    r = verify_integrity(nodes, str(tmp_path))
    assert r["ok"] is False
    assert ("art", "fantasma") in r["missing_parent_ref"]
    assert "unexposed_xref" in r  # chave sempre presente


def test_unexposed_xref_sempre_presente_no_retorno(tmp_path):
    """Chave unexposed_xref sempre existe no dict, mesmo quando tudo ok."""
    nodes = [_node("x", "simulador")]
    r = verify_integrity(nodes, str(tmp_path))
    assert "unexposed_xref" in r


def test_link_sem_ref_ignorado(tmp_path):
    """Link sem campo 'ref' não causa erro em D4."""
    nodes = [
        _node("sim-a", "simulador", links=[{"domain": "lei", "kind": "note"}]),  # sem ref
        _node("lei-x", "lei"),
    ]
    r = verify_integrity(nodes, str(tmp_path))
    assert r["unexposed_xref"] == []
    assert r["ok"] is True


def test_ref_inexistente_nao_conta_em_unexposed_xref(tmp_path):
    """Se o alvo não existe no grafo, já cai em missing_parent_ref (dangling), não em unexposed_xref."""
    nodes = [
        _node("sim-a", "simulador", links=[{"domain": "lei", "ref": "fantasma", "kind": "grounding"}]),
    ]
    r = verify_integrity(nodes, str(tmp_path))
    # Nó não existe -> missing_parent_ref, NÃO unexposed_xref
    assert ("sim-a", "fantasma") in r["missing_parent_ref"]
    assert ("sim-a", "fantasma") not in r["unexposed_xref"]
