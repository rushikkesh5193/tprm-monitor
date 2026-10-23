"""Reports: KPIs, markdown and JSON."""
from __future__ import annotations

import json
from collections import Counter

OVERDUE_CHECKS = {"UNASSESSED", "ASSESSMENT_OVERDUE"}


def kpis(profiles, issues):
    active = [p for p in profiles if p["status"] != "terminated"]
    in_scope = [p for p in active if p["tier"] <= 3]
    late_ids = {i.vendor_id for i in issues if i.check in OVERDUE_CHECKS}
    on_time = [p for p in in_scope if p["id"] not in late_ids]
    return {
        "vendors_total": len(profiles),
        "vendors_active": len(active),
        "by_tier": dict(sorted(Counter(p["tier"] for p in active).items())),
        "assessed_on_time_pct": round(100 * len(on_time) / len(in_scope), 1) if in_scope else None,
        "issues_by_severity": {s: sum(1 for i in issues if i.severity == s)
                               for s in ("critical", "high", "medium", "low")},
        "overdue_findings": sum(1 for i in issues if i.check == "FINDING_OVERDUE"),
    }


def to_json(profiles, issues, as_of):
    return json.dumps({"as_of": str(as_of), "kpis": kpis(profiles, issues),
                       "vendors": profiles, "issues": [i.as_dict() for i in issues]},
                      indent=2)


def _cell(x):
    return "-" if x is None else str(x)


def to_markdown(profiles, issues, as_of):
    k = kpis(profiles, issues)
    s = k["issues_by_severity"]
    L = [f"# Third-Party Risk Monitoring Report", "",
         f"As of **{as_of}**. Data in this report is synthetic unless you supplied your own.", "",
         "## Summary", "",
         f"- Vendors: {k['vendors_total']} ({k['vendors_active']} active)",
         "- Active by tier: " + ", ".join(f"Tier {t}: {n}" for t, n in k["by_tier"].items()),
         f"- Tier 1-3 vendors with a current assessment: {_cell(k['assessed_on_time_pct'])}%",
         f"- Open issues: {s['critical']} critical, {s['high']} high, {s['medium']} medium, {s['low']} low",
         f"- Overdue audit findings: {k['overdue_findings']}", ""]

    L += ["## Issues needing action", ""]
    if not issues:
        L += ["No issues found.", ""]
    for sev in ("critical", "high", "medium", "low"):
        group = [i for i in issues if i.severity == sev]
        if not group:
            continue
        L += [f"### {sev.capitalize()} ({len(group)})", "",
              "| Vendor | Tier | Check | Detail | Action |", "|---|---|---|---|---|"]
        for i in group:
            L.append(f"| {i.vendor_name} ({i.vendor_id}) | {i.tier} | {i.check} | "
                     f"{i.detail} | {i.action} |")
        L.append("")

    L += ["## Vendor register", "",
          "| ID | Vendor | Status | Tier | Inherent | Control | Residual | Last assessed | Next due | Issues |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for p in sorted(profiles, key=lambda p: (-p["residual"], p["id"])):
        L.append(f"| {p['id']} | {p['name']} | {p['status']} | {p['tier']} | {p['inherent']} | "
                 f"{_cell(p['control'])} | {p['residual']} | {_cell(p['last_assessment'])} | "
                 f"{_cell(p['next_due'])} | {p['issues']} |")
    L += ["", "Scores are 0-100. Residual = inherent risk reduced by control strength; "
          "a vendor with no usable questionnaire gets no credit (residual = inherent).", ""]
    return "\n".join(L)
