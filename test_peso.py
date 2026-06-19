"""Suíte pytest do cálculo determinístico de peso (peso.py). Sem LLM."""

from peso import compute_pesos, PESO_BASE, relatorio_ancoragem


def test_passa_so_nao_bloqueante_fica_positivo():
    """Caso 1: claim PASSA com só itens '(não bloqueante)' -> peso positivo (~10)."""
    claims = [{"id": "nome-split"}]
    vereditos = [
        {
            "id": "nome-split",
            "lacunas_estruturais": [],
            "itens_verificar": [
                "(não bloqueante) 'Split' disponível como marca no INPI?",
                "(não bloqueante) 'Split' é distintivo ou genérico demais?",
            ],
        }
    ]
    p = compute_pesos(claims, vereditos)
    assert p["nome-split"] == PESO_BASE  # 10 — não-bloqueantes não derrubam


def test_seis_duvidas_reais_da_quatro():
    """Caso 2: claim com 6 dúvidas reais -> peso = 10 - 6 = 4."""
    claims = [{"id": "c"}]
    vereditos = [
        {
            "id": "c",
            "lacunas_estruturais": ["l1", "l2", "l3"],
            "itens_verificar": ["v1", "v2", "v3"],
        }
    ]
    p = compute_pesos(claims, vereditos)
    assert p["c"] == 4


def test_resolver_duvida_sobe_peso():
    """Caso 3: marcar uma dúvida como resolvida -> peso sobe."""
    claims = [{"id": "c"}]
    antes = compute_pesos(
        claims, [{"id": "c", "itens_verificar": ["v1", "v2", "v3"]}]
    )
    depois = compute_pesos(
        claims,
        [{"id": "c", "itens_verificar": ["v1", "v2"], "itens_verificados": ["v3"]}],
    )
    assert antes["c"] == 7          # 10 - 3
    assert depois["c"] == 9         # 10 - 2 + 1
    assert depois["c"] > antes["c"]  # fechar dúvida sobe o peso


def test_filho_herda_pai_e_propaga_queda():
    """Caso 4: derivado herda peso do pai; abrir dúvida no pai derruba pai e filho."""
    claims = [{"id": "P"}, {"id": "C", "deriva_de": ["P"]}]

    # baseline: pai sem dúvida (10), filho herda -> 10 + 10 = 20
    base = compute_pesos(claims, [{"id": "P"}, {"id": "C"}])
    assert base["P"] == 10
    assert base["C"] == 20  # nasce com o peso do pai somado à própria base, não do zero

    # abrir 1 dúvida real no pai -> pai cai e filho cai junto (propagação)
    comdiv = compute_pesos(
        claims, [{"id": "P", "itens_verificar": ["fato"]}, {"id": "C"}]
    )
    assert comdiv["P"] == 9
    assert comdiv["C"] == 19
    assert comdiv["P"] < base["P"]
    assert comdiv["C"] < base["C"]  # a queda do pai propagou para o filho


def test_guarda_de_ciclo():
    """Ciclo em deriva_de é detectado, não trava."""
    import pytest

    with pytest.raises(ValueError):
        compute_pesos(
            [{"id": "A", "deriva_de": ["B"]}, {"id": "B", "deriva_de": ["A"]}],
            [{"id": "A"}, {"id": "B"}],
        )


# ───────────────────────── FASE 2 — constelação-lei / ancoragem ─────────────────────────

DOC_LEI = (
    "Art. 31. Os prestadores de serviços de pagamento devem segregar e recolher "
    "o IBS e a CBS no momento da liquidação financeira da operação. "
    "Art. 47. O direito ao crédito do adquirente somente pode ser exercido quando "
    "ocorrida a extinção do tributo por qualquer das modalidades do art. 27."
)


def test_lei_nasce_leve_sem_ancoragem():
    """Claim-lei cujo trecho NÃO está no documento nasce leve (peso 0)."""
    claims = [{
        "id": "lei-inventada",
        "fonte": {"documento": "LC 214/2025", "trecho": "o split é facultativo para todos"},
    }]
    p = compute_pesos(claims, [{"id": "lei-inventada"}], doc_text=DOC_LEI)
    assert p["lei-inventada"] == 0  # interpretação não-confirmada não pesa


def test_lei_ganha_peso_por_ancoragem_real():
    """Claim-lei com trecho literalmente presente no documento ganha peso (ancoragem)."""
    claims = [{
        "id": "lei-split-liquidacao",
        "fonte": {
            "documento": "LC 214/2025",
            "trecho": "segregar e recolher o IBS e a CBS no momento da liquidação financeira",
        },
    }]
    p = compute_pesos(claims, [{"id": "lei-split-liquidacao"}], doc_text=DOC_LEI)
    assert p["lei-split-liquidacao"] == 10  # 0 base-lei + 10 ancoragem
    assert relatorio_ancoragem(claims, DOC_LEI)["lei-split-liquidacao"] is True


def test_ancoragem_e_rastreabilidade_nao_verdade():
    """Ancoragem só diz 'o texto diz isto'; a verdade/constitucionalidade continua
    [VERIFICAR] aberto e DERRUBA o peso, não o sobe."""
    claims = [{
        "id": "lei-art47-condiciona-credito",
        "fonte": {
            "documento": "LC 214/2025",
            "trecho": "O direito ao crédito do adquirente somente pode ser exercido quando ocorrida a extinção do tributo",
        },
    }]
    # o trecho é ancorável (existe), mas a tese de (in)constitucionalidade é [VERIFICAR] humano
    vereditos = [{
        "id": "lei-art47-condiciona-credito",
        "itens_verificar": ["O art. 47 é constitucional?"],
    }]
    p = compute_pesos(claims, vereditos, doc_text=DOC_LEI)
    assert relatorio_ancoragem(claims, DOC_LEI)["lei-art47-condiciona-credito"] is True
    assert p["lei-art47-condiciona-credito"] == 9  # 0 + 10 ancora - 1 verdade-pendente
    # sem o [VERIFICAR] de verdade, seria 10: a verdade NÃO é somada, só a ancoragem


def test_ideia_com_fonte_decisao_humana_mantem_base_10():
    """Claim-ideia com fonte 'decisão humana' continua com base 10 (não é claim-lei)."""
    claims = [{"id": "publico", "fonte": "decisão humana"}]
    p = compute_pesos(claims, [{"id": "publico"}])
    assert p["publico"] == 10
