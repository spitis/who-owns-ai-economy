# Figure 3: the enforcement-club ledger

This directory contains the simulation behind Figure 3 of
["Who Owns the AI Economy?"](https://silviupitis.com/blog/2026/who-owns-the-ai-economy/).
The essay proposes an annual levy on large corporations, paid in newly issued
non-voting shares and enforced through market access. Each member collects a
share of the levy according to the firm's sales into its market, wherever the
firm is based.

The model places listed-company value into six market buckets: the United
States, European Union, United Kingdom, Japan/Korea/Taiwan, China including
Hong Kong, and the rest of the world. Each bucket has a market-value proxy and
a constructed vector of sales destinations. [`DATA.md`](DATA.md) gives the
complete input table and provenance.

## Allocation rule

Each firm's annual charge starts at 1% of its equity value. A member's initial
claim is the share of that charge matching the firm's sales in its market. If
20% of a firm's sales are American, for example, the United States begins with
20% of the charge.

Sales in holdout markets leave part of the charge unclaimed. The existing
members divide that part in proportion to their initial claims, subject to a
cap: together they cannot collect more than three times the firm's combined
sales share in their markets. Suppose a firm makes 20% of its sales in the
United States, 10% in the European Union, and 70% in holdout markets. The two
members divide collections two to one, reflecting their 20% and 10% sales
shares. Because only 30% of the firm's sales are inside the club, the cap lets
them collect 90% of the charge. The United States receives 60%, the European
Union receives 30%, and the final 10% remains uncollected. Once at least
one-third of a firm's sales are inside the club, the cap permits collection of
the full charge.

The code verifies that members' collections sum to the capped charge for every
firm group and for all 64 possible membership sets.

## Sensitivity

- Changing the cap from 3x to 2x reduces the everyone-but-China club's annual
  collection from $1,177 billion to $1,153 billion. Raising it to 5x increases
  the collection to $1,226 billion. The corresponding uncollected charge on
  Chinese firms is $90 billion at 3x, $114 billion at 2x, and $41 billion at
  5x.
- Scaling market values to the Figure 4 baseline post-levy valuation reduces
  every dollar flow by 21.6% without changing its allocation.

## Scope and limitations

The model is a one-year snapshot using end-2024 market values, before repricing
or avoidance. It uses total listed-company value as a simplifying proxy for
firms above the essay's $1 billion threshold and does not model the phase-in
between $1 billion and $10 billion. U.S. index data indicate that companies
below the threshold make up only a few percent of listed value, although
comparable evidence is not available for every market.

The sales matrix is an illustrative construction anchored to published revenue
data. Public disclosures mix customer location, billing location, and customer
headquarters, and the Japan/Korea/Taiwan and rest-of-world rows require the
most judgment. The exact matrix, the evidence for each row, and the stated
uncertainty are in [`DATA.md`](DATA.md). [`BURDEN.md`](BURDEN.md) estimates the
initial markdown by investor residence, while Figure 3 allocates collections
according to sales.

## Reproduce

```bash
python3 figure3.py
python3 figure3.py --render
```
