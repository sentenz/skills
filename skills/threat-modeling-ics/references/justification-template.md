# Justification Templates

Use these templates after completing review steps 1–13. Select the template from the final `State`, replace every bracketed placeholder with row-specific evidence, and omit optional clauses when evidence does not support them. Write the result as one paragraph in the generated CSV cell.

- [1. Baseline-Derived Structure](#1-baseline-derived-structure)
- [2. Universal Rules](#2-universal-rules)
- [3. Mitigated](#3-mitigated)
- [4. Not Applicable](#4-not-applicable)
- [5. Needs Investigation](#5-needs-investigation)
- [6. Not Started](#6-not-started)

## 1. Baseline-Derived Structure

Use the completed SERIAL baseline as evidence for narrative shape, not as text to copy:

- For `Mitigated` rows, move from the concrete scenario to the protocol or control limitation, required access and actor when material, applied controls, residual risk, and treatment.
- For `Not Applicable` rows, use a shorter contradiction narrative that identifies the impossible or eliminated attack path.
- Include only the EMB3D mitigation levels that apply. Do not emit empty Foundational, Intermediate, or Leading clauses.
- Use `Implemented controls` for verified controls enforced within the assessed product or device boundary.
- Use `Compensating controls` for verified controls enforced outside the vulnerable component or device boundary, including environmental, installation, network, monitoring, physical-access, or procedural measures.
- Do not use `Basic mitigation` or `Basic controls`. `Basic` is not an EMB3D mitigation level and does not communicate the control enforcement boundary.

Do not treat omissions in an example row as permission to omit evidence required by the current output contract or mapping rules.

## 2. Universal Rules

- State the decision rationale before supporting framework details.
- Describe behavior and evidence rather than repeating `ATT&CK ID`, `EMB3D PID`, `EMB3D TID`, `CWE ID`, the full CVSS vector, or other dedicated-column values.
- For every populated `EMB3D TID`, describe the architecture or product evidence that makes at least one recorded `EMB3D PID` applicable. A source PID-to-TID relationship is necessary but does not by itself prove that the property exists in the assessed product.
- When retaining a CWE marked `Allowed-with-Review` or `Discouraged`, add `CWE mapping rationale: ...` with the supporting evidence and why no more-specific `Allowed` entry fits.
- Classify controls by where they are enforced, not by perceived strength. A firmware, hardware, or product-integrated control verified inside the assessed device boundary is an `Implemented control`. A gateway, firewall, segmentation mechanism, monitoring service, cabinet or site-access restriction, external workstation control, or procedure enforced outside that boundary is a `Compensating control`.
- Include an MID only when row evidence supports the mitigation, the mitigation asset maps it to at least one TID in the row, and the row's PID-to-TID relationship is source-valid. Copy its exact source name and Foundational, Intermediate, or Leading level. Distinguish a source-backed recommendation from a control verified as implemented. Omit MIDs when `EMB3D TID` is `N/A`. No dedicated MID column exists.
- Do not present an external gateway, network firewall, segmentation control, monitoring service, cabinet or site-access restriction, external workstation control, or procedure as an EMB3D mitigation implemented by the embedded device. Record such measures as compensating controls and describe the device-native residual exposure separately.
- Add attack vector, access requirements, minimum actor, CVSS severity, likelihood, or inherent risk only when they explain the decision.
- End a finalized risk narrative with the treatment-specific evidence: remaining exposure, residual risk, owner or approving stakeholder, and approval mechanism where required.
- Use no semicolons or embedded line breaks. Let the CSV writer enclose the complete cell in double quotes.
- Never invent a device property, control, owner, approval, transfer mechanism, or architectural fact to complete a template.

## 3. Mitigated

```plaintext
[Actor or failure mode] can [action] through [protocol, interface, or trust relationship], causing [effect]. [Protocol, component, or process] lacks [control] or relies on [validated limitation]. [Optional: EMB3D property evidence: [architecture or product fact] supports [property name].] [Optional: The path requires [access] and the minimum capable actor is [actor] because [capability evidence].] Implemented controls include [confirmed controls enforced within the assessed product or device boundary]. [Optional: Compensating controls include [confirmed external, environmental, installation, network, monitoring, physical-access, workstation, or procedural controls], while [remaining device-native exposure] remains.] [Optional: Foundational mitigation: [name] ([MID-NNN]). Intermediate mitigation: [name] ([MID-NNN]). Leading mitigation: [name] ([MID-NNN]).] Residual risk is [level] after [controls and remaining exposure]. Treatment is [Mitigation, Acceptance, or Transfer] because [decision rationale]. [Residual-risk owner or approving stakeholder] records approval through [mechanism or pending status].
```

For `Acceptance`, replace the control-focused treatment sentence with the business rationale, acceptance threshold, approving stakeholder, and explicit approval mechanism. For `Transfer`, identify the named third party, contract, SLA, warranty, insurance policy, or managed service and state which consequences remain with the product owner.

## 4. Not Applicable

```plaintext
[Candidate scenario] does not apply because [architectural contradiction, absent capability, removed element, or out-of-scope boundary]. [Evidence] confirms that [rejected precondition or unavailable effect]. [Optional: The related weakness remains covered by threat row [Id or title] through [applicable path].]
```

Name the architectural record or design decision when `Risk Treatment = Avoidance`. Do not add mitigation tiers, residual-risk ownership, or approval prose when the row has no residual risk and `Risk Approval = Not Required`.

## 5. Needs Investigation

```plaintext
[Candidate scenario and affected interface]. The row remains Needs Investigation because [specific evidence gap or conflict]. The gap prevents a defensible decision for [affected mappings, score, actor, treatment, or approval]. Resolve it with [required artifact, test, owner decision, or architecture clarification].
```

Leave unsupported review fields blank. For EMB3D, leave both `EMB3D PID` and `EMB3D TID` blank when device-property applicability is unresolved. When device-property applicability is established but the mapped threat's scenario relevance remains unresolved, retain the evidence-backed `EMB3D PID`, leave `EMB3D TID` blank, and keep the row in `Needs Investigation` until the threat can be confirmed or excluded. Do not convert missing evidence into `Not Applicable`, `Mitigated`, or a speculative governance decision.

## 6. Not Started

Preserve the native source justification and leave enrichment and governance fields blank. Do not synthesize a reviewed narrative for an unreviewed row.
