(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.WhoOwnsAIFigure4 = api;
}(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const YEARS = 50;
  const DCF_HORIZON = 400;
  const MARKET0 = 62.1857e12;
  const GDP0 = 32e12;
  const POPULATION0 = 342e6;
  const POPULATION_GROWTH = 0.004;
  const LABOR_SHARE0 = 0.55;
  const PAYOUT0_GDP_SHARE = 1.5 / 32.0;
  const WAGE_TO_PAYOUT = 0.5;
  const SCENARIOS = [
    { key: "baseline", label: "baseline", growth: 0.018,
      discountRate: 0.055, laborFloor: 0.45 },
    { key: "moderate", label: "moderate AI", growth: 0.030,
      discountRate: 0.0625, laborFloor: 0.35 },
    { key: "strong", label: "strong AI", growth: 0.040,
      discountRate: 0.070, laborFloor: 0.30 }
  ];

  function laborShare(year, floor) {
    return floor + (LABOR_SHARE0 - floor) * Math.exp(-year / 20.0);
  }

  function levyRate(labor) {
    const shift = Math.max(0.0, LABOR_SHARE0 - labor);
    const raw = 0.01 + 0.03 * Math.pow(shift / 0.25, 1.5);
    return Math.min(0.04, Math.max(0.01, raw));
  }

  function retirementRouting(year) {
    return 1.0 - (1.0 / 3.0) * Math.exp(-year / 25.0);
  }

  function advanceOwnership(publicShare, marketValue, statutoryRate, year,
      cashIncome) {
    const avoidance = 0.10 + 2.0 * statutoryRate;
    const effectiveRate = statutoryRate * (1.0 - avoidance);
    const routing = retirementRouting(year);
    const shareAfterIssuance =
      (1.0 - effectiveRate) * publicShare + effectiveRate * routing;
    const netTaxTransfer = (shareAfterIssuance - publicShare) * marketValue;
    const early = 0.035 * publicShare * marketValue + 0.25 * netTaxTransfer;
    const mature = cashIncome + netTaxTransfer;
    const weight = 1.0 / (1.0 + Math.exp(-(year - 22.0) / 6.0));
    const payout = (1.0 - weight) * early + weight * mature;
    const endingShare = shareAfterIssuance +
      (cashIncome - payout) / marketValue;
    return {
      qStart: publicShare,
      qPlus: shareAfterIssuance,
      qEnd: endingShare,
      avoidance,
      effectiveRate,
      routing,
      netTaxTransfer,
      cashIncome,
      payout
    };
  }

  function simulateSimple(scenario, years) {
    years = years === undefined ? YEARS : years;
    let publicShare = 0.0;
    const rows = [];
    for (let year = 1; year <= years; year += 1) {
      const labor = laborShare(year, scenario.laborFloor);
      const statutoryRate = levyRate(labor);
      const marketValue = MARKET0 * Math.pow(1.0 + scenario.growth, year);
      const gdp = GDP0 * Math.pow(1.0 + scenario.growth, year);
      const corporatePayout = (PAYOUT0_GDP_SHARE +
        WAGE_TO_PAYOUT * (LABOR_SHARE0 - labor)) * gdp;
      const cashIncome = publicShare * corporatePayout;
      const event = advanceOwnership(
        publicShare, marketValue, statutoryRate, year, cashIncome);
      const population = POPULATION0 *
        Math.pow(1.0 + POPULATION_GROWTH, year);
      rows.push(Object.assign(event, {
        year,
        marketCap: marketValue,
        gdp,
        marketGdpRatio: marketValue / gdp,
        corporatePayout,
        payoutYield: corporatePayout / marketValue,
        perCapitaPayout: event.payout / population,
        population,
        statutoryRate
      }));
      publicShare = event.qEnd;
    }
    return rows;
  }

  function economicPaths(scenario) {
    const payout = new Array(DCF_HORIZON + 1);
    const statutoryRate = new Array(DCF_HORIZON + 1);
    const avoidance = new Array(DCF_HORIZON + 1);
    const effectiveRate = new Array(DCF_HORIZON + 1);
    for (let year = 0; year <= DCF_HORIZON; year += 1) {
      const labor = laborShare(year, scenario.laborFloor);
      const gdp = GDP0 * Math.pow(1.0 + scenario.growth, year);
      payout[year] = (PAYOUT0_GDP_SHARE +
        WAGE_TO_PAYOUT * (LABOR_SHARE0 - labor)) * gdp;
      statutoryRate[year] = levyRate(labor);
      avoidance[year] = 0.10 + 2.0 * statutoryRate[year];
      effectiveRate[year] = year === 0 ? 0.0 :
        statutoryRate[year] * (1.0 - avoidance[year]);
    }
    return { payout, statutoryRate, avoidance, effectiveRate };
  }

  function valuePaths(payout, effectiveRate, discountRate) {
    const policy = new Array(DCF_HORIZON + 1).fill(0.0);
    const noLevy = new Array(DCF_HORIZON + 1).fill(0.0);
    for (let year = DCF_HORIZON - 1; year >= 0; year -= 1) {
      policy[year] = (payout[year + 1] +
        (1.0 - effectiveRate[year + 1]) * policy[year + 1]) /
        (1.0 + discountRate);
      noLevy[year] = (payout[year + 1] + noLevy[year + 1]) /
        (1.0 + discountRate);
    }
    return { policy, noLevy };
  }

  function simulateDcf(scenario, years) {
    years = years === undefined ? YEARS : years;
    const paths = economicPaths(scenario);
    const values = valuePaths(
      paths.payout, paths.effectiveRate, scenario.discountRate);
    let publicShare = 0.0;
    const rows = [];
    for (let year = 1; year <= years; year += 1) {
      const marketValue = values.policy[year];
      const cashIncome = publicShare * paths.payout[year];
      const event = advanceOwnership(
        publicShare, marketValue, paths.statutoryRate[year], year, cashIncome);
      const population = POPULATION0 *
        Math.pow(1.0 + POPULATION_GROWTH, year);
      rows.push(Object.assign(event, {
        year,
        marketValue,
        corporatePayout: paths.payout[year],
        perCapitaPayout: event.payout / population,
        population,
        statutoryRate: paths.statutoryRate[year]
      }));
      publicShare = event.qEnd;
    }
    return {
      rows,
      markdown: 1.0 - values.policy[0] / values.noLevy[0]
    };
  }

  function crossingYear(rows, level) {
    let previousYear = 0.0;
    let previousValue = 0.0;
    for (const row of rows) {
      if (previousValue < level && level <= row.perCapitaPayout) {
        return previousYear + (level - previousValue) /
          (row.perCapitaPayout - previousValue);
      }
      previousYear = row.year;
      previousValue = row.perCapitaPayout;
    }
    return null;
  }

  return {
    YEARS,
    DCF_HORIZON,
    MARKET0,
    SCENARIOS,
    simulateSimple,
    economicPaths,
    valuePaths,
    simulateDcf,
    crossingYear
  };
}));
