import csv, pathlib

LENTES = pathlib.Path(__file__).parent.parent / "engine" / "lentes.csv"

def test_lentes_parseia_e_shape():
    rows = list(csv.DictReader(open(LENTES, encoding="utf-8")))
    assert len(rows) >= 6
    cols = {"categoria", "nome", "descricao", "quando_usar"}
    for r in rows:
        assert set(r) == cols
        assert all(v and v.strip() for v in r.values())

def test_lentes_nomes_unicos_e_esperados():
    rows = list(csv.DictReader(open(LENTES, encoding="utf-8")))
    nomes = [r["nome"] for r in rows]
    assert len(nomes) == len(set(nomes))
    assert {"pre-mortem", "red-team", "first-principles"} <= set(nomes)
