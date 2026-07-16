# Figure 4: the public-fund simulation

This directory contains the simulation behind Figure 4 of
["Who Owns the AI Economy?"](https://silviupitis.com/blog/2026/who-owns-the-ai-economy/).
The essay proposes an annual levy on large corporations, paid in newly issued
non-voting shares to a public fund. The simulation follows the fund for fifty
years and reports its annual dividend per U.S. resident in real 2026 dollars.

The opening dollar values use the latest available observations, spanning
end-2024 through 2026, as scale anchors for the real-2026-dollar calibration.

The figure in the essay uses a discounted-cash-flow model that values covered
equity from projected shareholder payouts. A simpler cross-check holds covered
market value at its opening ratio to GDP. Both models use the same economic
scenarios, levy rule, retirement protection, payout rule, and annual ownership
ledger.

## Calibration and assumptions

| Input | Value | Use and basis |
|---|---:|---|
| Opening listed-market value | $62.1857T | The simple model's market-value anchor. It is the end-2024 U.S. listed-company capitalization in the [SIFMA 2025 Capital Markets Fact Book](https://www.sifma.org/wp-content/uploads/2024/07/2025-SIFMA-Capital-Markets-Factbook.pdf), used as a proxy for firms above the essay's threshold. The DCF derives market value from projected payouts. |
| Opening U.S. GDP | $32T | A round real-2026-dollar starting value. Current-dollar GDP was $31.49T at an annual rate in 2025 Q4 in the [BEA release](https://www.bea.gov/sites/default/files/2026-02/gdp4q25-adv.pdf), making $32T a reasonable calibration for 2026. |
| Opening shareholder payout | $1.5T a year | Combined dividends and net buybacks. This anchors fund income in both models and market value in the DCF. The round value is conservative relative to the $1.685T returned by the S&P 500 alone over the twelve months through 2025 Q3, according to [S&P Dow Jones Indices](https://www.spglobal.com/spdji/en/corporate-news/article/sp-500-q3-2025-buybacks-post-modest-62-gain-to-249-0-billion-after-declining-20-1-amidst-uncertainty-in-q2/). |
| Opening labor share | 55% | A round starting value for the indexed series. The [BLS methodology](https://www.bls.gov/opub/hom/opt/calculation.htm) describes the published measure. |
| Opening population | 342M | A round U.S. population near enactment, consistent with the [Census Bureau](https://www.census.gov/about/history/stories/monthly/2026/july-2026.html). |
| Population growth | 0.4% a year | Scenario assumption used to calculate the dividend per person. |
| Real GDP growth | 1.8%, 3%, 4% | Baseline, moderate-AI, and strong-AI assumptions. The baseline is close to CBO's 1.8% average projection for 2027 through 2036 in its [2026 outlook](https://www.cbo.gov/publication/62105). |
| Long-run labor-share floors | 45%, 35%, 30% | Scenario assumptions. Each path approaches its floor with a 20-year time constant. |
| Wage-to-payout conversion | 50% | Scenario assumption. Half of the modeled decline in labor income becomes additional payouts by covered firms. |
| Real required return | 5.5%, 6.25%, 7% | DCF assumptions for the three economic scenarios. |
| Statutory levy | 1% to 4% | Policy choice. The rate rises with the decline in labor's share. |
| Avoidance | 12% to 18% of statutory issuance | The assumed formula is `0.10 + 2*tau`, where `tau` is the statutory rate. |
| Retirement protection | Roughly one-third initially | The protected share runs off with a 25-year time constant. |
| Fund payout rule | 3.5% of assets plus 25% of net receipts initially | A logistic transition centered on year 22 moves toward paying shareholder income plus net receipts. |

## Economic and policy paths

Let `t` be years after enactment, `L_t` labor's share, `G_t` GDP, `Y_t` the
covered firms' combined shareholder payout, and `tau_t` the statutory levy.
For scenario growth `g` and labor-share floor `L_floor`:

```
G_t   = 32T * (1 + g)^t
L_t   = L_floor + (0.55 - L_floor) * exp(-t/20)
Y_t   = [1.5/32 + 0.5*(0.55 - L_t)] * G_t
tau_t = clamp(0.01 + 0.03*((0.55 - L_t)/0.25)^1.5, 0.01, 0.04)
a_t   = 0.10 + 2*tau_t
lambda_t = tau_t * (1 - a_t)
```

`lambda_t` is the effective issuance and dilution rate after avoidance.

## Annual ownership ledger

Let `q` be the fund's share immediately before the year's shareholder payout,
`M` the covered equity value, and
`rho_t = 1-(1/3)*exp(-t/25)` the fraction of new shares routed to the public
fund. The remaining issuance protects grandfathered retirement holdings.

Opening holders receive the year's shareholder payout before new levy shares
are issued. The fund receives `cash_income = q*Y_t`, and issuance changes its
share to:

```
q_plus = (1-lambda_t)*q + lambda_t*rho_t
net_receipts = (q_plus-q)*M
```

The citizen dividend blends an early rule with the mature flow available to
the fund:

```
early  = 0.035*q*M + 0.25*net_receipts
mature = cash_income + net_receipts
w_t    = 1 / [1 + exp(-(t-22)/6)]
dividend_t = (1-w_t)*early + w_t*mature
```

Fund income left after the citizen dividend is reinvested in covered equity:

```
q_end = q_plus + (cash_income-dividend_t)/M
```

Each period therefore satisfies
`q_end*M + dividend_t = q_plus*M + cash_income`. The fund can turn shares into
cash through issuer dividends, participation in buybacks, or sales at the
modeled price. The calculation omits transaction costs and price impact.

## Valuation models

### Payout-valued DCF used in the essay

The DCF derives market value from the payout stream after future dilution. For
real required return `r`:

```
V_t = [Y_(t+1) + (1-lambda_(t+1))*V_(t+1)] / (1+r)
```

The payout at `t+1` goes to holders in place before that year's issuance.
Issuance then dilutes the continuation value. The fifty-year ownership ledger
uses values from a 400-year pricing recurrence because the policy is assumed
to continue after year 50. Comparing this value with the same payout stream
without dilution gives the modeled enactment markdown.

The opening DCF values are $48.77T in the baseline scenario, $65.87T under
moderate AI, and $74.17T under strong AI.

### Simple market-value cross-check

The central simple model begins with the observed $62.1857T listed-value proxy
and keeps market value at its opening ratio to GDP, 1.9433. It uses the same
labor-linked shareholder payouts as the DCF, which allows the payout yield to
rise as labor's share falls. This model leaves the enactment markdown outside
the calculation.

Two additional variants show how capitalization affects the result. The first
holds the opening payout yield and market-value-to-GDP ratio constant while
omitting the wage-to-payout shift. The second capitalizes the additional payout
at the opening yield, allowing market value to rise with shareholder payouts.

## Results

Year-50 dividend per person, ending public ownership, and DCF markdown are:

| Scenario | Simple cross-check | Payout-valued DCF | DCF markdown |
|---|---:|---:|---:|
| Baseline | $6,630 / 13.67% | $6,499 / 14.21% | 27.66% |
| Moderate AI | $21,345 / 20.57% | $24,354 / 18.86% | 40.69% |
| Strong AI | $44,108 / 24.89% | $52,209 / 21.67% | 47.64% |

The DCF reaches $10,000 per person in the strong-AI scenario in year 23.27 and
$35,000 in year 41.13. The central simple model reaches those levels in years
25.25 and 44.65.

The year-50 sensitivity bracket is:

| Scenario | No wage-to-payout shift | Central simple model | Constant payout yield | Payout-valued DCF |
|---|---:|---:|---:|---:|
| Baseline | $5,407 / 11.93% | $6,630 / 13.67% | $10,702 / 11.93% | $6,499 / 14.21% |
| Moderate AI | $15,065 / 15.95% | $21,345 / 20.57% | $44,565 / 15.95% | $24,354 / 18.86% |
| Strong AI | $29,112 / 18.25% | $44,108 / 24.89% | $100,370 / 18.25% | $52,209 / 21.67% |

[`final/results.csv`](final/results.csv) contains all four model variants at
years 1, 25, and 50. The `final` directory also contains light and dark static
figures for the central simple model and the DCF.

## Reproduce

```bash
python3 -m unittest
python3 figure4.py
python3 figure4.py --render
node web/test_models.js
```
