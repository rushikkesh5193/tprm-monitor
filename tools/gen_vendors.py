"""Generate a SYNTHETIC vendor inventory for demos and tests.

All vendor names are invented. Ten scenario vendors carry deliberately injected
problems (so tests can check the monitor finds exactly those); the rest are
clean fillers built to pass every check.

    python3 tools/gen_vendors.py examples/sample_vendors.json
"""
from __future__ import annotations

import json
import random
import sys
from datetime import date, timedelta

AS_OF = date(2026, 10, 23)
QIDS = ["GOV-1", "GOV-2", "ACC-1", "ACC-2", "DAT-1", "DAT-2",
        "INC-1", "INC-2", "BCP-1", "VUL-1", "VUL-2", "SUB-1"]


def d(offset_days):
    return str(AS_OF + timedelta(days=offset_days))


def answers(**overrides):
    a = {q: "yes" for q in QIDS}
    a.update({k.replace("_", "-"): v for k, v in overrides.items()})
    return a


def scenarios():
    base = dict(owner="Procurement", dpa_signed=True)
    return [
        # V001: many problems at once
        dict(base, id="V001", name="Northwind Payroll Services", service="Payroll processing",
             criticality=4, data_types=["sensitive_personal", "financial"], access="remote_limited",
             dpa_signed=False, contract_end="2026-12-01", last_assessment="2025-06-10",
             soc2_report_date="2026-03-01",
             certifications=[{"name": "ISO 27001", "expiry": "2026-08-01"}],
             answers=answers(ACC_1="no", ACC_2="partial", INC_2="no"),
             findings=[{"id": "N-1", "title": "Shared admin account", "severity": "high",
                        "opened": "2025-07-01", "due": "2025-09-01", "closed": "2025-08-20"}]),
        # V002: never assessed
        dict(base, id="V002", name="Lakeside Cloud Hosting", service="IaaS hosting",
             criticality=4, data_types=["personal"], access="remote_privileged",
             contract_end="2027-06-30", last_assessment=None, active_access=True),
        # V003: overdue audit finding
        dict(base, id="V003", name="Brightpath Marketing Analytics", service="Campaign analytics",
             criticality=2, data_types=["personal"], access="none", contract_end="2027-03-31",
             last_assessment="2026-05-01", answers=answers(VUL_1="partial"),
             findings=[{"id": "B-1", "title": "No TLS on reporting endpoint", "severity": "high",
                        "opened": "2026-06-15", "due": "2026-09-01"}]),
        # V004: terminated but access remains
        dict(base, id="V004", name="Old Harbor Backup Co", service="Offsite backup",
             criticality=3, data_types=["personal"], access="remote_privileged",
             status="terminated", active_access=True, last_assessment="2024-02-01"),
        # V005: stale SOC 2 and certificate about to expire
        dict(base, id="V005", name="Quartz Identity Provider", service="SSO / IdP",
             criticality=4, data_types=["internal"], access="remote_privileged",
             contract_end="2027-09-01", last_assessment="2026-03-01",
             soc2_report_date="2025-07-15", answers=answers(),
             certifications=[{"name": "ISO 27001", "expiry": "2026-12-05"}]),
        # V006: assessment due soon
        dict(base, id="V006", name="Pinecrest Facilities Management", service="Building services",
             criticality=1, data_types=["none"], access="onsite_privileged",
             contract_end="2027-05-01", last_assessment="2024-12-20", answers=answers()),
        # V007: overdue and an incomplete questionnaire
        dict(base, id="V007", name="Meridian CRM Cloud", service="Customer CRM",
             criticality=3, data_types=["personal"], access="remote_limited",
             contract_end="2027-08-01", last_assessment="2025-09-15",
             answers={q: "yes" for q in QIDS[:5]}),
        # V008: contract lapsed but vendor still in use
        dict(base, id="V008", name="Delta Courier Logistics", service="Courier",
             criticality=2, data_types=["internal"], access="none", contract_end="2026-08-30",
             last_assessment="2026-02-01", answers=answers()),
        # V009: offboarding, access not yet revoked
        dict(base, id="V009", name="Vertex HR Platform", service="HR system (being replaced)",
             criticality=3, data_types=["sensitive_personal"], access="remote_limited",
             status="offboarding", active_access=True, last_assessment="2026-01-10",
             answers=answers()),
        # V010: low-risk vendor never assessed
        dict(base, id="V010", name="Silverline Stationery", service="Office supplies",
             criticality=1, data_types=["none"], access="none", last_assessment=None),
    ]


def fillers(rng, n):
    first = ["Alder", "Birch", "Cedar", "Dune", "Ember", "Fjord", "Grove", "Harbor",
             "Iris", "Juniper", "Kestrel", "Lumen", "Maple", "Nimbus", "Orchid"]
    last = ["Software", "Systems", "Networks", "Consulting", "Data Labs", "Logistics"]
    names = [f"{a} {b}" for a in first for b in last]
    rng.shuffle(names)
    out = []
    for i in range(n):
        data = rng.choice([["none"], ["internal"], ["personal"], ["internal", "personal"]])
        out.append(dict(
            id=f"V{11 + i:03d}", name=names[i], service="Service " + str(i + 1),
            owner=rng.choice(["IT", "Finance", "HR", "Operations"]),
            criticality=rng.choice([1, 2, 3]), data_types=data,
            access=rng.choice(["none", "remote_limited"]),
            active_access=True, status="active",
            contract_end=d(rng.randint(120, 700)),
            last_assessment=d(-rng.randint(30, 150)),
            soc2_report_date=d(-rng.randint(30, 240)),
            dpa_signed=True,
            certifications=[{"name": "ISO 27001", "expiry": d(rng.randint(200, 700))}],
            answers=answers(), findings=[],
        ))
    return out


def main(path):
    rng = random.Random(7)
    vendors = scenarios() + fillers(rng, 20)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"_note": "SYNTHETIC DATA. Vendor names are invented.", "vendors": vendors}, fh, indent=1)
    print(f"wrote {len(vendors)} vendors to {path}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "examples/sample_vendors.json")
