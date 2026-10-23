import unittest
from datetime import date

from tprm.models import add_months, parse_date
from tprm.scoring import inherent_score, tier_for, control_score, domain_scores, residual_score
from helpers import CFG, QIDS, vendor


class TestInherentAndTier(unittest.TestCase):
    def test_max_risk_is_100_min_is_0(self):
        hi = vendor(criticality=4, data_types=["health"], access="onsite_privileged")
        lo = vendor(criticality=1, data_types=["none"], access="none")
        self.assertEqual(inherent_score(hi, CFG), 100.0)
        self.assertEqual(inherent_score(lo, CFG), 10.0)

    def test_most_sensitive_data_type_wins(self):
        a = vendor(data_types=["internal", "health"])
        b = vendor(data_types=["health"])
        self.assertEqual(inherent_score(a, CFG), inherent_score(b, CFG))

    def test_tier_boundaries(self):
        self.assertEqual(tier_for(70, CFG), 1)
        self.assertEqual(tier_for(69.9, CFG), 2)
        self.assertEqual(tier_for(45, CFG), 2)
        self.assertEqual(tier_for(44.9, CFG), 3)
        self.assertEqual(tier_for(25, CFG), 3)
        self.assertEqual(tier_for(24.9, CFG), 4)

    def test_criticality_out_of_range_rejected(self):
        with self.assertRaises(ValueError):
            vendor(criticality=5)


class TestControlScore(unittest.TestCase):
    def test_all_yes_is_100_all_no_is_0(self):
        self.assertEqual(control_score(vendor(), CFG), 100.0)
        self.assertEqual(control_score(vendor(answers={q: "no" for q in QIDS}), CFG), 0.0)

    def test_weighted_not_simple_average(self):
        # ACC-1 has weight 3 of 24 total, so failing it costs 12.5 points.
        a = {q: "yes" for q in QIDS}
        a["ACC-1"] = "no"
        self.assertEqual(control_score(vendor(answers=a), CFG), 87.5)

    def test_partial_is_half(self):
        a = {q: "yes" for q in QIDS}
        a["ACC-1"] = "partial"        # weight 3 -> loses 1.5 of 24
        self.assertEqual(control_score(vendor(answers=a), CFG), 93.8)

    def test_na_is_excluded_not_penalised(self):
        a = {q: "yes" for q in QIDS}
        a["SUB-1"] = "na"
        self.assertEqual(control_score(vendor(answers=a), CFG), 100.0)

    def test_too_few_answers_gives_none(self):
        self.assertIsNone(control_score(vendor(answers={"GOV-1": "yes"}), CFG))

    def test_coverage_boundary(self):
        # Answering exactly 80% of the total weight (19.2 of 24) is not reachable
        # with integer weights, so check either side: 20/24 passes, 18/24 fails.
        keep20 = {q["id"]: "yes" for q in CFG["questionnaire"] if q["id"] not in ("DAT-2", "INC-1")}
        self.assertEqual(sum(q["weight"] for q in CFG["questionnaire"] if q["id"] in keep20), 20)
        self.assertEqual(control_score(vendor(answers=keep20), CFG), 100.0)
        keep18 = dict(keep20)
        del keep18["BCP-1"]
        del keep18["VUL-1"]
        self.assertIsNone(control_score(vendor(answers=keep18), CFG))

    def test_domain_scores_find_weak_area(self):
        a = {q: "yes" for q in QIDS}
        a["ACC-1"] = a["ACC-2"] = "no"
        d = domain_scores(vendor(answers=a), CFG)
        self.assertEqual(d["Access control"], 0.0)
        self.assertEqual(d["Governance"], 100.0)

    def test_residual(self):
        self.assertEqual(residual_score(80, None, CFG), 80)       # no credit when unknown
        self.assertEqual(residual_score(80, 100, CFG), 16.0)
        self.assertEqual(residual_score(80, 0, CFG), 80.0)


class TestDates(unittest.TestCase):
    def test_add_months_clamps_month_end(self):
        self.assertEqual(add_months(date(2026, 1, 31), 1), date(2026, 2, 28))
        self.assertEqual(add_months(date(2024, 1, 31), 1), date(2024, 2, 29))
        self.assertEqual(add_months(date(2026, 11, 15), 3), date(2027, 2, 15))

    def test_bad_date_is_a_clear_error(self):
        with self.assertRaises(ValueError):
            parse_date("23/10/2026")


if __name__ == "__main__":
    unittest.main()
