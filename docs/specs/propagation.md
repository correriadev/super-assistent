# spec — propagation (`engine/propagation.py`)

Cicatriz que cruza grafos + log de eventos (ADR-008).

**`propagate(source_claim_id, claims, verdicts, log_path, ts=None)`** — para cada claim dependente (via `links[].ref` ou legado `provenance.ref`): marca `stale: review`, reabre a dúvida (`verification_items`), loga evento. **Assert** garante que content/rationale/binding não mudam.

**`log_event` / `read_events` / `events_between(since, until)`** — log append-only JSONL. "Versão" = marco; "diff" = eventos entre marcos.

**Invariantes:** ABRE nunca FECHA; nunca reescreve a resposta; o dono re-resolve à mão. Testes: `test_propagation.py`.
