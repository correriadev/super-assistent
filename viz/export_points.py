#!/usr/bin/env python3
"""export_points.py — gera viz/points.json com o estado atual dos domínios do projeto.

Lê os níveis de claims do domínio "simulador" (ideação → código) + o domínio "lei"
(claims-source.json), calcula scores, marca provisional e emite um ponto por claim.

Cada ponto inclui um campo `domain` e um campo `edgeObjects` com arestas estruturadas:
  [{ ref, kind: "posse" | "ref", cross_domain: bool }, ...]

Determinístico, sem LLM.

Uso: python3 viz/export_points.py [pasta_dados]
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.score import compute_scores
from engine.integrity import verify_integrity, is_artifact

LEVELS = [
    ("ideação", "claims.json", "verdicts.json"),
    ("concepção", "claims-nivel-1.json", "verdicts-nivel-1.json"),
    ("arquitetura", "claims-nivel-2.json", "verdicts-nivel-2.json"),
    ("cenários", "claims-nivel-3.json", "verdicts-nivel-3.json"),
    ("testes", "claims-nivel-4-testes.json", "verdicts-nivel-4-testes.json"),
    ("código", "claims-nivel-5-codigo.json", "verdicts-nivel-5-codigo.json"),
]

LEI_CLAIMS_FILE = "claims-source.json"


def _load(path):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else []


def main(dados):
    # --- Domínio simulador ---
    sim_claims, sim_verdicts, level_of = [], [], {}
    for i, (name, cf, vf) in enumerate(LEVELS):
        claims = _load(os.path.join(dados, cf))
        sim_verdicts += _load(os.path.join(dados, vf))
        for c in claims:
            level_of[c["id"]] = (i, name)
            if "domain" not in c:
                c["domain"] = "simulador"
        sim_claims += claims

    # --- Domínio lei ---
    lei_claims = _load(os.path.join(dados, LEI_CLAIMS_FILE))
    for c in lei_claims:
        if "domain" not in c:
            c["domain"] = "lei"

    # Combinar tudo para scores e integridade
    all_claims = sim_claims + lei_claims
    all_verdicts = sim_verdicts  # lei claims não têm verdicts separados por ora

    scores = compute_scores(all_claims, all_verdicts)
    v_by = {v["id"]: v for v in all_verdicts}

    # Índice de domínio por id (para resolver cross_domain)
    domain_of = {c["id"]: c.get("domain", "simulador") for c in all_claims}

    # Integridade (apenas sobre claims do simulador para não quebrar)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    integ = verify_integrity(sim_claims, repo_root=root, app_dir=os.path.join(root, "app"))
    nao_ancorado = set(
        integ["orphans"] + integ["ungrounded_symbol"] + integ["red"] +
        [n for n, _ in integ["missing_parent_ref"]]
    )
    art_ids = {c["id"] for c in sim_claims if is_artifact(c)}

    def is_open(cid, domain):
        if domain == "lei":
            # lei claims: aberto se não há veredito PASSA
            return v_by.get(cid, {}).get("status") != "PASSA"
        if cid in art_ids:
            return cid in nao_ancorado
        return v_by.get(cid, {}).get("status") != "PASSA"

    def _raw_edges(c):
        """Pares (ref, kind) de todas as arestas do nó: parent=posse, links=ref, derives_from legado=ref."""
        refs = []
        p = c.get("parent")
        if p is not None:
            refs.append((p, "posse"))
        for link in c.get("links") or []:
            r = link.get("ref")
            if r:
                refs.append((r, "ref"))
        if not refs:
            for d in c.get("derives_from") or []:
                refs.append((d, "ref"))
        return refs

    def _edge_objects(c):
        """Lista de {ref, kind, cross_domain} para o ponto."""
        my_domain = c.get("domain", "simulador")
        result = []
        for ref, kind in _raw_edges(c):
            target_domain = domain_of.get(ref, my_domain)
            result.append({
                "ref": ref,
                "kind": kind,
                "cross_domain": target_domain != my_domain,
            })
        return result

    def _edges_flat(c):
        """Lista plana de refs (compatibilidade com provisional)."""
        return [ref for ref, _ in _raw_edges(c)]

    memo = {}
    id_to_claim = {c["id"]: c for c in all_claims}

    def provisional(cid, stack=()):
        if cid in memo:
            return memo[cid]
        if cid in stack:
            return False
        c_node = id_to_claim.get(cid)
        parents = _edges_flat(c_node) if c_node else []
        dom = c_node.get("domain", "simulador") if c_node else "simulador"
        r = any(is_open(p, domain_of.get(p, dom)) or provisional(p, stack + (cid,)) for p in parents)
        memo[cid] = r
        return r

    points = []

    # --- Pontos do domínio simulador ---
    for c in sim_claims:
        i, name = level_of[c["id"]]
        edge_objs = _edge_objects(c)
        edges_flat = [e["ref"] for e in edge_objs]
        points.append({
            "id": c["id"],
            "domain": c.get("domain", "simulador"),
            "level": name,
            "levelIndex": i,
            "score": scores.get(c["id"], 0),
            "status": v_by.get(c["id"], {}).get("status"),
            "open": is_open(c["id"], "simulador"),
            "provisional": provisional(c["id"]),
            "derivation": c.get("derivation"),
            "parent": c.get("parent"),
            "links": c.get("links") or [],
            "edges": edges_flat,
            "edgeObjects": edge_objs,
            "binding": c.get("binding"),
            "artifact": is_artifact(c),
            "exposed": c.get("exposed", False),
            "file": c.get("provenance", {}).get("file") if is_artifact(c) else None,
            "content": (c.get("content") or "")[:160],
        })

    # --- Pontos do domínio lei ---
    # Lei claims não pertencem à hierarquia de níveis do simulador.
    # Usamos levelIndex=-1 e level="lei" para distingui-los na viz.
    for j, c in enumerate(lei_claims):
        edge_objs = _edge_objects(c)
        edges_flat = [e["ref"] for e in edge_objs]
        points.append({
            "id": c["id"],
            "domain": "lei",
            "level": "lei",
            "levelIndex": -1,
            "score": scores.get(c["id"], 0),
            "status": v_by.get(c["id"], {}).get("status"),
            "open": is_open(c["id"], "lei"),
            "provisional": provisional(c["id"]),
            "derivation": c.get("derivation"),
            "parent": c.get("parent"),
            "links": c.get("links") or [],
            "edges": edges_flat,
            "edgeObjects": edge_objs,
            "binding": c.get("binding"),
            "artifact": False,
            "exposed": c.get("exposed", False),
            "file": None,
            "content": (c.get("content") or "")[:160],
        })

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "points.json")
    json.dump({"points": points}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"{len(points)} pontos -> {out}")

    by_domain = {}
    by_level = {}
    for p in points:
        by_domain.setdefault(p["domain"], 0)
        by_domain[p["domain"]] += 1
        by_level.setdefault(p["level"], 0)
        by_level[p["level"]] += 1

    print("por domínio:", by_domain)
    print("por nível:", by_level)

    cross = sum(1 for p in points for e in p["edgeObjects"] if e["cross_domain"])
    total_edges = sum(len(p["edgeObjects"]) for p in points)
    print(f"arestas totais: {total_edges} | pontes cross-domínio: {cross}")
    print("provisional:", sum(p["provisional"] for p in points), "| abertos:", sum(p["open"] for p in points))


if __name__ == "__main__":
    dados = sys.argv[1] if len(sys.argv) > 1 else "projetos/02-simulador-caixa-split/dados"
    main(dados)
