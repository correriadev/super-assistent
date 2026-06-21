# ADR-003 — confirms/refutes é pista, nunca veredito

**Status:** aceito, construído (`engine/linking.py`).

**Contexto:** o linking devolve uma polaridade ao casar dúvida↔fonte. Tratá-la como decisão violaria o ADR-002.

**Decisão:** a polaridade vem de uma heurística rasa (negação-XOR) **de propósito**. É pista a confirmar por humano, com a confidence = score do claim-fonte (fonte leve → "não confie ainda").

**Consequência:** nunca persistir confirms/refutes como verdade. O sinal confiável é o **excerpt grounded**, não o rótulo. Ver ADR-010 (matching) e ADR-011 (empate).
