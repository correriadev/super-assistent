# ADR-013 — Modalidade (binding) é humana

**Status:** aceito, construído (`extractor`/`expander` setam `null`; gate exige).

**Contexto:** quando o modelo infere modalidade, o mesmo texto recebe valores diferentes em execuções diferentes, desestabilizando toda a avaliação do gate.

**Decisão:** `binding ∈ {vinculante, ilustrativo, default-sobrescrevivel}` é setado **só por humano**, em lote. Extractor/expander gravam `binding: null`. O gate não prossegue com `null`.

**Consequência:** o orchestrator coleta modalidade em lote (passo 2) antes do gate. Vocabulário de `binding` é congelado (ver glossary).
