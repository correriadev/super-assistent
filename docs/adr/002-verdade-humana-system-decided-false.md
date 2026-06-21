# ADR-002 — Verdade é humana; o sistema nunca fecha a dúvida

**Status:** aceito, invariante.

**Contexto:** o risco fatal (caso LGPD) é um LLM afirmar fato/verdade jurídica com autoridade. Decompor por LLM E confirmar por LLM = raposa auditando o galinheiro.

**Decisão:** o sistema **jamais** afirma verdade/constitucionalidade. Todo desfecho de resolução volta ao usuário com `system_decided: False`. Verdade é `[VERIFICAR]` humano.

**Consequência:** todo `to_user` carrega `system_decided: False, action_required: True`. Vale para o gate (fronteira fato/estrutura), o linking e a propagação.
