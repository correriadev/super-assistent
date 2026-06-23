# A Cidade — o modelo visual (2.5D iso, de ponta-cabeça)

A metáfora visual do método. Substitui a antiga "constelação/água/montanha": o estado do projeto é uma **cidade** vista em perspectiva 3/4 (isométrica, tipo jogo), com a câmera de ângulo fixo — legível para leigo, sem a desorientação do 3D livre. Implementado em `viz/iso.html`; dados gerados por `viz/export_points.py`.

## De ponta-cabeça — upstream em cima, downstream embaixo

A cidade é **invertida** de propósito:

- **Topo = céu = névoa.** É onde moram as **ideias** (upstream): abstrato, menos concretizado, "flutua na névoa". A **presidência** (de onde saem as ideias) fica no alto. A névoa é mais densa no céu — decks translúcidos marcam isso.
- **Chão = trabalhadores.** Embaixo ficam os andares concretos (downstream): testes, **código**. É onde o trabalho assenta no real.

Ordem dos andares (do céu pro chão): **ideação → concepção → arquitetura → cenários → testes → código**. Subir (↑) vai em direção às ideias/névoa; descer (↓) vai pro código/chão.

## Prédios, andares, setores — domínios × subdomínios

- **Prédio = domínio** (uma fonte de grounding própria: o simulador, a lei, o AWS). Os prédios formam um **quarteirão** — a cidade.
- **Andar = nível** (a etapa de concretude). Um prédio é a pilha de andares do seu domínio.
- **Setor = subdomínio.** Um andar pode ter **mais de um setor** lado a lado — ex: no andar de testes, **unitários e e2e coexistem** como setores distintos. Setor = `subdomain` do nó (na falta, o próprio nível).
- **Passarelas (ciano) = links cross-domínio.** Um nó de um prédio referencia um nó exposto de outro prédio — a ponte liga os prédios. (Ex: o simulador precisa de um gateway definido no prédio AWS.)

## Peso, foco e nível de detalhe

- **Tamanho do nó = peso** (score). Afundado/resolvido pesa mais; leve/aberto flutua na névoa.
- **Foco de andar:** o andar em foco fica **nítido**; os demais **escurecem** (mais ainda com zoom). Resolve o "espaguete" de arestas cruzando andares.
- **LOD (level of detail):** **longe = caixas** coloridas por setor (a cidade como blocos legíveis); **perto (zoom, espaço) = esferas** (os nós individuais) + arestas. Caixa↔esfera faz crossfade pelo zoom.

## Controles (de jogo)

`← → / A D` giram a cidade · `↑ ↓ / W S` sobem/descem de andar · **espaço** (segura) = zoom vai-vem (caixas→esferas) · `esc` = visão geral · hover = detalhe.

## Cores

Andares por nível: ideação azul · concepção verde · arquitetura roxo · cenários rosa · testes âmbar · código vermelho · lei dourado. Arestas: posse cinza (árvore interna) · referência âmbar · **ponte cross-domínio ciano**. Anel ciano = nó **exposto** (interface pública do domínio).

## Outras vistas

`viz/index.html` = 3D livre (orbit, power-view). `viz/2d.html` = force-directed plano (estilo Obsidian). A `iso.html` (cidade) é a vista principal, pensada pra leigo.
