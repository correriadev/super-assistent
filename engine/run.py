"""Runner do beta-tester: roda a cadeia determinística sobre projetos/NN/ e reporta.
Uso: python3 -m engine.run projetos/02-simulador-caixa-split"""
import json
import os
import sys
from engine.contract import validate_claims, validate_verdicts, ContractError
from engine.score import compute_scores as score_claims


def _load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_project(proj_dir):
    dados = os.path.join(proj_dir, "dados")
    claims = _load(os.path.join(dados, "claims.json"))
    verdicts = _load(os.path.join(dados, "verdicts.json"))
    rep = {"contract_ok": True, "contract_error": None, "scores": {}}
    try:
        validate_claims(claims)
        validate_verdicts(verdicts)
    except ContractError as e:
        rep["contract_ok"] = False
        rep["contract_error"] = str(e)
        return rep
    rep["scores"] = score_claims(claims, verdicts)
    return rep


if __name__ == "__main__":
    r = run_project(sys.argv[1])
    print(json.dumps(r, ensure_ascii=False, indent=2))
