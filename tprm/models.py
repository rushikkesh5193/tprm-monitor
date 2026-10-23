"""Data models and small date helpers."""
from __future__ import annotations

import calendar
from dataclasses import dataclass, field, asdict
from datetime import date

SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def parse_date(value):
    """Accept 'YYYY-MM-DD', a date, or None."""
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise ValueError(f"bad date {value!r}: expected YYYY-MM-DD") from exc


def add_months(d: date, months: int) -> date:
    """Calendar-aware month addition (Jan 31 + 1 month = Feb 28/29)."""
    idx = d.month - 1 + months
    year, month = d.year + idx // 12, idx % 12 + 1
    return date(year, month, min(d.day, calendar.monthrange(year, month)[1]))


@dataclass
class Finding:
    id: str
    title: str
    severity: str
    opened: date
    due: date
    closed: date | None = None

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"], title=d["title"], severity=d["severity"].lower(),
            opened=parse_date(d["opened"]), due=parse_date(d["due"]),
            closed=parse_date(d.get("closed")),
        )


@dataclass
class Certification:
    name: str
    expiry: date

    @classmethod
    def from_dict(cls, d):
        return cls(name=d["name"], expiry=parse_date(d["expiry"]))


@dataclass
class Vendor:
    id: str
    name: str
    service: str
    owner: str
    criticality: int                      # 1 (minor) .. 4 (business critical)
    data_types: list = field(default_factory=list)
    access: str = "none"
    status: str = "active"                # active | offboarding | terminated
    active_access: bool = False
    contract_end: date | None = None
    last_assessment: date | None = None
    soc2_report_date: date | None = None
    dpa_signed: bool = False
    certifications: list = field(default_factory=list)
    answers: dict = field(default_factory=dict)
    findings: list = field(default_factory=list)

    @classmethod
    def from_dict(cls, d):
        crit = int(d["criticality"])
        if not 1 <= crit <= 4:
            raise ValueError(f"{d.get('id')}: criticality must be 1..4, got {crit}")
        return cls(
            id=d["id"], name=d["name"], service=d.get("service", ""),
            owner=d.get("owner", ""), criticality=crit,
            data_types=[x.lower() for x in d.get("data_types", [])],
            access=d.get("access", "none"),
            status=d.get("status", "active"),
            active_access=bool(d.get("active_access", False)),
            contract_end=parse_date(d.get("contract_end")),
            last_assessment=parse_date(d.get("last_assessment")),
            soc2_report_date=parse_date(d.get("soc2_report_date")),
            dpa_signed=bool(d.get("dpa_signed", False)),
            certifications=[Certification.from_dict(c) for c in d.get("certifications", [])],
            answers={k: str(v).lower() for k, v in d.get("answers", {}).items()},
            findings=[Finding.from_dict(f) for f in d.get("findings", [])],
        )


@dataclass
class Issue:
    vendor_id: str
    vendor_name: str
    tier: int
    check: str
    severity: str
    title: str
    detail: str
    action: str

    def as_dict(self):
        return asdict(self)
