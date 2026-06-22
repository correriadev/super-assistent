#!/usr/bin/env python3
"""
score.py — confidence/maturity score determinístico de cada claim.

O score mede quão RESOLVIDO/ASSENTADO um claim está. Score alto = afunda no graph.
Score baixo = flutua (low confidence). NÃO é julgamento de LLM — é função pura das
dúvidas, da herança (`derives_from`) e, no source graph, do grounding rastreável.

Fórmula:

    score = base + herança + dúvidas_fechadas − dúvidas_abertas

  - base:
      * claim do IDEA GRAPH (provenance = "human decision" ou ausente): base = 10.
        Decisão humana é o chão — nasce assentado.
      * claim do SOURCE GRAPH (provenance = {document, excerpt}): base = 0 (nasce
        leve, interpretação não-confirmada) + 10 SE o `excerpt` estiver literalmente
        no texto do documento (GROUNDING rastreável). Grounding = "o texto diz isto",
        NÃO "isto é verdadeiro/constitucional". Verdade nunca pesa automático — segue
        verification_item humano.
  - herança = soma do score de cada pai em `derives_from`. Filho nasce com o score do
    pai; pai cai → filhos caem, recursivamente (propagação topológica).
  - dúvidas_abertas = structural_gaps + verification_items REAIS não resolvidos. Itens
    marcados "(non-blocking)"/"(não bloqueante)" NÃO contam.
  - dúvidas_fechadas = resolved_gaps + verified_items; cada uma SOBE o score.

Uso:
    python3 score.py <claims.json> <verdicts.json> [scores.json] [--doc <texto_fonte>]
"""

import json
import sys

SCORE_BASE = 10        # base do claim do idea graph (decisão humana é o chão)
SOURCE_BASE = 0        # claim do source graph nasce leve (não confirmado)
GROUNDING_BONUS = 10   # claim-fonte com excerpt localizável ganha isto

_NONBLOCK_MARKERS = ("não bloqueante", "nao bloqueante", "non-blocking")


def _norm(s):
    return " ".join((s or "").split()).lower()


def is_source_claim(claim):
    """Claim do source graph: provenance estruturada com excerpt literal."""
    p = claim.get("provenance")
    return isinstance(p, dict) and "excerpt" in p


def is_grounded(claim, doc_text):
    """Grounded = o excerpt existe literalmente no documento. Rastreabilidade pura
    (substring normalizado), nunca juízo de verdade."""
    if not is_source_claim(claim) or not doc_text:
        return False
    excerpt = claim["provenance"].get("excerpt") or ""
    if not excerpt.strip():
        return False
    return _norm(excerpt) in _norm(doc_text)


def grounding_report(claims, doc_text):
    """Mapa {id: bool} de grounding dos claims do source graph."""
    return {c["id"]: is_grounded(c, doc_text) for c in claims if is_source_claim(c)}


def _base(claim, doc_text):
    if is_source_claim(claim):
        return SOURCE_BASE + (GROUNDING_BONUS if is_grounded(claim, doc_text) else 0)
    return SCORE_BASE


def item_text(item):
    """Texto de um verification_item / structural_gap. Aceita string (legado) ou
    objeto {text, domain, critical} (forma A)."""
    if isinstance(item, dict):
        return item.get("text", "")
    return item if isinstance(item, str) else ""


def _is_nonblocking(item):
    t = item_text(item).lower()
    return any(m in t for m in _NONBLOCK_MARKERS)


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


def _open_issues(v):
    return _count_open(v.get("structural_gaps")) + _count_open(v.get("verification_items"))


def _closed_issues(v):
    return _count_closed(v.get("resolved_gaps")) + _count_closed(v.get("verified_items"))


def compute_scores(claims, verdicts, doc_text=None):
    """
    claims: lista de {id, ..., derives_from?: [ids],
                      provenance?: "human decision" | {document, excerpt}}
    verdicts: lista de {id, structural_gaps?, verification_items?,
                        resolved_gaps?, verified_items?}
    doc_text: texto do documento-fonte, para grounding de claims do source graph.
    Retorna dict {id: score}.
    """
    v_by_id = {v["id"]: v for v in verdicts}
    # posse (D5): herança vem do `parent` ÚNICO, não dos links. Compat com derives_from legado.
    derives = {c["id"]: ([c["parent"]] if c.get("parent") else list(c.get("derives_from") or []))
               for c in claims}

    own = {}
    for c in claims:
        v = v_by_id.get(c["id"], {})
        own[c["id"]] = _base(c, doc_text) + _closed_issues(v) - _open_issues(v)

    score = {}
    visiting = set()

    def resolve(cid):
        if cid in score:
            return score[cid]
        if cid in visiting:
            raise ValueError(f"ciclo em derives_from envolvendo: {cid}")
        visiting.add(cid)
        inherited = 0
        for parent in derives.get(cid, []):
            if parent in own:
                inherited += resolve(parent)
        score[cid] = own.get(cid, SCORE_BASE) + inherited
        visiting.discard(cid)
        return score[cid]

    for c in claims:
        resolve(c["id"])
    return score


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
    verdicts = _load(argv[1])
    out = argv[2] if len(argv) >= 3 else "dados/scores.json"

    score = compute_scores(claims, verdicts, doc_text)
    result = [{"id": cid, "score": score[cid]} for cid in (c["id"] for c in claims)]
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    for r in result:
        print(f"{r['id']}: {r['score']}")
    print(f"\nGravado em {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
