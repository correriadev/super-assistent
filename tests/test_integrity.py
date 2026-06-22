"""Portão de integridade (engine.integrity) — torna o nó-artefato órfão impossível. Sem LLM."""

# `tests_green` aliasado: nome com prefixo `test*` é coletado por engano pelo pytest.
from engine.integrity import is_artifact, symbol_present, verify_integrity
from engine.integrity import tests_green as green_check


def _node(id_, **kw):
    return {"id": id_, **kw}


def test_is_artifact():
    assert is_artifact({"provenance": {"file": "a.js", "symbol": "f"}}) is True
    assert is_artifact({"provenance": "human decision"}) is False
    assert is_artifact({}) is False


def test_symbol_present_grounding(tmp_path):
    f = tmp_path / "calc.js"
    f.write_text("export function calculateCashFlow(){}\n", encoding="utf-8")
    base = str(tmp_path)
    assert symbol_present({"provenance": {"file": "calc.js", "symbol": "calculateCashFlow"}}, base) is True
    assert symbol_present({"provenance": {"file": "calc.js", "symbol": "inexistente"}}, base) is False
    assert symbol_present({"provenance": {"file": "sumiu.js", "symbol": "x"}}, base) is False
    assert symbol_present({"provenance": {"file": "calc.js"}}, base) is True  # sem símbolo: basta existir


def test_tests_green():
    n = _node("c", grounded_by={"tests": ["t1", "t2"]})
    assert green_check(n, {"t1": True, "t2": True}) is True
    assert green_check(n, {"t1": True, "t2": False}) is False
    assert green_check(n, {"t1": True}) is False  # ausente = não-verde
    assert green_check(_node("x"), {}) is None     # não declara teste


def test_verify_pega_orfao(tmp_path):
    f = tmp_path / "a.js"; f.write_text("function f(){}", encoding="utf-8")
    nodes = [_node("art", provenance={"file": "a.js", "symbol": "f"})]  # SEM derives_from
    r = verify_integrity(nodes, str(tmp_path))
    assert r["ok"] is False and r["orphans"] == ["art"]


def test_verify_pega_pai_inexistente(tmp_path):
    f = tmp_path / "a.js"; f.write_text("function f(){}", encoding="utf-8")
    nodes = [_node("art", parent="fantasma", provenance={"file": "a.js", "symbol": "f"})]
    r = verify_integrity(nodes, str(tmp_path))
    assert r["ok"] is False and ("art", "fantasma") in r["missing_parent_ref"]


def test_verify_pega_simbolo_ausente(tmp_path):
    f = tmp_path / "a.js"; f.write_text("function outra(){}", encoding="utf-8")
    nodes = [_node("pai"), _node("art", parent="pai", provenance={"file": "a.js", "symbol": "calcular"})]
    r = verify_integrity(nodes, str(tmp_path))
    assert r["ok"] is False and r["ungrounded_symbol"] == ["art"]


def test_verify_pega_teste_vermelho(tmp_path):
    f = tmp_path / "a.js"; f.write_text("function f(){}", encoding="utf-8")
    # app_dir=None -> sem evidência de verde -> nó que declara teste cai como vermelho
    nodes = [_node("pai"), _node("art", parent="pai",
                                  provenance={"file": "a.js", "symbol": "f"},
                                  grounded_by={"tests": ["algum teste"]})]
    r = verify_integrity(nodes, str(tmp_path), app_dir=None)
    assert r["ok"] is False and r["red"] == ["art"]


def test_verify_ok_quando_ligado_e_ancorado(tmp_path):
    f = tmp_path / "a.js"; f.write_text("function f(){}", encoding="utf-8")
    nodes = [_node("pai"), _node("art", parent="pai", provenance={"file": "a.js", "symbol": "f"})]
    r = verify_integrity(nodes, str(tmp_path))
    assert r["ok"] is True


def test_verify_pega_id_duplicado(tmp_path):
    nodes = [_node("x", parent=None), _node("x", parent=None)]  # mesmo id 2x
    r = verify_integrity(nodes, str(tmp_path))
    assert r["ok"] is False and r["dup_ids"] == ["x"]


def test_alias_torna_rename_seguro(tmp_path):
    f = tmp_path / "a.js"; f.write_text("function f(){}", encoding="utf-8")
    # 'art' aponta o parent pelo id ANTIGO 'velho'; 'novo' absorveu 'velho' via aliases
    art = _node("art", parent="velho", provenance={"file": "a.js", "symbol": "f"})
    novo = _node("novo", aliases=["velho"])
    assert verify_integrity([novo, art], str(tmp_path))["ok"] is True  # alias resolve
    # sem o alias, a mesma ref quebra
    r = verify_integrity([_node("outro"), art], str(tmp_path))
    assert r["ok"] is False and ("art", "velho") in r["missing_parent_ref"]
