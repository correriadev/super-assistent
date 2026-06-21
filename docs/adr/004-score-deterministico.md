# ADR-004 — Score determinístico, nunca LLM

**Status:** aceito, construído (`engine/score.py`).

**Contexto:** testar peso/herança/propagação via LLM foi identificado como causa real de queda de produtividade (gasto de token em aritmética).

**Decisão:** `score = base + herança(derives_from) + dúvidas_fechadas − dúvidas_abertas`. Função pura, pytest, grátis. Base 10 (idea graph) ou 0+10-se-grounded (source graph). "(non-blocking)" não conta.

**Consequência:** nunca pedir a um agent para "avaliar o score". Recalcular a cada rodada. O score é o termômetro; a profundidade visual emerge dele (ver concept).
