"""Árvore de decisão do cross-graph linking (resolution.py). Sem LLM."""

from resolution import resolve_verification_item, OUTCOMES

SRC = [{"id": "art47",
        "content": "o art. 47 condiciona o crédito do adquirente à extinção do tributo",
        "provenance": {"document": "LC 214", "excerpt": "o crédito do adquirente à extinção do tributo"}}]
DOMAINS = {"lei": {"claims": SRC, "scores": {"art47": 10}}}


def _item(text, domain="lei"):
    return {"text": text, "domain": domain, "critical": True}


def test_no_domain_quando_sem_endereco():
    r = resolve_verification_item(_item("qualquer coisa", domain=None), DOMAINS)
    assert r["outcome"] == "no-domain" and r["system_decided"] is False


def test_no_domain_quando_dominio_inexistente():
    r = resolve_verification_item(_item("x", domain="financeiro"), DOMAINS)
    assert r["outcome"] == "no-domain"


def test_found_strong_quando_fonte_grounded():
    r = resolve_verification_item(
        _item("o art. 47 condiciona o crédito do adquirente à extinção do tributo?"), DOMAINS)
    assert r["outcome"] == "found-strong"
    assert r["result"] == "confirms"
    assert r["source_claim"] == "art47"
    assert r["confidence"] == 10
    assert r["system_decided"] is False


def test_found_weak_quando_fonte_leve():
    domains = {"lei": {"claims": SRC, "scores": {"art47": 0}}}  # fonte não-ancorada/leve
    r = resolve_verification_item(
        _item("o art. 47 condiciona o crédito do adquirente à extinção do tributo?"), domains)
    assert r["outcome"] == "found-weak" and "não confie ainda" in r["note"]


def test_not_found_quando_nenhum_no_responde():
    r = resolve_verification_item(_item("qual a paleta de cores da interface?"), DOMAINS)
    assert r["outcome"] == "not-found"


def test_hook_lazy_decompose_e_chamado_no_not_found():
    chamadas = []

    def hook(item, entry):
        chamadas.append(item)
        # simula decompor a seção e achar resposta
        return {"result": "confirms", "source_claim": "novo", "excerpt": "trecho",
                "confidence": 10, "reliable": True, "note": "decomposto on-demand"}

    r = resolve_verification_item(_item("algo fora do grafo atual"), DOMAINS, on_not_found=hook)
    assert chamadas, "hook deveria ter sido chamado no not-found"
    assert r["outcome"] == "found-strong" and r["source_claim"] == "novo"


def test_todo_desfecho_volta_ao_usuario():
    for item in [_item("x", domain=None), _item("paleta de cores?"),
                 _item("o art. 47 condiciona o crédito à extinção?")]:
        r = resolve_verification_item(item, DOMAINS)
        assert r["system_decided"] is False and r["action_required"] is True
        assert r["outcome"] in OUTCOMES
