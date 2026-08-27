# CWE Root-Cause Evidence Examples

Use these examples to distinguish a threat or impact from an evidenced product weakness. They complement the schema-oriented `SERIAL_Threat_Model_Generated.csv` baseline and follow the current CWE mapping rules.

## Confirmed weakness

```text
CWE ID: CWE-319
CWE root-cause evidence: CWE-319 — security-relevant maintenance telemetry is transmitted in cleartext over an interface that can be observed outside the component trust boundary.
```

The information-disclosure threat nominates candidate weaknesses. The product-specific transmission behavior is what substantiates CWE-319.

## Threat outcome without a confirmed weakness

```text
Threat: sustained service traffic can degrade availability
CWE ID: N/A
Justification: The availability effect is established, but the available evidence does not establish deadlock, unbounded allocation, parser failure, or another specific product weakness. No CWE is assigned from the denial-of-service outcome alone.
```

Do not map a possible cause merely because it could produce the observed effect.

## Multiple weaknesses

When two weaknesses are independently evidenced, provide one clause for each mapped ID:

```text
CWE ID: CWE-306, CWE-778
CWE root-cause evidence: CWE-306 — the maintenance function accepts security-relevant configuration requests without authenticating the requesting endpoint.
CWE root-cause evidence: CWE-778 — the same function records no security-relevant audit event for accepted configuration changes.
```

Do not add ancestors, descendants, or alternative hypotheses unless each is separately established as a concrete weakness in the assessed product.

## Candidate mitigation to verified control

Treat CWE `potential_mitigations` as source guidance rather than product requirements or implementation evidence. Preserve the source `mitigation_id` when present, lifecycle phase, strategy, effectiveness, effectiveness notes, and description during analysis, then record the local decision separately.

```text
CWE candidate mitigation: <source mitigation and metadata>
Applicability: Applicable because <architecture-specific reason>
Engineering control: The product SHALL <normative, testable behavior>.
Verification: <review, analysis, automated test, negative test, inspection, or other evidence>
Status: Implemented and verified | Planned | Not applicable | Superseded by equivalent control
```

Only implemented and verified product controls may be used to justify residual-risk reduction. MITRE's qualitative mitigation effectiveness remains source guidance and is not a numeric risk multiplier.
