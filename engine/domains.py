"""domains.py — registry de domínios e helpers de encapsulamento (D4).

Agrupa nós por domínio, indexa por id, e declara a regra de exposição:
um nó só é parte da interface pública de seu domínio quando `exposed: true`.
"""


def registry(nodes):
    """Agrupa nodes por domínio. Retorna {domain: [nodes]}."""
    result = {}
    for n in nodes:
        d = n.get("domain")
        result.setdefault(d, []).append(n)
    return result


def node_index(nodes):
    """Índice id -> node para lookup O(1)."""
    return {n["id"]: n for n in nodes}


def is_exposed(node):
    """True se e somente se node['exposed'] é exatamente o booleano True."""
    return node.get("exposed") is True
