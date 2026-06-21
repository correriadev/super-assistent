// Validação de entrada — contrato do ciclo 3. Acumula todos os erros (não short-circuit).

export function validate(entrada) {
  const erros = [];
  if (!(entrada.faturamentoBruto >= 0)) erros.push("faturamentoBruto must be >= 0");
  if (!(entrada.recolhimentoOffsetDias > 0)) erros.push("recolhimentoOffsetDias must be > 0");
  if (!(entrada.mesesSimulacao > 0)) erros.push("mesesSimulacao must be > 0");
  return { valido: erros.length === 0, erros };
}
