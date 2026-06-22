#!/usr/bin/env python3
"""
propagation.py — cascade invalidation entre graphs + event log.

Quando um claim-fonte é INVALIDADO (uma emenda abre dúvida nele, score cai), todo
claim de QUALQUER graph cujo `links` aponta para ele (`links[].ref`) também é
invalidado. A perda de score atravessa a fronteira do graph.

REGRA DURA: a propagação MARCA STALE (invalida, "revise") e REABRE a dúvida (score
cai) — NUNCA reescreve a resposta. Reescrever seria interpretação automática,
proibida. Cada dono de domínio re-resolve à mão.

Event log append-only (JSONL, não event-sourcing completo, não banco): cada evento =
{ts, type, claim, cause}. O "diff entre versões" é a lista de eventos entre dois
marcos (events_between), não diff de linha. Git versiona os arquivos.
"""

import datetime
import json


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def log_event(log_path, type_, claim, cause, ts=None):
    """Anexa um evento ao log append-only. Retorna o evento."""
    ev = {"ts": ts or _now(), "type": type_, "claim": claim, "cause": cause}
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    return ev


def read_events(log_path):
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            return [json.loads(linha) for linha in f if linha.strip()]
    except FileNotFoundError:
        return []


def events_between(log_path, since=None, until=None):
    """O 'diff' entre dois marcos: a lista de eventos no intervalo [since, until]."""
    evs = read_events(log_path)
    return [
        e for e in evs
        if (since is None or e["ts"] >= since) and (until is None or e["ts"] <= until)
    ]


def depends_on(claim, source_claim_id):
    """Claim depende de um claim-fonte se algum `links` aponta para ele (ponte
    cross-graph persistida), ou — legado — se `provenance.ref` aponta."""
    for a in claim.get("links") or []:
        if isinstance(a, dict) and a.get("ref") == source_claim_id:
            return True
    p = claim.get("provenance")
    return isinstance(p, dict) and p.get("ref") == source_claim_id


def referenced_by(nodes):
    """Constrói o índice reverso de referências: {ref_id: [ids dos nós que referenciam ref_id]}.

    Para cada nó considera:
      - parent   (posse, 1 por nó)
      - links[].ref  (referências explícitas, N, incluindo cross-domínio)
      - provenance.ref  (legado)

    Análogo ao broadcast desacoplado do Godot: o alvo não conhece quem o referencia;
    este índice resolve "quem aponta pra mim" sem varrer todos os nós a cada consulta.
    """
    idx = {}
    for node in nodes:
        node_id = node.get("id")
        if not node_id:
            continue

        # parent = posse (1 por nó, pode ser None)
        parent = node.get("parent")
        if parent is not None:
            idx.setdefault(parent, []).append(node_id)

        # links[].ref = referências explícitas (N, cross-domínio)
        for link in node.get("links") or []:
            ref = link.get("ref") if isinstance(link, dict) else None
            if ref:
                idx.setdefault(ref, []).append(node_id)

        # legado: provenance.ref
        prov = node.get("provenance")
        if isinstance(prov, dict):
            ref = prov.get("ref")
            if ref:
                idx.setdefault(ref, []).append(node_id)

    return idx


def mark_stale(claim, source_claim_id):
    """Marca o claim como 'revise' SEM tocar na resposta. Idempotente."""
    claim["stale"] = {
        "state": "review",
        "source": source_claim_id,
        "reason": "fonte invalidada; re-resolver à mão (sistema não reescreve)",
    }
    return claim


_REVIEW_MARK = "[REVIEW] source {ref} invalidada — re-resolver à mão"


def propagate(source_claim_id, claims, verdicts, log_path, ts=None):
    """
    Propaga a invalidação de `source_claim_id` para os claims dependentes.

    Usa o índice reverso `referenced_by` para localizar dependentes em O(dependentes)
    em vez de varrer todos os claims com depends_on (O(n)). Funciona com nós de
    múltiplos domínios na mesma lista — o índice resolve quem aponta para a fonte
    independentemente de domínio (broadcast desacoplado, Godot signals).

    Para cada dependente: marca stale + reabre dúvida (score cai) + loga evento.
    NUNCA reescreve content/rationale/resposta.
    Retorna (ids_afetados, verdicts_atualizados).
    """
    # Índice reverso construído uma única vez para toda a lista (O(n) build,
    # O(dependentes) lookup — contra O(n) por dependente no loop antigo).
    idx = referenced_by(claims)
    dependentes_ids = set(idx.get(source_claim_id, []))

    c_by_id = {c["id"]: c for c in claims if c.get("id")}
    v_by_id = {v["id"]: v for v in verdicts}
    afetados = []

    for dep_id in dependentes_ids:
        c = c_by_id.get(dep_id)
        if c is None:
            continue

        antes = {k: c.get(k) for k in ("content", "rationale", "binding")}
        mark_stale(c, source_claim_id)
        depois = {k: c.get(k) for k in ("content", "rationale", "binding")}
        assert antes == depois, "propagação proibida de reescrever a resposta"

        for a in c.get("links") or []:
            if isinstance(a, dict) and a.get("ref") == source_claim_id:
                a["state"] = "review"

        v = v_by_id.setdefault(c["id"], {"id": c["id"]})
        v.setdefault("verification_items", [])
        mark = _REVIEW_MARK.format(ref=source_claim_id)
        if mark not in v["verification_items"]:
            v["verification_items"].append(mark)

        log_event(log_path, "cascade-invalidation", c["id"], source_claim_id, ts)
        afetados.append(c["id"])

    return afetados, list(v_by_id.values())
