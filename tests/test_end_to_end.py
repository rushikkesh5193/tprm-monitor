import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tprm import load_config, load_vendors, analyse
from tprm.report import kpis, to_markdown
from helpers import AS_OF

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "examples" / "sample_vendors.json"

EXPECTED = {
    ("V001", "DPA_MISSING"), ("V001", "ASSESSMENT_OVERDUE"), ("V001", "CERT_EXPIRED"),
    ("V001", "RENEWAL_BLOCKER"), ("V001", "LOW_CONTROL_SCORE"),
    ("V002", "UNASSESSED"), ("V003", "FINDING_OVERDUE"), ("V004", "OFFBOARD_ACCESS"),
    ("V005", "SOC2_STALE"), ("V005", "CERT_EXPIRING"), ("V006", "ASSESSMENT_DUE_SOON"),
    ("V007", "ASSESSMENT_OVERDUE"), ("V007", "QUESTIONNAIRE_INCOMPLETE"),
    ("V008", "CONTRACT_EXPIRED"), ("V009", "OFFBOARD_ACCESS"), ("V010", "UNASSESSED"),
}


class TestSampleData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = load_config()
        cls.vendors = load_vendors(SAMPLE)
        cls.profiles, cls.issues = analyse(cls.vendors, cls.cfg, AS_OF)

    def test_finds_exactly_the_injected_problems(self):
        got = {(i.vendor_id, i.check) for i in self.issues}
        self.assertEqual(got - EXPECTED, set(), "false positives")
        self.assertEqual(EXPECTED - got, set(), "missed")

    def test_clean_filler_vendors_are_quiet(self):
        noisy = {i.vendor_id for i in self.issues if i.vendor_id > "V010"}
        self.assertEqual(noisy, set())

    def test_ranking_puts_critical_first(self):
        sev = [i.severity for i in self.issues]
        order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        self.assertEqual(sev, sorted(sev, key=order.get))

    def test_kpis(self):
        k = kpis(self.profiles, self.issues)
        self.assertEqual(k["vendors_total"], 30)
        self.assertEqual(k["vendors_active"], 29)
        self.assertEqual(k["overdue_findings"], 1)
        self.assertEqual(sum(k["issues_by_severity"].values()), len(EXPECTED))

    def test_low_control_vendor_has_residual_below_inherent(self):
        p = next(p for p in self.profiles if p["id"] == "V001")
        self.assertLess(p["residual"], p["inherent"])
        u = next(p for p in self.profiles if p["id"] == "V002")   # unassessed: no credit
        self.assertEqual(u["residual"], u["inherent"])

    def test_markdown_mentions_top_issue(self):
        md = to_markdown(self.profiles, self.issues, AS_OF)
        self.assertIn("Northwind Payroll Services", md)
        self.assertIn("### Critical (3)", md)


class TestCli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "tprm", *args], cwd=ROOT,
                              capture_output=True, text=True)

    def test_writes_reports(self):
        with tempfile.TemporaryDirectory() as d:
            r = self.run_cli(str(SAMPLE), "--as-of", "2026-10-23", "--out-dir", d)
            self.assertEqual(r.returncode, 0, r.stderr)
            data = json.loads((Path(d) / "report.json").read_text())
            self.assertEqual(len(data["issues"]), len(EXPECTED))
            self.assertTrue((Path(d) / "report.md").read_text().startswith("# Third-Party"))

    def test_fail_on_exit_codes(self):
        self.assertEqual(self.run_cli(str(SAMPLE), "--as-of", "2026-10-23", "--fail-on", "critical").returncode, 1)

    def test_missing_file_exit_2(self):
        self.assertEqual(self.run_cli("nope.json").returncode, 2)

    def test_bad_date_exit_2(self):
        r = self.run_cli(str(SAMPLE), "--as-of", "yesterday")
        self.assertEqual(r.returncode, 2)
        self.assertIn("expected YYYY-MM-DD", r.stderr)

    def test_duplicate_ids_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "v.json"
            v = {"id": "A", "name": "a", "criticality": 1}
            p.write_text(json.dumps({"vendors": [v, v]}))
            r = self.run_cli(str(p))
            self.assertEqual(r.returncode, 2)
            self.assertIn("duplicate", r.stderr)


if __name__ == "__main__":
    unittest.main()
