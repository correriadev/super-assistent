# Roadmap — Super Assistente de Validação de Projetos

> Baseado no `README.md`. Mesma disciplina: tudo é **[VALIDADO]** (testado) ou **[VISÃO]** (hipótese).
>
> **Princípio que ordena o roadmap:** o caminho mais curto até a pergunta de §10 do README — *"a crítica sóbria faz um terceiro parar e dizer 'não tinha visto isso'?"*. Nada de mecânica nova antes desse teste. Construir mais sistema antes da Fase 2 é a fuga confortável que o README registra como anti-meta.

**Estado atual do repo:** só `README.md`. Zero código. Sem `.opencode/agent/`, sem `dados/`, sem `projetos/`. A spec existe; a implementação não.

**Dois runtimes em paralelo.** Os agents devem rodar tanto no **Claude Code** quanto no **opencode**. Toda alteração de configuração/agent vale para ambos os ambientes:
- Claude Code: `C:\Users\artursc\.claude`
- opencode: `C:\Users\artursc\.config\opencode`

Os agents do repo vivem em `.opencode/agent/` (markdown), formato comum aos dois harnesses. Configs específicas de cada runtime (hooks, settings) ficam nas pastas acima e precisam ser mantidas em sincronia — uma mudança num ambiente exige refletir no outro.

---

## Fase 0 — Esqueleto

Tornar o repo rodável. Nada de lógica nova — apenas materializar a spec do README.

- [ ] `.opencode/agent/`: 5 markdowns (decompositor, gate, tradutor, expansor, orquestrador)
- [ ] `dados/` + `projetos/<nome>/` (ideia.md + JSONs)
- [ ] Schema JSON travado: claim, veredito, binding
- [ ] Orquestrador roda o ciclo de um nível end-to-end na ideia do autor (Hub Contábil)
- [ ] **Validar em ambos os runtimes:** mesmo ciclo roda no Claude Code (`.claude`) e no opencode (`.config/opencode`)

**Saída:** ciclo de ideação completo funciona no repo novo.

---

## Fase 1 — Reproduzir o [VALIDADO]

Provar que o esqueleto novo mantém o que o README marca como validado (§4). Sem isso, regressão silenciosa.

- [ ] Re-rodar os ~6 claims do Hub Contábil
- [ ] Fronteira factual: LGPD → `[VERIFICAR]`, nunca endossada
- [ ] `PRECISA-JUSTIFICAR` estável para claims sem justificativa
- [ ] Precedência: `INCOMPLETO` vence `PENDENTE-VERIFICAÇÃO` quando ambos presentes
- [ ] Modo socrático não amolece rigor

> **gate é o ativo central** — foco do esforço de teste aqui.

**Saída:** checklist §4 do README reproduzido no código novo.

### Melhoria aplicada — criticidade do `[VERIFICAR]`

Achada no teste da ideia fiscal (SaaS subvenção/Reforma): fato FALSO ("split obrigatório desde jan/2026") ficava enterrado como dívida comum sob veredito `INCOMPLETO` (vagueza vence por precedência). Correção aplicada em `gate.md` + `tradutor.md` (2 runtimes):
- Campo `criticidade: <crítica | comum>`; fato cuja falsidade colapsa o claim → marcador `[VERIFICAR-CRÍTICO]`.
- Tradutor tria por criticidade, não só por veredito-topo: crítico cruza o limiar sozinho mesmo sob `INCOMPLETO`.
- **Precedência intocada** (ortogonal — muda o que sobe ao humano, não qual veredito vence). Regressão confirmou: topo segue `INCOMPLETO`, fato falso sai crítico, discriminação preservada.

---

## Fase 2 — O teste que decide tudo (§10) ⭐

Não-negociável antes de qualquer mecânica nova. Decide se há produto.

- [ ] Pegar ideia de um **terceiro** (contador/fundador — perfil §10)
- [ ] Rodar pelo sistema; mostrar o alerta sóbrio do tradutor
- [ ] Medir: o terceiro para e diz **"não tinha visto isso"**? (sim/não)

**Saída:** veredito binário sobre existir produto.

**Gate de decisão:**
- Falha → repensar o produto, **não** construir mais sistema.
- Passa → liberar Fase 3.

### ✅ RESULTADO (2026-06-12) — PASSOU

Terceiro rodou ideia de domínio próprio (SaaS fiscal: subvenção ICMS + Reforma Tributária) e **viu valor** — pediu para avançar com o desenvolvimento. O pivô abriu. A pergunta de §10 ("alguém que não é o autor para e diz 'não tinha visto isso'?") teve resposta **sim** pela primeira vez.

Sub-resultado de engenharia: o teste fiscal estressou a fronteira factual no terreno difícil (direito contestado, Tema 1.182/STJ, fatos falsos sobre 2026) e ela segurou — nenhum fato falso endossado. Gerou a melhoria de criticidade do `[VERIFICAR]` (ver Fase 1).

---

## Fase 3 — Fluxo quente: volume documental ⭐ (prioridade atual)

O terceiro quer rodar um fluxo **mais quente**: estruturar uma ideia própria e alimentar o motor com **os documentos que já tem em mãos — muitos**. Aqui a proporção muda: a entrada deixa de ser "uma ideia em texto livre" e passa a ser **um corpus documental**. É a primeira dor real de escala — e o gatilho que §12 do README previa ("adicione tecnologia quando a dor aparecer, nunca antes"). A dor apareceu: agora avaliar, não antes.

**O que quebra com volume (mapear antes de codar):**
- [ ] **Ingestão de N documentos** — pipeline doc → claims, não mais texto único → claims. decompositor roda por documento; precisa deduplicar e consolidar claims repetidos entre docs.
- [ ] **Procedência obrigatória** — cada claim aponta o documento-fonte (e trecho). Sem rastreabilidade, o stakeholder não confia no veredito nem audita. Campo novo no schema do claim: `fonte_documento`.
- [ ] **Conflito entre documentos** — doc A contradiz doc B. Novo tipo de checagem (parente do `CONTRADIZ-NIVEL-ACIMA`, mas horizontal): o gate/orquestrador precisa sinalizar quando dois claims de docs diferentes colidem.
- [ ] **A premissa "cabe no contexto" cai** (§12) — README apostava que ideia + claims cabem no contexto e RAG "provavelmente nunca". Volume documental é o **primeiro teste legítimo** dessa aposta. Avaliar (não assumir): persistência (SQLite) e recuperação (RAG/índice) deixam de ser over-engineering quando o corpus não cabe.

**Anti-meta ainda vale:** avaliar a dor real, medir o que não cabe, e só então adicionar. Não construir grafo+RAG+SQLite de uma vez porque "agora tem documento". Medir qual é o gargalo concreto (contexto estourou? reabrir incomoda? recuperação falha?) e atacar esse.

**Saída:** motor roda sobre o corpus do terceiro com procedência e detecção de conflito entre docs, sem perder a discriminação do gate.

---

## Fase 4 — Transição entre níveis [VISÃO → testar]

Primeira peça concreta da visão multi-nível.

- [ ] expansor + `restricao_do_pai` + `CONTRADIZ-NIVEL-ACIMA`
- [ ] **Teste plantado (§11.5):** claim de concepção que viola a ideação de propósito → o gate marca `CONTRADIZ-NIVEL-ACIMA`?
- [ ] Investigar elo mais frágil: `restricao_do_pai` do expansor (o mais novo)

**Saída:** tese central funciona em mais de um nível, fora da cabeça do autor.

---

## Fase 5+ — Visão completa [tudo NADA validado, §8]

Adicionar **só quando a dor aparecer** (§12). Cada item resolve um problema que o projeto ainda não tem.

- [ ] Grafo de claims com tiers de abstração
- [ ] Propagação de stale (risco real: paper STALE ~14% em cadeia indireta)
- [ ] Contradição ascendente
- [ ] SQLite (candidato a antecipar — ver Fase 3, se o volume documental for a dor)
- [ ] RAG / índice de recuperação (idem — só se o corpus não couber no contexto)
- [ ] Interface visual — **explicitamente por último**; o valor não está nela

---

## Caminho crítico

```
Fase 0 → Fase 1 → [Fase 2 ✅ pivô PASSOU] → [Fase 3 ⭐ volume documental] → Fase 4 → Fase 5+
```

Fase 2 passou (2026-06-12): terceiro viu valor, pediu desenvolvimento. O pivô que decidia se há produto foi cruzado. Agora a frente quente é a Fase 3 — alimentar o motor com o corpus documental do terceiro. É a primeira dor de escala; tratar com a mesma disciplina do README: medir a dor concreta antes de adicionar tecnologia.
