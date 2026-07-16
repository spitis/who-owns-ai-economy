#!/usr/bin/env python3
"""Model, report, and verification for Figure 3 of "Who Owns the AI Economy?".

In the published essay this is Figure 3 (the fund-dividend simulation in
`../figure4-fund/` is Figure 4).

The club levy: a member set collects an annual charge tau * (covered market
value) from every large firm, apportioned by the DESTINATION of the firm's
sales. Shares of the charge matching sales into non-member markets are
divided pro-rata among members (by their claimed shares of that firm), until
the destination country joins and claims its own. Total collection from any
one firm-bucket is capped at cap_mult times its member-market sales slice.

This is scenario arithmetic built on a stylized 6x6 matrix of listed-market
buckets and sales destinations. DATA.md documents the empirical anchors,
construction, and uncertainty.

Run:  python3 figure3.py           (numeric report + internal checks)
      python3 figure3.py --render  (also writes the figure to final/)
"""
import itertools
import os
import sys
import numpy as np

OUTDIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Allocation model
# ---------------------------------------------------------------------------
def collection_matrix(values, sales, members, rate, cap_multiple):
    """Amount each member collects from each listed-market group."""
    values = np.asarray(values, float)
    sales = np.asarray(sales, float)
    is_member = np.zeros(len(values), bool)
    is_member[list(members)] = True
    collections = np.zeros((len(values), len(values)))
    if not is_member.any():
        return collections

    member_sales = (sales * is_member[None, :]).sum(axis=1)
    for group in range(len(values)):
        if member_sales[group] <= 0:
            continue
        multiplier = min(1.0 / member_sales[group], cap_multiple)
        collections[group, is_member] = (
            rate * values[group] * sales[group, is_member] * multiplier)
    return collections


def bucket_ledger(values, sales, members, rate, cap_multiple):
    """Charge, collected amount, and uncollected amount by market group."""
    values = np.asarray(values, float)
    sales = np.asarray(sales, float)
    is_member = np.zeros(len(values), bool)
    is_member[list(members)] = True
    member_sales = (sales * is_member[None, :]).sum(axis=1)
    charge = rate * values
    collected = np.where(
        member_sales > 0,
        rate * values * np.minimum(1.0, cap_multiple * member_sales),
        0.0,
    )
    return {
        "charge": charge,
        "collected": collected,
        "uncollected": charge - collected,
        "D": member_sales,
        "cap_binds": (
            (values > 0)
            & (member_sales > 0)
            & (cap_multiple * member_sales < 1.0 - 1e-12)
        ),
    }


def member_revenue(values, sales, members, rate, cap_multiple):
    """Total collection by member economy; zero for non-members."""
    return collection_matrix(
        values, sales, members, rate, cap_multiple).sum(axis=0)


def join_delta(values, sales, members, rate, cap_multiple, joiner):
    """Collections before and after one holdout joins the club."""
    before = member_revenue(values, sales, members, rate, cap_multiple)
    after = member_revenue(
        values, sales, list(members) + [joiner], rate, cap_multiple)
    return {
        "joiner_gets": after[joiner],
        "incumbent_before": before,
        "incumbent_after": after,
        "incumbent_change": after - before,
    }

# ===========================================================================
# PARAMETERS  (all values sourced/justified in DATA.md; see error bars there)
# ===========================================================================
BUCKETS = ["US", "EU", "UK", "JKT", "CN", "RoW"]
BUCKET_LONG = {
    "US": "United States", "EU": "European Union", "UK": "United Kingdom",
    "JKT": "Japan+Korea+Taiwan", "CN": "China (+HK)", "RoW": "Rest of World",
}
N = len(BUCKETS)

TAU = 0.01              # levy floor (the essay's 1% floor)
CAP_MULT = 3.0          # collection cap: cap_mult * member-market sales slice
VALUE_BASIS = "mktcap"  # "mktcap" (observed) or "payout" (Figure 4 anchor)

# ---- Covered market value by listed-market group, $ trillions --------------
# Domestic listed-company market cap, end-2024 (WFE definition), from the
# SIFMA 2025 Capital Markets Fact Book country table; Korea via World Bank/
# KRX, Taiwan via TWSE Fact Book at Fed H.10 year-end FX; RoW = residual of
# the $126.7T world total. Total listed value is a simplifying proxy for the
# value above $1B. U.S. index data indicate that companies below the cutoff
# represent only a few percent of value, while comparable evidence is not
# available for every market. All sources are in DATA.md.
V_MKTCAP = np.array([62.19, 11.06, 4.40, 10.12, 16.31, 22.63])  # US EU UK JKT CN RoW

# Fund-figure payout anchor: scale all covered values by the ratio of the
# fund model's post-markdown baseline US value (E_mkt_0 = $48.7676T,
# from simulate_dcf(SCENARIOS[0])["market_value"][0] in
# ../figure4-fund/figure4.py) to observed US cap.
PAYOUT_RATIO = 48.76764884328553 / 62.19   # ~0.784 payout-anchored scaling

# ---- Sales matrix S[listed-market group, destination], rows sum to 1 --------
# Constructed vectors; anchors, per-cell reasoning, and rough uncertainty
# ranges (+-2 to +-6pp) in DATA.md. Key anchors: FactSet GeoRev S&P 500 58% US
# (Jan 2026); MSCI Europe rev exposure Europe 48% / US 21-24.5%; FTSE
# Russell FTSE 100 >80% overseas, ~30% US; MSCI China 85% domestic
# (Apr 2024); Toyota/Sony/TSMC/Samsung segment notes for JKT.
S_BROAD = np.array([
    [0.58, 0.13, 0.02, 0.08, 0.06, 0.13],   # US firms
    [0.22, 0.44, 0.04, 0.06, 0.07, 0.17],   # EU-listed proxy group
    [0.28, 0.18, 0.19, 0.05, 0.06, 0.24],   # UK firms
    [0.24, 0.09, 0.01, 0.40, 0.13, 0.13],   # JKT firms
    [0.04, 0.04, 0.01, 0.03, 0.85, 0.03],   # CN firms
    [0.20, 0.12, 0.02, 0.08, 0.08, 0.50],   # RoW firms
])

# ---- Firm universes: (covered value vector, sales-destination matrix) ------
# Tech sub-universe: the Magnificent Seven as a US-home basket, $22T combined
# market cap (June 2026; see DATA.md --
# note the vintage differs from the end-2024 broad table, so the two
# universes are reported separately, never summed). Destination vector from
# the 10-K blend in SOURCES.md (payer-destination basis;
# US 55 / Europe 20 / China 5 / rest-of-Asia 8.5 / RoW 12, +-2-4pp), with
# the EU/UK split of Europe and the JKT/RoW split of Asia being our own
# further judgment, and China nudged to 6 for Tesla's 22% China share.
V_TECH = np.array([22.0, 0.0, 0.0, 0.0, 0.0, 0.0])        # US EU UK JKT CN RoW
S_TECH = np.vstack([
    np.array([0.55, 0.17, 0.03, 0.07, 0.06, 0.12]),        # Mag-7 destination
    # rows 2-6 unused (zero covered value) but kept row-stochastic for checks
    np.full((5, 6), 1.0 / 6.0),
])

# ---- Scale anchors: revenue as % of general government expenditure ----------
# One denominator KIND for every economy (all-levels general government
# expenditure), so cross-economy comparison is fair and does not invert the
# figure's block sizes. The EU denominator includes member-state spending
# rather than only the EU central budget. Values combine IMF 2025 general-government
# expenditure as a share of GDP with IMF 2025 current-dollar GDP. DATA.md gives
# the indicators, groupings, and calculation. (report label, short label, $B)
ANCHORS = {
    "US": ("all US government spending (all levels, ~$11.60T)",
           "all US government spending", 11600.6),
    "EU": ("all EU general government spending (~$10.49T)",
           "all EU public spending", 10491.4),
    "UK": ("all UK general government spending (~$1.75T)",
           "all UK public spending", 1747.1),
    "JKT": ("government spending across Japan, Korea, Taiwan (~$2.25T)",
            "the region's public spending", 2249.4),
    "CN": ("all China and Hong Kong government spending (~$6.55T)",
           "all Chinese government spending", 6552.1),
    "RoW": ("general government spending, rest of world (~$10.98T)",
            "the rest of the world's spending", 10982.0),
}

# ---- Club scenarios (member sets, by bucket index) -------------------------
def _idx(names):
    return [BUCKETS.index(n) for n in names]

SCENARIOS = [
    ("US only",             _idx(["US"])),
    ("US + EU",             _idx(["US", "EU"])),
    ("US + EU + UK + JKT",  _idx(["US", "EU", "UK", "JKT"])),
    ("everyone but China",  _idx(["US", "EU", "UK", "JKT", "RoW"])),
    ("global",              _idx(["US", "EU", "UK", "JKT", "CN", "RoW"])),
]


# ===========================================================================
def universes():
    """Return dict label -> (V $T, S) using the selected value basis."""
    scale = 1.0 if VALUE_BASIS == "mktcap" else PAYOUT_RATIO
    return {
        "broad listed-value proxy": (V_MKTCAP * scale, S_BROAD),
        "Magnificent Seven only":  (V_TECH * scale, S_TECH),
    }


def report():
    print("=" * 78)
    print("CLUB LEVY  (tau=%.0f%%, cap=%gx member slice, basis=%s)"
          % (TAU * 100, CAP_MULT, VALUE_BASIS))
    print("=" * 78)
    for ulabel, (V, S) in universes().items():
        print("\n" + "#" * 78)
        print(f"# FIRM UNIVERSE: {ulabel}   (covered value ${V.sum():.1f}T)")
        print("#" * 78)
        _report_universe(V, S)


def _report_universe(V, S):
    for slabel, M in SCENARIOS:
        rev = member_revenue(V, S, M, TAU, CAP_MULT) * 1000.0   # $B
        led = bucket_ledger(V, S, M, TAU, CAP_MULT)
        collected = led["collected"].sum() * 1000.0
        charge = led["charge"].sum() * 1000.0
        caps = [BUCKETS[i] for i in range(N) if led["cap_binds"][i]]
        print(f"\n[{slabel}]  members={{{', '.join(BUCKETS[i] for i in M)}}}"
              f"   club take ${collected:,.0f}B/yr"
              f"  ({collected/charge:.0%} of ${charge:,.0f}B total charge)"
              f"   cap binds: {caps if caps else 'none'}")
        for j in M:
            aname, _, aval = ANCHORS[BUCKETS[j]]
            pct = 100.0 * rev[j] / aval if aval else float("nan")
            print(f"    {BUCKET_LONG[BUCKETS[j]]:20s} collects ${rev[j]:7,.0f}B/yr"
                  f"   = {pct:5.0f}% of {aname}")
        # join deltas for non-members
        nonmem = [j for j in range(N) if j not in M]
        for j in nonmem:
            jd = join_delta(V, S, M, TAU, CAP_MULT, j)
            joiner_collection = jd["joiner_gets"] * 1000.0
            inc_loss = (
                jd["incumbent_before"][M] - jd["incumbent_after"][M]
            ).sum() * 1000.0
            print(f"    AFTER JOINING  {BUCKET_LONG[BUCKETS[j]]:20s}"
                  f" collects ${joiner_collection:7,.0f}B/yr"
                  f"   (incumbents collect ${inc_loss:,.0f}B less)")


def checks():
    print("\n" + "=" * 78)
    print("INTERNAL CHECKS")
    print("=" * 78)
    ok = True
    for basis in ("mktcap", "payout"):
        scale = 1.0 if basis == "mktcap" else PAYOUT_RATIO
        for ulabel, (Vb, S) in {
            "broad": (V_MKTCAP * scale, S_BROAD),
            "tech": (V_TECH * scale, S_TECH),
        }.items():
            # (1) destination rows sum to 1
            rs = S.sum(axis=1)
            c1 = np.allclose(rs, 1.0, atol=1e-9)
            # (2) per member set: total collected <= tau * total covered value
            #     and revenue == collected (conservation) and cap identity
            c2 = c3 = c4 = True
            for _, M in SCENARIOS:
                led = bucket_ledger(Vb, S, M, TAU, CAP_MULT)
                rev = member_revenue(Vb, S, M, TAU, CAP_MULT)
                c2 &= led["collected"].sum() <= TAU * Vb.sum() + 1e-9
                c3 &= abs(rev.sum() - led["collected"].sum()) < 1e-9
                # conservation per bucket: claimed + uncollected == charge
                c4 &= np.allclose(led["collected"] + led["uncollected"],
                                  led["charge"], atol=1e-9)
            # (5) cap binds only where member-dest share < 1/cap_mult
            c5 = True
            for _, M in SCENARIOS:
                led = bucket_ledger(Vb, S, M, TAU, CAP_MULT)
                expect = (Vb > 0) & (led["D"] > 0) & (CAP_MULT * led["D"] < 1.0 - 1e-9)
                c5 &= np.array_equal(led["cap_binds"], expect)
            allok = c1 and c2 and c3 and c4 and c5
            ok &= allok
            print(f"  [{basis:6s}/{ulabel:5s}] rows=1:{c1}  collect<=charge:{c2}"
                  f"  conserv:{c3}  bucket-conserv:{c4}  cap-logic:{c5}"
                  f"   {'OK' if allok else '** FAIL **'}")
    # (7) full 2^N membership sweep (broad+tech, mktcap): per-bucket
    #     conservation and no-overcharge, covering the widget's whole state space
    c7 = True
    for Vb, S in ((V_MKTCAP, S_BROAD), (V_TECH, S_TECH)):
        for r in range(N + 1):
            for combo in itertools.combinations(range(N), r):
                M = list(combo)
                led = bucket_ledger(Vb, S, M, TAU, CAP_MULT)
                C = collection_matrix(Vb, S, M, TAU, CAP_MULT)
                rev = member_revenue(Vb, S, M, TAU, CAP_MULT)
                c7 &= np.allclose(C.sum(axis=1), led["collected"], atol=1e-9)
                c7 &= np.allclose(C.sum(axis=0), rev, atol=1e-9)
                c7 &= bool((C.sum(axis=1) <= led["charge"] + 1e-9).all())
                c7 &= np.allclose(led["collected"] + led["uncollected"],
                                  led["charge"], atol=1e-9)

    # Targeted cases formerly kept in a separate unit-test file.
    sample_values = np.array([100.0, 50.0, 25.0])
    sample_sales = np.array([
        [0.60, 0.30, 0.10],
        [0.20, 0.70, 0.10],
        [0.25, 0.25, 0.50],
    ])
    c7 &= np.array_equal(
        collection_matrix(sample_values, sample_sales, [], 0.01, 3.0),
        np.zeros((3, 3)),
    )
    global_ledger = bucket_ledger(
        sample_values, sample_sales, [0, 1, 2], 0.01, 3.0)
    c7 &= np.allclose(global_ledger["collected"], 0.01 * sample_values)
    sample_matrix = collection_matrix(
        sample_values, sample_sales, [0, 1], 0.01, 3.0)
    for home in range(3):
        observed = sample_matrix[home, [0, 1]]
        observed = observed / observed.sum()
        expected = sample_sales[home, [0, 1]]
        expected = expected / expected.sum()
        c7 &= np.allclose(observed, expected)
    expected_cap = 0.01 * sample_values * np.minimum(
        1.0, 3.0 * sample_sales[:, 2])
    c7 &= np.allclose(
        bucket_ledger(sample_values, sample_sales, [2], 0.01, 3.0)["collected"],
        expected_cap,
    )
    before = member_revenue(sample_values, sample_sales, [0], 0.01, 3.0)
    after = member_revenue(sample_values, sample_sales, [0, 1], 0.01, 3.0)
    delta = join_delta(sample_values, sample_sales, [0], 0.01, 3.0, 1)
    c7 &= np.allclose(delta["incumbent_before"], before)
    c7 &= np.allclose(delta["incumbent_after"], after)
    c7 &= np.allclose(delta["incumbent_change"], after - before)
    ok &= c7
    print(f"  [subset sweep] 2^{N} states, per-bucket conservation & "
          f"no-overcharge (broad+tech): {c7}   {'OK' if c7 else '** FAIL **'}")
    # (6) China cap should bind in every non-global broad scenario, then release
    led_out = bucket_ledger(V_MKTCAP, S_BROAD, _idx(["US", "EU", "UK", "JKT", "RoW"]), TAU, CAP_MULT)
    led_in = bucket_ledger(V_MKTCAP, S_BROAD, _idx(BUCKETS), TAU, CAP_MULT)
    ci = BUCKETS.index("CN")
    c6 = led_out["cap_binds"][ci] and (not led_in["cap_binds"][ci])
    ok &= c6
    print(f"  [china cap] binds when China out, releases when in: {c6}"
          f"   {'OK' if c6 else '** FAIL **'}")
    print("\n  " + ("ALL CHECKS PASS" if ok else "** CHECKS FAILED **"))
    return ok


def sensitivity():
    print("\n" + "=" * 78)
    print("SENSITIVITY")
    print("=" * 78)
    V, S = V_MKTCAP, S_BROAD
    print("\ncap multiple (broad universe, 'everyone but China'):")
    M = _idx(["US", "EU", "UK", "JKT", "RoW"])
    for cm in (2.0, 3.0, 5.0):
        rev = member_revenue(V, S, M, TAU, cm) * 1000.0
        led = bucket_ledger(V, S, M, TAU, cm)
        print(f"  cap={cm:g}x: club take ${led['collected'].sum()*1000:,.0f}B/yr"
              f"   US ${rev[0]:,.0f}B  EU ${rev[1]:,.0f}B"
              f"   China charge left on table ${led['uncollected'][BUCKETS.index('CN')]*1000:,.0f}B")
    print("\nvalue basis (broad universe, 'US + EU'):")
    M = _idx(["US", "EU"])
    for basis, scale in (("mktcap", 1.0), ("payout", PAYOUT_RATIO)):
        rev = member_revenue(V * scale, S, M, TAU, CAP_MULT) * 1000.0
        print(f"  {basis:6s} (scale {scale:.2f}): US ${rev[0]:,.0f}B  EU ${rev[1]:,.0f}B")


def main():
    report()
    sensitivity()
    ok = checks()
    if "--render" in sys.argv:
        import render
        fig_anchors = {k: (short, val) for k, (_, short, val) in ANCHORS.items()}
        render.write_assets(sys.modules[__name__], V_MKTCAP, S_BROAD, BUCKETS,
                            BUCKET_LONG, TAU, CAP_MULT, fig_anchors, OUTDIR)
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
