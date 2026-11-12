# Core Logical Components (after NIST SP 800-207 §3)

My own drawing of the abstract model: a subject on an untrusted path reaches an enterprise
resource only through a Policy Enforcement Point, which the Policy Decision Point controls.

```mermaid
flowchart LR
    subgraph Inputs["Policy inputs"]
        direction TB
        CDM["CDM / device posture"]
        TI["Threat intelligence"]
        LOGS["Activity logs"]
        DAP["Data access policies"]
        PKI["Enterprise PKI"]
        IDM["Identity management"]
        SIEM["SIEM"]
    end

    subgraph CP["Control plane"]
        direction TB
        PE["Policy Engine<br/>(trust algorithm)"]
        PA["Policy Administrator"]
        PE <--> PA
    end

    Subject["Subject<br/>(user / NPE + device)"]
    PEP{{"Policy Enforcement Point"}}
    Resource[("Enterprise resource")]

    Inputs --> PE
    Subject -- "untrusted" --> PEP
    PA -- "allow / deny / revoke" --> PEP
    PEP -- "implicit trust zone" --> Resource

    classDef cp fill:#e8f0fe,stroke:#3367d6;
    classDef dp fill:#fef7e0,stroke:#f9ab00;
    class PE,PA cp;
    class PEP,Resource,Subject dp;
```

**How to read it**

- **PE + PA = PDP.** The PE decides; the PA carries the decision out by configuring the PEP.
- The **implicit trust zone** behind the PEP should be as small as possible. Shrinking it is
  what micro-segmentation does.
- The policy inputs are the same sources listed in the 800-207 summary
  (`docs/nist_800-207_summary.md`).
