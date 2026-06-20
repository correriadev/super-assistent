# Camada Conceitual — Sessão 2 (constelação, dimensões, peso, versionamento)

> **Adendo ao `CONTEXTO-REPOSITORIO.md`.** Este documento captura tudo que foi decidido na sessão de design de hoje — a camada conceitual que ainda não estava em nenhum arquivo (os agents em disco são da sessão anterior). Regra mantida: cada item marcado **[DECIDIDO]** (fechado, vira construção), **[A CONSTRUIR]** (decidido mas ainda não codado), **[BUG CONHECIDO]** (existe, com defeito mapeado) ou **[EM ABERTO]** (ainda precisa de decisão).
>
> Ordem de leitura: o conceito central é **peso**; tudo o mais (constelação, dimensões, cicatriz, versionamento) é consequência ou extensão dele.

---

> **Terminologia.** Os termos cunhados aqui (peso, constelação, fonte, cicatriz, sobreposição, névoa, montanha) são a **linguagem de design** — boa para pensar e para a futura camada visual. No **código, dados e agents** o projeto adota agora os termos técnicos/de-mercado equivalentes: peso→**score**, constelação→**knowledge graph** (idea graph / source graph), fonte→**provenance**, ancoragem→**grounding**, cicatriz→**stale/invalidation**, sobreposição→**cross-graph linking**, propagação→**cascade invalidation**. Mapa completo e congelados em [`GLOSSARY.md`](GLOSSARY.md). Abaixo o texto mantém a metáfora; o identificador técnico vai entre parênteses quando importa.

## 1. PESO (score) — o número que sustenta tudo

**[DECIDIDO]** Cada claim tem um **peso**: um número que mede **quão resolvido ele está**. Peso não é atribuído por ninguém — é **computado** a partir das lacunas estruturais e itens a verificar. É a inversão central da sessão: o gate aponta o que falta, e o peso é o **efeito** disso, não uma calibração de entrada.

**Fórmula:**
```
peso = peso_base + herança_dos_pais + dúvidas_fechadas − dúvidas_abertas
```
- `peso_base` = 10 (positivo, para um claim sem pendência assentar, não nascer negativo).
- `dúvidas_abertas` = só lacunas e `[VERIFICAR]` reais não resolvidos. Itens "(não bloqueante)" **NÃO contam**.
- `dúvidas_fechadas` = pendências já resolvidas; cada uma **sobe** o peso (resolver afunda o ponto).
- `herança_dos_pais` = claim derivado herda o peso do(s) pai(s) via `deriva_de`; nasce com o peso do pai, não do zero.

**Princípio que define a fórmula [DECIDIDO]:** só **fechar dúvida** dá peso. **Definir conteúdo sem que nada seja questionado é neutro** — não pesa. (Afirmar não é resolver. Isso impede inflar densidade escrevendo mais; o sistema premia resolução, não verborragia.)

**[CORRIGIDO]** O bug (pesos negativos, inclusive PASSA negativo porque itens "(não bloqueante)" eram contados como dúvida) foi resolvido. `peso.py` agora aplica `peso_base = 10`, herança via `deriva_de`, crédito por dúvida fechada, e ignora itens "(não bloqueante)". Verificado por pytest (`test_peso.py`): claim PASSA fica assentado (≥10), nunca negativo. Código determinístico, sem LLM — testá-lo via LLM foi identificado como desperdício de tokens.

**[DECIDIDO]** Peso negativo é válido e significa **"afundado em névoa"** (muita dúvida aberta). Positivo significa **assentado** (resolvido). O que importa é a posição relativa, não o sinal — mas um PASSA jamais pode ser negativo.

---

## 2. CONSTELAÇÃO COMO ÁGUA — a representação visual

**[DECIDIDO]** A constelação é um campo onde cada ponto (claim) assenta numa **profundidade contínua determinada pelo seu peso**. Não há degraus/faixas fixas — é água, fluida. Um conceito por natureza tem poucas resoluções, então **boia raso**; um item muito resolvido (ex: código) **afunda**. A profundidade é **coordenada visual**, não um campo de dado separado — emerge do peso.

**Comportamentos [DECIDIDO]:**
- **Derivar mantém o filho perto do pai** (herança de peso). Cadeia de derivação = cadeia coesa, pontos próximos.
- **Resolver afunda** o ponto (ganha peso, desce).
- **Ideia nova reabre o ponto que ela toca**, fazendo-o **subir** (perde peso, reflutua). Não cria ponto distante — reabre o existente. Só cria ponto novo se o assunto for inédito.
- A **onda** (relevo irregular) se forma porque pontos diferentes estão em estágios de resolução diferentes num mesmo instante.

**Diagnóstico embutido [DECIDIDO]:** se um ponto sobe sozinho, a mudança foi **pontual**; se sobe e **arrasta os filhos** junto (pela cadeia de derivação), foi **estrutural**. A propagação distingue os dois visualmente.

**Decisão de design importante [DECIDIDO]:** a visualização NÃO é uma camada separada a construir — ela é a **renderização direta do cálculo de peso**. Os estágios visuais emergem sozinhos se o peso for computado certo. Construir o visual é DEPOIS do peso estar sólido (anti-meta: não desenhar a montanha sobre um número que ainda treme).

---

## 3. OS SETE ESTÁGIOS DA MONTANHA

**[DECIDIDO]** A evolução visual de um projeto, derivável do peso ao longo do tempo:

0. **Plano** — grid totalmente liso (ausência de ideias, tudo no zero).
1. **Irregular** — primeiras ideias surgem, primeiros relevos.
2. **Mais irregular** — primeiras expansões (derivações).
3. **Guarda-chuva** — densidade dos pontos aumentando + expansões; forma começa a se organizar.
4. **Montanhoso** — muitas cadeias em estágios diferentes; picos e vales.
5. **Montanha (vista de longe)** — projeto solidificando; base larga (muito derivou da raiz), topo estável (o conceito-raiz raramente reabre).
6. **CICATRIZ** — uma ideia/emenda disruptiva. **CORREÇÃO IMPORTANTE da intuição inicial:** a disrupção NÃO ergue um "pedaço de bolo". Ela **desfaz resolução**: abre uma **cicatriz de névoa** que rasga a montanha na coluna atingida (o ponto impactado e tudo que dele deriva perdem peso e reflutuam). A largura/profundidade da cicatriz = o alcance da disrupção (fina = pontual; desce a montanha toda = estrutural).
7. **Cicatriz preenchida** — conforme os pontos reabertos são re-resolvidos, a coluna de névoa reganha massa e afunda, preenchendo o corte. A montanha volta sólida, **possivelmente com forma nova** (a re-resolução pode ter mudado o que havia ali).

---

## 4. DIMENSÕES SOBREPOSTAS — constelações por domínio

**[DECIDIDO]** Existem **múltiplas constelações para o mesmo projeto**, uma por domínio: constelação-ideia (o produto, nome de trabalho "domínio-app"), constelação-lei, e potencialmente outras (jurídico, financeiro, engenharia — como setores de uma empresa). **Todas são a mesma estrutura** (claims + peso + cicatriz) — mesmo motor. Diferem só na **origem e direção de crescimento**:
- **Ideia nasce de cima** (o conceito) e **desce derivando** (wireframe, arquitetura, código).
- **Lei nasce de baixo** (o texto promulgado, denso, concreto) e quando vem uma emenda, ela se liga por baixo e **propaga pra cima** (reabre a regra, que reabre o princípio).
- Mesma cicatriz, sentidos opostos. Mesmo motor de propagação.

**`[VERIFICAR]` são pontes entre dimensões [DECIDIDO]:** um `[VERIFICAR]` de uma constelação se **sobrepõe** à constelação-destino e busca o ponto que responde a dúvida. Resultado: **confirma** (a fonte diz isso), **refuta** (a fonte diz o contrário — automatiza o que foi feito à mão no caso LGPD), ou **não-encontrado** (nem a fonte resolve — e agora você sabe disso). Cada dúvida carrega o **endereço dimensional** de onde sua resposta mora (lei → jurídico, viabilidade → engenharia, custo → financeiro).

**Natureza, não RAG vetorial [DECIDIDO]:** a busca é por **relação de resolução** (existe um ponto que responde, e qual seu peso/confiabilidade?), não por similaridade de texto. É parente de graph RAG / knowledge-graph retrieval, com o acréscimo do **peso como medida de confiabilidade da resposta**. **[EM ABERTO/VERIFICAR]** se "peso como confiabilidade" já existe formalizado (procurar GraphRAG, knowledge graph retrieval) — não foi confirmado se é novidade.

---

## 5. PESO POR DOMÍNIO — como cada constelação ganha massa

**[DECIDIDO]** O motor é o mesmo, mas **o que dá peso difere por domínio**, porque a fonte de verdade difere:
- **Domínio-ideia:** a fonte de verdade é **você** (a ideia é sua). Peso vem de **decisão humana** resolvendo dúvida. Não há texto externo contra o qual conferir.
- **Domínio-lei (e qualquer fonte externa):** a fonte de verdade é **o texto da lei**, externo e fixo — e o sistema pode lê-lo errado. Por isso a constelação-lei **nasce inteira leve** (interpretação crua não-confirmada) e só ganha peso por **verificação contra o texto-fonte**. O peso impede a fonte de mentir com autoridade.

**Campo `fonte` em toda estrela [DECIDIDO]:** cada claim registra sua origem. Na constelação-ideia, "decisão humana". Na constelação-lei, o **documento oficial + trecho literal**. O `fonte` é o que permite a cicatriz **cruzar dimensões** (ver seção 7).

### 5.1 Como a constelação-lei ganha peso — Saída 1 [DECIDIDO]

Decisão crítica do dia, depois de identificar o risco fatal: se um LLM decompõe a lei E um LLM "confirma" a decomposição, é a raposa auditando o galinheiro — reintroduz o erro da LGPD com autoridade ampliada. A saída escolhida:

- A constelação-lei é **decomposta por LLM**, MAS a "confirmação" é **ancoragem rastreável, não julgamento de verdade**.
- O processo automático **localiza e anexa o trecho literal** do texto-fonte que originou cada claim. O peso vem de **o claim ter um trecho-fonte apontável que de fato existe e diz aquilo** — verificável por qualquer humano que clique e leia.
- **Distinção obrigatória:** "o texto diz X" (rastreável, pesa) ≠ "X é verdadeiro/constitucional" (continua `[VERIFICAR]` humano, NUNCA ganha peso automático). O sistema **jamais afirma verdade jurídica** — só ancora o que o texto diz literalmente.
- Exemplo do risco concreto (artigo sobre split payment usado no teste): o artigo argumenta que "o art. 47 é inconstitucional" — isso é **tese contestável**, não fato do texto. O sistema deve extrair como "o artigo afirma X [fonte: trecho]", não assentar "X é inconstitucional" como verdade.

---

## 6. CONSTRUÇÃO DE MÃO DUPLA — as duas direções

**[DECIDIDO]** O sistema cresce nos dois sentidos, com o mesmo motor:
- **Cima → baixo (ideia):** o conceito gera derivações cada vez mais concretas. O **expansor** projeta pontos mais fundos a partir de pontos com peso suficiente para sustentá-los (não se deriva tela de uma tese ainda em névoa). Filho herda peso do pai.
- **Baixo → cima (lei/fonte):** o texto promulgado é a base densa; uma emenda entra por baixo, se liga à regra que altera, e **propaga a perda de peso pra cima** pela cadeia de dependência. A regra reabre, o princípio que dependia dela reabre.

Isso garante simetria: **uma alteração na lei impacta a constelação do mesmo jeito que uma ideia nova impacta o projeto** — abre cicatriz, propaga, exige re-resolução.

---

## 7. PROPAGAÇÃO CROSS-CONSTELAÇÃO — a cicatriz que cruza dimensões

**[DECIDIDO]** O `fonte` permite a cicatriz saltar entre montanhas. Quando um claim-lei reflutua (emenda abre dúvida nele), **todo claim de qualquer constelação cujo `fonte` aponta para ele também reflutua** — a perda de peso propaga entre constelações. É uma notificação que chega a todos os domínios que "beberam" daquele ponto.

**REGRA DURA [DECIDIDO] — a decisão mais importante da propagação:**
- A propagação **ABRE cicatriz automaticamente** (invalida: "isto não vale mais, confira") — seguro, é o alarme que nenhum sistema comum tem.
- A propagação **NUNCA fecha a cicatriz automaticamente** (NUNCA reescreve a resposta). Reescrever seria **interpretação jurídica automática** = reintroduzir o erro da LGPD em escala.
- Abrir é sempre certo (no máximo gera trabalho à toa). Fechar errado é pior que não abrir (falsa segurança).
- Cada **dono de domínio re-resolve à mão** o que a cicatriz reabriu. O jurídico não decide o produto; ele só faz a montanha do produto tremer onde tocava a lei que mudou.

Mecanismo: emenda entra na constelação-lei (via área jurídica) → reflutua os nós atingidos → **notifica** as dimensões que citam aquela `fonte` → os responsáveis veem os pontos que reflutuaram e re-resolvem.

---

## 8. INTERAÇÃO, VERSIONAMENTO E HISTÓRICO

**[CONSTRUÍDO]** O sistema é **dirigido por eventos**. Git versiona **arquivos** (estado de texto) e continua útil, mas o histórico valioso é o **log de eventos de propagação**, não o diff de linhas. Implementado em `propagation.py` (log append-only JSONL + `events_between` para o "diff" semântico entre marcos), testado em `test_propagation.py`.

**Decisões [DECIDIDO]:**
- O **diff que o responsável vê** ao clicar numa notificação é **semântico** — "quais nós reflutuaram, por qual causa/fonte" — não diff de arquivo. O campo `fonte` torna a cadeia causal navegável.
- "Versão" = **marco no log de eventos** (não número de commit). O diff entre v99 e v100 = a **lista de eventos entre os dois marcos**.
- **Caminho escolhido:** log de eventos **append-only em arquivo** (cada evento = {timestamp, tipo, claim afetado, causa/fonte}), recalculando o peso na hora. NÃO event-sourcing completo (over-engineering hoje), NÃO banco. Git mantém o estado dos arquivos.
- **[EM ABERTO/VERIFICAR]** a tecnologia específica conforme o volume real crescer — começar com log JSON em arquivo, migrar quando doer.

---

## 9. CORREÇÕES DE AGENTS DECIDIDAS HOJE

**[CONSTRUÍDO]** (aplicado em `.claude/agents/`; nomes técnicos: extractor, expander, orchestrator, gate, reporter, critic, intake)
- **Extractor (ex-decompositor):** remover o número fixo de "3 a 6 claims". Extrair **um claim por assunto distinto** encontrado, quantos forem (um documento legislativo que mexe em 12 pontos gera 12 claims). Ideia nova sobre projeto existente **reabre os claims que toca** (abre lacuna), só cria claim novo se o assunto for inédito.
- **Expander (ex-expansor):** o filho **herda o score do pai** ao nascer (não nasce leve nem zerado). Fica mais leve que o pai só se tiver mais issues próprias.
- **Orchestrator (ex-orquestrador):** após consolidar verdicts, **chamar o cálculo de score** (`score.py`) e gravar `dados/scores.json`. Recalcular a cada rodada e a cada nova ideia.

---

## 10. PRINCÍPIOS REAFIRMADOS HOJE (anti-metas)

- **Determinístico = código, nunca LLM.** Peso, propagação, herança são aritmética → pytest, grátis, instantâneo. Testá-los via LLM é desperdício de tokens (identificado como causa real da queda de produtividade).
- **LLM só para julgamento** (o gate discrimina? o decompositor ancora o trecho certo?) — caro, rodar com parcimônia.
- **Construir na ordem de dependência, uma fase por vez.** Peso primeiro (base de tudo); dimensões e versionamento DEPOIS do peso passar. Construir tudo junto = cego para a causa do próximo bug.
- **O sistema nunca afirma fato/verdade jurídica** — só ancora texto literal e sinaliza `[VERIFICAR]`. Vale para a constelação-lei tanto quanto para o gate.
- **Sem banco, sem RAG vetorial, sem interface visual ainda.** JSON em arquivo + log append-only.
- **Fronteira fato/estrutura, seis vereditos, binding por humano:** intocados.

---

## 11. ESTADO ATUAL E PRÓXIMO PASSO

- **Score (peso):** corrigido e testado (base 10, herança, issue fechada credita, "(non-blocking)" ignorado). pytest verde.
- **Dimensões, provenance, cross-graph linking, cascade invalidation, event log:** construídos e testados nesta sessão — `score.py`, `linking.py`, `propagation.py`, 19/19 pytest. Extractor/expander/orchestrator atualizados em disco. Vocabulário técnico em [`GLOSSARY.md`](GLOSSARY.md).
- **Próximo foco — construir algo útil ao AUTOR primeiro.** Sobre o peso já sólido: a visualização da constelação (água/montanha/7 estágios) e rodar o fluxo end-to-end num projeto real do próprio autor. A montanha emerge do peso; o peso está firme. O valor se prova no uso real, construindo — não em validação externa antecipada.

## 12. RESOLUÇÃO DE DÚVIDA SOB DEMANDA (cross-graph linking) — decidido nesta sessão

**[DECIDIDO]** O fluxo de quando um `verification_item` do idea graph busca resposta em outro domínio. Princípio que amarra tudo: **todo caminho termina no usuário** — o sistema nunca decide, só muda *o que entrega na mão dele*. `confirms`/`refutes` é sempre PISTA, nunca veredito.

Árvore de decisão:

```
verification_item (com endereço de domínio: lei / engenharia / financeiro)
│
1. existe domínio próprio (source graph p/ esse endereço)?
│   ├── NÃO → devolve ao usuário: "sem domínio; responda à mão OU
│   │         autorize ingerir o documento desse domínio"
│   └── SIM ↓
│
2. procura nos nós (resolve_link sobre os claims do domínio)
│   ├── not-found (grafo existe, nenhum nó responde)
│   │     2a. [LAZY] a seção relevante já foi decomposta?
│   │         ├── NÃO → recupera o trecho do doc + decompõe on-demand
│   │         │         (cresce o grafo) → volta ao passo 2
│   │         └── já decomposto e ainda nada → devolve ao usuário
│   │
│   └── found (NUNCA auto-resolve; devolve, mas com algo na mão)
│         confidence = score do nó-fonte:
│         ├── grounded (score alto) → PISTA: confirms/refutes + excerpt;
│         │                            humano confirma a polaridade
│         └── leve (score ≤ 0)      → "achei, mas não confie ainda"
```

**Dois "não existe" distintos [DECIDIDO]:** (a) domínio inexistente (sem source graph) ≠ (b) domínio existe mas nenhum nó responde. Em (b), antes de desistir, cabe a **decomposição lazy dirigida pela dúvida** (passo 2a).

**Onde o RAG entra [DECIDIDO]:** só no passo 2a — navegação para achar *qual seção decompor* quando o grafo do domínio está incompleto. Recupera → decompõe → grounding exato → busca de novo. **RAG nunca vira fonte de verdade nem de score.** É a "versão forte" da hipótese de RAG (decomposição on-demand), não "RAG genérico antes de decompor".

**Estado das peças:**
- [CONSTRUÍDO] passo 2 (`resolve_link`), confidence por score, persistência (`link_claim`).
- [CONSTRUÍDO] passo 1 (existe domínio próprio?) — `resolution.resolve_verification_item` lê `domain_of(item)` e checa o registry de domínios.
- [CONSTRUÍDO] a etapa que embrulha os 4 desfechos (`no-domain`/`not-found`/`found-weak`/`found-strong`) e devolve ao usuário (`system_decided: False` sempre). `resolution.py` + `load_domains`; coberto por `test_resolution.py`; demo end-to-end no source graph 'lei' do projeto 02.
- [A CONSTRUIR] passo 2a (lazy decompose dirigido pela dúvida) — **hipótese forte do RAG**. O hook `on_not_found(item, entry)` em `resolve_verification_item` já é o ponto de entrada: recebe o item no `not-found`, deve recuperar a seção relevante do doc, decompor on-demand (extractor modo legal), e devolver uma resolução atualizada. É o ÚNICO ponto que pode usar RAG/LLM. **Próximo tijolo.**

**Pré-requisito [CONSTRUÍDO]:** o `verification_item` agora é objeto `{text, domain, critical}` (forma A), onde `domain` ∈ `lei | engenharia | financeiro | null` é o endereço dimensional. Gate emite no novo schema; `score.py`/`linking.py` aceitam objeto e string legada (retrocompat, sem migração); `linking.domain_of(item)` lê o endereço pro passo 1. Coberto por `test_domain.py`. **Passo 1 + wrapper dos 4 desfechos: CONSTRUÍDOS** (`resolution.py`, ver abaixo). **Próximo tijolo:** passo 2a (lazy decompose via hook `on_not_found`).

**Anti-regressão:** a ancoragem continua substring exato; a verdade continua humana; o `confirms/refutes` por negação-XOR é pista rasa de propósito (não confiar como veredito). Ver §5.1, §7 e [`GLOSSARY.md`].

> Nota de honestidade: o **motor determinístico** — peso, ancoragem da constelação-lei, sobreposição dimensional, propagação cross-constelação, log de eventos — saiu do conceito e virou **código testado** (pytest, 17/17). O que **ainda é só conceito**: a visualização (água/montanha/7 estágios) e o fluxo end-to-end num projeto real. A elegância do modelo não prova que é útil — o próximo passo é construir algo que sirva ao autor no uso real, e descobrir o valor usando.