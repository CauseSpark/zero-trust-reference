# NIST SP 800-207 Zero Trust Architecture: Study Summary

> Personal study notes in my own words. Not a substitute for the publication.
> Official source: **NIST SP 800-207, *Zero Trust Architecture*, Final, August 2020**:
> <https://csrc.nist.gov/pubs/sp/800/207/final> · DOI: <https://doi.org/10.6028/NIST.SP.800-207>
>
> Version check (Nov 2026): the CSRC page still lists the August 2020 final as current, with no
> newer revision or draft. The companion SP 800-207A, on cloud-native access control, is a separate publication.

## The core idea

Location on the network doesn't earn trust. Every request to a resource is evaluated on its own
merits (who is asking, from what device, how healthy that device is, how sensitive the
resource is, and what looks normal right now), and access is granted as narrowly as possible
for as short a time as possible.

800-207 describes an **architecture and a set of principles**, not a control catalog. That's
why this repo maps zero trust capabilities to **SP 800-53** controls (see `mapping/`): 800-53 is
where you find the "shall" statements an assessor can test.

## The seven tenets (Section 2.1), paraphrased

| # | My paraphrase | GRC question I'd ask |
|---|---|---|
| T1 | Everything that holds data or provides a service counts as a resource, personal devices that reach enterprise resources included. | Is the asset and service inventory complete, including BYOD and SaaS? |
| T2 | Protect every communication the same way, wherever it comes from; "internal" traffic gets no free pass. | Is internal east-west traffic encrypted and authenticated? |
| T3 | Grant access one session at a time, with the least privilege needed for that task. | Do sessions expire and get re-evaluated, or do grants persist? |
| T4 | Access decisions come from dynamic policy that weighs identity, the application, device state and behavioral or environmental signals. | What attributes does the policy actually consume today? |
| T5 | Continuously monitor and measure the security posture of every owned and associated asset. | How fast does a non-compliant device lose access? |
| T6 | Authentication and authorization are dynamic and strictly enforced *before* access, in a constant cycle. | Where is MFA required, and is re-authentication triggered by risk? |
| T7 | Gather as much telemetry as practical about assets, network and communications, and use it to improve. | Does telemetry feed back into policy, or does it just sit in a SIEM? |

The tenet numbers (T1–T7) are used in `mapping/zt_to_800-53.csv`.

## Logical components (Section 3)

| Component | Role |
|---|---|
| **Policy Engine (PE)** | Makes the grant or deny decision, using enterprise policy plus external inputs through a *trust algorithm*. |
| **Policy Administrator (PA)** | Carries out the PE's decision: sets up or tears down the session path and issues session credentials or tokens. |
| **Policy Decision Point (PDP)** | The PE and PA together. |
| **Policy Enforcement Point (PEP)** | Sits in the data path. Enables, monitors and terminates the connection between subject and resource. |

**Inputs that feed the PE** include continuous diagnostics and mitigation (CDM) data,
industry compliance requirements, threat intelligence, network and system activity logs,
data access policies, enterprise PKI, identity management, and SIEM.

The architecture separates a **control plane** (PDP traffic) from a **data plane**
(application traffic). See `diagrams/01_core_logical_components.md`.

## Deployment approaches (Section 3.1)

1. **Enhanced identity governance**: identity and its attributes drive policy.
2. **Micro-segmentation**: resources sit behind gateways or host agents that enforce policy per segment.
3. **Network infrastructure and software-defined perimeters**: the network layer (e.g., an overlay) is reconfigured per session.

Most real programs blend all three.

### Deployment models (Section 3.2)

- **Device agent / gateway**: an agent on the endpoint talks to a gateway in front of the resource.
- **Enclave gateway**: one gateway guards a group of resources (useful for legacy systems).
- **Resource portal**: a single portal fronts resources, with no agent required (good for BYOD, though it sees less about the device).
- **Device application sandboxing**: trusted apps run isolated on the endpoint.

## Trust algorithm (Section 3.3)

- **Criteria-based**: every required attribute must be met, and the answer is yes or no.
- **Score-based**: a confidence score is computed and compared against a threshold for the resource.
- **Singular**: each request is judged alone.
- **Contextual**: recent history of the subject is considered (better for spotting misuse, but it needs more data).

## Threats the document calls out (Section 5), in brief

Subversion of the decision process, denial of service against the PEP or PDP, stolen
credentials and insider threat, limited visibility into encrypted traffic, compromise of
stored policy or telemetry, reliance on proprietary formats, and the risks introduced by
non-person entities (including automated agents) acting in the architecture.

## Migrating (Section 7)

The document expects most organizations to run a **hybrid** of perimeter and zero trust
for a long time. Its suggested path, in my words: identify actors, inventory assets,
identify key processes and their risk, write policies for a candidate process, pick
solutions, deploy in monitor mode first, then expand.

## How this repo uses 800-207

- `diagrams/` draws the PE, PA and PEP model and a reference architecture for a **fictional** company.
- `mapping/zt_to_800-53.csv` tags each capability with the tenets it supports.
- `assessment/` plus `src/maturity_score.py` score maturity using CISA ZTMM stages, because 800-207 itself has no maturity scale.
