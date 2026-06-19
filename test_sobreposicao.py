"""Suíte pytest da sobreposição dimensional ideia↔lei (sobreposicao.py). Sem LLM."""

import json
from peso import compute_pesos
from sobreposicao import buscar_resposta

DOC = open("ideias/pub_780677977.txt", encoding="utf-8").read()
CLAIMS_LEI = json.load(
    open("projetos/02-simulador-caixa-split/dados/claims-lei.json", encoding="utf-8")
)
PESOS_LEI = compute_pesos(CLAIMS_LEI, [], doc_text=DOC)  # todos ancorados -> 10


def test_confirma_com_fonte_ancorada():
    """[VERIFICAR] da ideia encontra resposta confirmatória ancorada na lei."""
    pergunta = "O art. 47 condiciona o direito ao crédito do adquirente à extinção do tributo?"
    r = buscar_resposta(pergunta, CLAIMS_LEI, PESOS_LEI)
    assert r["resultado"] == "confirma"
    assert r["claim_lei"] == "art-47-condicao-extincao-tributo"
    assert r["confiabilidade"] == 10
    assert r["confiavel"] is True
    assert r["trecho"]  # devolve o trecho-fonte ancorado


def test_refuta_quando_negacao_desalinha():
    """Fonte que nega o que a pergunta afirma -> pista 'refuta'."""
    claims = [{
        "id": "lei-credito-independe-fornecedor",
        "content": "o texto diz que o crédito não depende da conduta do fornecedor",
        "fonte": {"documento": "X", "trecho": "o crédito não depende da conduta do fornecedor"},
    }]
    pesos = {"lei-credito-independe-fornecedor": 10}
    pergunta = "o crédito depende da conduta do fornecedor?"
    r = buscar_resposta(pergunta, claims, pesos)
    assert r["resultado"] == "refuta"
    assert r["claim_lei"] == "lei-credito-independe-fornecedor"


def test_nao_encontrado_quando_lei_nao_enderaca():
    """Dúvida que a constelação-lei não cobre -> não-encontrado, continua [VERIFICAR]."""
    pergunta = "Qual a paleta de cores da interface do simulador para o cliente?"
    r = buscar_resposta(pergunta, CLAIMS_LEI, PESOS_LEI)
    assert r["resultado"] == "não-encontrado"
    assert r["claim_lei"] is None
    assert r["confiavel"] is False


def test_fonte_leve_responde_nao_confie_ainda():
    """Claim-lei leve (peso <= 0) responde, mas marca baixa confiabilidade."""
    claims = [{
        "id": "lei-leve",
        "content": "o art. 47 condiciona o crédito do adquirente à extinção do tributo",
        "fonte": {"documento": "X", "trecho": "trecho-inventado-que-nao-existe-no-doc"},
    }]
    pesos = {"lei-leve": 0}  # não-ancorado -> leve
    pergunta = "o art. 47 condiciona o crédito do adquirente à extinção do tributo?"
    r = buscar_resposta(pergunta, claims, pesos)
    assert r["claim_lei"] == "lei-leve"
    assert r["confiavel"] is False
    assert "não confie ainda" in r["nota"]
