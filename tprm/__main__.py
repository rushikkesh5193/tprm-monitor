"""CLI: python3 -m tprm vendors.json [--as-of YYYY-MM-DD] [--config c.json] [--out-dir DIR] [--fail-on SEVERITY]"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from . import load_config, load_vendors, analyse
from .models import SEV_ORDER, parse_date
from .report import to_json, to_markdown, kpis


def main(argv=None):
    ap = argparse.ArgumentParser(prog="tprm", description="Third-party risk monitoring")
    ap.add_argument("vendors", help="vendor inventory JSON")
    ap.add_argument("--as-of", help="evaluation date, default today (use a fixed date for reproducible output)")
    ap.add_argument("--config")
    ap.add_argument("--out-dir", help="write report.md and report.json here")
    ap.add_argument("--fail-on", choices=list(SEV_ORDER),
                    help="exit 1 if any issue at this severity or worse (for CI/cron use)")
    a = ap.parse_args(argv)

    if not Path(a.vendors).is_file():
        print(f"error: {a.vendors} not found", file=sys.stderr)
        return 2
    try:
        as_of = parse_date(a.as_of) if a.as_of else date.today()
        cfg = load_config(a.config)
        vendors = load_vendors(a.vendors)
    except (ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    profiles, issues = analyse(vendors, cfg, as_of)
    md = to_markdown(profiles, issues, as_of)
    if a.out_dir:
        out = Path(a.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "report.md").write_text(md, encoding="utf-8")
        (out / "report.json").write_text(to_json(profiles, issues, as_of), encoding="utf-8")
        k = kpis(profiles, issues)
        print(f"{len(issues)} issues {k['issues_by_severity']} -> {out}/report.md, report.json")
    else:
        print(md)

    if a.fail_on and any(SEV_ORDER[i.severity] <= SEV_ORDER[a.fail_on] for i in issues):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
