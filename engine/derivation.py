"""Assinatura de derivação Γ_pai ⊢ filho. MECANISMO (as regras nascem vazias, entram por
projeto — não inventar regra canônica). Cada transição de nível PODE declarar uma regra:
um predicado sobre o par (pai, filho). O checker a aplica. Sem regra declarada = ok
vacuamente, nunca um falso bloqueio — o motor não inventa a restrição que o projeto não deu."""


def check_derivation(parent, child, rule=None):
    """rule: callable (parent, child) -> bool, ou None. None = ok vacuamente.
    Retorna {ok, rule_declared}."""
    if rule is None:
        return {"ok": True, "rule_declared": False}
    return {"ok": bool(rule(parent, child)), "rule_declared": True}


def check_level(parents_by_id, children, rules, parent_level, child_level):
    """Aplica a regra da transição (parent_level -> child_level), se declarada em
    `rules` ({(pl, cl): callable}, vazio por padrão), a cada filho contra seu pai
    (via child['parent']). Filho cujo pai não existe em parents_by_id é ignorado.
    Retorna a lista de ids que VIOLAM a regra."""
    rule = rules.get((parent_level, child_level))
    if rule is None:
        return []
    violados = []
    for child in children:
        parent = parents_by_id.get(child.get("parent"))
        if parent is None:
            continue
        if not check_derivation(parent, child, rule)["ok"]:
            violados.append(child["id"])
    return violados
