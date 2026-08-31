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

- For `Mitigated` rows, move from the concrete scenario to the protocol or control limitation, required access and actor when material, enforcement-boundary control categories, residual risk, and treatment.
- For `Not Applicable` rows, use a shorter contradiction narrative that identifies the impossible or eliminated attack path.
- Classify verified controls as `Implemented controls` when enforced within the assessed product or device boundary and `Compensating controls` when enforced outside that boundary.
- Include only the control categories and EMB3D source levels that apply. A compensating-only mitigated narrative is valid. Do not emit an empty or invented `Implemented controls` clause.
- Keep `EMB3D Foundational mitigation`, `EMB3D Intermediate mitigation`, and `EMB3D Leading mitigation` clauses separate from the enforcement-boundary categories.

Do not treat omissions in an example row as permission to omit evidence required by the current output contract or mapping rules.

## 2. Universal Rules

- State the decision rationale before supporting framework details.
- Describe behavior and evidence rather than repeating `ATT&CK ID`, `EMB3D TID`, `CWE ID`, the full CVSS vector, or other dedicated-column values.
- When retaining a CWE marked `Allowed-with-Review` or `Discouraged`, add `CWE mapping rationale: ...` with the supporting evidence and why no more-specific `Allowed` entry fits.
- Define the assessed product or device boundary before classifying controls. If a control spans the boundary, split the narrative into separately evidenced within-boundary and outside-boundary parts.
- Use `Implemented controls:` only for verified controls enforced inside the assessed boundary. Use `Compensating controls:` for external physical, network, workstation, installation, monitoring, or procedural controls.
- Include an MID only when row evidence supports the mitigation and the mitigation asset maps it to at least one TID in the row. Copy its exact source name and Foundational, Intermediate, or Leading level under an `EMB3D <level> mitigation:` clause. Omit MIDs when `EMB3D TID` is `N/A`. No dedicated MID column exists.
- Treat an MID as source-backed guidance unless device-specific evidence proves implementation. When claiming implementation, add `Device-specific evidence:` to the EMB3D clause and describe the verified within-boundary behavior separately under `Implemented controls:`.
- Add attack vector, access requirements, minimum actor, CVSS severity, likelihood, or inherent risk only when they explain the decision.
- End a finalized risk narrative with the treatment-specific evidence: remaining exposure, residual risk, owner or approving stakeholder, and approval mechanism where required.
- Use no semicolons or embedded line breaks. Let the CSV writer enclose the complete cell in double quotes.
- Never invent a control, owner, approval, transfer mechanism, or architectural fact to complete a template.

## 3. Mitigated

```plaintext
[Actor or failure mode] can [action] through [protocol, interface, or trust relationship], causing [effect]. [Protocol, component, or process] lacks [control] or relies on [validated limitation]. [Optional: The path requires [access] and the minimum capable actor is [actor] because [capability evidence].] [Optional: Implemented controls: [verified controls enforced within the assessed product or device boundary].] [Optional: Compensating controls: [controls enforced outside the assessed product or device boundary].] [Optional: EMB3D Foundational mitigation: [exact source name] ([MID-NNN]). EMB3D Intermediate mitigation: [exact source name] ([MID-NNN]). EMB3D Leading mitigation: [exact source name] ([MID-NNN]).] [Optional: Device-specific evidence: [design, configuration, test, or verified behavior evidence].] Residual risk is [level] after [controls and remaining exposure]. Treatment is [Mitigation, Acceptance, or Transfer] because [decision rationale]. [Residual-risk owner or approving stakeholder] records approval through [mechanism or pending status].
```

Omit every optional category that lacks evidence. In particular, a mitigated narrative supported only by external controls should contain `Compensating controls:` and no `Implemented controls:` clause. For `Acceptance`, replace the control-focused treatment sentence with the business rationale, acceptance threshold, approving stakeholder, and explicit approval mechanism. For `Transfer`, identify the named third party, contract, SLA, warranty, insurance policy, or managed service and state which consequences remain with the product owner.

## 4. Not Applicable

```plaintext
[Candidate scenario] does not apply because [architectural contradiction, absent capability, removed element, or out-of-scope boundary]. [Evidence] confirms that [rejected precondition or unavailable effect]. [Optional: The related weakness remains covered by threat row [Id or title] through [applicable path].]
```

Name the architectural record or design decision when `Risk Treatment = Avoidance`. Do not add mitigation tiers, residual-risk ownership, or approval prose when the row has no residual risk and `Risk Approval = Not Required`.

## 5. Needs Investigation

```plaintext
[Candidate scenario and affected interface]. The row remains Needs Investigation because [specific evidence gap or conflict]. The gap prevents a defensible decision for [affected mappings, score, actor, treatment, or approval]. Resolve it with [required artifact, test, owner decision, or architecture clarification].
```

Leave unsupported review fields blank. Do not convert missing evidence into `Not Applicable`, `Mitigated`, or a speculative governance decision.

## 6. Not Started

Preserve the native source justification and leave enrichment and governance fields blank. Do not synthesize a reviewed narrative for an unreviewed row.
