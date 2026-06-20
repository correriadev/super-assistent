"""Gate parametrizável de descida + marca provisional (descent.py). Sem LLM."""

from descent import (
    is_resolved, open_claims, descent_gate, mark_provisional, refresh_provisional,
)

CLAIMS = [
    {"id": "a", "binding": "vinculante"},
    {"id": "b", "binding": "ilustrativo"},
    {"id": "c", "binding": "default-sobrescrevivel"},
]


def _v(id_, status, **kw):
    return {"id": id_, "status": status, **kw}


def test_is_resolved_passa_e_aceite():
    assert is_resolved(_v("a", "PASSA")) is True
    assert is_resolved(_v("a", "PENDENTE-VERIFICAÇÃO")) is False
    assert is_resolved(_v("a", "PENDENTE-VERIFICAÇÃO", accepted=True)) is True
    assert is_resolved(_v("a", "PENDENTE-VERIFICAÇÃO"), accepted=("a",)) is True


def test_contradiz_nunca_resolvido_nem_por_aceite():
    assert is_resolved(_v("a", "CONTRADIZ-NIVEL-ACIMA", accepted=True)) is False
    assert is_resolved(_v("a", "CONTRADIZ-NIVEL-ACIMA"), accepted=("a",)) is False


def test_strict_bloqueia_com_aberto_e_libera_com_tudo_resolvido():
    verds = [_v("a", "PENDENTE-VERIFICAÇÃO"), _v("b", "PASSA"), _v("c", "PASSA")]
    assert descent_gate(CLAIMS, verds, "strict")["allowed"] is False
    verds_ok = [_v("a", "PASSA"), _v("b", "PASSA"), _v("c", "PASSA")]
    assert descent_gate(CLAIMS, verds_ok, "strict")["allowed"] is True


def test_vinculante_only_deixa_ilustrativo_aberto_passar():
    # b (ilustrativo) e c (default) abertos, a (vinculante) PASSA -> libera
    verds = [_v("a", "PASSA"), _v("b", "PENDENTE-VERIFICAÇÃO"), _v("c", "PRECISA-JUSTIFICAR")]
    d = descent_gate(CLAIMS, verds, "vinculante_only")
    assert d["allowed"] is True and d["blocked_by"] == []
    # agora a (vinculante) aberto -> bloqueia
    verds2 = [_v("a", "PENDENTE-VERIFICAÇÃO"), _v("b", "PASSA"), _v("c", "PASSA")]
    assert descent_gate(CLAIMS, verds2, "vinculante_only")["allowed"] is False


def test_threshold_pela_fracao():
    verds = [_v("a", "PASSA"), _v("b", "PASSA"), _v("c", "PENDENTE-VERIFICAÇÃO")]  # 2/3
    assert descent_gate(CLAIMS, verds, "threshold", min_fraction=0.6)["allowed"] is True
    assert descent_gate(CLAIMS, verds, "threshold", min_fraction=0.9)["allowed"] is False


def test_provisional_sempre_desce_e_lista_pais_abertos():
    verds = [_v("a", "PENDENTE-VERIFICAÇÃO"), _v("b", "PASSA"), _v("c", "INCOMPLETO")]
    d = descent_gate(CLAIMS, verds, "provisional")
    assert d["allowed"] is True and set(d["provisional_parents"]) == {"a", "c"}


def test_force_desce_sem_marca():
    verds = [_v("a", "PENDENTE-VERIFICAÇÃO"), _v("b", "PASSA"), _v("c", "PASSA")]
    d = descent_gate(CLAIMS, verds, "force")
    assert d["allowed"] is True and d["provisional_parents"] == []


def test_contradiz_fura_ate_force_e_provisional():
    verds = [_v("a", "CONTRADIZ-NIVEL-ACIMA"), _v("b", "PASSA"), _v("c", "PASSA")]
    for pol in ("provisional", "force", "threshold", "vinculante_only", "strict"):
        d = descent_gate(CLAIMS, verds, pol)
        assert d["allowed"] is False and d["blocked_by"] == ["a"]


def test_mark_provisional_carimba_e_limpa():
    child = {"id": "x", "derives_from": ["a", "b"]}
    assert mark_provisional(child, ["a"]) is True
    assert child["provisional"]["parents"] == ["a"] and child["provisional"]["state"] == "review"
    # pai 'a' resolveu -> some da lista -> marca limpa, filho vira normal
    assert mark_provisional(child, []) is False and "provisional" not in child


def test_refresh_provisional_segue_o_estado_atual_dos_pais():
    children = [
        {"id": "x", "derives_from": ["a"]},
        {"id": "y", "derives_from": ["b"]},
    ]
    assert set(refresh_provisional(children, ["a", "b"])) == {"x", "y"}
    # 'a' resolveu, 'b' segue aberto
    assert refresh_provisional(children, ["b"]) == ["y"]
    assert "provisional" not in children[0]


def test_refresh_provisional_transitivo_pega_filho_de_irmao_provisional():
    children = [
        {"id": "x", "derives_from": ["a"]},       # a = pai aberto -> provisional
        {"id": "z", "derives_from": ["x"]},       # deriva de x (irmão provisional) -> transitivo
        {"id": "w", "derives_from": ["nome"]},    # nome = pai resolvido (não aberto) -> limpo
    ]
    prov = set(refresh_provisional(children, ["a"]))  # só 'a' aberto; 'nome' resolvido
    assert prov == {"x", "z"}            # z pega a cicatriz via x
    assert "provisional" not in children[2]          # w limpo (pai resolvido)
    # a cadeia aponta a causa direta
    assert children[1]["provisional"]["parents"] == ["x"]
