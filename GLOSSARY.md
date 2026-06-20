# Glossário — termos cunhados ↔ termos técnicos/de-mercado

Fonte única da verdade da renomeação. Esquerda = vocabulário poético da fase de design; direita = termo técnico adotado no código, dados, agents e docs.

## Conceitos centrais

| Cunhado | Técnico / mercado | Identificador no código |
|---|---|---|
| constelação | knowledge graph (por domínio) | idea graph / source graph |
| constelação-ideia | idea graph | claims (origem `"human decision"`) |
| constelação-lei | source graph | claims (origem `{document, excerpt}`) |
| claim | claim / node | `claim` |
| peso | confidence/maturity score | `score` · `score.py` · `compute_scores` |
| névoa / flutua / afunda | low/high score (UI metaphor) | — (só rótulo de UI) |
| fonte | provenance | campo `provenance` |
| trecho | excerpt | `provenance.excerpt` |
| ancoragem / ancorado | grounding / grounded | `is_grounded` · `grounding_report` |
| âncora (ponte cross-grafo) | link | campo `links` · `link_claim` |
| sobreposição dimensional | cross-graph link resolution | `linking.py` · `resolve_link` |
| cicatriz | stale / invalidation flag | campo `stale` · `mark_stale` |
| reflutuar / reflutuação | invalidate / invalidation | — |
| propagação cross-constelação | cascade invalidation / dependency propagation | `propagation.py` · `propagate` · `depends_on` |
| log de eventos | event log | `events.jsonl` · `log_event` · `read_events` · `events_between` |

## Campos de claim / veredito

| Cunhado | Técnico | Chave |
|---|---|---|
| justificativa | rationale | `rationale` |
| deriva_de | derives from | `derives_from` |
| veredito (chave) | status | `status` |
| lacunas_estruturais | structural gaps | `structural_gaps` |
| itens_verificar | verification items | `verification_items` |
| lacunas_resolvidas | resolved gaps | `resolved_gaps` |
| itens_verificados | verified items | `verified_items` |
| pergunta_elicitacao | elicitation question | `elicitation_question` |
| contradicao | contradiction | `contradiction` |
| "(não bloqueante)" | non-blocking marker | `(non-blocking)` (PT ainda aceito) |

## Agents (arquivos `.claude/agents/`)

| Cunhado | Técnico |
|---|---|
| briefista | intake |
| decompositor | extractor |
| expansor | expander |
| gate | gate (mantido — já padrão) |
| tradutor | reporter |
| conselheiro | critic |
| orquestrador | orchestrator |

## CONGELADO (não traduzir — vocabulário de contrato)

- Os **seis rótulos de veredito**: `CONTRADIZ-NIVEL-ACIMA`, `PRECISA-JUSTIFICAR`, `INCOMPLETO`, `PENDENTE-VERIFICAÇÃO`, `CONTESTADO`, `PASSA`.
- O campo **`binding`** e seus valores: `vinculante`, `ilustrativo`, `default-sobrescrevivel`.
- `content`, `category` — já neutros, mantidos.

Esses são vocabulário de domínio deliberadamente fixo; renomear quebraria a fronteira fato/estrutura do gate.
