#!/usr/bin/env python3
"""
linking.py — cross-graph link resolution (determinístico).

Um verification_item do IDEA GRAPH pode buscar resposta no SOURCE GRAPH: procura o
claim-fonte cujo conteúdo/provenance endereça a dúvida e devolve um de três
resultados — `confirms`, `refutes`, `not-found` — com a CONFIDENCE, que é o score do
claim-fonte encontrado (fonte leve responde "não confie ainda").

REGRA DURA: isto NÃO decide verdade. Só localiza onde o texto endereça a dúvida
(rastreabilidade) e mede confiança pelo grounding (score). `confirms`/`refutes` é
PISTA de polaridade que um humano confirma — nunca sentença do sistema. Matching
determinístico (sobreposição de termos), nunca LLM.
"""

import re

_STOP = {
    "a", "o", "as", "os", "um", "uma", "de", "do", "da", "dos", "das", "e", "ou",
    "que", "em", "no", "na", "nos", "nas", "por", "para", "com", "sem", "ao", "aos",
    "à", "às", "se", "seu", "sua", "ser", "é", "the", "of", "quando", "qual",
    "quais", "como", "onde", "pode", "deve", "já",
}
_NEG = {"não", "nao", "fora", "nunca", "jamais", "nem", "exceto", "salvo"}

_THRESHOLD = 0.16  # sobreposição mínima (Jaccard) para considerar "encontrado"


def _tokens(texto):
    bruto = re.findall(r"[0-9a-zA-ZÀ-ÿ§]+", (texto or "").lower())
    return [t for t in bruto if t not in _STOP and len(t) > 1]


def _terms(texto):
    return set(_tokens(texto)) - _NEG


def _jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _has_negation(texto):
    return bool(set(_tokens(texto)) & _NEG)


def _claim_text(claim):
    p = claim.get("provenance")
    excerpt = p.get("excerpt", "") if isinstance(p, dict) else ""
    return f"{claim.get('content', '')} {excerpt}"


def item_text(item):
    """Texto de um verification_item: string (legado) ou objeto {text, domain, critical}."""
    if isinstance(item, dict):
        return item.get("text", "")
    return item if isinstance(item, str) else ""


def domain_of(item):
    """Endereço de domínio de um verification_item (forma A). String legada -> None.
    É o que o passo 1 ('existe domínio próprio?') lê para saber onde procurar."""
    return item.get("domain") if isinstance(item, dict) else None


def resolve_link(question, source_claims, source_scores, threshold=_THRESHOLD):
    """
    question: string do verification_item do idea graph.
    source_claims: lista de claims do source graph (content + provenance).
    source_scores: dict {id: score} (saída de score.compute_scores no source graph).
    Retorna dict {result, source_claim, excerpt, confidence, reliable, note}.
    result ∈ {"confirms", "refutes", "not-found"}.
    `question` aceita string ou um verification_item objeto (usa o .text).
    """
    question = item_text(question) if isinstance(question, dict) else question
    q_terms = _terms(question)

    best, best_score = None, 0.0
    for c in source_claims:
        s = _jaccard(q_terms, _terms(_claim_text(c)))
        if s > best_score:
            best, best_score = c, s

    if best is None or best_score < threshold:
        return {
            "result": "not-found",
            "source_claim": None,
            "excerpt": None,
            "confidence": 0,
            "reliable": False,
            "note": "nem o source graph endereça esta dúvida; segue verification_item humano.",
        }

    polarity = "refutes" if (_has_negation(question) ^ _has_negation(_claim_text(best))) else "confirms"
    sc = source_scores.get(best["id"], 0)
    reliable = sc > 0
    prov = best.get("provenance") or {}
    note = (
        "fonte grounded; pista a confirmar por um humano (o sistema não decide verdade)."
        if reliable
        else "fonte LEVE (score ≤ 0) — não confie ainda; excerpt não-grounded ou cheio de dúvida."
    )
    return {
        "result": polarity,
        "source_claim": best["id"],
        "excerpt": prov.get("excerpt") if isinstance(prov, dict) else None,
        "confidence": sc,
        "reliable": reliable,
        "note": note,
    }


def link_claim(idea_claim, question, resolution):
    """Persiste um match de `resolve_link` como LINK no claim do idea graph — a ponte
    cross-graph que encosta no disco.

    `provenance` = origem (intocada: "human decision"). `links` = pontes para outros
    graphs; é o que `propagation.depends_on` lê. Só linka `confirms`/`refutes`
    (`not-found` não cria elo). Idempotente por (ref, question).
    Retorna o link gravado, ou None.
    """
    if resolution.get("result") not in ("confirms", "refutes"):
        return None
    novo = {
        "graph": "source",
        "ref": resolution["source_claim"],
        "question": question,
        "result": resolution["result"],
        "confidence": resolution["confidence"],
        "excerpt": resolution.get("excerpt"),
    }
    links = idea_claim.setdefault("links", [])
    for a in links:
        if a.get("ref") == novo["ref"] and a.get("question") == question:
            a.update(novo)
            return a
    links.append(novo)
    return novo
