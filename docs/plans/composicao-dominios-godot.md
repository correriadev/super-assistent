# Plano — composição domínios × subdomínios (modelo Godot scenes/nodes)

**Status:** **Fases 1–5 construídas e auditadas (2026-06-22)** — produção delegada a subagentes sonnet, auditoria no main thread (produtor≠certificador). Adiado por YAGNI: alias/tombstone completo (só o guard de id-duplicado + resolução por alias foi feito) e template de domínio (inherited scene). Origem: a regra de domínios×subdomínios + "1 posse, resto vira referência", confirmada pelo modelo de scenes/nodes do Godot.

## Decisão base

O Godot separa **duas coisas que nunca se misturam**: a **árvore de posse** (cada nó tem **um** `owner`, hierarquia/composição) e as **referências** (`ext_resource`/`NodePath`/signals, many-to-many, apontam pra qualquer lugar). Adotamos a mesma separação:

- **`parent` (1) = posse.** Substitui o `derives_from` multi-pai. É o owner: o nó nasce e é ancorado num único home.
- **`links` (N) = referência.** Toda origem extra, todo cruzamento de domínio, vai pra cá. Many-to-many, cross-domínio, por id estável.

## O que vem do Godot (filtrado por ponytail)

| Conceito Godot | Adoção no motor | Veredito |
|---|---|---|
| `owner` (1 por nó) | `parent` único = home/posse | **ADOTAR** (fase 1) |
| `ext_resource` + **UID** | `links[].ref` e `parent` apontam **id imutável**, nunca posição/path | **ADOTAR** (fase 1) |
| Scene auto-contida + instancing recursivo | domínio = grafo nomeado; subdomínio = domínio instanciado dentro de outro, recursivo | **ADOTAR** (fase 2) |
| scene-unique `%Nome` + owner | nós **expostos**: um domínio publica só sua interface; link cross-domínio só mira nó exposto | **ADOTAR** (fase 2) — controla acoplamento |
| Signals (broadcast desacoplado) | propagação varre o grafo de referências por índice reverso (quem referencia X) | **ADOTAR** (fase 4) |
| Inherited scene | template de domínio (um projeto herda um domínio-AWS base) | **ADIAR** — YAGNI até 2º projeto usar |
| NodePath (sintaxe de path) | — usamos id estável, não path navegável | **NÃO ADOTAR** |
| Instancing em runtime (mecânica) | — somos grafo de conhecimento, não árvore de runtime | **NÃO ADOTAR** |

## Decisões de design

- **D1 — `parent` único (posse).** Multi-origem → `links`. Raiz tem `parent: null`.
- **D2 — ids são UID estáveis.** Imutáveis, nunca reusados nem repropositados. Refatorar um domínio não pode quebrar quem o referencia.
- **D3 — 1 home por nó.** Cada nó é definido e ancorado (grounding) em exatamente um domínio. Uma âncora só (anti raposa-galinheiro).
- **D4 — referência cross-domínio mira só nó EXPOSTO.** Domínio publica interface (`exposed: true`), esconde as tripas. Encapsulamento, como `owner`+`%`.
- **D5 — score herda só do `parent`.** Profundidade/peso = `own + cadeia de posse` (uma linhagem). `links` carregam **confiança/grounding** (score do nó referenciado, como o cross-graph hoje), **não** somam profundidade de posse. Mantém a árvore de profundidade legível.
- **D6 — propagação = broadcast desacoplado.** O emissor (nó que mudou) não conhece os assinantes; índice reverso resolve "quem linkou pra mim" e a cicatriz cruza domínios.

## Plano em fases (determinístico, testável, grátis)

### Fase 1 — Schema posse-vs-referência
- Schema do nó: `id` (UID estável), `domain`, `parent` (1 | null), `links` (N), `provenance` (grounding do home).
- Migrar `derives_from` (multi) → `parent` (1) + o resto pra `links`. Nos dados do projeto 02: escolher o pai-posse de cada nó multi-derivado; os demais viram links.
- `score.py`: herança sobre `parent` único; `links` viram sinal de confiança, não soma de posse (D5). Re-derivar scores.
- Testes: herança single-parent; link não infla profundidade.

### Fase 2 — Registry de domínios + composição recursiva + exposição
- Registry domínio → nós (estende `load_domains` para N domínios).
- Subdomínio = domínio referenciado/instanciado dentro de outro (recursivo).
- Campo `exposed` no nó; `verify_integrity` recusa link cross-domínio mirando nó não-exposto (D4).
- Testes: link só resolve em nó exposto; composição recursiva carrega.

### Fase 3 — Estabilidade de id + integridade cross-domínio
- Regra de id estável (lint: id nunca some sem tombstone). `verify_integrity` estende: `parent`/`link.ref` apontando id inexistente ou não-exposto = violação (já pega dangling; soma exposto + cross-domínio).
- Testes: ref quebrada bloqueia; rename quebra é pego.

### Fase 4 — Propagação como broadcast (índice reverso)
- Índice `referenced_by` (quem aponta pra X). `propagate` cruza domínios via registry; cicatriz O(dependentes), não O(todos).
- Testes: emenda no domínio AWS reabre o nó do simulador que linka o gateway.

### Fase 5 — Viz
- Domínios como constelações **lado a lado**; `parent` = árvore interna; `links` = pontes entre constelações (cor distinta cross-domínio). Reaproveita o exporter (separar tree de bridges).

### Adiado
- Template de domínio (inherited scene) — só quando um 2º projeto reusar um domínio.

## Riscos / fronteiras a vigiar
- **Migração de score (D5):** hoje nós multi-derivados somam vários pais (ex: `calculo-regime-atual` herda de 2). Com posse única, a profundidade muda — re-derivar e revisar que a montanha continua coerente.
- **Escolha do pai-posse:** qual dos N pais é a posse e quais viram link é um julgamento por nó na migração. Critério: o pai-posse é o que *define a existência* do filho; os outros são *dependências*.
- **Sprawl de domínios:** `exposed` + "domínio = fonte de grounding distinta" seguram. Sem critério, tudo vira domínio.

## O que isso resolve
O órfão de código (o erro vital) e a "necessidade solta" (gateway sem dono) deixam de existir: tudo tem **um home ancorado** e referências **por id estável** que a propagação cruza. Traceability vira teia, não corrente — com a disciplina do Godot por trás.
