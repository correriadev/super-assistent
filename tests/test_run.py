import json
from engine.run import run_project

def _mk(tmp_path):
    d = tmp_path / "dados"; d.mkdir()
    (d / "claims.json").write_text(json.dumps([
        {"id": "a", "content": "c", "binding": "vinculante",
         "provenance": "human decision", "parent": None, "links": []}
    ]), encoding="utf-8")
    (d / "verdicts.json").write_text(json.dumps([
        {"id": "a", "status": "PASSA", "structural_gaps": [], "verification_items": [],
         "elicitation_question": None, "contradiction": None}
    ]), encoding="utf-8")
    return tmp_path

def test_run_projeto_valido_reporta_ok(tmp_path):
    proj = _mk(tmp_path)
    rep = run_project(str(proj))
    assert rep["contract_ok"] is True
    assert rep["scores"]["a"] >= 10

def test_run_projeto_com_status_invalido_falha_alto(tmp_path):
    proj = _mk(tmp_path)
    v = json.loads((proj / "dados" / "verdicts.json").read_text())
    v[0]["status"] = "INVENTADO"
    (proj / "dados" / "verdicts.json").write_text(json.dumps(v), encoding="utf-8")
    rep = run_project(str(proj))
    assert rep["contract_ok"] is False
    assert "INVENTADO" in rep["contract_error"]
