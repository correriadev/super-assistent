# Super Assistente de Validação de Projetos — Contexto Completo

> **Leia isto primeiro.** Documento único e autossuficiente para iniciar o repositório. Compila o que o projeto é, o que foi validado empiricamente, o que ainda é hipótese, como os agents funcionam, e o que fazer a seguir. Escrito para que outra pessoa (ou outra instância de IA) entenda o projeto inteiro sem contexto prévio.
>
> **Regra que governa o documento:** tudo é marcado **[VALIDADO]** (testado de fato) ou **[VISÃO]** (hipótese não testada). Não confunda os dois. A fatia validada é pequena e real; a visão é grande e não-provada. Manter a separação honesta foi a disciplina central que produziu este projeto.

---

## 1. O que é, em uma frase

Um **interrogador adversarial de decisões de projeto**: recebe uma ideia, quebra em afirmações discretas (claims), e aponta onde cada uma está mal-fundamentada — sem bajular e, crucialmente, **sem fingir saber o que não sabe** (separa o que pode julgar do que precisa mandar verificar).

## 2. O problema que ataca

Quem decide um produto registra decisões como se fossem fundamentadas quando frequentemente não são. Três falhas recorrentes:

1. **Decisão sem porquê** — "vamos cobrar por cartão", afirmado como lei, sem a razão.
2. **Fato presumido** — "a LGPD exige isso", afirmação sobre o mundo tratada como verdade sem verificação. (A mais traiçoeira: soa informada.)
3. **Vagueza operacional** — "público de pequeno e médio porte", termo que ninguém consegue operacionalizar.

Ferramentas de IA comuns **pioram** a falha 2: endossam o fato presumido com confiança. Em teste real, 3 de 4 modelos confirmaram que "a LGPD exige residência nacional de dados" — **falso** (art. 33 permite transferência internacional via cláusulas-padrão). Um assistente que concorda com confiança é pior que nenhum: dá falsa sensação de rigor. **[VALIDADO]**

## 3. O núcleo: a fronteira que distingue este produto

A peça que separa isto de "pedir crítica a um chatbot" é uma **fronteira rígida** entre dois tipos de julgamento:

- **Estrutural** (a lógica da afirmação) — falta justificativa? o termo é vago? a modalidade foi respeitada? → o assistente **decide sozinho, com confiança**. **[VALIDADO como confiável]**
- **Factual** (afirmações sobre o mundo) — a LGPD exige isso? o mercado está saturado? → o assistente é **proibido de afirmar** e **obrigado a sinalizar** para verificação externa (`[VERIFICAR]`). **[VALIDADO como confiável]**

Esta separação é o ativo central. Não é a interface, não é o grafo. É o fato de que o assistente sabe a diferença entre o que pode julgar e o que precisa mandar verificar. Foi a lição mais cara do projeto e nasceu de um erro real (a LGPD).

## 4. O que foi VALIDADO (evidência, não aspiração)

Testado com claims reais de um projeto do autor (Hub Contábil — SaaS de automação para escritórios de contabilidade no Brasil), em múltiplos modelos (Claude Opus/Sonnet/Haiku, Gemini, DeepSeek) e dois harnesses (Claude Code, opencode):

- **[VALIDADO] Discrimina.** Dá vereditos diferentes por tipo de problema, em vez de reprovar tudo igual. (Falhou nas primeiras versões — reprovava 100% — e foi corrigido.)
- **[VALIDADO] Fronteira factual estável e correta cross-model.** A afirmação sobre a LGPD foi marcada para verificação — nunca endossada — em todos os modelos após a correção. É o componente mais robusto do sistema.
- **[VALIDADO] Detecção de ausência de justificativa é estável.** Claims sem justificativa recebem `PRECISA-JUSTIFICAR` consistentemente entre rodadas e modelos.
- **[VALIDADO] Modo socrático não amolece o rigor.** Ausência de justificativa vira pergunta (convite); furo lógico ainda trava (`CONTESTADO`); fato não-verificado ainda bloqueia (`PENDENTE-VERIFICAÇÃO`). Suavização cirúrgica, não geral.
- **[VALIDADO] Precedência de veredito estável.** Quando um claim tem vagueza + fato pendente, `INCOMPLETO` vence. Confirmado estável em rodadas repetidas.

### Limites honestos da validação
- Testado apenas na ideia **do próprio autor** — o avaliador mais leniente possível.
- **A utilidade para um terceiro é a hipótese central ainda NÃO testada.** É o que decide se há produto.
- O **decompositor** (quebra a ideia em claims) é instável: inferia modalidade inconsistente entre rodadas. **Mitigação aplicada:** modalidade agora é setada por humano, não inferida.
- Testado em ~6 claims, um nível. Nada sobre escala ou transição entre níveis.

## 5. Vocabulário do modelo

- **Claim** — afirmação/decisão discreta. Unidade do sistema.
- **Binding (modalidade)** — `vinculante` (lei do projeto, exige justificativa) · `ilustrativo` (exemplo, não exclui nada) · `default-sobrescrevivel` (escolha inicial que pode evoluir). **Setado por humano, nunca inferido** (decisão validada pela instabilidade observada quando inferido).
- **Veredito** — resultado da avaliação. Seis rótulos, precedência fixada (o primeiro que se aplica vence):
  1. `CONTRADIZ-NIVEL-ACIMA` — só em claims derivados; viola restrição declarada do nível acima. **[VISÃO — não testado]**
  2. `PRECISA-JUSTIFICAR` — vinculante/default sem justificativa. Convite a fundamentar, com pergunta de elicitação. **[VALIDADO]**
  3. `INCOMPLETO` — vagueza operacional (vence fato pendente se ambos presentes). **[VALIDADO]**
  4. `PENDENTE-VERIFICAÇÃO` — justificativa presente, repousa em fato não-verificado. **[VALIDADO]**
  5. `CONTESTADO` — justificativa presente e completa, mas com furo lógico interno. **[VALIDADO]**
  6. `PASSA` — de pé, sem ausência, sem vagueza, sem fato pendente. **[VALIDADO]**
- **`[VERIFICAR]`** — item factual sinalizado em vez de afirmado. Formulado como **pergunta aberta**, nunca hipótese embutida (que ancoraria quem verifica). Acompanha fonte sugerida.

## 6. Arquitetura: os agents

> Núcleo de 5 (decompositor, gate, tradutor, expansor, orquestrador) + 2 de borda: **briefista** (passo 0, antes do motor) e **conselheiro** (modo adversarial avulso).

Runtime: **Claude Code** (foco único atual; opencode adiado — ver ROADMAP) com agents em markdown em `agents/`. Sem código de integração com LLM próprio — tentativas disso quebraram repetidamente no ambiente e foram abandonadas. Dados em arquivos JSON, sem banco.

### Fluxo de um nível (ideação)
```
ideia (texto livre)
   │
   ▼
[decompositor] → claims.json (binding: null)
   │
   ▼
HUMANO atribui modalidade em lote   ← passo de controle, rápido mas não removível
   │
   ▼
[gate] ×N em paralelo → vereditos.json
   │
   ▼
[tradutor] → alerta sóbrio (a saída que o humano lê)
   │
   ▼
HUMANO resolve os flags
```

### Transição entre níveis (sob comando explícito) — [VISÃO, recém-construído, NÃO testado]
```
"desce para concepção"
   │
   ▼
orquestrador checa pré-condição (nenhum claim em aberto)
   │
   ▼
[expansor] → claims do novo nível, cada um marcado:
   [Implicado]   — o pai força este filho (já autorizado)
   [Compatível]  — coerente, mas proposta do expansor (precisa OK)
   [Especulativo]— invenção do expansor (precisa decisão explícita)
   + deriva_de + restricao_do_pai
   │
   ▼
HUMANO revisa a expansão (corta/aprova os [Especulativo])
   │
   ▼
[gate] avalia + checa CONTRADIZ-NIVEL-ACIMA contra restricao_do_pai
```

### Papel de cada agent
- **decompositor** — quebra a ideia em 3-6 claims; extrai justificativa do texto ou marca `null`; **nunca decide binding** (sempre `null`).
- **gate** — avalia UM claim isolado; aplica a fronteira estrutural/factual; emite um dos seis vereditos. O ativo central.
- **tradutor** — converte vereditos técnicos em alerta sóbrio-concreto para o stakeholder. Triagem por gravidade (não número fixo), valoração conceitual ("você deixa de ganhar com X"), **revela mas NUNCA sugere solução**, sem jargão de intimidade, sem inventar número. **[VISÃO — escrito, não testado]**
- **expansor** — gera claims do próximo nível a partir dos resolvidos; marca grau de derivação e declara `restricao_do_pai`. **[VISÃO — não testado]**
- **orquestrador** — maestro; roda o ciclo, coordena a transição, mantém os pontos de controle humano.
- **briefista** — passo 0, antes do decompositor: tira ideia vaga da névoa → `ideia.md` na voz da pessoa. Pergunta, **nunca propõe decisão** (justificativa fantasma é o pior modo de falha, um andar acima do gate). [VISÃO — escrito, não testado]
- **conselheiro** — conselheiro adversarial avulso (fora do pipeline): testa raciocínio, não confirma. Mesma fronteira fato/lógica do gate, sem bajulação. [VISÃO — escrito, não testado]

## 7. Decisões de design travadas (com a razão)

- **Modalidade por humano, não inferida** — porque inferida é instável (observado).
- **Fronteira factual rígida** — o assistente nunca afirma fato; o erro da LGPD provou o custo.
- **Presença de justificativa é binária** — proibido adjetivo de mérito ("robusta"); adjetivo é juízo factual disfarçado.
- **Tradutor revela, não sugere** — sugerir solução é fingir saber o que não sabe (mesmo pecado da LGPD) e soa presunçoso ao especialista do domínio.
- **Transição sob comando, com pré-condição** — não desce de nível com claim em aberto; o concreto não nasce de fundação instável.
- **Detecção de contradição ancorada** (Forma 2) — o gate checa contra `restricao_do_pai` declarada pelo expansor, não julga contradição no vácuo (que seria instável, conforme literatura).

## 8. Visão completa — [VISÃO, NADA validado]

Direção imaginada, documentada para não se perder, separada para não se disfarçar de pronto:

- **Grafo de claims com tiers de abstração** — da concepção ao código, claims ligados por arestas tipadas. A camada abstrata tem "autoridade de coerência": nada concreto diverge dela em silêncio.
- **Propagação de stale** — quando um claim muda, descendentes que dependem dele são marcados suspeitos. *A mecânica determinística foi testada em código isolado (passou), mas a propagação julgada por modelo em cadeia indireta é onde a literatura (paper STALE, 2026) mostra modelos caindo para ~14% — risco real não endereçado.*
- **Contradição ascendente** — o concreto que não satisfaz o abstrato dispara sinal que força revisão na origem. (O `CONTRADIZ-NIVEL-ACIMA` é a primeira peça concreta disso.)
- **Regra dura** — o concreto não avança sem autorização do abstrato. Escolha deliberada.
- **Interface visual** — originalmente uma "constelação"/matriz de níveis. **Explicitamente adiada para último — o valor não está nela.**
- **Memória de projeto, curadoria de skills** — não desenhados.

## 9. Referências externas relevantes

- **BMAD-METHOD** (github.com/bmad-code-org/BMAD-METHOD) — framework de planejamento agêntico, 48k estrelas. Filosofia OPOSTA: ele **gera** (a IA te guia produzindo artefatos); este projeto **fura** (interroga o que foi produzido). Útil como referência de design de workflow (escala-adaptativa, papéis-especialistas), NÃO como dependência. O nicho deste projeto é ser o controle de qualidade adversarial que um gerador não tem.
- **TDD como adversário** — observação do autor: escrever testes antes funciona como adversário do agente de código, evitando alucinação. É o mesmo princípio deste projeto aplicado ao nível do código: um adversário-especificação que existe antes da geração e que a geração deve satisfazer. Sugere que a tese ("adversário contido em cada nível") tem prova de conceito em pelo menos um nível.

## 10. O próximo passo que decide tudo

Tudo acima é **o motor**. A pergunta que ainda não tem resposta e que separa "ferramenta pessoal" de "produto":

> **A crítica, traduzida e sóbria, faz alguém que NÃO é o autor parar e dizer "não tinha visto isso"?**

Nenhuma quantidade de mecânica nova responde isso. O teste é: rodar a ideia de um terceiro (contador, fundador) pelo sistema e ver se um alerta muda uma decisão dele. Perfil de usuário de referência (do autor, 10 anos de experiência): profissional ocupado, direto, ancorado em documento/processo; confia em quem fala pouco e certo, desconfia de bajulação; quer saber o que não viu e o que custa, em poucas palavras.

**Anti-meta registrada:** não construir grafo/propagação/interface antes do teste com terceiro. Construir mais sistema é a fuga confortável quando o desconforto real é interpessoal (arriscar ouvir "e daí?"). Isso aconteceu repetidamente durante o design e foi corrigido cada vez.

## 11. Como começar o repositório

1. Os agents vão em `agents/` (decompositor, gate, tradutor, expansor, orquestrador + briefista, conselheiro).
2. JSONs por projeto em `projetos/<nome>/` (claims, vereditos, claims-nivel-N). Sem banco — pasta + JSON é suficiente até haver volume real.
3. Estrutura para testes pessoais: uma pasta por projeto (`projetos/<nome>/` com ideia.md + os JSONs), versionada em git — histórico de graça, consultável com grep quando preciso. Ideias livres ficam em `ideias/`.
4. Para rodar: abra o Claude Code, fale com o orquestrador, dê a ideia.
5. **Primeiro teste a fazer:** rodar um projeto descendo de ideação para concepção e **plantar uma contradição de propósito** (um claim de concepção que viola a ideação). Se o gate marcar `CONTRADIZ-NIVEL-ACIMA`, a tese central funcionou fora da cabeça do autor pela primeira vez. Se não, a `restricao_do_pai` declarada pelo expansor é o elo a investigar (é o mais novo e mais provável de estar torto).

## 12. Tecnologia: o que NÃO adicionar ainda

Cada uma resolve um problema que o projeto ainda não tem. Adicionar antes da dor é over-engineering:
- **SQLite** — só quando reabrir projetos antigos virar comum e arquivo solto incomodar. Primeiro upgrade legítimo, ainda distante.
- **Banco de grafo** — só quando o grafo [VISÃO] existir de fato com muitos nós. Não antes do grafo existir.
- **RAG / cache** — provavelmente nunca para este produto. Não há problema de recuperação (ideia + claims cabem no contexto) nem repetição cara a cachear.

Gatilho geral: **adicione tecnologia quando a dor aparecer, nunca antes.**