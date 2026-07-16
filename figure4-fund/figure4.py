#!/usr/bin/env python3
"""Models, result tables, and command-line report for Figure 4.

The essay uses the payout-valued DCF. A simpler model holds covered market
value at its opening ratio to GDP and provides a cross-check. Both models use
the same economic scenarios, levy rule, retirement protection, payout rule,
and annual ownership ledger.

Run ``python3 figure4.py`` for the numerical report. Add ``--render`` to write
``final/results.csv`` and the light and dark assets for both models.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
import sys


YEARS = 50
DCF_HORIZON = 400

# Opening values in real 2026 dollars.
MARKET0 = 62.1857e12
GDP0 = 32e12
POPULATION0 = 342e6
POPULATION_GROWTH = 0.004
PAYOUT0_GDP_SHARE = 1.5 / 32.0
LABOR_SHARE0 = 0.55
WAGE_TO_PAYOUT = 0.5

# Policy and payout parameters.
LEVY_FLOOR, LEVY_CEILING = 0.01, 0.04
PAYOUT_RAMP_CENTER, PAYOUT_RAMP_SCALE = 22.0, 6.0
EARLY_ASSET_PAYOUT, EARLY_RECEIPT_PAYOUT = 0.035, 0.25

SCENARIOS = (
    dict(key="baseline", label="baseline", growth=0.018,
         discount_rate=0.055, labor_floor=0.45),
    dict(key="moderate", label="moderate AI", growth=0.030,
         discount_rate=0.0625, labor_floor=0.35),
    dict(key="strong", label="strong AI", growth=0.040,
         discount_rate=0.070, labor_floor=0.30),
)

SIMPLE_NO_SHIFT = "simple_no_income_shift"
SIMPLE_FIXED_MARKET = "simple_fixed_market_gdp"
SIMPLE_FIXED_YIELD = "simple_fixed_payout_yield"
SIMPLE_VARIANTS = (SIMPLE_NO_SHIFT, SIMPLE_FIXED_MARKET, SIMPLE_FIXED_YIELD)


# ---------------------------------------------------------------------------
# Shared economic paths and annual ownership ledger
# ---------------------------------------------------------------------------
def labor_share(year: int, floor: float) -> float:
    return floor + (LABOR_SHARE0 - floor) * math.exp(-year / 20.0)


def levy_rate(labor: float) -> float:
    shift = max(0.0, LABOR_SHARE0 - labor)
    raw = LEVY_FLOOR + 0.03 * (shift / 0.25) ** 1.5
    return min(LEVY_CEILING, max(LEVY_FLOOR, raw))


def retirement_routing(year: int) -> float:
    """Fraction of effective issuance routed to the public fund."""
    return 1.0 - (1.0 / 3.0) * math.exp(-year / 25.0)


def economic_state(
    year: int, scenario: dict, wage_to_payout: float = WAGE_TO_PAYOUT
) -> dict[str, float]:
    """Shared economic and policy values for one year."""
    labor = labor_share(year, scenario["labor_floor"])
    gdp = GDP0 * (1.0 + scenario["growth"]) ** year
    corporate_payout = (
        PAYOUT0_GDP_SHARE
        + wage_to_payout * (LABOR_SHARE0 - labor)
    ) * gdp
    statutory_rate = levy_rate(labor)
    avoidance = 0.10 + 2.0 * statutory_rate
    return dict(
        labor_share=labor,
        gdp=gdp,
        corporate_payout=corporate_payout,
        statutory_rate=statutory_rate,
        avoidance=avoidance,
        effective_rate=statutory_rate * (1.0 - avoidance),
    )


def issuance_update(
    public_share: float, effective_rate: float, routing: float
) -> float:
    """Public ownership after issuance and before reinvestment."""
    if not 0.0 <= public_share <= 1.0:
        raise ValueError("public_share must be in [0, 1]")
    if not 0.0 <= effective_rate <= 1.0:
        raise ValueError("effective_rate must be in [0, 1]")
    if not 0.0 <= routing <= 1.0:
        raise ValueError("routing must be in [0, 1]")
    return ((1.0 - effective_rate) * public_share
            + effective_rate * routing)


def advance_ownership(
    *, public_share: float, market_value: float, statutory_rate: float,
    year: int, cash_income: float, routing: float | None = None,
    payout_weight: float | None = None,
) -> dict[str, float]:
    """Apply one levy event and the public-fund payout decision.

    ``public_share`` is measured before the year's shareholder payout.
    Opening holders receive that payout before new levy shares are issued.
    Fund income left after the citizen dividend is reinvested at the modeled
    market value.
    """
    if market_value <= 0.0:
        raise ValueError("market_value must be positive")
    if not 0.0 <= statutory_rate <= 0.4:
        raise ValueError("statutory_rate must keep issuance valid")

    avoidance = 0.10 + 2.0 * statutory_rate
    effective_rate = statutory_rate * (1.0 - avoidance)
    route = retirement_routing(year) if routing is None else routing
    share_after_issuance = issuance_update(
        public_share, effective_rate, route)
    net_receipts = (share_after_issuance - public_share) * market_value

    early_payout = (EARLY_ASSET_PAYOUT * public_share * market_value
                    + EARLY_RECEIPT_PAYOUT * net_receipts)
    mature_payout = cash_income + net_receipts
    weight = (
        1.0 / (1.0 + math.exp(
            -(year - PAYOUT_RAMP_CENTER) / PAYOUT_RAMP_SCALE))
        if payout_weight is None else payout_weight
    )
    citizen_payout = ((1.0 - weight) * early_payout
                      + weight * mature_payout)
    ending_share_raw = (
        share_after_issuance + (cash_income - citizen_payout) / market_value)
    if not -1e-12 <= ending_share_raw <= 1.0 + 1e-12:
        raise AssertionError(f"ownership outside [0, 1]: {ending_share_raw}")
    ending_share = min(1.0, max(0.0, ending_share_raw))

    return dict(
        q_start=public_share,
        q_plus=share_after_issuance,
        q_end=ending_share,
        avoidance=avoidance,
        effective_rate=effective_rate,
        routing=route,
        net_tax_transfer=net_receipts,
        cash_income=cash_income,
        early_payout=early_payout,
        mature_payout=mature_payout,
        payout_weight=weight,
        payout=citizen_payout,
    )


def crossing_year(rows: list[dict], level: float) -> float | None:
    previous_year, previous_value = 0.0, 0.0
    for row in rows:
        value = row["per_capita_payout"]
        if previous_value < level <= value:
            return (previous_year
                    + (level - previous_value) / (value - previous_value))
        previous_year, previous_value = row["year"], value
    return None


# ---------------------------------------------------------------------------
# Simple market-value alternatives
# ---------------------------------------------------------------------------
OPENING_PAYOUT_YIELD = 1.5e12 / MARKET0


def _simple_market_and_payout(
    year: int, scenario: dict, variant: str, state: dict[str, float]
) -> tuple[float, float, float]:
    observed_market = MARKET0 * (1.0 + scenario["growth"]) ** year
    if variant == SIMPLE_NO_SHIFT:
        return (observed_market,
                observed_market * OPENING_PAYOUT_YIELD,
                state["gdp"])
    if variant == SIMPLE_FIXED_MARKET:
        return observed_market, state["corporate_payout"], state["gdp"]
    return (state["corporate_payout"] / OPENING_PAYOUT_YIELD,
            state["corporate_payout"], state["gdp"])


def simple_market_and_payout(
    year: int, scenario: dict, variant: str = SIMPLE_FIXED_MARKET,
    wage_to_payout: float = WAGE_TO_PAYOUT,
) -> tuple[float, float, float]:
    """Return market value, corporate payout, and GDP for one year."""
    if variant not in SIMPLE_VARIANTS:
        raise ValueError(f"unknown simple-model variant: {variant}")
    state = economic_state(year, scenario, wage_to_payout)
    return _simple_market_and_payout(year, scenario, variant, state)


def advance_simple_year(
    *, public_share: float, market_value: float, statutory_rate: float,
    year: int, payout_yield: float = OPENING_PAYOUT_YIELD,
    routing: float | None = None, payout_weight: float | None = None,
) -> dict[str, float]:
    """Advance one year with the market value supplied directly."""
    cash_income = public_share * market_value * payout_yield
    return advance_ownership(
        public_share=public_share,
        market_value=market_value,
        statutory_rate=statutory_rate,
        year=year,
        cash_income=cash_income,
        routing=routing,
        payout_weight=payout_weight,
    )


def simulate_simple(
    scenario: dict, years: int = YEARS, *, public_share0: float = 0.0,
    variant: str = SIMPLE_FIXED_MARKET,
    wage_to_payout: float = WAGE_TO_PAYOUT,
) -> list[dict]:
    public_share = public_share0
    rows = []
    for year in range(1, years + 1):
        state = economic_state(year, scenario, wage_to_payout)
        market, corporate_payout, gdp = _simple_market_and_payout(
            year, scenario, variant, state)
        payout_yield = corporate_payout / market
        row = advance_simple_year(
            public_share=public_share,
            market_value=market,
            statutory_rate=state["statutory_rate"],
            year=year,
            payout_yield=payout_yield,
        )
        population = POPULATION0 * (1.0 + POPULATION_GROWTH) ** year
        previous_market = simple_market_and_payout(
            year - 1, scenario, variant, wage_to_payout)[0]
        market_growth = market / previous_market - 1.0
        row.update(
            year=year,
            scenario=scenario["key"],
            label=scenario["label"],
            model=variant,
            corporate_payout=corporate_payout,
            labor_share=state["labor_share"],
            statutory_rate=state["statutory_rate"],
            market_cap=market,
            gdp=gdp,
            market_gdp_ratio=market / gdp,
            payout_yield=payout_yield,
            population=population,
            per_capita_payout=row["payout"] / population,
            capital_growth=market_growth,
            total_return=((1.0 + market_growth) * (1.0 + payout_yield) - 1.0),
        )
        rows.append(row)
        public_share = row["q_end"]
    return rows


# ---------------------------------------------------------------------------
# Payout-valued DCF used in the essay
# ---------------------------------------------------------------------------
def economic_paths(
    scenario: dict, horizon: int = DCF_HORIZON,
    policy_years: int | None = None,
) -> dict[str, list[float]]:
    years = list(range(horizon + 1))
    states = [economic_state(year, scenario) for year in years]
    labor = [state["labor_share"] for state in states]
    gdp = [state["gdp"] for state in states]
    payout = [state["corporate_payout"] for state in states]
    statutory_rate = [state["statutory_rate"] for state in states]
    avoidance = [state["avoidance"] for state in states]
    effective_rate = [0.0] + [
        states[year]["effective_rate"]
        if policy_years is None or year <= policy_years else 0.0
        for year in years[1:]
    ]
    return dict(
        year=years,
        labor=labor,
        gdp=gdp,
        payout=payout,
        tau=statutory_rate,
        avoidance=avoidance,
        effective_rate=effective_rate,
    )


def value_paths(
    payout: list[float], effective_rate: list[float], discount_rate: float
) -> tuple[list[float], list[float]]:
    """Return levy and no-levy ex-current-payout equity values.

    ``V_t = [Y_(t+1) + (1-lambda_(t+1))*V_(t+1)]/(1+r)``. Issuance
    therefore dilutes continuation value after the next payout.
    """
    horizon = len(payout) - 1
    policy = [0.0] * (horizon + 1)
    no_levy = [0.0] * (horizon + 1)
    for year in range(horizon - 1, -1, -1):
        policy[year] = (
            payout[year + 1]
            + (1.0 - effective_rate[year + 1]) * policy[year + 1]
        ) / (1.0 + discount_rate)
        no_levy[year] = (
            payout[year + 1] + no_levy[year + 1]
        ) / (1.0 + discount_rate)
    return policy, no_levy


def simulate_dcf(scenario: dict, years: int = YEARS) -> dict:
    paths = economic_paths(scenario)
    market_values, no_levy_values = value_paths(
        paths["payout"], paths["effective_rate"], scenario["discount_rate"])
    public_share = 0.0
    rows = []
    for year in range(1, years + 1):
        market = market_values[year]
        cash_income = public_share * paths["payout"][year]
        row = advance_ownership(
            public_share=public_share,
            market_value=market,
            statutory_rate=paths["tau"][year],
            year=year,
            cash_income=cash_income,
        )
        population = POPULATION0 * (1.0 + POPULATION_GROWTH) ** year
        row.update(
            year=year,
            market_value=market,
            corporate_payout=paths["payout"][year],
            per_capita_payout=row["payout"] / population,
            population=population,
            statutory_rate=paths["tau"][year],
            avoidance=paths["avoidance"][year],
        )
        rows.append(row)
        public_share = row["q_end"]
    return dict(
        rows=rows,
        market_value=market_values,
        no_levy_value=no_levy_values,
        markdown=1.0 - market_values[0] / no_levy_values[0],
        paths=paths,
    )


def simulate_value_recurrence(
    scenario: dict, years: int = YEARS
) -> list[dict]:
    """Independent dollar-value recurrence for the DCF accounting ledger."""
    paths = economic_paths(scenario)
    market_values, _ = value_paths(
        paths["payout"], paths["effective_rate"], scenario["discount_rate"])
    fund_value = 0.0
    rows = []
    previous_market = market_values[1]
    for year in range(1, years + 1):
        market = market_values[year]
        if year > 1:
            fund_value *= market / previous_market
        public_share = fund_value / market
        cash_income = public_share * paths["payout"][year]
        effective_rate = paths["effective_rate"][year]
        routing = retirement_routing(year)
        value_after_issuance = (
            (1.0 - effective_rate) * fund_value
            + effective_rate * routing * market)
        net_receipts = value_after_issuance - fund_value
        event = advance_ownership(
            public_share=public_share,
            market_value=market,
            statutory_rate=paths["tau"][year],
            year=year,
            cash_income=cash_income,
        )
        fund_value = value_after_issuance + cash_income - event["payout"]
        rows.append(dict(
            year=year,
            q_start=public_share,
            q_end=fund_value / market,
            fund_value=fund_value,
            payout=event["payout"],
            net_tax_transfer=net_receipts,
            cash_income=cash_income,
        ))
        previous_market = market
    return rows


# ---------------------------------------------------------------------------
# Published result table and command-line interface
# ---------------------------------------------------------------------------
RESULT_FIELDS = (
    "model", "scenario", "year", "per_capita_payout",
    "public_ownership_q", "market_gdp_ratio", "payout_yield",
    "crossing_year_10000", "crossing_year_35000", "dcf_markdown",
)


def _format_crossing(value: float | None) -> str:
    return "" if value is None else f"{value:.6f}"


def results_rows() -> list[dict[str, str | int]]:
    output = []
    for variant in SIMPLE_VARIANTS:
        for scenario in SCENARIOS:
            rows = simulate_simple(scenario, variant=variant)
            crossing_10k = crossing_year(rows, 10_000)
            crossing_35k = crossing_year(rows, 35_000)
            for year in (1, 25, 50):
                row = rows[year - 1]
                output.append(dict(
                    model=variant,
                    scenario=scenario["label"],
                    year=year,
                    per_capita_payout=f"{row['per_capita_payout']:.6f}",
                    public_ownership_q=f"{row['q_end']:.9f}",
                    market_gdp_ratio=f"{row['market_gdp_ratio']:.9f}",
                    payout_yield=f"{row['payout_yield']:.9f}",
                    crossing_year_10000=_format_crossing(crossing_10k),
                    crossing_year_35000=_format_crossing(crossing_35k),
                    dcf_markdown="",
                ))

    for scenario in SCENARIOS:
        result = simulate_dcf(scenario)
        rows = result["rows"]
        crossing_10k = crossing_year(rows, 10_000)
        crossing_35k = crossing_year(rows, 35_000)
        for year in (1, 25, 50):
            row = rows[year - 1]
            output.append(dict(
                model="payout_dcf",
                scenario=scenario["label"],
                year=year,
                per_capita_payout=f"{row['per_capita_payout']:.6f}",
                public_ownership_q=f"{row['q_end']:.9f}",
                market_gdp_ratio="",
                payout_yield="",
                crossing_year_10000=_format_crossing(crossing_10k),
                crossing_year_35000=_format_crossing(crossing_35k),
                dcf_markdown=f"{result['markdown']:.9f}",
            ))
    return output


def write_results(path: str | Path) -> None:
    with Path(path).open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=RESULT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(results_rows())


def report() -> None:
    print("PAYOUT-VALUED DCF USED IN THE ESSAY")
    for scenario in SCENARIOS:
        result = simulate_dcf(scenario)
        rows = result["rows"]
        values = ", ".join(
            f"y{year} ${rows[year - 1]['per_capita_payout']:,.0f}, "
            f"q={rows[year - 1]['q_end']:.2%}"
            for year in (1, 25, 50)
        )
        print(f"  {scenario['label']} (markdown {result['markdown']:.2%}): "
              f"{values}")

    print("\nSIMPLE FIXED-MARKET-TO-GDP CROSS-CHECK")
    for scenario in SCENARIOS:
        rows = simulate_simple(scenario)
        values = ", ".join(
            f"y{year} ${rows[year - 1]['per_capita_payout']:,.0f}, "
            f"q={rows[year - 1]['q_end']:.2%}"
            for year in (1, 25, 50)
        )
        print(f"  {scenario['label']}: {values}")


def main() -> None:
    report()
    if "--render" in sys.argv:
        output_dir = Path(__file__).with_name("final")
        output_dir.mkdir(exist_ok=True)
        results_path = output_dir / "results.csv"
        write_results(results_path)
        import render
        written = render.write_assets(sys.modules[__name__], output_dir)
        print(f"\nwrote {results_path}")
        for path in written:
            print(f"wrote {path}")


if __name__ == "__main__":
    main()
