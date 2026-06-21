# Invariantes — as fronteiras que não se quebram

Anti-regressão. Quebrar qualquer uma descaracteriza o método.

1. **Grounding = substring exato**, nunca similaridade (ADR-001).
2. **O sistema nunca afirma verdade** nem fecha a dúvida — `system_decided: False` sempre (ADR-002).
3. **confirms/refutes é pista**, não veredito; o sinal confiável é o excerpt grounded (ADR-003).
4. **Score é determinístico**, nunca LLM (ADR-004).
5. **LLM só na borda, injetado** (ADR-005).
6. **Propagação ABRE cicatriz, nunca reescreve** a resposta (ADR-008).
7. **Modalidade (binding) é humana** — o modelo nunca infere (ADR-013).
8. **CONTRADIZ-NIVEL-ACIMA** bloqueia a descida em qualquer política (ADR-012).
9. **Empate não é resolvido pelo sistema, é exposto** (ADR-010/011).
10. **Fronteira fato/estrutura + seis vereditos** congelados (ver glossary).
