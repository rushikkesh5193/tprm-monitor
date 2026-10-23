import unittest

from helpers import checks, issues_for, AS_OF, QIDS


class TestCleanBaseline(unittest.TestCase):
    def test_clean_vendor_raises_nothing(self):
        self.assertEqual(checks(), set())


class TestAssessment(unittest.TestCase):
    def test_never_assessed_severity_follows_tier(self):
        # criticality 4 + personal + remote_privileged => Tier 1 => critical
        i = issues_for(criticality=4, data_types=["personal"], access="remote_privileged",
                       last_assessment=None)
        self.assertIn(("UNASSESSED", "critical"), {(x.check, x.severity) for x in i})
        i = issues_for(criticality=1, data_types=["none"], last_assessment=None)
        self.assertIn(("UNASSESSED", "low"), {(x.check, x.severity) for x in i})

    def test_overdue_vs_not(self):
        # Tier 3 cadence = 24 months. 2024-10-22 is one day past it, 2024-10-23 is exactly due.
        self.assertIn("ASSESSMENT_OVERDUE", checks(last_assessment="2024-10-22"))
        self.assertNotIn("ASSESSMENT_OVERDUE", checks(last_assessment="2024-10-23"))

    def test_cadence_depends_on_tier(self):
        # Same dates: fine for Tier 3 (24m) but overdue for Tier 1 (12m).
        self.assertNotIn("ASSESSMENT_OVERDUE", checks(last_assessment="2025-01-01"))
        self.assertIn("ASSESSMENT_OVERDUE",
                      checks(last_assessment="2025-01-01", criticality=4,
                             data_types=["personal"], access="remote_privileged"))

    def test_due_soon_window(self):
        self.assertIn("ASSESSMENT_DUE_SOON", checks(last_assessment="2024-12-20"))   # 58 days left
        self.assertNotIn("ASSESSMENT_DUE_SOON", checks(last_assessment="2025-01-10"))  # 79 days left


class TestCertificates(unittest.TestCase):
    def cert(self, expiry):
        return [{"name": "ISO 27001", "expiry": expiry}]

    def test_expired_expiring_and_ok(self):
        self.assertIn("CERT_EXPIRED", checks(certifications=self.cert("2026-10-22")))
        self.assertIn("CERT_EXPIRING", checks(certifications=self.cert("2027-01-21")))   # 90 days
        self.assertNotIn("CERT_EXPIRING", checks(certifications=self.cert("2027-01-22")))  # 91 days
        self.assertEqual(checks(certifications=self.cert("2028-01-01")), set())

    def test_expiring_today_is_not_yet_expired(self):
        got = checks(certifications=self.cert("2026-10-23"))
        self.assertIn("CERT_EXPIRING", got)
        self.assertNotIn("CERT_EXPIRED", got)


class TestSoc2(unittest.TestCase):
    TIER2 = dict(criticality=3, data_types=["personal"], access="remote_limited")

    def test_stale_only_for_top_tiers(self):
        self.assertIn("SOC2_STALE", checks(soc2_report_date="2025-10-01", **self.TIER2))
        self.assertNotIn("SOC2_STALE", checks(soc2_report_date="2025-10-01"))      # Tier 3
        self.assertNotIn("SOC2_STALE", checks(soc2_report_date="2025-11-01", **self.TIER2))


class TestContract(unittest.TestCase):
    def test_renewal_blocker_needs_both_conditions(self):
        late = dict(last_assessment="2024-01-01")                       # overdue for Tier 3
        self.assertIn("RENEWAL_BLOCKER", checks(contract_end="2026-12-01", **late))
        self.assertNotIn("RENEWAL_BLOCKER", checks(contract_end="2027-06-01", **late))   # too far away
        self.assertNotIn("RENEWAL_BLOCKER", checks(contract_end="2026-12-01"))           # assessment current

    def test_renewal_blocker_when_never_assessed(self):
        self.assertIn("RENEWAL_BLOCKER", checks(contract_end="2026-12-01", last_assessment=None))

    def test_expired_contract(self):
        self.assertIn("CONTRACT_EXPIRED", checks(contract_end="2026-10-22"))
        self.assertNotIn("CONTRACT_EXPIRED", checks(contract_end="2026-10-23"))


class TestDpa(unittest.TestCase):
    def test_missing_dpa_only_for_personal_data(self):
        self.assertIn("DPA_MISSING", checks(data_types=["personal"], dpa_signed=False))
        self.assertNotIn("DPA_MISSING", checks(data_types=["internal"], dpa_signed=False))
        self.assertNotIn("DPA_MISSING", checks(data_types=["personal"], dpa_signed=True))

    def test_sensitive_data_is_critical(self):
        sev = {i.severity for i in issues_for(data_types=["health"], dpa_signed=False)
               if i.check == "DPA_MISSING"}
        self.assertEqual(sev, {"critical"})
        sev = {i.severity for i in issues_for(data_types=["personal"], dpa_signed=False)
               if i.check == "DPA_MISSING"}
        self.assertEqual(sev, {"high"})


class TestFindings(unittest.TestCase):
    def f(self, **kw):
        d = {"id": "F-1", "title": "t", "severity": "high", "opened": "2026-06-01", "due": "2026-09-01"}
        d.update(kw)
        return [d]

    def test_open_past_due_flagged_with_days_late(self):
        i = [x for x in issues_for(findings=self.f()) if x.check == "FINDING_OVERDUE"]
        self.assertEqual(len(i), 1)
        self.assertIn("52 days overdue", i[0].detail)
        self.assertEqual(i[0].severity, "high")

    def test_closed_or_not_yet_due_not_flagged(self):
        self.assertNotIn("FINDING_OVERDUE", checks(findings=self.f(closed="2026-09-10")))
        self.assertNotIn("FINDING_OVERDUE", checks(findings=self.f(due="2026-10-23")))

    def test_each_overdue_finding_reported_separately(self):
        fs = self.f() + self.f(id="F-2")
        self.assertEqual(len([x for x in issues_for(findings=fs) if x.check == "FINDING_OVERDUE"]), 2)


class TestControls(unittest.TestCase):
    def test_low_score_flagged_against_tier_floor(self):
        bad = {q: "no" for q in QIDS}
        self.assertIn("LOW_CONTROL_SCORE", checks(answers=bad))

    def test_floor_is_stricter_for_higher_tiers(self):
        a = {q: "yes" for q in QIDS}
        a["ACC-1"] = "no"; a["INC-2"] = "no"; a["DAT-1"] = "no"     # 24-9=15 -> 62.5
        self.assertNotIn("LOW_CONTROL_SCORE", checks(answers=a))   # Tier 3 floor 50
        self.assertIn("LOW_CONTROL_SCORE",
                      checks(answers=a, criticality=4, data_types=["personal"],
                             access="remote_privileged"))         # Tier 1 floor 75

    def test_incomplete_questionnaire_only_for_top_tiers(self):
        few = {"GOV-1": "yes"}
        self.assertIn("QUESTIONNAIRE_INCOMPLETE",
                      checks(answers=few, criticality=4, data_types=["personal"], access="remote_privileged"))
        self.assertNotIn("QUESTIONNAIRE_INCOMPLETE", checks(answers=few))

    def test_unassessed_vendor_not_also_flagged_for_controls(self):
        got = checks(last_assessment=None, answers={})
        self.assertNotIn("QUESTIONNAIRE_INCOMPLETE", got)


class TestOffboarding(unittest.TestCase):
    def test_terminated_with_access_is_critical(self):
        i = issues_for(status="terminated", active_access=True, access="remote_limited")
        self.assertEqual({(x.check, x.severity) for x in i}, {("OFFBOARD_ACCESS", "critical")})

    def test_offboarding_with_access_is_high(self):
        i = issues_for(status="offboarding", active_access=True)
        self.assertIn(("OFFBOARD_ACCESS", "high"), {(x.check, x.severity) for x in i})

    def test_terminated_vendor_skips_other_checks(self):
        # Overdue assessment and expired cert no longer matter once terminated and access is gone.
        got = checks(status="terminated", active_access=False, last_assessment="2020-01-01",
                     certifications=[{"name": "x", "expiry": "2020-01-01"}])
        self.assertEqual(got, set())


if __name__ == "__main__":
    unittest.main()
