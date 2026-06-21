# ADR-008 — Propagação abre cicatriz, nunca reescreve

**Status:** aceito, construído (`engine/propagation.py`).

**Contexto:** quando um claim-fonte é invalidado, os dependentes (via `links`) precisam saber. Reescrever a resposta automaticamente seria interpretação automática (viola ADR-002).

**Decisão:** a propagação **ABRE** cicatriz (marca `stale: review` + reabre a dúvida, score cai) e **NUNCA fecha** (nunca reescreve content/rationale). Cada dono de domínio re-resolve à mão. Cada evento vai pro log append-only (JSONL).

**Consequência:** abrir é sempre seguro (no máximo trabalho à toa); fechar errado é falsa segurança. "Versão" = marco no log; "diff" = eventos entre marcos (`events_between`).
