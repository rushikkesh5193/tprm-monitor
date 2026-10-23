"""Continuous-monitoring checks. Each check takes (vendor, ctx) and returns Issues.

ctx carries the config, the as-of date and the vendor's computed profile.
A terminated vendor is only checked for lingering access: everything else
(assessments, certificates, contracts) no longer applies.
"""
from __future__ import annotations

from .models import Issue, add_months

TIER_SEV = {1: "high", 2: "high", 3: "medium", 4: "low"}


def _issue(v, ctx, check, severity, title, detail, action):
    return Issue(v.id, v.name, ctx["tier"], check, severity, title, detail, action)


def check_offboarding_access(v, ctx):
    if v.status in ("terminated", "offboarding") and v.active_access:
        sev = "critical" if v.status == "terminated" else "high"
        return [_issue(v, ctx, "OFFBOARD_ACCESS", sev,
                       f"{v.status.capitalize()} vendor still has active access",
                       f"Status is '{v.status}' but access ('{v.access}') has not been revoked.",
                       "Revoke accounts, keys and network paths; obtain data deletion/return certificate.")]
    return []


def check_assessment(v, ctx):
    cfg, today, tier = ctx["cfg"], ctx["as_of"], ctx["tier"]
    if v.last_assessment is None:
        sev = {1: "critical", 2: "high", 3: "medium", 4: "low"}[tier]
        return [_issue(v, ctx, "UNASSESSED", sev, "Vendor has never been risk-assessed",
                       f"Tier {tier} vendor with no assessment on record.",
                       "Send the security questionnaire and collect evidence before further reliance.")]
    due = add_months(v.last_assessment, cfg["cadence_months"][str(tier)])
    ctx["next_due"] = due
    if today > due:
        late = (today - due).days
        return [_issue(v, ctx, "ASSESSMENT_OVERDUE", TIER_SEV[tier],
                       "Periodic assessment is overdue",
                       f"Last assessed {v.last_assessment}; Tier {tier} cadence is "
                       f"{cfg['cadence_months'][str(tier)]} months, due {due} ({late} days late).",
                       "Schedule reassessment now.")]
    if (due - today).days <= cfg["due_soon_days"]:
        return [_issue(v, ctx, "ASSESSMENT_DUE_SOON", "low",
                       "Assessment due soon",
                       f"Due {due} ({(due - today).days} days).",
                       "Send the questionnaire ahead of the due date.")]
    return []


def check_certifications(v, ctx):
    out, today, cfg, tier = [], ctx["as_of"], ctx["cfg"], ctx["tier"]
    for c in v.certifications:
        left = (c.expiry - today).days
        if left < 0:
            out.append(_issue(v, ctx, "CERT_EXPIRED", "high" if tier <= 2 else "medium",
                              f"{c.name} certificate expired",
                              f"Expired {c.expiry} ({-left} days ago).",
                              "Request the renewed certificate or a written explanation."))
        elif left <= cfg["expiring_days"]:
            out.append(_issue(v, ctx, "CERT_EXPIRING", "medium" if tier <= 2 else "low",
                              f"{c.name} certificate expiring",
                              f"Expires {c.expiry} ({left} days).",
                              "Ask for the renewal evidence before expiry."))
    return out


def check_soc2_age(v, ctx):
    if v.soc2_report_date is None or ctx["tier"] > 2:
        return []
    limit = add_months(v.soc2_report_date, ctx["cfg"]["soc2_max_age_months"])
    if ctx["as_of"] > limit:
        return [_issue(v, ctx, "SOC2_STALE", "medium", "SOC 2 report is older than 12 months",
                       f"Report dated {v.soc2_report_date}; consider it stale after {limit}.",
                       "Request the latest report and a bridge letter for the gap period.")]
    return []


def check_contract(v, ctx):
    cfg, today = ctx["cfg"], ctx["as_of"]
    if v.contract_end is None:
        return []
    days = (v.contract_end - today).days
    if days < 0:
        return [_issue(v, ctx, "CONTRACT_EXPIRED", "medium", "Contract has expired but vendor is still active",
                       f"Contract ended {v.contract_end} ({-days} days ago).",
                       "Renew, extend formally, or start offboarding.")]
    stale = v.last_assessment is None or ctx.get("next_due") is not None and today > ctx["next_due"]
    if days <= cfg["contract_renewal_days"] and stale:
        return [_issue(v, ctx, "RENEWAL_BLOCKER", "high",
                       "Contract renews soon without a current assessment",
                       f"Contract ends {v.contract_end} ({days} days) and the assessment is missing or overdue.",
                       "Complete the assessment before signing the renewal.")]
    return []


def check_dpa(v, ctx):
    cfg = ctx["cfg"]
    personal = [t for t in v.data_types if t in cfg["personal_data_types"]]
    if personal and not v.dpa_signed:
        sev = "critical" if {"sensitive_personal", "health"} & set(personal) else "high"
        return [_issue(v, ctx, "DPA_MISSING", sev, "No data processing agreement on file",
                       f"Vendor handles {', '.join(sorted(personal))} data without a signed DPA.",
                       "Execute a DPA (processing purpose, security terms, breach notice, deletion) before further processing.")]
    return []


def check_findings(v, ctx):
    out = []
    for f in v.findings:
        if f.closed is None and f.due < ctx["as_of"]:
            late = (ctx["as_of"] - f.due).days
            out.append(_issue(v, ctx, "FINDING_OVERDUE", f.severity,
                              f"Open {f.severity} finding past its due date",
                              f"{f.id}: {f.title}. Due {f.due}, {late} days overdue.",
                              "Get a dated remediation plan from the vendor or record a risk acceptance."))
    return out


def check_controls(v, ctx):
    score, tier, cfg = ctx["control"], ctx["tier"], ctx["cfg"]
    if v.last_assessment is None:
        return []
    if score is None:
        if tier <= 2:
            return [_issue(v, ctx, "QUESTIONNAIRE_INCOMPLETE", "medium",
                           "Questionnaire too incomplete to score",
                           "Fewer than the required share of questions are answered.",
                           "Chase the missing answers and supporting evidence.")]
        return []
    floor = cfg["min_control_score"][str(tier)]
    if score < floor:
        weakest = sorted(ctx["domains"].items(), key=lambda kv: kv[1])[:2]
        weak = ", ".join(f"{d} {s:.0f}" for d, s in weakest)
        return [_issue(v, ctx, "LOW_CONTROL_SCORE", TIER_SEV[tier] if tier <= 2 else "medium",
                       "Control score is below the minimum for this tier",
                       f"Score {score} < required {floor}. Weakest areas: {weak}.",
                       "Agree a remediation plan with dates, or accept the risk in writing.")]
    return []


ACTIVE_CHECKS = [check_assessment, check_certifications, check_soc2_age,
                 check_contract, check_dpa, check_findings, check_controls]
