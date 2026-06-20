#!/usr/bin/env python3
"""
resolution.py — orquestra a resolução de um verification_item entre graphs (README §12).

Determinístico, sem LLM. Implementa a árvore de decisão do cross-graph linking:

    verification_item (com domain)
    │
    1. existe domínio próprio (source graph p/ esse domain)?
    │   ├── NÃO → outcome "no-domain"  (devolve ao usuário: responder à mão ou ingerir doc)
    │   └── SIM ↓
    2. procura nos nós (linking.resolve_link)
    │   ├── not-found ↓
    │   │     2a. hook on_not_found (lazy-decompose / RAG navegação) — ÚNICO ponto
    │   │         que pode usar LLM no futuro; default não faz nada
    │   │     └── ainda not-found → outcome "not-found"
    │   └── found → confidence pelo score do nó-fonte:
    │         ├── reliable (score > 0) → outcome "found-strong"  (pista confirms/refutes + excerpt)
    │         └── leve (score ≤ 0)     → outcome "found-weak"    ("não confie ainda")

REGRA DURA: o sistema NUNCA fecha a dúvida. Todo desfecho volta ao usuário
(`system_decided: False`). confirms/refutes é pista, não veredito.
"""

import json

from linking import resolve_link, domain_of, item_text

OUTCOMES = ("no-domain", "not-found", "ambiguous", "found-weak", "found-strong")


def _to_user(outcome, item, **payload):
    out = {
        "outcome": outcome,
        "system_decided": False,   # invariante: o sistema nunca decide
        "action_required": True,
        "item": item_text(item),
    }
    out.update(payload)
    return out


def resolve_verification_item(item, domains, on_not_found=None, embed_fn=None):
    """
    item: verification_item objeto {text, domain, critical} (ou string legada).
    domains: dict {domain_name: {"claims": [...], "scores": {id: score}}}.
    on_not_found: hook opcional p/ lazy-decompose dirigido pela dúvida (passo 2a).
                  Recebe (item, domain_entry); devolve uma resolução estilo
                  resolve_link (com novo "claims"/"scores" já decompostos) ou None.
                  É o ÚNICO ponto que pode usar RAG/LLM no futuro. Default: None.
    Retorna um dict 'to_user' com outcome ∈ OUTCOMES. NUNCA fecha a dúvida.
    """
    domain = domain_of(item)

    # passo 1 — existe domínio próprio? (registrado conta, mesmo com grafo vazio:
    # um grafo esparso é resolvido pelo lazy-decompose no passo 2a, não é "no-domain")
    entry = domains.get(domain) if domain else None
    if entry is None:
        return _to_user(
            "no-domain", item, domain=domain,
            suggestion="responda à mão OU autorize ingerir um documento deste domínio",
        )

    # passo 2 — procura nos nós (semântico se embed_fn dado)
    r = resolve_link(item, entry["claims"], entry.get("scores", {}), embed_fn=embed_fn)

    # passo 2a — hook de lazy-decompose (navegação RAG), se fornecido
    if r["result"] == "not-found" and on_not_found is not None:
        r2 = on_not_found(item, entry)
        if r2 and r2.get("result") != "not-found":
            r = r2

    if r["result"] == "not-found":
        return _to_user(
            "not-found", item, domain=domain,
            suggestion="nem a fonte deste domínio resolve; responda à mão ou decomponha a seção relevante",
        )

    # empate — dois claims-fonte quase iguais; o humano escolhe qual responde
    if r["result"] == "ambiguous":
        return _to_user(
            "ambiguous", item, domain=domain,
            candidates=r["candidates"],
            suggestion="dois trechos-fonte empatam; escolha qual responde (o sistema não decide qual)",
            note=r["note"],
        )

    # found — confidence pelo score do nó-fonte
    outcome = "found-strong" if r.get("reliable") else "found-weak"
    return _to_user(
        outcome, item, domain=domain,
        result=r["result"],                 # confirms | refutes (PISTA, não veredito)
        source_claim=r["source_claim"],
        excerpt=r.get("excerpt"),
        confidence=r["confidence"],
        note=r["note"],
    )


def attach_candidates(item, resolution):
    """Carimba os candidatos de um match AMBÍGUO no próprio verification_item (slot
    `candidates`) — a superfície que o humano lê p/ escolher entre os trechos em conflito.

    O item segue ABERTO (a dúvida não fechou; o sistema não decide qual responde). Se a
    resolução não é ambígua, limpa qualquer `candidates` antigo. Retorna True se carimbou.
    """
    if resolution.get("result") != "ambiguous":
        item.pop("candidates", None)
        return False
    item["candidates"] = resolution["candidates"]
    return True


def make_lazy_decompose(decompose_fn, embed_fn=None, nav_floor=0.16):
    """Fábrica do hook `on_not_found` (passo 2a, README §12) — lazy decompose dirigido
    pela dúvida. Plumbing determinístico + UMA chamada LLM injetada (`decompose_fn`).

    decompose_fn(secao_texto) -> lista de novos claims-fonte (extractor modo legal).
                                 É o ÚNICO ponto que usa LLM. Injetado p/ manter testável.
    embed_fn: se dado, navegação semântica (embeddings); senão, lexical (grátis).
    nav_floor: piso de score da navegação — abaixo dele NÃO decompõe (poupa a chamada
               num palpite fraco). Escala difere entre lexical (jaccard) e cosseno;
               ajuste conforme o ranqueador injetado.

    Retorna um hook(item, entry) compatível com `resolve_verification_item`.
    entry precisa carregar `doc_text`. Mantém `entry["decomposed"]` como ledger
    anti-bomba: nunca re-decompõe a mesma seção.
    """
    from score import compute_scores
    from retrieval import retrieve

    def hook(item, entry):
        doc = entry.get("doc_text")
        if not doc:
            return None
        ranked = retrieve(item, doc, embed_fn=embed_fn, top_k=1)
        if not ranked:
            return None
        nav_score, chunk = ranked[0]
        if nav_score < nav_floor:
            return None  # navegação fraca: não decompõe no chute
        if chunk["id"] in entry.get("decomposed", []):
            return None  # já decomposto: o not-found é real, não re-gasta token

        new_claims = decompose_fn(chunk["text"])  # ← LLM na borda (extractor)
        if not new_claims:
            return None

        entry.setdefault("decomposed", []).append(chunk["id"])
        entry["claims"] = entry["claims"] + new_claims
        entry["scores"] = compute_scores(entry["claims"], [], doc_text=doc)
        return resolve_link(item, entry["claims"], entry["scores"])

    return hook


def load_domains(mapping):
    """Helper: monta o dict `domains` a partir de arquivos.
    mapping: {domain: {"claims_path": ..., "doc_path": ...(opcional), "verdicts": [...](opcional)}}.
    Calcula o score de cada source graph (grounding se houver doc_path)."""
    from score import compute_scores
    out = {}
    for dom, m in mapping.items():
        claims = json.load(open(m["claims_path"], encoding="utf-8"))
        doc = open(m["doc_path"], encoding="utf-8").read() if m.get("doc_path") else None
        scores = compute_scores(claims, m.get("verdicts", []), doc_text=doc)
        out[dom] = {"claims": claims, "scores": scores}
    return out
