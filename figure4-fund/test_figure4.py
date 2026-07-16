import math
import tempfile
import unittest
from pathlib import Path

import figure4 as model
import render


class SharedLedgerTests(unittest.TestCase):
    def test_published_scenarios(self):
        self.assertEqual(
            [(row["growth"], row["discount_rate"], row["labor_floor"])
             for row in model.SCENARIOS],
            [(0.018, 0.055, 0.45), (0.030, 0.0625, 0.35),
             (0.040, 0.070, 0.30)],
        )

    def test_zero_tax(self):
        row = model.advance_simple_year(
            public_share=0.0, market_value=100.0,
            statutory_rate=0.0, year=1)
        self.assertEqual(row["q_end"], 0.0)
        self.assertEqual(row["payout"], 0.0)

    def test_issuance_compounds(self):
        public_share = 0.0
        rates = (0.10, 0.20, 0.05)
        for rate in rates:
            public_share = model.issuance_update(public_share, rate, 1.0)
        self.assertAlmostEqual(
            public_share, 1.0 - math.prod(1.0 - rate for rate in rates))

    def test_full_ownership_survives_full_routing(self):
        self.assertEqual(model.issuance_update(1.0, 0.27, 1.0), 1.0)

    def test_avoidance_and_routing_are_separate(self):
        row = model.advance_simple_year(
            public_share=0.2, market_value=100.0,
            statutory_rate=0.03, year=7, routing=0.6,
            payout_yield=0.0, payout_weight=1.0)
        self.assertAlmostEqual(row["avoidance"], 0.16)
        self.assertAlmostEqual(row["effective_rate"], 0.0252)
        self.assertAlmostEqual(
            row["q_plus"], (1.0 - 0.0252) * 0.2 + 0.0252 * 0.6)

    def test_scale_invariance(self):
        small = model.advance_simple_year(
            public_share=0.2, market_value=100.0,
            statutory_rate=0.02, year=10)
        large = model.advance_simple_year(
            public_share=0.2, market_value=1e9,
            statutory_rate=0.02, year=10)
        self.assertAlmostEqual(small["q_end"], large["q_end"])
        self.assertAlmostEqual(large["payout"] / small["payout"], 1e7)

    def test_mature_payout_stabilizes_ownership(self):
        for public_share in (0.0, 0.1, 0.37, 0.9, 1.0):
            for rate in (0.0, 0.01, 0.04):
                row = model.advance_simple_year(
                    public_share=public_share,
                    market_value=100.0,
                    statutory_rate=rate,
                    year=30,
                    routing=1.0,
                    payout_weight=1.0,
                )
                self.assertAlmostEqual(row["q_end"], public_share)

    def test_resource_identity_grid(self):
        for public_share in (0.0, 0.2, 0.8):
            for rate in (0.0, 0.01, 0.04):
                for year in (1, 22, 50):
                    row = model.advance_simple_year(
                        public_share=public_share,
                        market_value=1234.0,
                        statutory_rate=rate,
                        year=year,
                    )
                    left = row["q_end"] * 1234.0 + row["payout"]
                    right = row["q_plus"] * 1234.0 + row["cash_income"]
                    self.assertAlmostEqual(left, right)

    def test_current_issuance_gets_no_current_payout(self):
        no_issue = model.advance_simple_year(
            public_share=0.25, market_value=100.0,
            statutory_rate=0.0, year=4)
        issued = model.advance_simple_year(
            public_share=0.25, market_value=100.0,
            statutory_rate=0.04, year=4)
        self.assertEqual(no_issue["cash_income"], issued["cash_income"])
        self.assertAlmostEqual(
            issued["cash_income"], 25.0 * model.OPENING_PAYOUT_YIELD)

    def test_routing_endpoints(self):
        self.assertAlmostEqual(model.retirement_routing(0), 2.0 / 3.0)
        self.assertAlmostEqual(model.retirement_routing(10_000), 1.0)

    def test_extreme_bounds(self):
        for public_share in (0.0, 1.0):
            for rate in (0.0, 0.04):
                for routing in (0.0, 1.0):
                    row = model.advance_simple_year(
                        public_share=public_share,
                        market_value=1e12,
                        statutory_rate=rate,
                        year=50,
                        routing=routing,
                        payout_weight=1.0,
                    )
                    self.assertGreaterEqual(row["q_end"], 0.0)
                    self.assertLessEqual(row["q_end"], 1.0)

    def test_two_year_hand_calculation(self):
        public_share, market, rate, payout_yield = 0.1, 200.0, 0.02, 0.03
        for year in (1, 2):
            avoidance = 0.10 + 2.0 * rate
            effective_rate = rate * (1.0 - avoidance)
            share_after_issuance = (
                (1.0 - effective_rate) * public_share
                + effective_rate * 0.75)
            net_receipts = (share_after_issuance - public_share) * market
            cash_income = public_share * market * payout_yield
            payout = (0.035 * public_share * market
                      + 0.25 * net_receipts)
            expected = share_after_issuance + (cash_income - payout) / market
            row = model.advance_simple_year(
                public_share=public_share,
                market_value=market,
                statutory_rate=rate,
                year=year,
                payout_yield=payout_yield,
                routing=0.75,
                payout_weight=0.0,
            )
            self.assertAlmostEqual(row["q_end"], expected)
            public_share = expected
            market *= 1.04


class SimpleModelTests(unittest.TestCase):
    def test_opening_anchor_for_all_variants(self):
        self.assertEqual(model.MARKET0, 62.1857e12)
        self.assertAlmostEqual(
            model.MARKET0 * model.OPENING_PAYOUT_YIELD, 1.5e12, places=2)
        for variant in model.SIMPLE_VARIANTS:
            market, payout, gdp = model.simple_market_and_payout(
                0, model.SCENARIOS[0], variant)
            self.assertAlmostEqual(market, model.MARKET0, places=2)
            self.assertAlmostEqual(payout, 1.5e12, places=2)
            self.assertEqual(gdp, model.GDP0)

    def test_default_is_fixed_market_to_gdp(self):
        scenario = model.SCENARIOS[1]
        self.assertEqual(
            model.simulate_simple(scenario),
            model.simulate_simple(
                scenario, variant=model.SIMPLE_FIXED_MARKET),
        )

    def test_variant_resource_identities(self):
        for variant in model.SIMPLE_VARIANTS:
            for scenario in model.SCENARIOS:
                for row in model.simulate_simple(scenario, variant=variant):
                    market = row["market_cap"]
                    left = row["q_end"] * market + row["payout"]
                    right = row["q_plus"] * market + row["cash_income"]
                    self.assertTrue(math.isclose(left, right, rel_tol=1e-15))

    def test_variants_coincide_without_income_shift(self):
        for scenario in model.SCENARIOS:
            no_shift = model.simulate_simple(
                scenario, variant=model.SIMPLE_NO_SHIFT)
            for variant in (model.SIMPLE_FIXED_MARKET,
                            model.SIMPLE_FIXED_YIELD):
                linked = model.simulate_simple(
                    scenario, variant=variant, wage_to_payout=0.0)
                for expected, actual in zip(no_shift, linked):
                    self.assertTrue(math.isclose(
                        expected["market_cap"], actual["market_cap"],
                        rel_tol=1e-15))
                    self.assertTrue(math.isclose(
                        expected["corporate_payout"],
                        actual["corporate_payout"], rel_tol=1e-15))
                    self.assertAlmostEqual(
                        expected["q_end"], actual["q_end"], places=14)
                    self.assertTrue(math.isclose(
                        expected["payout"], actual["payout"], rel_tol=2e-15))

    def test_fifty_events_and_population_timing(self):
        rows = model.simulate_simple(model.SCENARIOS[0])
        self.assertEqual(len(rows), 50)
        self.assertEqual([row["year"] for row in rows], list(range(1, 51)))
        self.assertAlmostEqual(
            rows[0]["population"],
            model.POPULATION0 * (1.0 + model.POPULATION_GROWTH))
        self.assertAlmostEqual(
            rows[-1]["population"],
            model.POPULATION0 * (1.0 + model.POPULATION_GROWTH) ** 50)


class DcfModelTests(unittest.TestCase):
    def test_share_and_value_recurrences_are_equivalent(self):
        for scenario in model.SCENARIOS:
            direct = model.simulate_dcf(scenario)["rows"]
            bridge = model.simulate_value_recurrence(scenario)
            for expected, actual in zip(direct, bridge):
                self.assertAlmostEqual(
                    expected["q_start"], actual["q_start"], places=12)
                self.assertAlmostEqual(
                    expected["q_end"], actual["q_end"], places=12)
                self.assertTrue(math.isclose(
                    expected["payout"], actual["payout"], rel_tol=1e-13))
                self.assertTrue(math.isclose(
                    expected["net_tax_transfer"],
                    actual["net_tax_transfer"], rel_tol=1e-13))

    def test_current_issuance_cannot_claim_current_payout(self):
        payout = [0.0, 10.0, 20.0]
        no_dilution, _ = model.value_paths(
            payout, [0.0, 0.0, 0.0], 0.1)
        current_dilution, _ = model.value_paths(
            payout, [0.0, 0.5, 0.0], 0.1)
        self.assertAlmostEqual(
            no_dilution[0] - current_dilution[0],
            0.5 * no_dilution[1] / 1.1)
        self.assertAlmostEqual(
            current_dilution[0],
            (10.0 + 0.5 * current_dilution[1]) / 1.1)

    def test_avoidance_enters_pricing_and_ledger_at_same_rate(self):
        result = model.simulate_dcf(model.SCENARIOS[1])
        for year in (1, 25, 50):
            row = result["rows"][year - 1]
            expected = row["statutory_rate"] * (1.0 - row["avoidance"])
            self.assertAlmostEqual(row["effective_rate"], expected)
            self.assertAlmostEqual(
                result["paths"]["effective_rate"][year], expected)
            self.assertAlmostEqual(
                row["q_plus"],
                (1.0 - expected) * row["q_start"]
                + expected * row["routing"])

    def test_retirement_routing_does_not_enter_pricing(self):
        paths = model.economic_paths(model.SCENARIOS[0])
        values_a, _ = model.value_paths(
            paths["payout"], paths["effective_rate"], 0.055)
        self.assertAlmostEqual(model.retirement_routing(0), 2.0 / 3.0)
        self.assertGreater(
            model.retirement_routing(50), model.retirement_routing(1))
        values_b, _ = model.value_paths(
            paths["payout"], paths["effective_rate"], 0.055)
        self.assertEqual(values_a, values_b)

    def test_fifty_ledger_events_with_permanent_policy(self):
        paths = model.economic_paths(model.SCENARIOS[2])
        self.assertTrue(all(
            paths["effective_rate"][year] > 0
            for year in range(1, model.DCF_HORIZON + 1)))
        rows = model.simulate_dcf(model.SCENARIOS[2])["rows"]
        self.assertEqual(len(rows), 50)
        self.assertEqual([row["year"] for row in rows], list(range(1, 51)))
        self.assertAlmostEqual(
            rows[-1]["population"],
            model.POPULATION0 * (1.0 + model.POPULATION_GROWTH) ** 50)

    def test_year_fifty_sunset_creates_terminal_value_artifact(self):
        scenario = model.SCENARIOS[2]
        permanent = model.economic_paths(scenario)
        sunset = model.economic_paths(scenario, policy_years=50)
        permanent_value, _ = model.value_paths(
            permanent["payout"], permanent["effective_rate"],
            scenario["discount_rate"])
        sunset_value, _ = model.value_paths(
            sunset["payout"], sunset["effective_rate"],
            scenario["discount_rate"])
        self.assertGreater(sunset_value[50], permanent_value[50] * 1.25)

    def test_resource_identity(self):
        for scenario in model.SCENARIOS:
            for row in model.simulate_dcf(scenario)["rows"]:
                market = row["market_value"]
                left = row["q_end"] * market + row["payout"]
                right = row["q_plus"] * market + row["cash_income"]
                self.assertTrue(math.isclose(left, right, rel_tol=1e-15))

    def test_extreme_and_central_bounds(self):
        for scenario in model.SCENARIOS:
            result = model.simulate_dcf(scenario)
            self.assertGreater(result["market_value"][0], 0.0)
            self.assertGreaterEqual(result["markdown"], 0.0)
            self.assertLessEqual(result["markdown"], 1.0)
            for row in result["rows"]:
                self.assertGreaterEqual(row["q_end"], 0.0)
                self.assertLessEqual(row["q_end"], 1.0)


class PublishedOutputTests(unittest.TestCase):
    def test_results_csv_golden(self):
        golden = Path(model.__file__).with_name("final") / "results.csv"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "results.csv"
            model.write_results(output)
            self.assertEqual(output.read_text(), golden.read_text())

    def test_non_overwriting_assets_and_metadata(self):
        expected = {
            f"fund-dividend-{model_name}-{theme}.{extension}"
            for model_name in ("simple", "dcf")
            for theme in ("light", "dark")
            for extension in ("svg", "png")
        }
        with tempfile.TemporaryDirectory() as directory:
            paths = render.write_assets(model, directory)
            self.assertEqual({path.name for path in paths}, expected)
            for path in paths:
                self.assertGreater(path.stat().st_size, 1000)
                if path.suffix == ".svg":
                    content = path.read_text()
                    self.assertIn("<model-basis>", content)
                    self.assertIn("<desc>", content)
                    self.assertIn("Dividend per person", content)
                else:
                    self.assertEqual(
                        path.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")


if __name__ == "__main__":
    unittest.main()
