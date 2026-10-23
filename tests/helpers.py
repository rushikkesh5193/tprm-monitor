from datetime import date

from tprm import load_config, analyse
from tprm.models import Vendor

AS_OF = date(2026, 10, 23)
CFG = load_config()
QIDS = [q["id"] for q in CFG["questionnaire"]]


def vendor(**kw):
    """A clean Tier-3 vendor that triggers no checks; override fields per test."""
    d = dict(id="T1", name="Test Vendor", service="x", owner="o", criticality=2,
             data_types=["internal"], access="none", status="active", active_access=False,
             contract_end="2028-01-01", last_assessment="2026-08-01",
             soc2_report_date=None, dpa_signed=True, certifications=[],
             answers={q: "yes" for q in QIDS}, findings=[])
    d.update(kw)
    return Vendor.from_dict(d)


def checks(**kw):
    """Run analyse on one vendor and return the set of check ids raised."""
    _, issues = analyse([vendor(**kw)], CFG, AS_OF)
    return {i.check for i in issues}


def issues_for(**kw):
    return analyse([vendor(**kw)], CFG, AS_OF)[1]
