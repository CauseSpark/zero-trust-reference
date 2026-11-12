# zero-trust-reference

[![tests](https://github.com/CauseSpark/zero-trust-reference/actions/workflows/tests.yml/badge.svg)](https://github.com/CauseSpark/zero-trust-reference/actions/workflows/tests.yml)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

A zero trust reference kit for GRC work: pillar notes, an NIST SP 800-207 study summary, a
maturity self-assessment worksheet, a capability-to-SP 800-53 control mapping, Mermaid
reference architectures, and a small Python tool that scores the assessment.

Everything is built around **Kestrel Ridge Outfitters**, a **fictional** retailer.

## Purpose

Zero trust guidance is spread across three main federal sources that divide the problem
differently. This repo is my working reference for connecting them the way a GRC analyst
would have to:

1. **What does good look like?** CISA ZTMM pillars and stages, DoD pillars, NIST tenets
2. **Where are we today?** A maturity worksheet with evidence notes
3. **Which controls prove it?** A mapping to SP 800-53 Rev 5 controls an assessor can test
4. **What do we fix first?** A scored, ranked gap list

## Source documents and current versions

Checked **November 2026**. Each links to the official source; this repo summarizes in my own words and does not reproduce them.

| Document | Current version | Structure used here |
|---|---|---|
| [NIST SP 800-207, *Zero Trust Architecture*](https://csrc.nist.gov/pubs/sp/800/207/final) | **Final, August 2020** (no newer revision listed) | 7 tenets (T1–T7); PE / PA / PEP logical components |
| [CISA Zero Trust Maturity Model](https://www.cisa.gov/zero-trust-maturity-model) | **Version 2.0, April 2023** | 5 pillars: Identity, Devices, Networks, Applications and Workloads, Data. 3 cross-cutting capabilities: Visibility and Analytics, Automation and Orchestration, Governance. 4 stages: Traditional, Initial, Advanced, Optimal |
| [DoD Zero Trust Strategy](https://dodcio.defense.gov/Library/) | **2022 strategy** (listed in the DoD CIO library as the "DoW Zero Trust Strategy") | 7 pillars: User, Device, Application & Workload, Data, Network & Environment, Automation & Orchestration, Visibility & Analytics |
| [NIST SP 800-53 Rev 5](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) | **Rev 5, Release 5.2.0 (August 2025)** | Control IDs used in the mapping |

> **DoD Strategy 2.0:** DoD has publicly said a Zero Trust Strategy 2.0 is coming, extending
> coverage beyond IT. As of this check it isn't listed in the DoD CIO library, so this repo
> follows the 2022 strategy. Re-check before relying on the DoD material.

## Repository layout

```
zero-trust-reference/
├── docs/
│   ├── pillars.md                 CISA vs DoD pillars + crosswalk
│   └── nist_800-207_summary.md    Tenets, components, deployment models, migration
├── assessment/
│   └── maturity_worksheet.csv     25 ZTMM functions, current vs target, weights, evidence
├── mapping/
│   └── zt_to_800-53.csv           Each function → 800-53 Rev 5 controls + 800-207 tenets
├── diagrams/                      Mermaid: core components, reference architecture, access flow
├── src/maturity_score.py          Scoring CLI (standard library only)
├── tests/                         pytest: scoring logic + data-file consistency
└── .github/workflows/tests.yml    CI on Python 3.10, 3.12, 3.13
```

## Quick start

```bash
git clone https://github.com/CauseSpark/zero-trust-reference.git
cd zero-trust-reference
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

# Score the sample assessment
python -m src.maturity_score assessment/maturity_worksheet.csv

# JSON output, top 3 gaps
python -m src.maturity_score assessment/maturity_worksheet.csv --format json --top 3

# Run the tests
python -m pytest
```

Sample output (abridged):

```
**Overall:** mean stage 1.91 / 4 · maturity index 30.3 / 100

| Pillar   | Functions | Mean stage | Index | Floor stage | Mean gap |
| Identity |         4 |       2.30 |  43.3 | Initial     |     1.00 |
| Networks |         4 |       1.43 |  14.3 | Traditional |     0.86 |
...
```

### How the score works

- Stages map to numbers: Traditional = 1, Initial = 2, Advanced = 3, Optimal = 4.
- **Mean stage** is weighted by each function's `weight` (1–3, the business priority).
- **Maturity index** rescales the mean to 0–100.
- **Floor stage** is the lowest stage in the pillar. Averages can hide a weak function, and in
  practice a pillar is only as mature as its weakest part.
- **Weighted gap** = (target − current) × weight, which ranks the remediation backlog.

The worksheet validates input: unknown pillars, duplicate IDs, bad stages or weights, and
targets set below current all fail with the row number. This is my own scoring approach, not
an official CISA method.

## What this demonstrates

- **Framework literacy:** reading NIST, CISA and DoD zero trust guidance and crosswalking their different pillar models
- **Control mapping:** linking architecture-level capabilities to testable SP 800-53 Rev 5 controls, with a written rationale for each
- **Assessment design:** a maturity worksheet with targets, weights, owners and evidence notes, the way a real self-assessment would be run
- **Risk prioritization:** turning assessment data into a ranked gap list leadership can act on
- **Architecture communication:** reference diagrams tied to the PE / PA / PEP model
- **Engineering hygiene:** tested Python, data-consistency checks that keep the CSVs in sync, and CI on every push

## Disclaimer

This is **personal study material**. It is not official guidance and is not endorsed by NIST,
CISA, DoD or any other organization, and it doesn't represent certification, compliance
status or an authoritative interpretation of any framework. The mappings and scoring are my
own judgment for learning purposes; validate them against the official documents before using
them in any real assessment.

**Kestrel Ridge Outfitters and every scenario, system and finding here are fictional.**
Nothing in this repository is drawn from any real employer, mission, client or system, and
it contains no controlled unclassified information (CUI).

## License

[MIT](LICENSE) © 2026 Peyton Seay
