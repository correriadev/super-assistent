# ADR-012 — Descida de nível parametrizável + provisional

**Status:** aceito, construído (`engine/descent.py`).

**Contexto:** a pré-condição "só desce sobre claim resolvido", binária, é sentida como burocracia — mata o momentum. O usuário precisa **sentir** o projeto se movimentar.

**Decisão:** `descent_policy`: `strict` | `vinculante_only` | `threshold` | `provisional` | `force`. Descer sobre fundação aberta não bloqueia — gera filho `provisional` (cicatriz, herda score baixo do pai), e a propagação reabre quando o pai muda. Chão absoluto: `CONTRADIZ-NIVEL-ACIMA` nunca é furado, nem por aceite.

**Consequência:** movimento real + dívida rastreada (não some). Provisional é transitivo (filho de irmão provisional herda a marca). Só é honesto se a marca for lida e a propagação disparar. Ver [spec](../specs/descent.md).
