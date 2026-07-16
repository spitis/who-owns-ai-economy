# Figure 3 inputs and provenance

This file documents every empirical input and judgment used by `figure3.py`.
The six buckets are the United States (`US`), European
Union (`EU`), United Kingdom (`UK`), Japan/Korea/Taiwan (`JKT`), China including
Hong Kong (`CN`), and the rest of the world (`RoW`).

## Policy parameters

| Parameter | Value | Status |
|---|---:|---|
| Levy floor (`TAU`) | 1% of equity value | Policy choice in the essay |
| Collection cap (`CAP_MULT`) | 3 times the member-market sales share | Illustrative design choice. The report also tests 2x and 5x. |
| Value date | End of 2024 | Empirical snapshot |

The published figure uses observed market values. The optional `payout`
sensitivity scales them by 0.784, the ratio of Figure 4's baseline post-levy
valuation to the observed U.S. value below.

## Covered market values

The main source is the [SIFMA 2025 Capital Markets Fact
Book](https://www.sifma.org/wp-content/uploads/2024/07/2025-SIFMA-Capital-Markets-Factbook.pdf),
pp. 13–14, whose underlying series is the World Federation of Exchanges'
market capitalization of listed domestic companies. The NYSE and Nasdaq split
is on p. 40. Values are in trillions of U.S. dollars at the end of 2024.

| Bucket | Value | Construction |
|---|---:|---|
| US | 62.1857 | NYSE 31.5760 + Nasdaq 30.6097 |
| EU | 11.0557 | SIFMA EU total |
| UK | 4.3994 | SIFMA UK total |
| JKT | 10.1220 | Japan 6.3107 + Korea 1.5570 + Taiwan 2.2543 |
| CN | 16.3055 | Mainland China 11.7558 + Hong Kong 4.5497 |
| RoW | 22.6250 | Residual from the world total |
| **World** | **126.6930** | SIFMA total |

Korea comes from the [World Bank listed-company market-capitalization
series](https://data.worldbank.org/indicator/CM.MKT.LCAP.CD?locations=KR).
Taiwan is computed from the [TWSE 2025 Fact
Book](https://www.twse.com.tw/downloads/zh/about/company/factbook/2025/1.01.html)
at the Federal Reserve's year-end [TWD/USD exchange
rate](https://www.federalreserve.gov/releases/h10/hist/dat00_ta.htm). It
excludes the smaller TPEx market.

The source series does not filter firms at $1 billion. The [2025 Russell
reconstitution](https://www.lseg.com/content/dam/ftse-russell/en_us/documents/other/2025-russell-recon-recap-final.pdf)
implies that smaller companies account for less than 6% of listed U.S. value,
so the model applies no coverage haircut. The approximation is less certain
outside the United States.

WFE's domestic-company convention avoids most duplication from cross-listings,
although it is not a perfect measure of where an operating company is based.
The extraction and reconciliation appear in
[`SOURCES.md`](SOURCES.md#market-capitalization).

## Sales-destination matrix

The table below, stored as `S_BROAD` in the code, is a constructed estimate of
where each listed-company group makes its sales. Every row sums to one.

| Listed-company group | US | EU | UK | JKT | CN | RoW |
|---|---:|---:|---:|---:|---:|---:|
| US | .58 | .13 | .02 | .08 | .06 | .13 |
| EU | .22 | .44 | .04 | .06 | .07 | .17 |
| UK | .28 | .18 | .19 | .05 | .06 | .24 |
| JKT | .24 | .09 | .01 | .40 | .13 | .13 |
| CN | .04 | .04 | .01 | .03 | .85 | .03 |
| RoW | .20 | .12 | .02 | .08 | .08 | .50 |

No public dataset provides a consistent global destination-of-sales matrix.
The rows combine index-level revenue-exposure data with company filings. The
anchors and the judgments used to complete them are:

| Row | Empirical anchor | Construction and uncertainty |
|---|---|---|
| US | [FactSet](https://advantage.factset.com/hubfs/Website/Resources%20Section/Research%20Desk/Earnings%20Insight/EarningsInsight_011626.pdf) reports 58% of S&P 500 revenue from the United States in January 2026. | The 42% foreign share is divided using S&P regional data and megacap filings. The EU share is uncertain by about 3 percentage points and China by about 2. |
| EU | MSCI Europe companies derive about 24.5% of revenue from the United States, according to [MSCI](https://www.msci.com/research-and-insights/blog-post/some-see-a-renaissance-for-european-equities). A later [JPMorgan/MSCI chart](https://am.jpmorgan.com/content/dam/jpm-am-aem/global/en/insights/market-insights/guide-to-the-markets/mi-guide-to-the-markets-ce-en.pdf) gives Europe 48%, US 21%, and Asia-Pacific 19%. | MSCI Europe includes the UK, Switzerland, and other non-EU markets, while the model row represents EU-listed value. The source is therefore a regional anchor rather than a matched company universe, and dividing the total among the model's buckets requires judgment. The EU cell is uncertain by about 4 points and China by about 3. |
| UK | [FTSE Russell](https://www.lseg.com/en/insights/ftse-russell/the-uks-very-global-country-index) reports that more than 80% of FTSE 100 revenue comes from outside the UK. Its [regional analysis](https://www.lseg.com/en/insights/ftse-russell/uk-equities-a-haven-for-income-and-value) places roughly 30% in the United States. | The remaining foreign revenue is divided using the reported regional mix. The US and rest-of-world cells are uncertain by about 4 points. |
| JKT | No suitable index aggregate was found. The principal anchors are filings from [Toyota](https://www.sec.gov/Archives/edgar/data/1094517/000119312525115410/d904529dex991.htm), [Sony](https://www.sec.gov/Archives/edgar/data/313838/000119312525143137/d820387d20f.htm), [TSMC](https://www.sec.gov/Archives/edgar/data/1046179/000162828026025362/tsm-20251231.htm), and [Samsung](https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2025_con_quarter04_all.pdf). | This row has the widest stated uncertainty. The domestic and US cells are uncertain by about 5 points. |
| CN | [MSCI](https://www.msci.com/research-and-insights/blog-post/tracking-the-internationalization-of-chinese-companies) estimates that 85% of MSCI China revenue is domestic. | The small foreign share is divided across the other markets. Those cells are uncertain by about 2 points. |
| RoW | No aggregate corresponds to this heterogeneous residual bucket. | The entire row is a judgment. Its domestic cell is uncertain by about 6 points. |

Company disclosures classify revenue by customer location, billing location,
or customer headquarters, and the choice can materially change the result.
The model favors customer location when available. Detailed extracts and the
row-by-row construction are in
[`SOURCES.md`](SOURCES.md#sales-destinations).

## Government-spending comparisons

The percentages printed beneath member collections compare them with 2025
general-government expenditure, including national and subnational spending.
The values combine current-dollar GDP from the IMF's April 2026 [World
Economic Outlook](https://www.imf.org/external/datamapper/datasets/WEO) with
the expenditure shares in its April 2026 [Fiscal
Monitor](https://www.imf.org/external/datamapper/datasets/FM).

| Bucket | General-government expenditure ($T) |
|---|---:|
| US | 11.6006 |
| EU | 10.4914 |
| UK | 1.7471 |
| JKT | 2.2494 |
| CN | 6.5521 |
| RoW | 10.9820 |

These values affect only the contextual percentages displayed in the figure.

## Magnificent Seven calculation

The separate Magnificent Seven calculation uses a combined mid-2026 market
value of $22 trillion and the following constructed destination vector:

| US | EU | UK | JKT | CN | RoW |
|---:|---:|---:|---:|---:|---:|
| .55 | .17 | .03 | .07 | .06 | .12 |

The round market-value anchor is based on [AJ Bell's May 6,
2026 report](https://www.ajbell.co.uk/news/story-behind-magnificent-sevens-push-new-heights)
that the seven companies had reached a combined value of $22.5 trillion. The
sales shares combine the companies' latest geographic disclosures, with
judgment needed to divide Europe and Asia among the model's buckets. The broad
and megacap calculations use different valuation dates and are reported
separately. The filing extracts and calculations are in
[`SOURCES.md`](SOURCES.md#magnificent-seven).
