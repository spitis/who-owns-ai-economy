# Figure 3 source appendix

[`DATA.md`](DATA.md) states the inputs used by the simulation. This appendix
records their derivation and the principal measurement limitations. The final
section documents the ownership figures used separately in
[`BURDEN.md`](BURDEN.md).

## Market capitalization

The model uses end-2024 market capitalization of listed domestic companies
from the [SIFMA 2025 Capital Markets Fact
Book](https://www.sifma.org/wp-content/uploads/2024/07/2025-SIFMA-Capital-Markets-Factbook.pdf),
pp. 13–14. The NYSE and Nasdaq split is on p. 40. SIFMA draws the series from
the World Federation of Exchanges. Its country table sums to $126.693 trillion.

| Model bucket | End-2024 value ($B) | Derivation |
|---|---:|---|
| United States | 62,185.7 | NYSE 31,576.0 + Nasdaq 30,609.7 |
| European Union | 11,055.7 | SIFMA EU total |
| United Kingdom | 4,399.4 | SIFMA UK total |
| Japan, Korea, and Taiwan | 10,122.0 | Japan 6,310.7 + Korea 1,557.0 + Taiwan 2,254.3 |
| China and Hong Kong | 16,305.5 | Mainland China 11,755.8 + Hong Kong 4,549.7 |
| Rest of world | 22,625.0 | Residual from the world total after the first five buckets |
| **World** | **126,693.0** | SIFMA total |

Korea's $1.557 trillion comes from the [World Bank market-capitalization
series](https://data.worldbank.org/indicator/CM.MKT.LCAP.CD?locations=KR). A
calculation from year-end KOSPI and KOSDAQ values at the Federal Reserve's
[KRW/USD rate](https://www.federalreserve.gov/releases/h10/hist/dat00_ko.htm)
gives $1.556 trillion.

Taiwan's value is calculated from NT$73.899 trillion in the [TWSE 2025 Fact
Book](https://www.twse.com.tw/downloads/zh/about/company/factbook/2025/1.01.html)
at the Federal Reserve's year-end [TWD/USD
rate](https://www.federalreserve.gov/releases/h10/hist/dat00_ta.htm). The
result excludes the TPEx market because a comparable year-end TPEx total was
not available.

The WFE domestic-company definition includes domestic companies and foreign
companies listed exclusively on the exchange. It generally excludes a foreign
company that is also listed in its home market. This convention limits
duplication from cross-listings, although listing market remains an imperfect
proxy for the operating company's home economy. Combining mainland and Hong
Kong values also counts distinct A-share and H-share classes of the same
company, which raises the bucket's value relative to a unique-company measure.

SIFMA's residual for other emerging markets fell from $8.465 trillion in 2023
to $4.744 trillion in 2024 without an accompanying explanation. The named
country values are unaffected, but the rest-of-world residual may differ by
several trillion dollars under another classification. The model therefore
treats that bucket as approximate.

The source table covers all listed companies. The [2025 Russell
reconstitution](https://www.lseg.com/content/dam/ftse-russell/en_us/documents/other/2025-russell-recon-recap-final.pdf)
places 95.4% of Russell 3000 value in the Russell 1000, while the Russell 3000
covers about 98% of investable U.S. equity. Companies below $1 billion
therefore account for less than 6% of listed U.S. value. No equivalent bound
was available for every other market.

## Sales destinations

Public revenue disclosures use three geographic conventions. Customer
location is closest to the destination rule in the essay. Billing location
can reflect an intermediary or selling entity. Customer-headquarters location
assigns sales to the purchaser's corporate home even when the product is used
elsewhere. The model uses customer location when available and adjusts the
remaining evidence with the judgments stated in [`DATA.md`](DATA.md).

| Listed-company group | Principal evidence | Measurement limits |
|---|---|---|
| United States | [FactSet](https://advantage.factset.com/hubfs/Website/Resources%20Section/Research%20Desk/Earnings%20Insight/EarningsInsight_011626.pdf) reports 58% of S&P 500 revenue from the United States in January 2026. The older [S&P Global Sales report](https://www.spglobal.com/spdji/en/documents/research/sp-500-global-sales-2018.pdf) reports 57.1% domestic and 42.9% foreign revenue on its adjusted basis. | FactSet does not state a single geographic convention for the aggregate. The foreign split uses S&P regional data and company filings. |
| European Union | [MSCI](https://www.msci.com/research-and-insights/blog-post/some-see-a-renaissance-for-european-equities) reports 24.5% of MSCI Europe revenue from the United States in April 2025. A [JPMorgan chart](https://am.jpmorgan.com/content/dam/jpm-am-aem/global/en/insights/market-insights/guide-to-the-markets/mi-guide-to-the-markets-ce-en.pdf) reports Europe 48%, United States 21%, and Asia-Pacific 19% in June 2026. | MSCI Europe includes the United Kingdom, Switzerland, and other non-EU markets, while the model row represents EU-listed value. The source is therefore a regional anchor rather than a matched company universe. Dividing its regional totals among the model's buckets requires judgment. |
| United Kingdom | [FTSE Russell](https://www.lseg.com/en/insights/ftse-russell/the-uks-very-global-country-index) reports that more than four-fifths of FTSE 100 revenue comes from outside the United Kingdom. Its [2025 regional analysis](https://www.lseg.com/en/insights/ftse-russell/uk-equities-a-haven-for-income-and-value) places about 30% in the United States. | The public analysis does not provide a complete current regional vector. The remaining foreign share is allocated from older regional data and the FTSE All-Share comparison. |
| Japan, Korea, and Taiwan | Toyota reports Japan 16.1%, North America 39.5%, Europe 12.5%, Asia 16.5%, and other markets 15.4% by [external-customer location](https://www.sec.gov/Archives/edgar/data/1094517/000119312525115410/d904529dex991.htm). Sony reports Japan 17.3%, United States 31.9%, Europe 20.3%, China 9.6%, Asia-Pacific 12.7%, and other markets 8.3% in its [2025 filing](https://www.sec.gov/Archives/edgar/data/313838/000119312525143137/d820387d20f.htm). TSMC and Samsung provide the principal Korea and Taiwan evidence. | No public TOPIX, KOSPI, or TWSE aggregate was available. TSMC reports customer headquarters, and Samsung does not specify whether its regional table follows the selling subsidiary or the end customer. |
| China and Hong Kong | [MSCI](https://www.msci.com/research-and-insights/blog-post/tracking-the-internationalization-of-chinese-companies) reports that 15% of MSCI China revenue was international in April 2024. | MSCI does not publish the corresponding foreign-market split. The model allocates that 15% across the other five buckets. |
| Rest of world | The bucket combines markets with very different business mixes, including India, Canada, Switzerland, Australia, Brazil, and the Gulf states. | No index corresponds to the bucket. Its entire destination vector is a modeling judgment. |

The source vintages range from 2018 to 2026, and the matrix combines index
aggregates with company-level disclosures. Differences in reporting convention
and the judgment required to divide broad regions limit the precision of
individual cells.

## Magnificent Seven

The Magnificent Seven calculation uses a $22 trillion combined market value
in mid-2026 and a constructed sales vector. The filing data below cover the
latest fiscal year available for each company.

| Company | Reported geographic revenue | Reporting basis and limitation |
|---|---|---|
| Apple | Americas 42.9%, Europe 26.7%, Greater China 15.5%, Japan 6.9%, rest of Asia-Pacific 8.1% | [FY2025 filing](https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm). Apple generally uses customer location. Its Europe and Americas regions extend beyond the model's EU, UK, and US buckets. |
| Microsoft | United States 51.3%, other countries 48.7% | [FY2025 filing](https://www.sec.gov/Archives/edgar/data/789019/000095017025100235/msft-20250630.htm). The United States figure includes some multinational and OEM billings whose geographic source cannot be determined. No finer foreign split is disclosed. |
| Nvidia | United States 69.3%, Taiwan 19.6%, China including Hong Kong 9.1%, other 2.0% | [FY2026 filing](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000021/nvda-20260125.htm). Nvidia uses customer headquarters. It estimates that 76% of data-center revenue from Taiwan-headquartered customers was attributable to end customers in the United States and Europe. |
| Alphabet | United States 48.2%, EMEA 29.1%, APAC 16.8%, other Americas 5.9% | [FY2025 filing](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000018/goog-20251231.htm). Alphabet uses customer address. EMEA and APAC require division among the model's buckets. |
| Amazon | United States 68.3%, Germany 6.4%, United Kingdom 6.0%, Japan 4.3%, rest of world 15.0% | [FY2025 filing](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/amzn-20251231.htm). Amazon uses country-focused stores and, for AWS, the selling entity. The latter can place European revenue in Luxembourg. |
| Meta | United States and Canada 39.2%, Europe 23.2%, Asia-Pacific 26.8%, rest of world 10.8% | [FY2025 filing](https://www.sec.gov/Archives/edgar/data/1326801/000162828026003942/meta-20251231.htm). Meta uses advertiser billing address, which differs from user location. |
| Tesla | United States 50.2%, China 22.1%, other international 27.7% | [FY2025 filing](https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm). Tesla reports the sales location of its products. |

The quantitative blend begins with Apple, Microsoft, Nvidia, Alphabet, Amazon,
and Meta, whose combined FY2025–26 revenue was $2.235 trillion. Their revenue
weights were 18.6%, 12.6%, 9.7%, 18.0%, 32.1%, and 9.0%, respectively. The
company disclosures were translated into common regions as follows. A tilde
marks an interpolated value.

| Company | US | Europe | China | Other Asia | Rest of world |
|---|---:|---:|---:|---:|---:|
| Apple | ~37 | ~21.5 | 15.5 | ~12 | ~14 |
| Microsoft | ~50 | ~25 | ~1.5 | ~9 | ~14.5 |
| Nvidia | ~80 | ~5 | 9.1 | ~5 | ~1 |
| Alphabet | 48.2 | ~25 | ~2 | ~10 | ~15 |
| Amazon | 68.3 | ~18 | ~0.3 | ~5.5 | ~8 |
| Meta | ~37 | 23.2 | ~10 | ~11.6 | ~18 |

The weighted result is approximately 55% United States, 20% Europe, 5%
China, 8–9% other Asia, and 12% rest of world. Europe is divided into 17% EU
and 3% UK. Other Asia is divided into 7% Japan/Korea/Taiwan and the balance is
included in the rest of world. Tesla's comparatively large China share moves
the China cell from approximately 5% to 6%. The final vector in `figure3.py`
is therefore 55% US, 17% EU, 3% UK, 7% Japan/Korea/Taiwan, 6% China, and 12%
rest of world.

Semiconductor revenue creates the largest classification problem. Billing and
shipping data place sales in Taiwan, Singapore, or China when an intermediary
takes delivery. Customer-headquarters data assign the same sale to the United
States when the purchaser is based there, even when the resulting product
serves users worldwide. The model follows payer or customer destination where
possible and uses Nvidia's own end-customer estimate to reallocate its Taiwan
data-center revenue.

## Ownership data

The ownership figures support the companion U.S. calculation in
[`BURDEN.md`](BURDEN.md). Figure 3 itself uses the sales-destination matrix.

| Market or holding | Estimate | Source and limitation |
|---|---:|---|
| Foreign ownership of U.S. corporate equity | 18.4% in 2025 Q4 | The Federal Reserve's [Financial Accounts, table L.224](https://www.federalreserve.gov/releases/z1/20260319/html/l224.htm), reports $20.455 trillion held by the rest of the world out of $111.355 trillion outstanding. The series is broader than listed equity. |
| U.S. holdings of foreign equity | $12.1 trillion at end-2024 | Treasury, Federal Reserve Bank of New York, and Federal Reserve Board [portfolio survey](https://home.treasury.gov/news/press-releases/sb0325). |
| Foreign ownership of UK quoted shares | 58.8% in 2024 | UK Office for National Statistics [ownership survey](https://www.ons.gov.uk/economy/investmentspensionsandtrusts/bulletins/ownershipofukquotedshares/2024). |
| Foreign ownership of Japanese listed shares | 32.4% in FY2024 | The [JPX 2024 Shareownership Survey](https://www.jpx.co.jp/english/markets/statistics-equities/examination/sjcobq000001p5n9-att/e-bunpu2024.pdf) reports the market-value share held by foreign investors. |
| Foreign ownership of Korean listed shares | Approximately 28–31% | Financial Supervisory Service figures reported for different measures and dates. No consistent primary aggregate was available. |
| Foreign ownership of Taiwan market capitalization | 45.41% at end-2024 | Taiwan Stock Exchange [market review](https://www.twse.com.tw/market_insights/en/detail/8a8216d69517ec0c019527a7005a0062). |
| Foreign ownership of China A-shares | Less than approximately 5% | No official aggregate was found. Stock Connect holdings alone were 2.53% of A-share capitalization in December 2022. The estimate does not describe Hong Kong-listed mainland companies. |
| Foreign ownership of EU listed shares | No verified aggregate | ECB securities-holdings data do not provide a directly comparable synthesized share for the model's EU bucket. |

Applying the 18.4% foreign-held share to the model's $62.2 trillion U.S. value
leaves $50.8 trillion held by U.S. residents. Adding their $12.1 trillion of
foreign equity gives $62.9 trillion, or approximately half of the model's
$126.7 trillion world value. The calculation combines series with different
scopes and dates, so it supports an order-of-magnitude estimate.

The IMF Coordinated Portfolio Investment Survey attributes many intermediated
holdings to the jurisdiction of the fund or custodian. Coppola, Maggiori,
Neiman, and Schreger document the resulting distortions in [bilateral capital
positions](https://www.nber.org/papers/w26855). A complete ownership matrix
would require a separate reconstruction of the ultimate issuers and beneficial
owners.
