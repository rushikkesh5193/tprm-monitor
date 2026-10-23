# Third-Party Risk Monitoring Report

As of **2026-10-23**. Data in this report is synthetic unless you supplied your own.

## Summary

- Vendors: 30 (29 active)
- Active by tier: Tier 1: 3, Tier 2: 8, Tier 3: 17, Tier 4: 1
- Tier 1-3 vendors with a current assessment: 89.3%
- Open issues: 3 critical, 7 high, 4 medium, 2 low
- Overdue audit findings: 1

## Issues needing action

### Critical (3)

| Vendor | Tier | Check | Detail | Action |
|---|---|---|---|---|
| Northwind Payroll Services (V001) | 1 | DPA_MISSING | Vendor handles financial, sensitive_personal data without a signed DPA. | Execute a DPA (processing purpose, security terms, breach notice, deletion) before further processing. |
| Lakeside Cloud Hosting (V002) | 1 | UNASSESSED | Tier 1 vendor with no assessment on record. | Send the security questionnaire and collect evidence before further reliance. |
| Old Harbor Backup Co (V004) | 2 | OFFBOARD_ACCESS | Status is 'terminated' but access ('remote_privileged') has not been revoked. | Revoke accounts, keys and network paths; obtain data deletion/return certificate. |

### High (7)

| Vendor | Tier | Check | Detail | Action |
|---|---|---|---|---|
| Northwind Payroll Services (V001) | 1 | ASSESSMENT_OVERDUE | Last assessed 2025-06-10; Tier 1 cadence is 12 months, due 2026-06-10 (135 days late). | Schedule reassessment now. |
| Northwind Payroll Services (V001) | 1 | CERT_EXPIRED | Expired 2026-08-01 (83 days ago). | Request the renewed certificate or a written explanation. |
| Northwind Payroll Services (V001) | 1 | LOW_CONTROL_SCORE | Score 70.8 < required 75. Weakest areas: Access control 20, Incident response 40. | Agree a remediation plan with dates, or accept the risk in writing. |
| Northwind Payroll Services (V001) | 1 | RENEWAL_BLOCKER | Contract ends 2026-12-01 (39 days) and the assessment is missing or overdue. | Complete the assessment before signing the renewal. |
| Vertex HR Platform (V009) | 1 | OFFBOARD_ACCESS | Status is 'offboarding' but access ('remote_limited') has not been revoked. | Revoke accounts, keys and network paths; obtain data deletion/return certificate. |
| Meridian CRM Cloud (V007) | 2 | ASSESSMENT_OVERDUE | Last assessed 2025-09-15; Tier 2 cadence is 12 months, due 2026-09-15 (38 days late). | Schedule reassessment now. |
| Brightpath Marketing Analytics (V003) | 3 | FINDING_OVERDUE | B-1: No TLS on reporting endpoint. Due 2026-09-01, 52 days overdue. | Get a dated remediation plan from the vendor or record a risk acceptance. |

### Medium (4)

| Vendor | Tier | Check | Detail | Action |
|---|---|---|---|---|
| Quartz Identity Provider (V005) | 2 | CERT_EXPIRING | Expires 2026-12-05 (43 days). | Ask for the renewal evidence before expiry. |
| Quartz Identity Provider (V005) | 2 | SOC2_STALE | Report dated 2025-07-15; consider it stale after 2026-07-15. | Request the latest report and a bridge letter for the gap period. |
| Meridian CRM Cloud (V007) | 2 | QUESTIONNAIRE_INCOMPLETE | Fewer than the required share of questions are answered. | Chase the missing answers and supporting evidence. |
| Delta Courier Logistics (V008) | 3 | CONTRACT_EXPIRED | Contract ended 2026-08-30 (54 days ago). | Renew, extend formally, or start offboarding. |

### Low (2)

| Vendor | Tier | Check | Detail | Action |
|---|---|---|---|---|
| Pinecrest Facilities Management (V006) | 3 | ASSESSMENT_DUE_SOON | Due 2026-12-20 (58 days). | Send the questionnaire ahead of the due date. |
| Silverline Stationery (V010) | 4 | UNASSESSED | Tier 4 vendor with no assessment on record. | Send the security questionnaire and collect evidence before further reliance. |

## Vendor register

| ID | Vendor | Status | Tier | Inherent | Control | Residual | Last assessed | Next due | Issues |
|---|---|---|---|---|---|---|---|---|---|
| V002 | Lakeside Cloud Hosting | active | 1 | 73.3 | - | 73.3 | - | - | 1 |
| V004 | Old Harbor Backup Co | terminated | 2 | 63.3 | - | 63.3 | 2024-02-01 | - | 1 |
| V007 | Meridian CRM Cloud | active | 2 | 56.7 | - | 56.7 | 2025-09-15 | 2026-09-15 | 2 |
| V001 | Northwind Payroll Services | active | 1 | 86.7 | 70.8 | 37.6 | 2025-06-10 | 2026-06-10 | 5 |
| V009 | Vertex HR Platform | offboarding | 1 | 76.7 | 100.0 | 15.3 | 2026-01-10 | 2027-01-10 | 1 |
| V005 | Quartz Identity Provider | active | 2 | 63.3 | 100.0 | 12.7 | 2026-03-01 | 2027-03-01 | 2 |
| V011 | Grove Consulting | active | 2 | 56.7 | 100.0 | 11.3 | 2026-07-11 | 2027-07-11 | 0 |
| V019 | Dune Consulting | active | 2 | 56.7 | 100.0 | 11.3 | 2026-06-27 | 2027-06-27 | 0 |
| V024 | Nimbus Software | active | 2 | 56.7 | 100.0 | 11.3 | 2026-07-08 | 2027-07-08 | 0 |
| V010 | Silverline Stationery | active | 4 | 10.0 | - | 10.0 | - | - | 1 |
| V003 | Brightpath Marketing Analytics | active | 3 | 40.0 | 95.8 | 9.3 | 2026-05-01 | 2028-05-01 | 1 |
| V013 | Fjord Networks | active | 2 | 46.7 | 100.0 | 9.3 | 2026-09-21 | 2027-09-21 | 0 |
| V016 | Harbor Consulting | active | 2 | 46.7 | 100.0 | 9.3 | 2026-08-09 | 2027-08-09 | 0 |
| V026 | Lumen Software | active | 2 | 46.7 | 100.0 | 9.3 | 2026-07-24 | 2027-07-24 | 0 |
| V015 | Orchid Logistics | active | 3 | 36.7 | 100.0 | 7.3 | 2026-09-02 | 2028-09-02 | 0 |
| V020 | Iris Software | active | 3 | 36.7 | 100.0 | 7.3 | 2026-08-03 | 2028-08-03 | 0 |
| V027 | Birch Data Labs | active | 3 | 36.7 | 100.0 | 7.3 | 2026-06-27 | 2028-06-27 | 0 |
| V006 | Pinecrest Facilities Management | active | 3 | 30.0 | 100.0 | 6.0 | 2024-12-20 | 2026-12-20 | 1 |
| V008 | Delta Courier Logistics | active | 3 | 30.0 | 100.0 | 6.0 | 2026-02-01 | 2028-02-01 | 1 |
| V014 | Alder Software | active | 3 | 30.0 | 100.0 | 6.0 | 2026-06-17 | 2028-06-17 | 0 |
| V017 | Fjord Consulting | active | 3 | 30.0 | 100.0 | 6.0 | 2026-09-04 | 2028-09-04 | 0 |
| V018 | Ember Software | active | 3 | 30.0 | 100.0 | 6.0 | 2026-08-18 | 2028-08-18 | 0 |
| V021 | Juniper Consulting | active | 3 | 30.0 | 100.0 | 6.0 | 2026-08-28 | 2028-08-28 | 0 |
| V022 | Harbor Software | active | 3 | 30.0 | 100.0 | 6.0 | 2026-09-23 | 2028-09-23 | 0 |
| V023 | Alder Systems | active | 3 | 30.0 | 100.0 | 6.0 | 2026-06-04 | 2028-06-04 | 0 |
| V028 | Lumen Systems | active | 3 | 30.0 | 100.0 | 6.0 | 2026-07-19 | 2028-07-19 | 0 |
| V030 | Nimbus Networks | active | 3 | 30.0 | 100.0 | 6.0 | 2026-07-19 | 2028-07-19 | 0 |
| V012 | Cedar Logistics | active | 3 | 26.7 | 100.0 | 5.3 | 2026-09-16 | 2028-09-16 | 0 |
| V025 | Grove Networks | active | 3 | 26.7 | 100.0 | 5.3 | 2026-07-24 | 2028-07-24 | 0 |
| V029 | Cedar Data Labs | active | 3 | 26.7 | 100.0 | 5.3 | 2026-07-07 | 2028-07-07 | 0 |

Scores are 0-100. Residual = inherent risk reduced by control strength; a vendor with no usable questionnaire gets no credit (residual = inherent).
