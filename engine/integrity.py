#!/usr/bin/env python3
"""integrity.py — portão de integridade: torna o nó-artefato ÓRFÃO impossível de passar.

Estende o grounding ao código (o análogo do substring-match da lei): um nó de
implementação só é íntegro se (a) tem pai (`derives_from`), (b) seu artefato existe
(arquivo + símbolo presente no arquivo) e (c) os testes que ele declara estão VERDES.

`verify_integrity` falha enquanto houver órfão, símbolo ausente ou teste vermelho — é o
que o orchestrator checa para RECUSAR fechar o ciclo. Determinístico, sem LLM. Ninguém
ancora a si mesmo: o produtor (agente) escreve o artefato; ISTO o ancora contra o real.
"""

import os
import re
import subprocess
from collections import Counter

from engine.domains import node_index, is_exposed


def is_artifact(node):
    """Nó-artefato: provenance estruturada apontando um arquivo real."""
    p = node.get("provenance")
    return isinstance(p, dict) and "file" in p


def symbol_present(node, repo_root):
    """Grounding do código: o arquivo existe e o símbolo aparece literalmente nele
    (substring — igual ao excerpt da lei). Sem `symbol`, basta o arquivo existir."""
    p = node["provenance"]
    path = os.path.join(repo_root, p["file"])
    if not os.path.isfile(path):
        return False
    sym = p.get("symbol")
    if not sym:
        return True
    return sym in open(path, encoding="utf-8").read()


def run_node_tests(app_dir):
    """Roda `node --test` (TAP) e devolve {nome_do_teste: True/False}. Vazio se falhar."""
    try:
        r = subprocess.run(
            ["node", "--test", "--test-reporter=tap"],
            cwd=app_dir, capture_output=True, text=True, timeout=120,
        )
    except (OSError, subprocess.SubprocessError):
        return {}
    out = {}
    for line in (r.stdout or "").splitlines():
        m = re.match(r"(ok|not ok)\s+\d+\s+-\s+(.*)", line.strip())
        if m:
            out[m.group(2).strip()] = m.group(1) == "ok"
    return out


def tests_green(node, test_results):
    """Os testes que o nó declara (`grounded_by.tests`) estão todos verdes?
    None se o nó não declara teste (não é nó cuja âncora é execução)."""
    names = (node.get("grounded_by") or {}).get("tests")
    if not names:
        return None
    return all(test_results.get(n) is True for n in names)


def _all_refs(node):
    """Todas as refs de um nó: parent (posse) + links[].ref + derives_from legado."""
    refs = []
    p = node.get("parent")
    if p is not None:
        refs.append(p)
    for link in node.get("links") or []:
        r = link.get("ref")
        if r:
            refs.append(r)
    # fallback legado
    if not node.get("parent") and not node.get("links"):
        refs.extend(node.get("derives_from") or [])
    return refs


def _ownership_refs(node):
    """Refs de posse: [parent] se definido, senão derives_from legado."""
    if node.get("parent") is not None:
        return [node["parent"]]
    return list(node.get("derives_from") or [])


def _cross_domain_links(node):
    """Links de um nó que apontam para fora do domínio do nó.

    Detecta dois formatos:
    - link com `domain` explícito diferente do nó-fonte
    - link com `graph` (ex: 'source'), que por convenção indica grafo externo
    """
    src_domain = node.get("domain")
    result = []
    for link in node.get("links") or []:
        ref = link.get("ref")
        if not ref:
            continue
        link_domain = link.get("domain")
        link_graph = link.get("graph")
        # graph presente (ex: 'source') ou domain diferente do nó-fonte = cross-domain
        if link_graph or (link_domain and link_domain != src_domain):
            result.append(ref)
    return result


def verify_integrity(nodes, repo_root, app_dir=None):
    """Checa o grafo inteiro.
    Retorna {ok, orphans, ungrounded_symbol, red, missing_parent_ref, unexposed_xref}.
    ok=False => o ciclo NÃO fecha. Bloqueio, não aviso.

    orfão = nó-artefato SEM parent (e sem derives_from legado).
    dangling = qualquer ref em (parent + links[].ref) de artefato que não exista no grafo.
    unexposed_xref = link cross-domínio (qualquer nó) mirando nó não-exposto (D4).
    """
    ids = {n["id"] for n in nodes}
    idx = node_index(nodes)
    # D2 — id estável: alias (old id -> nó atual) torna rename seguro; id duplicado corromperia refs.
    alias_index = {a: n for n in nodes for a in (n.get("aliases") or [])}
    dup_ids = sorted(i for i, c in Counter(n["id"] for n in nodes).items() if c > 1)
    orphans, ungrounded, red, dangling, unexposed = [], [], [], [], []
    results = run_node_tests(app_dir) if app_dir else {}

    for n in nodes:
        # D4 — checagem cross-domínio para TODOS os nós
        for ref in _cross_domain_links(n):
            target = idx.get(ref) or alias_index.get(ref)
            if target is None:
                # alvo inexistente: cai em missing_parent_ref se for artefato (abaixo),
                # ou em dangling genérico; não conta em unexposed_xref
                dangling.append((n["id"], ref))
            elif not is_exposed(target):
                unexposed.append((n["id"], ref))

        if not is_artifact(n):
            continue

        # checagens existentes (apenas artefatos)
        ownership = _ownership_refs(n)
        if not ownership:
            orphans.append(n["id"])
        for ref in _all_refs(n):
            if ref not in ids and ref not in alias_index:  # alias resolve = não-dangling (rename-safe)
                entry = (n["id"], ref)
                if entry not in dangling:
                    dangling.append(entry)
        if not symbol_present(n, repo_root):
            ungrounded.append(n["id"])
        if tests_green(n, results) is False:
            red.append(n["id"])

    ok = not (orphans or ungrounded or red or dangling or unexposed or dup_ids)
    return {
        "ok": ok,
        "orphans": orphans,
        "ungrounded_symbol": ungrounded,
        "red": red,
        "missing_parent_ref": dangling,
        "unexposed_xref": unexposed,
        "dup_ids": dup_ids,
    }
