"""TPRM monitor: tier vendors, score controls and flag what needs attention."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .models import Vendor, SEV_ORDER, parse_date
from .scoring import inherent_score, tier_for, control_score, domain_scores, residual_score
from . import monitor

__all__ = ["load_config", "load_vendors", "analyse"]


def load_config(path=None):
    p = Path(path) if path else Path(__file__).with_name("config.json")
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def load_vendors(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    rows = data["vendors"] if isinstance(data, dict) else data
    vendors, seen = [], set()
    for r in rows:
        v = Vendor.from_dict(r)
        if v.id in seen:
            raise ValueError(f"duplicate vendor id {v.id}")
        seen.add(v.id)
        vendors.append(v)
    return vendors


def analyse(vendors, cfg, as_of: date):
    """Return (profiles, issues). Issues are ranked most urgent first."""
    profiles, issues = [], []
    for v in vendors:
        inh = inherent_score(v, cfg)
        tier = tier_for(inh, cfg)
        ctrl = control_score(v, cfg)
        ctx = {"cfg": cfg, "as_of": as_of, "tier": tier, "control": ctrl,
               "domains": domain_scores(v, cfg), "next_due": None}
        found = monitor.check_offboarding_access(v, ctx)
        if v.status != "terminated":
            for chk in monitor.ACTIVE_CHECKS:
                found += chk(v, ctx)
        issues += found
        profiles.append({
            "id": v.id, "name": v.name, "service": v.service, "owner": v.owner,
            "status": v.status, "tier": tier, "inherent": inh, "control": ctrl,
            "residual": residual_score(inh, ctrl, cfg),
            "last_assessment": str(v.last_assessment) if v.last_assessment else None,
            "next_due": str(ctx["next_due"]) if ctx["next_due"] else None,
            "issues": len(found),
        })
    issues.sort(key=lambda i: (SEV_ORDER[i.severity], i.tier, i.vendor_id, i.check))
    return profiles, issues
