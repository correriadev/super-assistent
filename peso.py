#!/usr/bin/env python3
"""
peso.py — cálculo determinístico do PESO de cada claim.

O peso mede quão RESOLVIDO/ASSENTADO um claim está. Peso alto = afunda na
constelação. Peso baixo = flutua, vira névoa.

NÃO é julgamento de LLM. É função pura das dúvidas, da herança (`deriva_de`) e,
para a constelação-lei, da ancoragem rastreável do trecho-fonte.

Fórmula:

    peso = base + herança_dos_pais + dúvidas_fechadas − dúvidas_abertas

  - base:
      * claim-IDEIA (fonte = "decisão humana" ou ausente): base = 10. A decisão
        humana é o chão — nasce assentado.
      * claim-LEI (fonte = {documento, trecho}): base = 0 (nasce LEVE, é
        interpretação não-confirmada) + 10 SE o `trecho` estiver literalmente
        localizável no texto do documento (ANCORAGEM rastreável). Ancoragem é
        "o texto diz isto", NÃO "isto é verdadeiro/constitucional". Verdade
        jurídica nunca pesa automático — continua [VERIFICAR] humano.
  - herança_dos_pais = soma do peso de cada pai em `deriva_de`. Filho nasce com o
    peso do pai; pai cai -> filhos caem, recursivamente (propagação topológica).
  - dúvidas_abertas = lacunas/itens [VERIFICAR] REAIS não resolvidos. Itens
    marcados "(não bloqueante)" NÃO contam.
  - dúvidas_fechadas = lacunas_resolvidas + itens_verificados; cada uma SOBE o peso.

Uso:
    python3 peso.py <claims.json> <vereditos.json> [pesos.json] [--doc <texto_lei>]
"""

import json
import sys

PESO_BASE = 10        # base do claim-ideia (decisão humana é o chão)
PESO_LEI_BASE = 0     # claim-lei nasce leve (interpretação não confirmada)
ANCORA_BONUS = 10     # claim-lei com trecho-fonte localizável ganha isto

# Itens com qualquer um destes marcadores são ruído não-bloqueante: não pesam.
_NONBLOCK_MARKERS = ("não bloqueante", "nao bloqueante")


def _norm(s):
    """Normaliza espaços/caixa para comparar trecho-fonte com o documento."""
    return " ".join((s or "").split()).lower()


def is_law_claim(claim):
    """Claim-lei: tem fonte estruturada com trecho literal do documento."""
    f = claim.get("fonte")
    return isinstance(f, dict) and "trecho" in f


def is_anchored(claim, doc_text):
    """Ancorado = o trecho-fonte existe literalmente no texto do documento.
    Rastreabilidade pura (substring normalizado), nunca juízo de verdade."""
    if not is_law_claim(claim) or not doc_text:
        return False
    trecho = claim["fonte"].get("trecho") or ""
    if not trecho.strip():
        return False
    return _norm(trecho) in _norm(doc_text)


def relatorio_ancoragem(claims, doc_text):
    """Mapa {id: bool} de ancoragem para os claims-lei (útil em teste/auditoria)."""
    return {c["id"]: is_anchored(c, doc_text) for c in claims if is_law_claim(c)}


def _base(claim, doc_text):
    if is_law_claim(claim):
        return PESO_LEI_BASE + (ANCORA_BONUS if is_anchored(claim, doc_text) else 0)
    return PESO_BASE


def _is_nonblocking(item):
    return isinstance(item, str) and any(m in item.lower() for m in _NONBLOCK_MARKERS)


def _count_open(lst):
    if lst is None:
        return 0
    if isinstance(lst, int):
        return lst
    return sum(1 for x in lst if not _is_nonblocking(x))


def _count_closed(x):
    if x is None:
        return 0
    if isinstance(x, int):
        return x
    return len(x)


def _open_doubts(ver):
    return _count_open(ver.get("lacunas_estruturais")) + _count_open(ver.get("itens_verificar"))


def _closed_doubts(ver):
    return _count_closed(ver.get("lacunas_resolvidas")) + _count_closed(ver.get("itens_verificados"))


def compute_pesos(claims, vereditos, doc_text=None):
    """
    claims: lista de {id, ..., deriva_de?: [ids], fonte?: "decisão humana" | {documento, trecho}}
    vereditos: lista de {id, lacunas_estruturais?, itens_verificar?,
                         lacunas_resolvidas?, itens_verificados?}
    doc_text: texto do documento legal, para verificar ancoragem de claims-lei.
    Retorna dict {id: peso}.
    """
    ver_by_id = {v["id"]: v for v in vereditos}
    claim_by_id = {c["id"]: c for c in claims}
    deriva = {c["id"]: list(c.get("deriva_de") or []) for c in claims}

    # contribuição própria: base (ideia=10 / lei=0+ancora) + fechadas - abertas
    own = {}
    for c in claims:
        v = ver_by_id.get(c["id"], {})
        own[c["id"]] = _base(c, doc_text) + _closed_doubts(v) - _open_doubts(v)

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
        peso[cid] = own.get(cid, PESO_BASE) + inherited
        visiting.discard(cid)
        return peso[cid]

    for c in claims:
        resolve(c["id"])
    return peso


def _load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(argv):
    doc_text = None
    if "--doc" in argv:
        i = argv.index("--doc")
        with open(argv[i + 1], "r", encoding="utf-8") as f:
            doc_text = f.read()
        argv = argv[:i] + argv[i + 2:]

    if len(argv) < 2:
        print(__doc__)
        return 2

    claims = _load(argv[0])
    vereditos = _load(argv[1])
    out = argv[2] if len(argv) >= 3 else "dados/pesos.json"

    peso = compute_pesos(claims, vereditos, doc_text)
    result = [{"id": cid, "peso": peso[cid]} for cid in (c["id"] for c in claims)]
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    for r in result:
        print(f"{r['id']}: {r['peso']}")
    print(f"\nGravado em {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
