# Constelação — o modelo conceitual

A metáfora visual e mental do método. A renderização é **direta do cálculo de peso** — não é camada separada; os estágios emergem se o peso for computado certo. Vocabulário em [glossary.md](glossary.md); decisões duras nos [ADRs](../adr/).

## Constelação como água — a representação visual

A constelação é um campo onde cada ponto (claim) assenta numa **profundidade contínua determinada pelo peso (score)**. Não há faixas fixas — é água. Conceito por natureza boia raso; item muito resolvido (ex: código) afunda.

- **Derivar mantém o filho perto do pai** (herança de peso) — cadeia coesa.
- **Resolver afunda** o ponto (ganha peso).
- **Ideia nova reabre o ponto que toca** → sobe (reflutua); não cria ponto distante.
- A **onda** (relevo irregular) vem de pontos em estágios diferentes no mesmo instante.
- **Diagnóstico embutido:** sobe sozinho = mudança pontual; sobe arrastando os filhos = estrutural.

## Os sete estágios da montanha

0. **Plano** — grid liso (tudo no zero). 1. **Irregular** — primeiras ideias. 2. **Mais irregular** — primeiras expansões. 3. **Guarda-chuva** — densidade + expansões organizando. 4. **Montanhoso** — muitas cadeias, picos e vales. 5. **Montanha (de longe)** — base larga (muito derivou da raiz), topo estável. 6. **Cicatriz** — emenda disruptiva **desfaz resolução**: rasga névoa na coluna atingida (largura = alcance). 7. **Cicatriz preenchida** — reabertos re-resolvidos; a coluna reganha massa, possivelmente com forma nova.

## Dimensões sobrepostas — constelações por domínio

Múltiplas constelações para o mesmo projeto, uma por domínio (ideia, lei, financeiro, engenharia). **Mesmo motor** (claims + peso + cicatriz). Diferem na origem e direção:
- **Ideia nasce de cima** (o conceito) e desce derivando (wireframe → código).
- **Lei nasce de baixo** (texto promulgado, denso) e propaga pra cima quando uma emenda entra.
- Mesma cicatriz, sentidos opostos. Os `[VERIFICAR]` (verification_items) são **pontes entre dimensões**, carregando o endereço dimensional de onde a resposta mora. Ver [ADR-007](../adr/007-cross-graph-linking-sob-demanda.md).

## Construção de mão dupla

- **Cima → baixo (ideia):** o expander projeta pontos mais fundos a partir de pais com peso suficiente. Filho herda peso do pai.
- **Baixo → cima (lei):** emenda entra por baixo e propaga a perda de peso pela cadeia.

Simetria: alteração na lei impacta a constelação como ideia nova impacta o projeto — abre cicatriz, propaga, exige re-resolução. Ver [spec/propagation](../specs/propagation.md).
