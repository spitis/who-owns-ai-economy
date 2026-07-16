"use strict";

const fs = require("fs");
const path = require("path");
const models = require("./models.js");

function parseCsv(filename) {
  const lines = fs.readFileSync(filename, "utf8").trim().split(/\r?\n/);
  const fields = lines[0].split(",");
  return lines.slice(1).map(line => {
    const values = line.split(",");
    return Object.fromEntries(fields.map((field, index) => [field, values[index]]));
  });
}

function close(actual, expected, tolerance, label) {
  if (Math.abs(actual - expected) > tolerance) {
    throw new Error(`${label}: got ${actual}, expected ${expected}`);
  }
}

function nullableClose(actual, expectedText, tolerance, label) {
  if (expectedText === "") {
    if (actual !== null) throw new Error(`${label}: got ${actual}, expected null`);
  } else close(actual, Number(expectedText), tolerance, label);
}

const root = path.resolve(__dirname, "..");
const expectedScenarios = [
  [0.018, 0.055, 0.45], [0.030, 0.0625, 0.35], [0.040, 0.070, 0.30]
];
if (JSON.stringify(models.SCENARIOS.map(row =>
    [row.growth, row.discountRate, row.laborFloor])) !==
    JSON.stringify(expectedScenarios)) {
  throw new Error("published scenario definitions are out of sync");
}
const results = parseCsv(path.join(root, "final", "results.csv"));
for (const scenario of models.SCENARIOS) {
  const rows = models.simulateSimple(scenario);
  const goldenRows = results.filter(row =>
    row.model === "simple_fixed_market_gdp" && row.scenario === scenario.label);
  for (const golden of goldenRows) {
    const actual = rows[Number(golden.year) - 1];
    close(actual.perCapitaPayout, Number(golden.per_capita_payout), 1e-6,
      `simple ${scenario.label} y${golden.year} payout`);
    close(actual.qEnd, Number(golden.public_ownership_q), 5e-10,
      `simple ${scenario.label} y${golden.year} ownership`);
  }
  nullableClose(models.crossingYear(rows, 10000), goldenRows[0].crossing_year_10000,
    1e-6, `simple ${scenario.label} $10k crossing`);
  nullableClose(models.crossingYear(rows, 35000), goldenRows[0].crossing_year_35000,
    1e-6, `simple ${scenario.label} $35k crossing`);
}

for (const scenario of models.SCENARIOS) {
  const result = models.simulateDcf(scenario);
  const goldenRows = results.filter(row =>
    row.model === "payout_dcf" && row.scenario === scenario.label);
  for (const golden of goldenRows) {
    const actual = result.rows[Number(golden.year) - 1];
    close(actual.perCapitaPayout, Number(golden.per_capita_payout), 1e-6,
      `dcf ${scenario.label} y${golden.year} payout`);
    close(actual.qEnd, Number(golden.public_ownership_q), 5e-10,
      `dcf ${scenario.label} y${golden.year} ownership`);
  }
  close(result.markdown, Number(goldenRows[0].dcf_markdown), 5e-10,
    `dcf ${scenario.label} markdown`);
  nullableClose(models.crossingYear(result.rows, 10000), goldenRows[0].crossing_year_10000,
    1e-6, `dcf ${scenario.label} $10k crossing`);
  nullableClose(models.crossingYear(result.rows, 35000), goldenRows[0].crossing_year_35000,
    1e-6, `dcf ${scenario.label} $35k crossing`);
}

console.log("JS golden tests passed for both models");
