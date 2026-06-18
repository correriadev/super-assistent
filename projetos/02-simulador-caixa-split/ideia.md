# Simulador de caixa — split payment

Sou contador, tenho escritório próprio e atendo umas 40 empresas pequenas e médias. O que me preocupa é o split payment da Reforma Tributária (LC 214/2025, arts. 31 a 35): o IBS e a CBS vão ser segregados na liquidação financeira da venda e mandados direto pro cofre público — o imposto nem entra mais no caixa do meu cliente. Hoje ele recebe o bruto, segura o tributo e recolhe depois; esse intervalo é capital de giro. Quando o split entrar, o intervalo some, e quem tem margem apertada e ciclo longo sente no fluxo de caixa. Quero um simulador que mostra pro cliente, antes de doer, o tamanho do buraco.

## Público — por quem começo

Começo pelos clientes de margem estreita e ciclo financeiro longo. É esse perfil que o split machuca, porque é deles que o intervalo entre receber e recolher fazia mais diferença.

## O que o simulador compara

Dois cenários lado a lado pro mesmo faturamento: o regime de hoje, onde o tributo entra no caixa e sai depois, e o split, onde o IBS/CBS sai na liquidação. A dor que eu quero tornar visível é a supressão do intervalo no tempo. Se não mostrar a diferença no tempo, não serve.

## De onde vem a alíquota

Idealmente a alíquota exata do split padrão B2B. Mas nem sempre vou ter a apuração exata na simulação; aí uso percentual predefinido — o split simplificado da própria lei opera assim quando a apuração em tempo real não dá. Uso como aproximação.

## Venda parcelada

Segrego proporcional em cada parcela, na data da liquidação de cada uma. A regra do split manda recolher proporcional em cada parcela; senão superestima a saída no mês da venda.

## Estorno e cancelamento (chargeback)

Tem que reverter no simulador. Se o imposto já saiu no split e a venda é cancelada ou estornada, aquele valor volta a contar como caixa. Se eu não tratar estorno e cancelamento, o simulador mostra um buraco maior do que o real e assusta o cliente à toa.

## Fonte dos dados de faturamento

Puxo da própria escrituração que eu já faço pra esses clientes. Eu já tenho o faturamento mensal deles na minha contabilidade, então puxo de lá em vez de pedir pra eles digitarem.

## Cobrança

Não sei ainda. Talvez embuta no honorário. Não tenho fechado.

> [ausência real — não fundamentou como vai cobrar; "talvez no honorário" é cogitação, não decisão]

## Nome

"Split", porque gira em torno do split payment. É só o que me soa.

> [ausência real — sem razão forte pro nome; só o que lhe soou no momento]
