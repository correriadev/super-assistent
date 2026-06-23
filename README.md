# super-assistente

Motor **determinístico** que pesa, propaga e deriva os *claims* de um projeto através de níveis de abstração (ideação → concepção → …). Mede quão resolvido cada decisão está, propaga o abalo quando algo muda, e desce de nível sem perder o rastro do que ainda é frágil. **LLM só na borda, injetado** — o núcleo é aritmética testável.

## Genérico por design

A ideia de referência é um simulador (app), mas a essência serve a **qualquer projeto que desce de abstração com dúvida e derivação**: takes de um filme, plano de viagem, mudança geográfica/de vida/treino. Claims, peso, cicatriz e descida de nível são o mesmo motor em qualquer domínio.

## Como rodar

```bash
python3 -m pytest -q                       # suíte determinística (84 testes, grátis)
python3 engine/score.py claims.json verdicts.json scores.json [--doc texto]
# embedder local (navegação/matching semântico): pip install no .venv
```

### Visualização 3D (constelações)

```bash
python3 viz/export_points.py               # gera viz/points.json (só se mudou dado)
python3 -m http.server 8731                # ES modules + fetch exigem http, não file://
```

Abra **http://localhost:8731/viz/**. Precisa de rede (three.js via CDN). Controles: arrastar = orbitar · scroll = zoom · hover = detalhe. Esquerda = constelação **simulador** (níveis ideação→código), direita = **lei**; **ciano** = ponte cross-domínio. Profundidade = peso (afunda = resolvido).

## Mapa de módulos (`engine/`)

| módulo | papel | spec |
|---|---|---|
| `score.py` | peso determinístico (base, herança, dúvidas) | [score](docs/specs/score.md) |
| `linking.py` | casa dúvida↔fonte (lexical/semântico, margin gate) | [linking](docs/specs/linking.md) |
| `resolution.py` | árvore de decisão do cross-graph linking | [cross-graph](docs/specs/cross-graph-linking.md) |
| `retrieval.py` | navegação (qual seção responde) | [retrieval](docs/specs/retrieval.md) |
| `propagation.py` | cicatriz cross-grafo + log de eventos | [propagation](docs/specs/propagation.md) |
| `descent.py` | gate de descida parametrizável + provisional | [descent](docs/specs/descent.md) |
| `embed.py` | embedder local injetado | — |

## Mapa de agents (`.claude/agents/`)

`intake` → `extractor` → `gate` → `reporter` (ciclo) · `expander` (descida) · `critic`, `orchestrator`. Fluxo em [pipeline](docs/specs/pipeline.md); tiers/custo em [token-budget](docs/quality/token-budget.md).

## Estado atual

- **Motor determinístico** (peso, grounding, linking, propagação, descida, **integridade**): código testado, **84 testes**.
- **Composição domínios×subdomínios (modelo Godot):** posse única (`parent`) vs referência (`links`); `verify_integrity` (`engine/integrity.py`) bloqueia órfão / símbolo ausente / teste vermelho / ref quebrada / link cross-domínio a nó não-exposto / id duplicado — o código é nó ancorado (símbolo existe + teste verde), nada flutua solto. Propagação = broadcast por índice reverso, cruza domínios. Plano e fases em [docs/plans](docs/plans/composicao-dominios-godot.md).
- **Cross-graph linking completo** ponta-a-ponta: navegação semântica (embedder local), matching semântico + margin gate, slot `candidates`. Validado no projeto 02 (grafo lei 4→11 claims, 3 fatos críticos verificados).
- **Descida parametrizável** (`descent_policy`) + marca `provisional` transitiva.
- **1 run completa ponta-a-ponta (5 ciclos do motor):** ideação → concepção → arquitetura → cenários de teste → codificação (TDD). Produziu artefato real: [`app/`](app/) — simulador de caixa (regime atual × split), `calc.js`/`validate.js` puros + **16 testes `node --test`** (red→green) + `index.html` (duas colunas). Fatia fina (núcleo computacional); o resto segue `provisional`/adiado, marcado, não perdido.
- **Só conceito ainda:** a visualização (água/montanha/7 estágios).

## Próximos passos

- Expandir a fatia: alíquota via fonte, parcelado, estorno, integração contábil (seguem `provisional`).
- Resolver itens ambíguos do projeto 02 e repontar links imprecisos (pick confiante-errado do matcher).
- Renderizar nós `provisional` e `candidates` no reporter (fechar o loop humano).
- Embedder maior se a precisão do match incomodar.
- Discutir "curadoria" como possível camada genérica nova.

## Quickstart (rodar o estado de um projeto)

    python3 -m engine.run projetos/02-simulador-caixa-split

Reporta: contrato OK?, score de cada claim, bloqueios. Se um agente emitiu JSON
fora do contrato (status inventado, campo faltando), falha-alto aqui com a causa.

## Documentação

Estruturada em [`docs/`](docs/): **[adr/](docs/adr/)** (decisões), **[specs/](docs/specs/)** (comportamento), **[quality/](docs/quality/)** (teste/invariantes/token), **[concept/](docs/concept/)** (constelação + glossário).
