#!/usr/bin/env python3
"""
peso.py — cálculo determinístico do PESO de cada claim.

O peso mede quão RESOLVIDO um claim está. Peso alto = resolvido (afunda na
constelação). Peso baixo = cheio de pendência (flutua, vira névoa).

NÃO é julgamento de LLM. É função pura das dúvidas (lacunas + itens a verificar)
e da herança pela cadeia de derivação `deriva_de`.

Fórmula do peso de um claim:

    peso(claim) = SOMA( peso(pai) para cada pai em deriva_de )   # herança
                + dúvidas_fechadas                               # só fechar pesa
                - dúvidas_abertas

  onde, para o próprio claim:
    dúvidas_fechadas = lacunas_resolvidas + itens_verificados
    dúvidas_abertas  = lacunas_estruturais (abertas) + itens_verificar (abertos)

Regras deliberadas:
  - Só FECHAR dúvida adiciona peso. Definir conteúdo sem que nada seja
    questionado é NEUTRO (abertas=0, fechadas=0 -> contribuição própria 0).
    Afirmar não é resolver.
  - PROPAGAÇÃO: como o peso de um filho inclui o peso do(s) pai(s), abrir uma
    dúvida num claim derruba o peso dele E o de todos os descendentes pela
    cadeia `deriva_de`. Queda que desce até as folhas = mudança estrutural;
    queda que para num claim = pontual. A propagação é automática porque o
    cálculo é topológico (resolve o pai antes do filho).

Claim raiz (sem `deriva_de`) começa a herança em 0.

Uso:
    python3 peso.py <claims.json> <vereditos.json> [pesos.json]
    python3 peso.py --self-test
"""

import json
import sys


def _count(x):
    """Aceita lista (conta itens) ou inteiro (usa direto). None/ausente -> 0."""
    if x is None:
        return 0
    if isinstance(x, int):
        return x
    return len(x)


def _open_doubts(ver):
    """Dúvidas abertas de um veredito: lacunas estruturais + itens a verificar."""
    return _count(ver.get("lacunas_estruturais")) + _count(ver.get("itens_verificar"))


def _closed_doubts(ver):
    """Dúvidas fechadas: lacunas resolvidas + itens já verificados."""
    return _count(ver.get("lacunas_resolvidas")) + _count(ver.get("itens_verificados"))


def compute_pesos(claims, vereditos):
    """
    claims: lista de {id, ..., deriva_de?: [ids]}
    vereditos: lista de {id, lacunas_estruturais?, itens_verificar?,
                         lacunas_resolvidas?, itens_verificados?}
    Retorna dict {id: peso}.
    """
    ver_by_id = {v["id"]: v for v in vereditos}
    deriva = {c["id"]: list(c.get("deriva_de") or []) for c in claims}

    # contribuição própria de cada claim (fechadas - abertas)
    own = {}
    for c in claims:
        v = ver_by_id.get(c["id"], {})
        own[c["id"]] = _closed_doubts(v) - _open_doubts(v)

    peso = {}
    visiting = set()

    def resolve(cid):
        if cid in peso:
            return peso[cid]
        if cid in visiting:
            raise ValueError(f"ciclo em deriva_de envolvendo: {cid}")
        visiting.add(cid)
        inherited = 0
        for parent in deriva.get(cid, []):
            if parent in own:  # ignora pai inexistente (nível anterior já consolidado)
                inherited += resolve(parent)
        peso[cid] = inherited + own.get(cid, 0)
        visiting.discard(cid)
        return peso[cid]

    for c in claims:
        resolve(c["id"])
    return peso


def _load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(argv):
    if len(argv) >= 1 and argv[0] == "--self-test":
        return _self_test()

    if len(argv) < 2:
        print(__doc__)
        return 2

    claims = _load(argv[0])
    vereditos = _load(argv[1])
    out = argv[2] if len(argv) >= 3 else "dados/pesos.json"

    peso = compute_pesos(claims, vereditos)
    result = [{"id": cid, "peso": peso[cid]} for cid in (c["id"] for c in claims)]
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    for r in result:
        print(f"{r['id']}: {r['peso']}")
    print(f"\nGravado em {out}")
    return 0


def _self_test():
    """Cobre os quatro casos de aceitação do design."""
    # Estrutura: raiz R -> filho F -> folha L  (cadeia de derivação)
    claims = [
        {"id": "R"},
        {"id": "F", "deriva_de": ["R"]},
        {"id": "L", "deriva_de": ["F"]},
    ]

    # baseline: tudo definido, nenhuma dúvida -> definir é neutro -> peso 0
    base_ver = [
        {"id": "R", "lacunas_estruturais": [], "itens_verificar": []},
        {"id": "F", "lacunas_estruturais": [], "itens_verificar": []},
        {"id": "L", "lacunas_estruturais": [], "itens_verificar": []},
    ]
    p = compute_pesos(claims, base_ver)
    assert p == {"R": 0, "F": 0, "L": 0}, p  # definir conteúdo sem dúvida = neutro

    # CASO propagação raiz: abrir 1 dúvida em R derruba R E descendentes (F e L)
    ver_root = [
        {"id": "R", "itens_verificar": ["fato pendente"]},
        {"id": "F"},
        {"id": "L"},
    ]
    p = compute_pesos(claims, ver_root)
    assert p["R"] == -1 and p["F"] == -1 and p["L"] == -1, p  # propagou até a folha

    # CASO folha isolada: abrir 1 dúvida em L só derruba L
    ver_leaf = [
        {"id": "R"},
        {"id": "F"},
        {"id": "L", "lacunas_estruturais": ["borda indefinida"]},
    ]
    p = compute_pesos(claims, ver_leaf)
    assert p["R"] == 0 and p["F"] == 0 and p["L"] == -1, p  # parou na folha

    # CASO fechar dúvida sobe o peso: R com 2 abertas vs R com 1 aberta + 1 fechada
    ver_aberto = [{"id": "R", "itens_verificar": ["a", "b"]}, {"id": "F"}, {"id": "L"}]
    ver_fechado = [
        {"id": "R", "itens_verificar": ["a"], "itens_verificados": ["b"]},
        {"id": "F"},
        {"id": "L"},
    ]
    pa = compute_pesos(claims, ver_aberto)
    pf = compute_pesos(claims, ver_fechado)
    assert pf["R"] > pa["R"], (pa["R"], pf["R"])  # fechar dúvida adiciona peso
    assert pf["R"] == 0 and pa["R"] == -2, (pa["R"], pf["R"])

    # CASO herança do expansor: filho nasce com o peso do pai (não zerado).
    # Pai resolvido com peso alto -> filho sem dúvidas próprias herda esse peso.
    claims2 = [{"id": "P"}, {"id": "C", "deriva_de": ["P"]}]
    ver2 = [
        {"id": "P", "itens_verificados": ["x", "y", "z"]},  # pai resolvido, peso +3
        {"id": "C"},  # filho recém-nascido, sem dúvida própria
    ]
    p2 = compute_pesos(claims2, ver2)
    assert p2["P"] == 3 and p2["C"] == 3, p2  # filho herda 3, não nasce zerado

    # filho só fica mais leve que o pai se tiver mais dúvidas abertas próprias
    ver3 = [
        {"id": "P", "itens_verificados": ["x", "y", "z"]},
        {"id": "C", "lacunas_estruturais": ["d1", "d2"]},  # 2 abertas próprias
    ]
    p3 = compute_pesos(claims2, ver3)
    assert p3["C"] == 1 and p3["C"] < p3["P"], p3  # 3 herdado - 2 abertas = 1

    # guarda de ciclo
    try:
        compute_pesos(
            [{"id": "A", "deriva_de": ["B"]}, {"id": "B", "deriva_de": ["A"]}],
            [{"id": "A"}, {"id": "B"}],
        )
        raise AssertionError("deveria ter detectado ciclo")
    except ValueError:
        pass

    print("self-test OK — propagação, folha isolada, fechar sobe, definir é neutro, herança.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
