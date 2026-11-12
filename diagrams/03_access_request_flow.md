# Access Request Flow (fictional scenario)

An analyst at Kestrel Ridge Outfitters (fictional) opens the order system from a managed
laptop. The sequence shows per-session evaluation (tenet T3), dynamic policy (T4) and
continuous re-evaluation (T5/T6).

```mermaid
sequenceDiagram
    autonumber
    actor U as Analyst (managed laptop)
    participant PEP as ZTNA gateway (PEP)
    participant IDP as Identity Provider
    participant PE as Policy Engine
    participant PA as Policy Administrator
    participant DEV as MDM / EDR
    participant APP as Order system

    U->>PEP: Request order system
    PEP->>IDP: Redirect for authentication
    IDP-->>U: MFA challenge (phishing-resistant)
    U->>IDP: Authenticator response
    IDP-->>PEP: Signed identity assertion
    PEP->>PE: Access request (identity, device ID, resource)
    PE->>DEV: Device posture?
    DEV-->>PE: Compliant, EDR healthy
    PE->>PE: Evaluate policy: role, data label, risk score, time/location
    PE-->>PA: Decision: allow, read-only, 8h session
    PA->>PEP: Configure session + short-lived token
    PEP->>APP: Proxied, encrypted session
    APP-->>U: Order data (read-only)

    Note over DEV,PE: Continuous monitoring
    DEV--)PE: Posture change: EDR alert on laptop
    PE-->>PA: Re-evaluate: revoke
    PA->>PEP: Terminate session
    PEP--xU: Session ended, re-auth from a healthy device required
```
