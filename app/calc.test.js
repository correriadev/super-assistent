// Cenários do ciclo 4 (nivel-3) como testes — TDD. Sem dependência: node:test + node:assert.
import { test } from "node:test";
import assert from "node:assert/strict";
import { calculateCashFlow, metricaDiferencial, saldoEm, ENUM_EVENTO } from "./calc.js";

const ev = (tl, tipo) => tl.find((e) => e.tipoEvento === tipo);

test("regime atual: recebe dia 0, recolhe no offset (tributo em caixa até lá)", () => {
  const { regimeAtual } = calculateCashFlow(1000, 0.27, 30);
  assert.deepEqual(ev(regimeAtual, "RECEBIMENTO"), { dia: 0, data: ev(regimeAtual, "RECEBIMENTO").data, tipoEvento: "RECEBIMENTO", valor: 1000, saldoAcumulado: 1000 });
  const rec = ev(regimeAtual, "RECOLHIMENTO");
  assert.equal(rec.dia, 30);
  assert.equal(rec.valor, -270);
  assert.equal(rec.saldoAcumulado, 730);
});

test("regime split: tributo sai no dia 0 (segregação na liquidação)", () => {
  const { regimeSplit } = calculateCashFlow(1000, 0.27, 30);
  const seg = ev(regimeSplit, "SEGREGACAO_SPLIT");
  assert.equal(seg.dia, 0);
  assert.equal(seg.valor, -270);
  assert.equal(seg.saldoAcumulado, 730);
});

test("diferencial = 270 durante a janela de retenção, 0 depois do recolhimento", () => {
  const r = calculateCashFlow(1000, 0.27, 30);
  const dif = (d) => saldoEm(r.regimeAtual, d) - saldoEm(r.regimeSplit, d);
  assert.equal(dif(0), 270);
  assert.equal(dif(15), 270);
  assert.equal(dif(30), 0); // tributo recolhido no dia 30
});

test("métrica diferencial: absoluto 270 e percentual 0.27 sobre o bruto", () => {
  const r = calculateCashFlow(1000, 0.27, 30);
  const m = metricaDiferencial(r, 1000);
  assert.equal(m.absoluto, 270);
  assert.equal(m.percentual, 0.27);
});

test("alíquota 0: sem recolhimento, os dois regimes ficam idênticos", () => {
  const { regimeAtual, regimeSplit } = calculateCashFlow(1000, 0, 30);
  assert.equal(regimeAtual.length, 1);
  assert.equal(regimeSplit.length, 1);
  assert.equal(regimeAtual[0].tipoEvento, "RECEBIMENTO");
  assert.deepEqual(regimeAtual, regimeSplit);
});

test("offset 1 dia: diferencial 270 no dia 0, 0 no dia 1", () => {
  const r = calculateCashFlow(1000, 0.27, 1);
  const dif = (d) => saldoEm(r.regimeAtual, d) - saldoEm(r.regimeSplit, d);
  assert.equal(dif(0), 270);
  assert.equal(dif(1), 0);
});

test("precisão: tributo arredondado a 2 casas; nenhum saldo com >2 decimais", () => {
  const r = calculateCashFlow(1000.555, 0.27, 30);
  assert.equal(ev(r.regimeAtual, "RECOLHIMENTO").valor, -270.15);
  for (const tl of [r.regimeAtual, r.regimeSplit])
    for (const e of tl)
      assert.ok(Number.isInteger(Math.round(e.saldoAcumulado * 100)) && (e.saldoAcumulado * 100) === Math.round(e.saldoAcumulado * 100), `>2 casas: ${e.saldoAcumulado}`);
});

test("datas em ISO 8601 (YYYY-MM-DD)", () => {
  const r = calculateCashFlow(1000, 0.27, 30);
  for (const tl of [r.regimeAtual, r.regimeSplit])
    for (const e of tl) assert.match(e.data, /^\d{4}-\d{2}-\d{2}$/);
});

test("tipoEvento sempre um do enum fechado", () => {
  const r = calculateCashFlow(1000, 0.27, 30);
  for (const tl of [r.regimeAtual, r.regimeSplit])
    for (const e of tl) assert.ok(ENUM_EVENTO.includes(e.tipoEvento), `fora do enum: ${e.tipoEvento}`);
});

test("pureza: mesma entrada → mesmo resultado, sem efeito colateral", () => {
  const a = calculateCashFlow(1000, 0.27, 30);
  const b = calculateCashFlow(1000, 0.27, 30);
  assert.deepEqual(a, b);
});
