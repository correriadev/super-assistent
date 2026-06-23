"""Histórico real (o 'porquê' humano), complementar ao events.jsonl (máquina).
- decision-log.md: toda decisão/override humana, append-only, voz humana.
- addendum.md: profundidade que o claim dropa (alternativa rejeitada, qualitativo).
- contexto.md: fatos/restrições estáticos do projeto (read-only aqui).
Reversão = linha nova, nunca reescrita. Porquê ausente = visível, não inventado."""
import os


def log_decision(path, *, nivel, decisao, porque, data):
    razao = porque if porque else "(sem porquê registrado)"
    linha = f"- [{data}] {nivel} · {decisao} — {razao}\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(linha)
    return linha


def read_decisions(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [ln.rstrip("\n") for ln in f if ln.startswith("- [")]


def append_addendum(path, *, texto, data):
    linha = f"- [{data}] {texto}\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(linha)
    return linha


def read_context(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
