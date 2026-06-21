# ADR-006 — verification_item como objeto {text, domain, critical}

**Status:** aceito, construído (`test_domain.py`).

**Contexto:** uma dúvida precisa carregar **onde** sua resposta mora e **se** sua falsidade derruba o claim.

**Decisão:** `verification_item` é objeto `{text, domain ∈ lei|engenharia|financeiro|null, critical}`. O gate emite no schema; `score`/`linking` aceitam objeto e string legada (retrocompat, sem migração).

**Consequência:** `domain` é o endereço dimensional que o passo 1 do linking lê (ADR-007). `critical` substitui o prefixo `[CRÍTICO]` por campo limpo.
