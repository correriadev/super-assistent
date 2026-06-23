"""Contrato LLM↔código. Valida o shape + vocabulário fechado dos JSON que o motor
consome. Falha-alto (ContractError), nunca silencioso — o LLM erra a forma, aqui pega.
Sem schema-framework: validação à mão, stdlib só."""

SIX_STATUS = {
    "CONTRADIZ-NIVEL-ACIMA", "PRECISA-JUSTIFICAR", "INCOMPLETO",
    "PENDENTE-VERIFICAÇÃO", "CONTESTADO", "PASSA",
}
BINDINGS = {"vinculante", "ilustrativo", "default-sobrescrevivel"}
DOMAINS = {"lei", "engenharia", "financeiro", None}


class ContractError(ValueError):
    pass


def _require(cond, msg):
    if not cond:
        raise ContractError(msg)


def validate_claim(c):
    _require(isinstance(c.get("id"), str) and c["id"], f"claim sem id válido: {c!r}")
    _require(isinstance(c.get("content"), str), f"claim {c['id']}: content ausente")
    _require(c.get("binding") in BINDINGS,
             f"claim {c['id']}: binding inválido {c.get('binding')!r}")
    _require("links" in c and isinstance(c["links"], list),
             f"claim {c['id']}: links deve ser lista")
    return c


def validate_verdict(v):
    cid = v.get("id")
    _require(isinstance(cid, str) and cid, f"verdict sem id válido: {v!r}")
    _require(v.get("status") in SIX_STATUS,
             f"verdict {cid}: status fora dos seis: {v.get('status')!r}")
    _require(isinstance(v.get("structural_gaps"), list), f"verdict {cid}: structural_gaps")
    items = v.get("verification_items")
    _require(isinstance(items, list), f"verdict {cid}: verification_items deve ser lista")
    for it in items:
        _require(isinstance(it.get("text"), str), f"verdict {cid}: item sem text")
        _require(it.get("domain") in DOMAINS, f"verdict {cid}: domain inválido {it.get('domain')!r}")
        _require(isinstance(it.get("critical"), bool), f"verdict {cid}: critical deve ser bool")
        for cand in it.get("candidates", []):
            _require(isinstance(cand.get("source_claim"), str), f"verdict {cid}: candidate sem source_claim")
            _require(isinstance(cand.get("excerpt"), str), f"verdict {cid}: candidate sem excerpt")
            _require(isinstance(cand.get("confidence"), (int, float)),
                     f"verdict {cid}: candidate confidence deve ser numérica")
    if v["status"] == "PRECISA-JUSTIFICAR":
        _require(isinstance(v.get("elicitation_question"), str) and v["elicitation_question"],
                 f"verdict {cid}: elicitation_question obrigatória em PRECISA-JUSTIFICAR")
    if v["status"] == "CONTRADIZ-NIVEL-ACIMA":
        _require(v.get("contradiction"), f"verdict {cid}: contradiction obrigatória em CONTRADIZ")
    return v


def validate_claims(claims):
    for c in claims:
        validate_claim(c)
    return claims


def validate_verdicts(verdicts):
    for v in verdicts:
        validate_verdict(v)
    return verdicts
