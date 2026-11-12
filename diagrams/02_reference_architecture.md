# Reference Architecture: Kestrel Ridge Outfitters (fictional)

**Scenario (fictional):** a mid-size outdoor-gear retailer with a headquarters, two
distribution centers, about 40 stores, an e-commerce site, and a mix of SaaS, cloud workloads
and one legacy on-prem order system. This is the target state the maturity worksheet
(`assessment/maturity_worksheet.csv`) is working toward.

```mermaid
flowchart TB
    subgraph Subjects
        EMP["Employees<br/>(managed laptops)"]
        STORE["Store staff<br/>(shared kiosks)"]
        CONTR["Contractors<br/>(BYOD)"]
        SVC["Service accounts / NPEs"]
    end

    subgraph Identity["Identity pillar"]
        IDP["Cloud Identity Provider<br/>phishing-resistant MFA"]
        PAM["Privileged access<br/>just-in-time elevation"]
    end

    subgraph Devices["Devices pillar"]
        MDM["MDM / compliance"]
        EDR["EDR"]
        CMDB["Asset inventory"]
    end

    subgraph PDP["Policy Decision Point"]
        PE["Policy Engine"]
        PA["Policy Administrator"]
    end

    subgraph Network["Networks pillar"]
        ZTNA{{"ZTNA gateway (PEP)"}}
        SEG{{"Micro-segmentation (PEP)<br/>DC + store VLANs"}}
    end

    subgraph Apps["Applications & Workloads pillar"]
        SAAS["SaaS (email, HR)"]
        ECOM["E-commerce site<br/>behind WAF"]
        ORDER["Legacy order system<br/>(enclave gateway)"]
        CICD["CI/CD with signed artifacts"]
    end

    subgraph Data["Data pillar"]
        CUST[("Customer data<br/>labeled: Confidential")]
        INV[("Inventory data<br/>labeled: Internal")]
        BKP[("Immutable backups")]
    end

    subgraph XC["Cross-cutting"]
        SIEM["SIEM / analytics"]
        SOAR["SOAR playbooks"]
        GOV["GRC: policy, metrics, risk register"]
    end

    EMP & STORE & CONTR & SVC --> IDP
    IDP --> PE
    MDM & EDR & CMDB --> PE
    SIEM --> PE
    PE <--> PA
    PA --> ZTNA
    PA --> SEG
    PAM --> PA

    ZTNA --> SAAS
    ZTNA --> ECOM
    ZTNA --> ORDER
    SEG --> ORDER
    ORDER --> CUST
    ECOM --> CUST
    ORDER --> INV
    CUST & INV --> BKP
    CICD --> ECOM

    IDP & EDR & ZTNA & SEG -. logs .-> SIEM
    SIEM --> SOAR
    SOAR -. revoke / quarantine .-> PA
    GOV -. policy .-> PE
```

**Design choices worth noting**

- **Store kiosks** are a known weak spot (shared devices). They get a tighter policy:
  inventory data only, no customer data, and sessions bound to kiosk device identity.
- The **legacy order system** can't take modern auth, so it sits behind an *enclave
  gateway* (800-207 §3.2.2) instead of being rewritten up front.
- **SOAR → PA** closes the loop: a detection can revoke a session without a human in the
  path. This is what moves Automation & Orchestration from Traditional toward Advanced.
