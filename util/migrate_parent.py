#!/usr/bin/env python3
"""migrate_parent.py — FASE 1: migra derives_from (multi-pai) → parent (posse única) + links.

Aplica a regra do plano composicao-dominios-godot.md:
  - claims.json:       parent=null, domain="simulador"
  - claims-source.json: parent=null, domain="lei"
  - nivel-1:          parent=primeiro derives_from (único), domain="simulador"
  - nivel-2,3:        parent=primeiro derives_from cujo alvo está no nível acima;
                      demais viram links {domain, ref, kind:"derivation"}
  - nivel-4:          parent=único derives_from (cenário), domain="simulador"
  - nivel-5:          parent=primeiro ref de arquitetura (nivel-2);
                      refs de teste (nivel-4) viram links kind="grounding";
                      outros viram links kind:"derivation"
                      Preserva grounded_by e provenance.

Uso: python3 util/migrate_parent.py [dados_dir]
"""

import json
import sys
import os


def _load(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def migrate_root_claims(claims, domain):
    """claims.json e claims-source.json: parent=null, domain dado."""
    out = []
    for c in claims:
        node = dict(c)
        node.pop("derives_from", None)
        node["parent"] = None
        node["domain"] = domain
        # preserve existing links array if present
        if "links" not in node:
            node["links"] = []
        out.append(node)
    return out


def migrate_simple(claims, domain):
    """Nivéis com um único derives_from (nivel-1 e nivel-4): parent=esse único ref."""
    out = []
    for c in claims:
        node = dict(c)
        df = node.pop("derives_from", None) or []
        node["parent"] = df[0] if df else None
        node["domain"] = domain
        # preserve existing links
        if "links" not in node:
            node["links"] = []
        # extra refs (should not happen at these levels, but be safe)
        extras = df[1:]
        for ref in extras:
            node["links"].append({"domain": domain, "ref": ref, "kind": "derivation"})
        out.append(node)
    return out


def migrate_multi(claims, domain, above_ids):
    """Nivéis com possível multi-derives_from (nivel-2 e nivel-3).

    parent = primeiro derives_from que está em above_ids.
    demais viram links kind:"derivation".
    """
    out = []
    for c in claims:
        node = dict(c)
        df = node.pop("derives_from", None) or []
        # find first ref that is in the level above
        parent = None
        links = list(node.get("links", []))
        for ref in df:
            if ref in above_ids:
                if parent is None:
                    parent = ref
                else:
                    links.append({"domain": domain, "ref": ref, "kind": "derivation"})
            else:
                # ref not in above_ids: also a link
                links.append({"domain": domain, "ref": ref, "kind": "derivation"})
        # if no above ref found, fallback to first
        if parent is None and df:
            parent = df[0]
            links = [{"domain": domain, "ref": r, "kind": "derivation"} for r in df[1:]]
        node["parent"] = parent
        node["domain"] = domain
        node["links"] = links
        out.append(node)
    return out


def migrate_nivel5(claims, domain, nivel2_ids, nivel4_ids):
    """nivel-5-codigo:
    parent = primeiro derives_from que é id de arquitetura (nivel-2).
    refs de teste (nivel-4) → links kind:"grounding".
    outros → links kind:"derivation".
    Preserva grounded_by e provenance.
    """
    out = []
    for c in claims:
        node = dict(c)
        df = node.pop("derives_from", None) or []
        parent = None
        links = list(node.get("links", []))
        for ref in df:
            if ref in nivel2_ids:
                if parent is None:
                    parent = ref
                else:
                    links.append({"domain": domain, "ref": ref, "kind": "derivation"})
            elif ref in nivel4_ids:
                links.append({"domain": domain, "ref": ref, "kind": "grounding"})
            else:
                links.append({"domain": domain, "ref": ref, "kind": "derivation"})
        if parent is None and df:
            parent = df[0]
        node["parent"] = parent
        node["domain"] = domain
        node["links"] = links
        # grounded_by and provenance are preserved (not touched)
        out.append(node)
    return out


def main(dados):
    p = lambda f: os.path.join(dados, f)

    # load id sets per level
    nivel1_ids = {c["id"] for c in _load(p("claims-nivel-1.json"))}
    nivel2_ids = {c["id"] for c in _load(p("claims-nivel-2.json"))}
    nivel3_ids = {c["id"] for c in _load(p("claims-nivel-3.json"))}
    nivel4_ids = {c["id"] for c in _load(p("claims-nivel-4-testes.json"))}

    # migrate claims.json (ideação) — no derives_from
    claims = _load(p("claims.json"))
    _save(p("claims.json"), migrate_root_claims(claims, "simulador"))
    print(f"claims.json: {len(claims)} nós migrados (parent=null, domain=simulador)")

    # migrate claims-source.json (lei) — no derives_from
    claims = _load(p("claims-source.json"))
    _save(p("claims-source.json"), migrate_root_claims(claims, "lei"))
    print(f"claims-source.json: {len(claims)} nós migrados (parent=null, domain=lei)")

    # nivel-1 (concepção) — parent = único derives_from, level above = ideação
    claims = _load(p("claims-nivel-1.json"))
    _save(p("claims-nivel-1.json"), migrate_simple(claims, "simulador"))
    print(f"claims-nivel-1.json: {len(claims)} nós migrados")

    # nivel-2 (arquitetura) — above = nivel-1
    claims = _load(p("claims-nivel-2.json"))
    _save(p("claims-nivel-2.json"), migrate_multi(claims, "simulador", nivel1_ids))
    print(f"claims-nivel-2.json: {len(claims)} nós migrados")

    # nivel-3 (cenários) — above = nivel-2
    claims = _load(p("claims-nivel-3.json"))
    _save(p("claims-nivel-3.json"), migrate_multi(claims, "simulador", nivel2_ids))
    print(f"claims-nivel-3.json: {len(claims)} nós migrados")

    # nivel-4 (testes) — 1 derives_from each (cenário)
    claims = _load(p("claims-nivel-4-testes.json"))
    _save(p("claims-nivel-4-testes.json"), migrate_simple(claims, "simulador"))
    print(f"claims-nivel-4-testes.json: {len(claims)} nós migrados")

    # nivel-5 (código) — arch → parent, tests → links grounding, others → links derivation
    claims = _load(p("claims-nivel-5-codigo.json"))
    _save(p("claims-nivel-5-codigo.json"), migrate_nivel5(claims, "simulador", nivel2_ids, nivel4_ids))
    print(f"claims-nivel-5-codigo.json: {len(claims)} nós migrados")

    # verify: no derives_from left
    all_files = [
        "claims.json", "claims-source.json",
        "claims-nivel-1.json", "claims-nivel-2.json", "claims-nivel-3.json",
        "claims-nivel-4-testes.json", "claims-nivel-5-codigo.json",
    ]
    remaining = []
    for f in all_files:
        for c in _load(p(f)):
            if "derives_from" in c:
                remaining.append((f, c["id"]))
    if remaining:
        print(f"\nERRO: ainda tem derives_from em: {remaining}")
        return 1
    print("\nOK: nenhum derives_from restante nos JSONs.")
    return 0


if __name__ == "__main__":
    dados = sys.argv[1] if len(sys.argv) > 1 else "projetos/02-simulador-caixa-split/dados"
    sys.exit(main(dados))
