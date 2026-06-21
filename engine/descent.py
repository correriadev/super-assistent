#!/usr/bin/env python3
"""descent.py — gate parametrizável de descida entre níveis + marca provisional.

A pré-condição "só desce sobre claim RESOLVIDO" (orchestrator §8), na forma binária
(tudo-resolvido-ou-pare), é sentida como burocracia. Aqui ela vira uma POLÍTICA: a
descida continua sob comando humano, mas o que ela PERMITE e o que ela MARCA muda com
`descent_policy`. Em vez de bloquear, descer sobre fundação aberta gera filho
`provisional` (cicatriz, espelho do `stale`); o filho herda o score baixo do pai via
`derives_from` (score.py já faz) — flutua, visível, em vez de travar o movimento.

Determinístico, sem LLM. NÃO decide verdade nem assenta claim — só decide se o gate
abre e carimba quem nasce sobre chão mole, para a propagação reabrir depois.

Chão absoluto: `CONTRADIZ-NIVEL-ACIMA` NUNCA é furado por nenhuma política (nem por
aceite humano) — filho que contradiz o pai é incoerência, não burocracia.
"""

HARD_BLOCK = "CONTRADIZ-NIVEL-ACIMA"  # nunca bypassável
POLICIES = ("strict", "vinculante_only", "threshold", "provisional", "force")


def is_resolved(verdict, accepted=()):
    """Resolvido = status PASSA, ou o humano aceitou explicitamente apesar do flag
    (`verdict["accepted"]` truthy, ou id em `accepted`). CONTRADIZ nunca conta como
    resolvido — só sai por re-resolução real, jamais por aceite."""
    st = verdict.get("status")
    if st == HARD_BLOCK:
        return False
    if st == "PASSA":
        return True
    return bool(verdict.get("accepted")) or verdict.get("id") in accepted


def open_claims(claims, verdicts, accepted=()):
    """Ids dos claims ainda abertos (não resolvidos). Claim sem veredito conta aberto."""
    vby = {v["id"]: v for v in verdicts}
    return [c["id"] for c in claims
            if not is_resolved(vby.get(c["id"], {"id": c["id"]}), accepted)]


def _decision(allowed, policy, blocked_by, provisional_parents, frac, reason):
    return {
        "allowed": allowed,
        "policy": policy,
        "blocked_by": blocked_by,                 # ids que impedem a descida (vazio se allowed)
        "provisional_parents": provisional_parents,  # pais abertos cujos filhos nascem provisional
        "resolved_fraction": round(frac, 3),
        "reason": reason,
    }


def descent_gate(claims, verdicts, policy="strict", min_fraction=0.6, accepted=()):
    """Decide se pode descer e o que marcar, conforme a `policy`.

    strict          — todos resolvidos ou pára (comportamento histórico).
    vinculante_only — bloqueia só `vinculante` aberto (ilustrativo/default passam).
    threshold       — desce se fração resolvida ≥ `min_fraction`.
    provisional     — sempre desce; pais abertos viram `provisional_parents`.
    force           — sempre desce, sem marca (escape hatch).

    `CONTRADIZ-NIVEL-ACIMA` aberto bloqueia em QUALQUER política.
    Retorna o dict de `_decision`.
    """
    if policy not in POLICIES:
        raise ValueError(f"policy desconhecida: {policy} (use {POLICIES})")
    vby = {v["id"]: v for v in verdicts}
    opens = open_claims(claims, verdicts, accepted)
    frac = 1.0 - len(opens) / len(claims) if claims else 1.0

    # chão absoluto
    contradiz = [c["id"] for c in claims if vby.get(c["id"], {}).get("status") == HARD_BLOCK]
    if contradiz:
        return _decision(False, policy, contradiz, [], frac,
                         "CONTRADIZ-NIVEL-ACIMA aberto — incoerência; nenhuma política fura")

    if policy == "strict":
        return _decision(not opens, policy, opens, [], frac,
                         "todos resolvidos" if not opens else "há claim aberto")
    if policy == "vinculante_only":
        cby = {c["id"]: c for c in claims}
        block = [cid for cid in opens if cby[cid].get("binding") == "vinculante"]
        return _decision(not block, policy, block, opens, frac,
                         "sem vinculante aberto" if not block else "vinculante aberto bloqueia")
    if policy == "threshold":
        ok = frac >= min_fraction
        return _decision(ok, policy, [] if ok else opens, opens, frac,
                         f"fração resolvida {frac:.2f} {'≥' if ok else '<'} {min_fraction}")
    if policy == "provisional":
        return _decision(True, policy, [], opens, frac,
                         "desce; filhos de pai aberto nascem provisional (cicatriz rastreada)")
    # force
    return _decision(True, policy, [], [], frac, "force: desce sem marca (escape hatch)")


def mark_provisional(child, provisional_parents):
    """Carimba `provisional` num claim-filho se algum `derives_from` cai em pai aberto.
    Espelho do `stale`: state review + os pais não-assentados. Se nenhum pai do filho
    está aberto, LIMPA marca antiga (pai resolveu → filho vira claim normal). Idempotente.
    Retorna True se ficou provisional."""
    unresolved = sorted(set(child.get("derives_from") or []) & set(provisional_parents))
    if not unresolved:
        child.pop("provisional", None)
        return False
    child["provisional"] = {
        "state": "review",
        "parents": unresolved,
        "reason": "desceu sobre fundação aberta; reabre se o pai mudar (o sistema não assenta por você)",
    }
    return True


def refresh_provisional(children, provisional_parents):
    """Propagação fiada na descida, TRANSITIVA: um filho é provisional se algum ancestral
    via `derives_from` é pai aberto OU é outro filho provisional. Pega cadeias multi-nível
    (filho de irmão provisional), não só a primeira geração — a cicatriz não para na
    primeira camada. Topológico, como a herança de score. Reabre/limpa conforme o estado
    ATUAL dos pais. Retorna os ids ainda provisional."""
    open_set = set(provisional_parents)
    by_id = {c["id"]: c for c in children}
    memo = {}

    def offenders(cid, stack):
        """Refs diretas que sujam `cid`: pai aberto, ou irmão-filho ele mesmo provisional."""
        if cid in memo:
            return memo[cid]
        if cid in stack:               # ciclo defensivo
            return []
        c = by_id.get(cid)
        if c is None:                  # ancestral fora dos filhos = pai de nível acima
            return []
        bad = []
        for p in c.get("derives_from") or []:
            if p in open_set or (p in by_id and offenders(p, stack | {cid})):
                bad.append(p)
        memo[cid] = bad
        return bad

    out = []
    for c in children:
        bad = offenders(c["id"], set())
        if bad:
            c["provisional"] = {
                "state": "review",
                "parents": sorted(set(bad)),
                "reason": "desceu sobre fundação aberta (direta ou herdada de ancestral); reabre se o ancestral mudar",
            }
            out.append(c["id"])
        else:
            c.pop("provisional", None)
    return out
