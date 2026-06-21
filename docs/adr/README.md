# ADRs — Architecture Decision Records

Uma decisão por arquivo: **Contexto → Decisão → Consequência → Status**. São as fronteiras duras do método; muitas são anti-regressão (quebrá-las descaracteriza o sistema).

| # | Decisão |
|---|---|
| [001](001-grounding-substring-exato.md) | Grounding por substring exato, nunca similaridade |
| [002](002-verdade-humana-system-decided-false.md) | Verdade é humana; o sistema nunca fecha a dúvida |
| [003](003-confirms-refutes-e-pista.md) | confirms/refutes é pista, nunca veredito |
| [004](004-score-deterministico.md) | Score determinístico, nunca LLM |
| [005](005-llm-so-na-borda-injetado.md) | LLM só na borda, injetado |
| [006](006-verification-item-objeto.md) | verification_item como objeto {text,domain,critical} |
| [007](007-cross-graph-linking-sob-demanda.md) | Cross-graph linking sob demanda (árvore de decisão) |
| [008](008-propagacao-abre-cicatriz.md) | Propagação abre cicatriz, nunca reescreve |
| [009](009-navegacao-lexical-vs-semantico.md) | Navegação: lexical grátis vs semântico injetado |
| [010](010-matching-semantico-margin-gate.md) | Matching semântico + margin gate (ambiguous) |
| [011](011-slot-candidates.md) | Slot candidates no verification_item |
| [012](012-descida-parametrizavel-provisional.md) | Descida parametrizável + provisional |
| [013](013-modalidade-e-humana.md) | Modalidade (binding) é humana |
| [014](014-gate-compacto-lotes-custo.md) | Gate compacto, lotes ≤5, custo |
