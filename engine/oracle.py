"""Tag de oráculo: qual oráculo fecha a dúvida de um claim. DERIVADA dos sinais que já
existem (provenance + verdict), não armazenada — o claim não ganha campo. Três tipos
(o garfo fato/estrutura/decisão): worldly (dúvida factual aberta -> fonte/humano),
structural (status não-passa ou structural_gaps -> julgamento), decision (axioma humano
assentado -> sem oráculo). Precedência: worldly > structural > decision."""

WORLDLY, STRUCTURAL, DECISION = "worldly", "structural", "decision"
_OPEN_STRUCTURAL_STATUS = {"PRECISA-JUSTIFICAR", "INCOMPLETO", "CONTESTADO", "CONTRADIZ-NIVEL-ACIMA"}


def _is_human_decision(claim):
    p = claim.get("provenance")
    return p == "human decision" or not isinstance(p, dict)


def oracle_of(claim, verdict):
    if verdict.get("verification_items"):
        return WORLDLY
    if verdict.get("status") in _OPEN_STRUCTURAL_STATUS or verdict.get("structural_gaps"):
        return STRUCTURAL
    if _is_human_decision(claim):
        return DECISION
    return STRUCTURAL


def oracle_mix(claims, verdicts):
    """{worldly, structural, decision} -> contagem, sobre claims×verdicts casados por id."""
    vby = {v["id"]: v for v in verdicts}
    mix = {WORLDLY: 0, STRUCTURAL: 0, DECISION: 0}
    for c in claims:
        v = vby.get(c["id"])
        if v is not None:
            mix[oracle_of(c, v)] += 1
    return mix
