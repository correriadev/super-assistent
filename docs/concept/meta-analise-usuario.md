# Meta-análise do usuário — o motor que mostra o caminho que o usuário não vê

**Status:** etapa criativa, recém-aberta. Decifrado de uma fala do autor (2026-06-22). A desenvolver.

## O problema (por que existe)

O usuário não consegue pensar em todos os andares. Ele tem a ideia, mas **não conhece o processo técnico** que a leva até o objetivo — não sabe que um simulador precisa de arquitetura → cenários → testes → código antes das telas. Disso nascem dois riscos opostos:

- **Dar voltas (spinning):** ele churna a mesma ideia no mesmo andar, sem assentar nem avançar — porque não vê quando "está bom o bastante" pra descer, nem pra onde ir.
- **Pular etapas (skipping):** ele cria meia dúzia de ideias e **força o motor a gerar o código das telas direto**, sem passar pelos andares anteriores — porque nem sabe que esses andares existem (ex: as N camadas do simulador).

## O que é a meta-análise

O motor faz uma **análise do próprio usuário e da ideia** — não só dos claims — para tornar **explícito o que normalmente está implícito**:

1. **O objetivo da ideia.** A ideia se expande **até atingir seu objetivo**. Qual é esse objetivo, e ele está claro pro usuário? Quase nunca está. O objetivo define onde o prédio termina.
2. **O caminho (os andares) até lá.** Quais níveis/domínios essa ideia específica precisa atravessar para chegar ao objetivo. Mostrar isso ao usuário = mostrar o prédio inteiro, inclusive os andares ainda vazios.
3. **Onde o usuário está** nesse caminho, e se ele está **dando voltas** ou **tentando pular**.

É metacognição **para** o usuário: o motor sabe a pilha que ele não sabe.

## Nem todo projeto é código denso corporativo

A pilha do simulador (ideação→concepção→arquitetura→cenários→testes→código) é **um template, não a regra**. Muitos projetos nascem como **planejamento, ideação, estratégia, documento** — e terminam num artefato que não é "tela". Um plano de viagem, uma mudança de vida, takes de um filme: cada **tipo de projeto** tem seu próprio conjunto de andares e seu próprio objetivo.

Logo a meta-análise precisa **classificar o tipo de projeto** e escolher (ou montar) o **floor-plan** adequado — não impor o prédio do big-tech a uma ideia que é, na verdade, um planejamento.

## Como conecta ao que já existe

- **Andares = caminho.** A cidade (`concept/cidade.md`) já é o caminho desenhado; falta marcar os **andares vazios que faltam pro objetivo** — a cidade vira o mapa da jornada, não só o estado atual.
- **`descent_gate`** já impede pular andar (descer sobre fundação aberta). A meta-análise dá o **porquê** e mostra os andares que faltam — converte o bloqueio em orientação.
- **Log de eventos + histórico de score** podem detectar **spinning** determinístico (muita revisão no mesmo claim sem o score subir = girando, não avançando).
- É o **valor pro leigo:** o motor guia quem não conhece a pilha — o mesmo momento em que o motor "se vende".

## Perguntas abertas (a desenvolver nesta etapa)

1. **Tipo de projeto → floor-plan:** uma taxonomia de tipos (app, plano, documento, estratégia…) com templates de andares? Quem classifica — o usuário no intake, ou o motor infere?
2. **O objetivo:** o usuário declara (intake) ou o motor propõe e ele confirma? É o objetivo que define o "topo do prédio" e o critério de conclusão.
3. **Detectar spinning sem confundir com refino legítimo:** o sinal é "churn sem ganho de score"? Quantas voltas = alerta? (Determinístico via log, idealmente, LLM só na borda.)
4. **Detectar skipping:** o `descent_gate` já pega; falta a camada que **mostra os andares pulados** e explica o que cada um entrega.
5. **Onde isto vive:** um agente de meta-análise? Um passo no orchestrator? Um painel na cidade?

Relaciona [[descida-de-nivel-parametrizavel-sentir-movimento]] (o usuário precisa SENTIR movimento — aqui ele precisa também VER o caminho e não girar em falso).
