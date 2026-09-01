# Justification Templates

Use these templates after completing review steps 1–13. Select the template from the final `State`, replace every bracketed placeholder with row-specific evidence, and omit optional clauses when evidence does not support them. Write the result as one paragraph in the generated CSV cell.

This file governs narrative structure and presentation. The applicable sections of [Mapping Rules](mapping-rules.md) remain authoritative for control and EMB3D classification, CWE mapping, risk-treatment decisions, evidence requirements, and approvals; follow only the sections linked below.

- [1. Baseline-Derived Structure](#1-baseline-derived-structure)
- [2. Universal Rules](#2-universal-rules)
- [3. Mitigated](#3-mitigated)
- [4. Not Applicable](#4-not-applicable)
- [5. Needs Investigation](#5-needs-investigation)
- [6. Not Started](#6-not-started)

## 1. Baseline-Derived Structure

Use the completed SERIAL baseline as evidence for narrative shape, not as text to copy:

- For `Mitigated` rows, move from the concrete scenario to the protocol or control limitation, required access and actor when material, enforcement-boundary control categories, residual risk, and treatment.
- For `Not Applicable` rows, use a shorter narrative centered on the architectural evidence that makes the path absent, outside the assessed boundary, or eliminated.

Do not treat omissions in an example row as permission to omit evidence required by the current output contract or the applicable mapping rules.

## 2. Universal Rules

- State the decision rationale before supporting framework details.
- Describe behavior and evidence rather than repeating `ATT&CK ID`, `EMB3D TID`, `CWE ID`, the full CVSS vector, or other dedicated-column values.
- Render the rationale required for a retained `Allowed-with-Review` or `Discouraged` CWE as `CWE mapping rationale: ...`.
- Treat the control and EMB3D clause labels as presentation of classifications already established under [Control Classification and EMB3D Mitigations](mapping-rules.md#6-control-classification-and-emb3d-mitigations), not as independent evidence.
- Add attack vector, access requirements, minimum actor, CVSS severity, likelihood, or inherent risk only when they explain the decision.
- End a finalized risk narrative with the applicable [Treatment Evidence Requirements](mapping-rules.md#114-treatment-evidence-requirements).
- Explain each intentional `N/A` or blank field at most once.
- Avoid unqualified legal safe-harbor language. Frame compliance-oriented statements as technical-documentation support or product-specific evidence pending stakeholder review.
- Use no semicolons or embedded line breaks. Let the CSV writer enclose the complete cell in double quotes.
- Never invent a control, owner, approval, transfer mechanism, or architectural fact to complete a template.

## 3. Mitigated

```plaintext
[Actor or failure mode] can [action] through [protocol, interface, or trust relationship], causing [effect]. [Protocol, component, or process] lacks [control] or relies on [validated limitation]. [Optional: The path requires [access] and the minimum capable actor is [actor] because [capability evidence].] [Optional: Implemented controls: [verified controls enforced within the assessed product or device boundary].] [Optional: Compensating controls: [controls enforced outside the assessed product or device boundary].] [Optional: EMB3D Foundational mitigation: [exact source name] ([MID-NNN]). EMB3D Intermediate mitigation: [exact source name] ([MID-NNN]). EMB3D Leading mitigation: [exact source name] ([MID-NNN]).] [Optional: Device-specific evidence: [design, configuration, test, or verified behavior evidence].] Residual risk is [level] after [controls and remaining exposure]. Treatment is [Mitigation, Acceptance, or Transfer] because [decision rationale]. [Residual-risk owner or approving stakeholder] records approval through [mechanism or pending status].
```

Omit every optional category that lacks evidence. Adapt the closing sentence to the selected treatment and include the corresponding evidence from [Treatment Evidence Requirements](mapping-rules.md#114-treatment-evidence-requirements).

## 4. Not Applicable

```plaintext
[Candidate scenario] does not apply because [architectural contradiction, absent capability, removed element, or evidence that the path is outside the assessed boundary]. [Evidence] confirms that [rejected precondition or unavailable effect]. [Optional: The related weakness remains covered by threat row [Id or title] through [applicable path].]
```

Use [Treatment Semantics](mapping-rules.md#111-treatment-semantics) to distinguish `N/A` from `Avoidance`, then include the corresponding [Treatment Evidence Requirements](mapping-rules.md#114-treatment-evidence-requirements) and [Risk Approval Mapping](mapping-rules.md#12-risk-approval-mapping). Do not add mitigation tiers or residual-risk ownership when no residual risk remains.

## 5. Needs Investigation

```plaintext
[Candidate scenario and affected interface]. The row remains Needs Investigation because [specific evidence gap or conflict]. The gap prevents a defensible decision for [affected mappings, score, actor, treatment, or approval]. Resolve it with [required artifact, test, owner decision, or architecture clarification].
```

Leave unsupported review fields blank. Do not convert missing evidence into `Not Applicable`, `Mitigated`, or a speculative governance decision.

## 6. Not Started

Preserve the native source justification and leave enrichment and governance fields blank. Do not synthesize a reviewed narrative for an unreviewed row.
