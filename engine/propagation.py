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
    claims/verdicts: listas de UM graph (chame uma vez por graph).
    Para cada dependente: marca stale + reabre dúvida (score cai) + loga evento.
    NUNCA reescreve content/rationale/resposta.
    Retorna (ids_afetados, verdicts_atualizados).
    """
    v_by_id = {v["id"]: v for v in verdicts}
    afetados = []
    for c in claims:
        if not depends_on(c, source_claim_id):
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
