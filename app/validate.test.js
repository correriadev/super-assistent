// Cenários de validação (ciclo 4) como testes — TDD.
import { test } from "node:test";
import assert from "node:assert/strict";
import { validate } from "./validate.js";

const base = { faturamentoBruto: 1000, aliquota: 0.27, recolhimentoOffsetDias: 30, mesesSimulacao: 1 };

test("faturamento 0 é válido (>= 0)", () => {
  assert.deepEqual(validate({ ...base, faturamentoBruto: 0 }), { valido: true, erros: [] });
});

test("faturamento negativo: inválido", () => {
  assert.deepEqual(validate({ ...base, faturamentoBruto: -100 }), {
    valido: false, erros: ["faturamentoBruto must be >= 0"],
  });
});

test("offset zero: inválido", () => {
  assert.deepEqual(validate({ ...base, recolhimentoOffsetDias: 0 }), {
    valido: false, erros: ["recolhimentoOffsetDias must be > 0"],
  });
});

test("offset negativo: inválido", () => {
  assert.deepEqual(validate({ ...base, recolhimentoOffsetDias: -10 }), {
    valido: false, erros: ["recolhimentoOffsetDias must be > 0"],
  });
});

test("meses zero: inválido", () => {
  assert.deepEqual(validate({ ...base, mesesSimulacao: 0 }), {
    valido: false, erros: ["mesesSimulacao must be > 0"],
  });
});

test("múltiplos erros acumulam em um array", () => {
  assert.deepEqual(validate({ faturamentoBruto: -100, aliquota: 0.27, recolhimentoOffsetDias: -10, mesesSimulacao: 0 }), {
    valido: false,
    erros: ["faturamentoBruto must be >= 0", "recolhimentoOffsetDias must be > 0", "mesesSimulacao must be > 0"],
  });
});
