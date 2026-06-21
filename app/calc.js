// Núcleo de cálculo do simulador — função PURA (contratos do ciclo 3).
// Mesma alíquota nos dois regimes; a diferença é só o TIMING do tributo.

export const ENUM_EVENTO = ["RECEBIMENTO", "RECOLHIMENTO", "SEGREGACAO_SPLIT"];

// Arredondamento bancário (half-to-even) a 2 casas. Tie é raro em fp; guard de eps.
export function round2(x) {
  const scaled = x * 100;
  const floor = Math.floor(scaled);
  const frac = scaled - floor;
  let r;
  if (Math.abs(frac - 0.5) < 1e-9) r = floor % 2 === 0 ? floor : floor + 1;
  else r = Math.round(scaled);
  return r / 100;
}

function isoDate(baseISO, dias) {
  const d = new Date(baseISO + "T00:00:00Z");
  d.setUTCDate(d.getUTCDate() + dias);
  return d.toISOString().slice(0, 10);
}

const evento = (dia, data, tipoEvento, valor, saldoAcumulado) => ({ dia, data, tipoEvento, valor, saldoAcumulado });

/**
 * @returns {{regimeAtual: Array, regimeSplit: Array}} duas Timelines de mesmo schema.
 * ponty: mesesSimulacao entra no contrato/validação mas a fatia modela 1 ciclo de venda;
 * multiplicar por meses é o próximo passo se a simulação recorrente importar.
 */
export function calculateCashFlow(faturamentoBruto, aliquota, recolhimentoOffsetDias, mesesSimulacao = 1, dataInicial = "2026-01-01") {
  const bruto = round2(faturamentoBruto);
  const tributo = round2(faturamentoBruto * aliquota);

  const regimeAtual = [evento(0, isoDate(dataInicial, 0), "RECEBIMENTO", bruto, bruto)];
  const regimeSplit = [evento(0, isoDate(dataInicial, 0), "RECEBIMENTO", bruto, bruto)];

  if (tributo > 0) {
    // atual: tributo fica em caixa e só sai no recolhimento (dia offset)
    regimeAtual.push(evento(recolhimentoOffsetDias, isoDate(dataInicial, recolhimentoOffsetDias), "RECOLHIMENTO", -tributo, round2(bruto - tributo)));
    // split: tributo segregado já na liquidação (dia 0)
    regimeSplit.push(evento(0, isoDate(dataInicial, 0), "SEGREGACAO_SPLIT", -tributo, round2(bruto - tributo)));
  }
  return { regimeAtual, regimeSplit };
}

/** Saldo de caixa acumulado num dia d = saldo do último evento com dia <= d (0 se nenhum). */
export function saldoEm(timeline, dia) {
  let saldo = 0;
  for (const e of timeline) if (e.dia <= dia) saldo = e.saldoAcumulado;
  return saldo;
}

/** Diferencial de caixa: o "buraco" = pico da diferença entre os regimes, absoluto e % do bruto. */
export function metricaDiferencial(resultado, faturamentoBruto) {
  const dias = [...resultado.regimeAtual, ...resultado.regimeSplit].map((e) => e.dia);
  let absoluto = 0;
  for (const d of dias) {
    const dif = saldoEm(resultado.regimeAtual, d) - saldoEm(resultado.regimeSplit, d);
    if (dif > absoluto) absoluto = dif;
  }
  absoluto = round2(absoluto);
  const percentual = faturamentoBruto > 0 ? round2(absoluto / faturamentoBruto) : 0;
  return { absoluto, percentual };
}
