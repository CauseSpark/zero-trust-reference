# Zero Trust Pillars: CISA ZTMM v2.0 and the DoD Zero Trust Strategy

> Personal study notes. This is my own summary, not official guidance. For the authoritative
> text, read the sources linked below.

## Sources and versions (checked November 2026)

| Framework | Version in use | Structure | Official link |
|---|---|---|---|
| CISA Zero Trust Maturity Model (ZTMM) | **Version 2.0, April 2023** | 5 pillars, 3 cross-cutting capabilities, 4 maturity stages | <https://www.cisa.gov/zero-trust-maturity-model> |
| DoD Zero Trust Strategy | **2022 strategy** (publicly released Nov 2022; now listed as the "DoW Zero Trust Strategy") | 7 pillars, 4 strategic goals, Target and Advanced levels | <https://dodcio.defense.gov/Library/> (Architectures & Strategies section) |
| NIST SP 800-207, Zero Trust Architecture | **Final, August 2020** | 7 tenets, logical components, deployment approaches | <https://csrc.nist.gov/pubs/sp/800/207/final> |

**DoD note:** DoD has announced a *Zero Trust Strategy 2.0* that would extend coverage beyond IT
(for example, to operational technology). As of this check I could not find that it has been
published (the DoD CIO library lists no 2.0), so these notes follow the 2022 strategy. Re-check the DoD CIO library before relying on this.

---

## CISA ZTMM v2.0

### The five pillars

| Pillar | What it covers (my words) |
|---|---|
| **Identity** | Users and non-person entities: proving who they are, and deciding what they can reach each time they ask. |
| **Devices** | Every asset that connects, including servers, laptops, phones, IoT and cloud instances: inventory, health and compliance. |
| **Networks** | Every path traffic takes, internal included: segmentation, encryption, and managing traffic by application need instead of by "inside" or "outside". |
| **Applications and Workloads** | On-prem, cloud and SaaS software: access control at the application layer, secure development, and testing. |
| **Data** | Information at rest, in transit and in use: inventory, categorization, encryption and access decisions driven by sensitivity. |

### The three cross-cutting capabilities

These apply to every pillar instead of standing on their own:

- **Visibility and Analytics**: collecting telemetry and turning it into risk-informed decisions.
- **Automation and Orchestration**: using that information to respond and enforce policy without waiting on manual steps.
- **Governance**: the policies, procedures and accountability that make the other pieces repeatable and auditable.

### The four maturity stages

| Stage | Short description (my words) |
|---|---|
| **Traditional** | Manual, static, siloed. Policies set once and enforced at the perimeter. |
| **Initial** | Some automation, early cross-pillar integration, policy starting to use more attributes. Version 2.0 added this stage. |
| **Advanced** | Centralized visibility and identity, automated controls across pillars, policy driven by risk. |
| **Optimal** | Fully automated, just-in-time, dynamic least privilege, continuous monitoring with self-reporting assets. |

### Functions used in this repo's worksheet

The worksheet (`assessment/maturity_worksheet.csv`) uses one row per ZTMM function. The function
*names* follow the ZTMM v2.0 labels so they are easy to cross-reference. The descriptions and
evidence notes are my own and describe a fictional company.

| Pillar | Functions |
|---|---|
| Identity | Authentication; Identity Stores; Risk Assessments; Access Management |
| Devices | Policy Enforcement & Compliance Monitoring; Asset & Supply Chain Risk Management; Resource Access; Device Threat Protection |
| Networks | Network Segmentation; Network Traffic Management; Traffic Encryption; Network Resilience |
| Applications and Workloads | Application Access; Application Threat Protections; Accessible Applications; Secure Application Development & Deployment Workflow; Application Security Testing |
| Data | Data Inventory Management; Data Categorization; Data Availability; Data Access; Data Encryption |
| Cross-cutting | Visibility & Analytics; Automation & Orchestration; Governance |

---

## DoD Zero Trust Strategy (2022)

### The seven pillars

| DoD pillar | Focus (my words) |
|---|---|
| **User** | Continuous authentication and authorization of people and non-person entities (ICAM). |
| **Device** | Real-time knowledge of device identity, health and compliance before it gets access. |
| **Application & Workload** | Securing everything from application code to containers and cloud workloads. |
| **Data** | Data-centric security: tagging, labeling, rights management and loss prevention. |
| **Network & Environment** | Logical and physical segmentation, isolating sensitive resources, limiting lateral movement. |
| **Automation & Orchestration** | Automated, policy-driven response across the enterprise (SOAR and similar). |
| **Visibility & Analytics** | Collecting and analyzing events (UEBA, SIEM) to detect anomalies and feed policy decisions. |

### Strategic goals

The strategy groups its work under four goals: building a zero trust culture, securing and
defending DoD information systems, accelerating technology, and enabling zero trust (the
supporting processes, policy and funding).

### Target vs. Advanced

DoD defines two maturity levels instead of four stages:

- **Target level**: the minimum set of capability outcomes. DoD has publicly stated a goal of reaching it by the end of FY2027.
- **Advanced level**: the full set of capability outcomes, with a longer timeline.

The exact activity and capability counts are in the strategy and its Capability Execution
Roadmap. I don't repeat them here so these notes don't drift out of date.

---

## Crosswalk: CISA ZTMM ↔ DoD pillars

| CISA ZTMM v2.0 | DoD ZT Strategy | Notes |
|---|---|---|
| Identity | User | Same idea. DoD says "User" but includes non-person entities. |
| Devices | Device | Direct match. |
| Networks | Network & Environment | DoD adds "Environment" to emphasize physical and logical isolation. |
| Applications and Workloads | Application & Workload | Direct match. |
| Data | Data | Direct match. DoD leans harder on tagging and labeling. |
| Visibility and Analytics *(cross-cutting)* | Visibility & Analytics *(pillar)* | CISA treats it as cross-cutting; DoD makes it a pillar. |
| Automation and Orchestration *(cross-cutting)* | Automation & Orchestration *(pillar)* | Same difference. |
| Governance *(cross-cutting)* | No dedicated pillar | In DoD this shows up through the strategic goals and the PfMO oversight model. |

**Why it matters for GRC work:** an assessment built on CISA's model can be reported in DoD
terms (and the other way around) without re-collecting evidence. The 5 + 3 and the 7 describe
the same ground and divide it differently. The only real gap is Governance, which in DoD's
framing lives at the program level.

## Further reading

- NIST SP 800-207A (Sept 2023), a ZTA model for access control in cloud-native applications in multi-cloud environments: <https://csrc.nist.gov/pubs/sp/800/207/a/final>
- NIST NCCoE, *Implementing a Zero Trust Architecture* (SP 1800-35): <https://www.nccoe.nist.gov/projects/implementing-zero-trust-architecture>
- OMB M-22-09, *Moving the U.S. Government Toward Zero Trust Cybersecurity Principles*: <https://www.whitehouse.gov/wp-content/uploads/2022/01/M-22-09.pdf>
