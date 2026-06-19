#!/usr/bin/env python3
"""
sobreposicao.py — sobreposição dimensional entre constelações (determinístico).

Um item [VERIFICAR] da constelação-IDEIA pode buscar resposta na constelação-LEI:
procura o claim-lei cujo conteúdo/fonte endereça a dúvida e devolve um de três
resultados — `confirma`, `refuta`, `não-encontrado` — junto com a CONFIABILIDADE,
que é o peso do claim-lei encontrado (claim-lei leve responde "não confie ainda").

REGRA DURA: isto NÃO decide verdade jurídica. Só localiza onde o texto endereça a
dúvida (rastreabilidade) e mede a confiabilidade pela ancoragem (peso). O resultado
`confirma`/`refuta` é uma PISTA de polaridade que um humano confirma — nunca uma
sentença do sistema. O matching é determinístico (sobreposição de termos), nunca LLM.
"""

import re

# Palavras vazias PT (mínimo) — não contam na sobreposição de termos.
_STOP = {
    "a", "o", "as", "os", "um", "uma", "de", "do", "da", "dos", "das", "e", "ou",
    "que", "em", "no", "na", "nos", "nas", "por", "para", "com", "sem", "ao", "aos",
    "à", "às", "se", "su", "seu", "sua", "ser", "é", "the", "of", "quando", "qual",
    "quais", "como", "onde", "pode", "deve", "ja", "já", "the",
}
# Marcadores de negação — usados só para a PISTA de polaridade.
_NEG = {"não", "nao", "fora", "nunca", "jamais", "nem", "exceto", "salvo"}

_LIMIAR = 0.16  # sobreposição mínima (Jaccard) para considerar "encontrado"


def _tokens(texto):
    bruto = re.findall(r"[0-9a-zA-ZÀ-ÿ§]+", (texto or "").lower())
    return [t for t in bruto if t not in _STOP and len(t) > 1]


def _termos(texto):
    return set(_tokens(texto)) - _NEG


def _jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _tem_negacao(texto):
    return bool(set(_tokens(texto)) & _NEG)


def _texto_do_claim(claim):
    f = claim.get("fonte")
    trecho = f.get("trecho", "") if isinstance(f, dict) else ""
    return f"{claim.get('content', '')} {trecho}"


def buscar_resposta(pergunta, claims_lei, pesos_lei, limiar=_LIMIAR):
    """
    pergunta: string do item [VERIFICAR] da constelação-ideia.
    claims_lei: lista de claims-lei (cada um com content e fonte).
    pesos_lei: dict {id: peso} (saída de peso.compute_pesos sobre a constelação-lei).
    Retorna dict:
      {resultado, claim_lei, trecho, confiabilidade, confiavel, nota}
    resultado ∈ {"confirma", "refuta", "não-encontrado"}.
    """
    termos_p = _termos(pergunta)

    melhor, melhor_score = None, 0.0
    for c in claims_lei:
        score = _jaccard(termos_p, _termos(_texto_do_claim(c)))
        if score > melhor_score:
            melhor, melhor_score = c, score

    if melhor is None or melhor_score < limiar:
        return {
            "resultado": "não-encontrado",
            "claim_lei": None,
            "trecho": None,
            "confiabilidade": 0,
            "confiavel": False,
            "nota": "nem a constelação-lei endereça esta dúvida; continua [VERIFICAR] humano.",
        }

    # PISTA de polaridade (não veredito): negação desalinhada => refuta, senão confirma.
    polaridade = "refuta" if (_tem_negacao(pergunta) ^ _tem_negacao(_texto_do_claim(melhor))) else "confirma"
    peso = pesos_lei.get(melhor["id"], 0)
    confiavel = peso > 0
    fonte = melhor.get("fonte") or {}
    nota = (
        "fonte ancorada; pista a confirmar por um humano (o sistema não decide verdade)."
        if confiavel
        else "fonte LEVE (peso ≤ 0) — não confie ainda; trecho não-ancorado ou cheio de dúvida."
    )
    return {
        "resultado": polaridade,
        "claim_lei": melhor["id"],
        "trecho": fonte.get("trecho") if isinstance(fonte, dict) else None,
        "confiabilidade": peso,
        "confiavel": confiavel,
        "nota": nota,
    }
