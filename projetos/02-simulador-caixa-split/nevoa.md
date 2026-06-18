# Névoa do contador — input bruto (pré-briefista)

> Transcrição crua que alimentou o briefista. Voz do humano simulado (contador).
> Guardada pra recuperação: é a fonte de onde o `ideia.md` foi estenografado.
> Cenário ancorado no artigo `ideias/pub_780677977.pdf` (split payment / LC 214/2025).

## Névoa inicial

"Sou contador, escritório próprio, atendo umas 40 empresas pequenas e médias — prestadores de serviço, comércio, uns de indústria leve. Tô preocupado com uma coisa da Reforma Tributária que meus clientes ainda não entenderam: o split payment. Pelo que li (LC 214/2025, arts. 31 a 35), o IBS e a CBS vão ser segregados na hora da liquidação financeira da venda e mandados direto pro cofre público — o dinheiro do imposto nem entra mais no caixa do meu cliente. Hoje não é assim: hoje ele recebe o bruto, segura o tributo no caixa e recolhe depois. Esse intervalo é capital de giro pra ele, mesmo que ele não pense nisso conscientemente. Quando o split entrar, esse intervalo some. Quem tem margem apertada e ciclo financeiro longo vai sentir no fluxo de caixa. Quero construir um simulador que mostra pro cliente, antes de doer, o tamanho do buraco: dado o faturamento dele, quanto sai na hora como IBS/CBS no split, e como isso muda o caixa comparado com o regime de hoje."

## Perguntas do briefista e respostas do contador

**P: quem sente essa dor com mais força?**
R: "Meus clientes de margem estreita e ciclo financeiro longo. É exatamente esse perfil que o split machuca, porque é deles que o intervalo entre receber e recolher fazia mais diferença. Começo por esses. Os de margem gorda aguentam, deixo pra depois."

**P: o que exatamente o simulador compara?**
R: "Dois cenários lado a lado pro mesmo faturamento: o regime de hoje, onde o tributo entra no caixa e sai depois, e o split, onde o IBS/CBS sai no instante da liquidação. A dor que eu quero tornar visível é a supressão desse intervalo — é isso que comprime o capital de giro. Se o simulador não mostrar a diferença no tempo, não serve."

**P: de onde vem a alíquota que entra na conta?**
R: "Idealmente a exata do split padrão, B2B, que o sistema identifica certo. Mas eu nem sempre vou ter a apuração exata na simulação. Aí eu uso percentual predefinido — o split simplificado da própria lei opera assim quando a apuração em tempo real não dá. Uso esse percentual como aproximação quando não tenho o número fino."

**P: e venda parcelada, como entra?**
R: "Segrego proporcional em cada parcela. A própria regra do split manda recolher proporcionalmente em cada parcela na data da liquidação dela, então o simulador tem que refletir isso, senão superestima a saída no mês da venda."

**P: como você vai cobrar por isso?**
R: "Não sei ainda. Talvez embuta no honorário que já cobro. Não tenho isso fechado." — *ausência real, não fundamentada.*

**P: tem nome?**
R: "'Split' porque a ideia gira em torno do split payment. Sinceramente é só o que me soa, não pensei muito." — *ausência real, sem razão forte.*
