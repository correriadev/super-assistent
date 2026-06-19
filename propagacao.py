#!/usr/bin/env python3
"""
propagacao.py — propagação de reflutuação entre constelações + log de eventos.

Quando um claim-lei REFLUTUA (uma emenda abre dúvida nele, peso cai), todo claim
de QUALQUER constelação cujo `fonte` aponta para ele (`fonte.ref == <id-lei>`)
também reflutua. A perda de peso atravessa a fronteira da constelação.

REGRA DURA: a propagação ABRE CICATRIZ (invalida, marca "reveja") e REABRE a
dúvida (para o peso cair) — NUNCA reescreve a resposta. Reescrever seria
interpretação jurídica automática, proibida. Cada dono de domínio re-resolve à mão.

Log de eventos append-only (JSONL, não event-sourcing completo, não banco):
cada evento = {ts, tipo, claim, causa}. O "diff entre versões" é a lista de
eventos entre dois marcos (eventos_entre), não diff de linha. Git versiona os arquivos.
"""

import datetime
import json


def _agora():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def registrar_evento(log_path, tipo, claim, causa, ts=None):
    """Anexa um evento ao log append-only. Retorna o evento."""
    ev = {"ts": ts or _agora(), "tipo": tipo, "claim": claim, "causa": causa}
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    return ev


def ler_eventos(log_path):
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            return [json.loads(linha) for linha in f if linha.strip()]
    except FileNotFoundError:
        return []


def eventos_entre(log_path, desde=None, ate=None):
    """O 'diff' entre dois marcos: a lista de eventos no intervalo [desde, ate]."""
    evs = ler_eventos(log_path)
    return [
        e for e in evs
        if (desde is None or e["ts"] >= desde) and (ate is None or e["ts"] <= ate)
    ]


def depende_de(claim, claim_lei_id):
    """Claim depende de um claim-lei se seu `fonte` aponta para ele via `ref`."""
    f = claim.get("fonte")
    return isinstance(f, dict) and f.get("ref") == claim_lei_id


def abrir_cicatriz(claim, claim_lei_id):
    """Marca o claim como 'reveja' SEM tocar na resposta. Idempotente."""
    claim["cicatriz"] = {
        "estado": "reveja",
        "fonte": claim_lei_id,
        "motivo": "fonte reflutuou; re-resolver à mão (sistema não reescreve)",
    }
    return claim


_MARCA_REVEJA = "[REVEJA] fonte {ref} reflutuou — re-resolver à mão"


def propagar(claim_lei_id, claims, vereditos, log_path, ts=None):
    """
    Propaga a reflutuação de `claim_lei_id` para os claims dependentes.
    claims/vereditos: listas de UMA constelação (chame uma vez por constelação).
    Para cada claim dependente: abre cicatriz + reabre dúvida (peso cai) + loga evento.
    NUNCA reescreve content/justificativa/resposta.
    Retorna (ids_afetados, vereditos_atualizados).
    """
    ver_by_id = {v["id"]: v for v in vereditos}
    afetados = []
    for c in claims:
        if not depende_de(c, claim_lei_id):
            continue
        # HARD RULE: a resposta não muda. Guardamos o antes e conferimos depois.
        antes = {k: c.get(k) for k in ("content", "justificativa", "binding")}
        abrir_cicatriz(c, claim_lei_id)
        depois = {k: c.get(k) for k in ("content", "justificativa", "binding")}
        assert antes == depois, "propagação proibida de reescrever a resposta"

        v = ver_by_id.setdefault(c["id"], {"id": c["id"]})
        v.setdefault("itens_verificar", [])
        marca = _MARCA_REVEJA.format(ref=claim_lei_id)
        if marca not in v["itens_verificar"]:
            v["itens_verificar"].append(marca)  # reabre dúvida REAL -> peso cai

        registrar_evento(log_path, "reflutuacao-propagada", c["id"], claim_lei_id, ts)
        afetados.append(c["id"])

    return afetados, list(ver_by_id.values())
