# spec — linking (`engine/linking.py`)

Casa uma dúvida (verification_item) com o claim-fonte que a endereça. Não decide verdade (ADR-002/003).

**`resolve_link(question, source_claims, source_scores, threshold=0.16, embed_fn=None, margin=0.05)`**
- match: jaccard (lexical) ou cosseno (se `embed_fn`, ADR-010).
- retorna `result ∈ {confirms, refutes, not-found, ambiguous}` + `source_claim`, `excerpt`, `confidence` (= score da fonte), `reliable`, `note`.
- **margin gate:** top-1 e top-2 quase empatados → `ambiguous` + `candidates` (não escolhe).

**`link_claim(idea_claim, question, resolution)`** — persiste a ponte em `idea_claim["links"]` (idempotente). Recusa `not-found`/`ambiguous`.

**Invariantes:** polaridade é pista rasa; sinal confiável = excerpt grounded. Testes: `test_linking.py`.
