# tprm-monitor

A small Python tool for **third-party risk management (TPRM)** monitoring. It takes a vendor inventory, tiers each vendor by inherent risk, scores their security questionnaire, and then keeps checking for the things an audit or GRC team has to chase: overdue assessments, expiring certificates, missing data processing agreements, overdue audit findings, and offboarded vendors that still have access.

It uses the Python standard library only (tested on Python 3.13).

> **Data note.** `examples/sample_vendors.json` is **synthetic**. Every vendor name is invented, and ten of the 30 vendors have problems injected on purpose so the tests can check the monitor finds exactly those. Nothing here comes from a real organisation.

## Why

A vendor review is a point-in-time exercise. The risk shows up *between* reviews: a certificate lapses, a finding stays open past its due date, a contract is about to renew with no current assessment. This tool does that between-reviews monitoring and produces a ranked action list.

## Quick start

```bash
python3 -m tprm examples/sample_vendors.json --as-of 2026-10-23              # report to the terminal
python3 -m tprm examples/sample_vendors.json --out-dir out                   # report.md + report.json
python3 -m tprm examples/sample_vendors.json --fail-on high                  # exit 1 if any high/critical issue (cron / CI)
python3 -m unittest discover -s tests                                        # 48 tests
bash scripts/run_demo.sh                                                     # regenerate data, report and run the tests
```

Pass `--as-of` for reproducible output; without it, today's date is used.

## How it works

**1. Inherent risk (0-100) and tier.** Combines the most sensitive data type the vendor handles (40%), business criticality 1-4 (40%) and access level (20%). Tier 1 is 70 and above, Tier 2 is 45 and above, Tier 3 is 25 and above, and the rest are Tier 4.

**2. Control score (0-100).** A 12-question questionnaire across governance, access control, data protection, incident response, resilience, vulnerability management and fourth parties. Each question has a weight, and answers are yes (1), partial (0.5), no (0) or n/a (excluded). If fewer than 80% of the total weight is answered, the score is `None` instead of a guess.

**3. Residual risk.** Inherent risk reduced by control strength, up to 80%. A vendor with no usable questionnaire gets **no credit**, so residual equals inherent.

**4. Monitoring checks.**

| Check | Raised when | Severity |
|---|---|---|
| `OFFBOARD_ACCESS` | Vendor is terminated or offboarding but access is still active | critical / high |
| `UNASSESSED` | Active vendor never assessed | by tier: critical to low |
| `ASSESSMENT_OVERDUE` / `ASSESSMENT_DUE_SOON` | Past cadence (T1-2: 12 months, T3: 24, T4: 36), or due within 60 days | high-low |
| `CERT_EXPIRED` / `CERT_EXPIRING` | Certificate past expiry, or expiring within 90 days | high-low |
| `SOC2_STALE` | Tier 1-2 vendor's SOC 2 report is older than 12 months | medium |
| `RENEWAL_BLOCKER` | Contract ends within 90 days and the assessment is missing or overdue | high |
| `CONTRACT_EXPIRED` | Contract ended but the vendor is still active | medium |
| `DPA_MISSING` | Handles personal, financial, sensitive or health data with no signed DPA | high; critical for sensitive/health |
| `FINDING_OVERDUE` | Open audit finding past its due date | follows the finding's severity |
| `LOW_CONTROL_SCORE` | Score below the tier minimum (T1: 75, T2: 65, T3: 50) | high / medium |
| `QUESTIONNAIRE_INCOMPLETE` | Tier 1-2 vendor assessed but too few answers to score | medium |

Issues are ranked by severity, then tier. All thresholds live in `tprm/config.json`.

## Input format

`vendors.json` is a list (or `{"vendors": [...]}`) of objects. Required fields are `id`, `name` and `criticality`; see `examples/sample_vendors.json` for all of them. Dates are `YYYY-MM-DD`. Duplicate IDs, a criticality outside 1-4 and malformed dates are rejected with a clear message (exit code 2).

## Tests

48 tests cover scoring, every check on both sides of its boundary (for example, a certificate expiring today versus yesterday), CLI behaviour and an end-to-end run that requires the monitor to find **exactly** the injected problems and nothing on the 20 clean vendors. I also broke the code five ways (a flipped boundary, removing the coverage rule, a loosened condition, and so on) and confirmed the tests fail each time.

## Limitations

- **The scoring model is illustrative.** The weights, tiers and cadences are reasonable defaults, not a standard. Tune them to your organisation's risk appetite.
- **Questionnaires are self-attested.** A vendor can answer "yes" and be wrong. The score reflects what they told you, not what you verified.
- **`dpa_signed` is a flag, not a review.** The tool does not read the DPA or judge whether its terms are adequate.
- **Presence checks only.** It cannot see inside systems, so `active_access` has to come from your IAM or access records.
- **No persistence or UI.** It reads JSON and writes reports. There is no database, no notifications and no authentication.
- **Not legal advice.** Whether a DPA is required for a given vendor depends on the laws that apply to you.

## Layout

```
tprm/        models.py  scoring.py  monitor.py  report.py  config.json  __main__.py
tools/       gen_vendors.py          synthetic data generator (seeded, reproducible)
tests/       48 tests
examples/    sample_vendors.json  report.md  report.json
scripts/     run_demo.sh
```
