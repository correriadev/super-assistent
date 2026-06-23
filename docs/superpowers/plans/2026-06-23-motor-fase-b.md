# Motor Fase B — Implementation Plan

> Executar via subagent-driven-development. TDD, commits frequentes. Branch `feat/motor-fase-b`.

**Goal:** Fundar e construir os itens de pesquisa pós-beta, com as decisões de design travadas pelo usuário (2026-06-23).

**Decisões travadas:**
- **Task 11 (derivação):** mecanismo agora, regras vazias (entram por projeto). Não inventar regras canônicas.
- **Task 10 (oracle slot):** MÍNIMO — teste vira nó com link `valida`→código; `verify_integrity` emite veredito; gate-da-ideia intocado.
- **Task 9 (oracle tag):** DERIVADA (`oracle_of`), não campo armazenado.
- **Task 12 (cross-graph):** human-triggered — anexa candidates, não persiste link automático.
- **Task 13 (histórico por-claim):** MORTA — git por projeto cobre o global.

**Tech:** Python stdlib + pytest. Sem deps novas. Não quebrar os 112 testes existentes.

---

## Task B1: `engine/oracle.py` — tag de oráculo derivada (era #9)

**Files:** Create `engine/oracle.py`, `tests/test_oracle.py`. Modify `engine/run.py` (surface oracle_mix).

`oracle_of(claim, verdict)` deriva dos sinais existentes (provenance + verdict), não armazena campo. Três tipos (garfo fato/estrutura/decisão): worldly (tem verification_items abertos) > structural (status não-passa ou structural_gaps) > decision (axioma humano assentado). Source-graph assentado = structural (grounding), não decision.

Testes: human-decision PASSA→decision; verdict com verification_items→worldly; INCOMPLETO→structural; source claim PASSA→structural; `oracle_mix` conta por id. Runner: `rep["oracle_mix"]`.

## Task B2: estender `engine/integrity.py` — teste-como-nó (era #10, mínimo)

**Files:** Modify `engine/integrity.py`, `tests/test_integrity.py` (append). NÃO mudar chaves/comportamento existentes; os 10 testes atuais ficam verdes.

Adicionar `is_test_node`, `validates_ref` (link type `valida`), `test_verdict(test_node, results)→PASSA|CONTESTADO|None`. Em `verify_integrity`: coletar `test_verdicts={id:veredito}`, nó-teste com `valida`→alvo inexistente vira dangling, nó-teste CONTESTADO entra em novo `red_test_nodes` e derruba `ok`. Chaves novas só ADICIONADAS ao dict de retorno.

## Task B3: estender `engine/linking.py` — loop cross-graph por domínio (era #12)

**Files:** Modify `engine/linking.py`, `tests/test_linking.py` (append).

`suggest_links(verdict, source_claims, source_scores, embed_fn=None)`: para cada `verification_item` com `domain`, filtra source_claims daquele domínio, roda `resolve_link`, anexa `item["candidates"]` (não persiste link — human-triggered). `not-found`→pula. Reusa `resolve_link`/`domain_of` existentes. Retorna itens enriquecidos.

## Task B4: `engine/derivation.py` — assinatura Γ_pai⊢filho (era #11, mecanismo)

**Files:** Create `engine/derivation.py`, `tests/test_derivation.py`.

`check_derivation(parent, child, rule=None)`: rule é callable `(parent,child)->bool` ou None; None=ok vacuamente (sem falso bloqueio). `check_level(parents_by_id, children, rules, parent_level, child_level)`: aplica a regra da transição (de `rules={(pl,cl):callable}`, vazio por padrão) a cada filho via `child['parent']`; retorna ids que violam. Regras nascem vazias — conteúdo é do projeto.

Testes: sem regra→ok+sem violação; regra de exemplo (filho exclui token proibido)→detecta violação; flag `rule_declared`.

---

Self-review: 9→B1, 10→B2, 12→B3, 11→B4. 13 morta. Cada task independente (B1/B4 novos arquivos; B2/B3 estendem, sem quebrar existentes).
