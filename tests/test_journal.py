from engine.journal import log_decision, read_decisions, append_addendum, read_context

def test_log_decision_anexa_linha(tmp_path):
    p = tmp_path / "decision-log.md"
    log_decision(str(p), nivel="ideacao", decisao="claim 3 vinculante", porque="é a lei do projeto", data="2026-06-23")
    log_decision(str(p), nivel="ideacao", decisao="desce p/ concepção (provisional)", porque="sentir movimento", data="2026-06-23")
    linhas = read_decisions(str(p))
    assert len(linhas) == 2
    assert "claim 3 vinculante" in linhas[0]
    assert linhas[0].startswith("- [2026-06-23]")

def test_log_decision_append_only_nao_reescreve(tmp_path):
    p = tmp_path / "decision-log.md"
    log_decision(str(p), nivel="x", decisao="A", porque="r1", data="2026-06-23")
    antes = p.read_text(encoding="utf-8")
    log_decision(str(p), nivel="x", decisao="reverte A", porque="novo fato", data="2026-06-23")
    assert p.read_text(encoding="utf-8").startswith(antes)

def test_porque_ausente_fica_visivel_nao_inventado(tmp_path):
    p = tmp_path / "decision-log.md"
    log_decision(str(p), nivel="x", decisao="A", porque=None, data="2026-06-23")
    assert "— (sem porquê registrado)" in read_decisions(str(p))[0]

def test_addendum_append(tmp_path):
    p = tmp_path / "addendum.md"
    append_addendum(str(p), texto="pensei em cobrar por uso, mas não", data="2026-06-23")
    assert "cobrar por uso" in p.read_text(encoding="utf-8")

def test_read_context_ausente_retorna_vazio(tmp_path):
    assert read_context(str(tmp_path / "contexto.md")) == ""

def test_read_context_le_fatos(tmp_path):
    p = tmp_path / "contexto.md"
    p.write_text("projeto jurídico: fato sem excerpt = crítico\n", encoding="utf-8")
    assert "jurídico" in read_context(str(p))
