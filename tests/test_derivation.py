from engine.derivation import check_derivation, check_level

def test_sem_regra_ok_vacuamente():
    r = check_derivation({"id": "p"}, {"id": "c"}, rule=None)
    assert r["ok"] is True
    assert r["rule_declared"] is False

def test_regra_satisfeita():
    rule = lambda parent, child: parent["nivel"] != child["nivel"]
    r = check_derivation({"id": "p", "nivel": "ideacao"}, {"id": "c", "nivel": "concepcao"}, rule)
    assert r["ok"] is True and r["rule_declared"] is True

def test_regra_violada():
    rule = lambda parent, child: "automacao" not in child.get("content", "")
    r = check_derivation({"id": "p"}, {"id": "c", "content": "tela de automacao"}, rule)
    assert r["ok"] is False and r["rule_declared"] is True

def test_check_level_sem_regra_declarada_nao_viola_nada():
    parents = {"p": {"id": "p"}}
    children = [{"id": "c", "parent": "p", "content": "qualquer"}]
    assert check_level(parents, children, {}, "ideacao", "concepcao") == []

def test_check_level_aplica_regra_da_transicao():
    rule = lambda parent, child: "proibido" not in child.get("content", "")
    rules = {("ideacao", "concepcao"): rule}
    parents = {"p": {"id": "p"}}
    children = [
        {"id": "ok", "parent": "p", "content": "limpo"},
        {"id": "bad", "parent": "p", "content": "contem proibido"},
        {"id": "orfao", "parent": "fantasma", "content": "proibido"},  # pai ausente: ignorado
    ]
    assert check_level(parents, children, rules, "ideacao", "concepcao") == ["bad"]

def test_check_level_transicao_sem_regra_no_dict():
    rule = lambda p, c: False
    rules = {("arquitetura", "cenarios"): rule}  # transição diferente da pedida
    parents = {"p": {"id": "p"}}
    children = [{"id": "c", "parent": "p"}]
    assert check_level(parents, children, rules, "ideacao", "concepcao") == []
