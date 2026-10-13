# Justification Templates

State-specific narrative specifications for `Justification`. Replace every bracketed placeholder with row-specific evidence and omit unsupported optional clauses. The [workflow](../SKILL.md#33-review) controls when the final-state template is selected.

- [1. Baseline-Derived Structure](#1-baseline-derived-structure)
- [2. Universal Rules](#2-universal-rules)
- [3. Mitigated](#3-mitigated)
- [4. Not Applicable](#4-not-applicable)
- [5. Needs Investigation](#5-needs-investigation)
- [6. Not Started](#6-not-started)
- [7. EMB3D Citation Format](#7-emb3d-citation-format)
- [8. Treatment Evidence](#8-treatment-evidence)

## 1. Baseline-Derived Structure

Use the completed SERIAL baseline as evidence for narrative shape, not as text to copy:

- For `Mitigated` rows, move from the concrete scenario to the protocol or control limitation, required access and actor when material, enforcement-boundary control categories, residual risk, and treatment.
- For `Not Applicable` rows, use a shorter contradiction narrative that identifies the impossible or eliminated attack path.
- Apply the [Universal Rules](#2-universal-rules) for control labels and the [EMB3D Citation Format](#7-emb3d-citation-format) for source-level clauses.

Do not treat omissions in an example row as permission to omit evidence required by the current output contract or mapping rules.

## 2. Universal Rules

- Write one concise analyst paragraph giving the evidence-based rationale for `State` and the concrete scenario, architectural contradiction, or evidence gap before supporting framework details. Do not use generic, short, or identifier-only justifications.
- Describe behavior and evidence rather than repeating `ATT&CK ID`, `EMB3D TID`, `CWE ID`, the full CVSS vector, or other dedicated-column values. Explain the ATT&CK behavior and EMB3D device property or missing control; prefer weakness names or exploit behavior for CWE unless repeating the ID is required for disambiguation.
- When retaining a CWE marked `Allowed-with-Review` or `Discouraged`, add `CWE mapping rationale: ...` with the supporting evidence and why no more-specific `Allowed` entry fits.
- Use `Implemented controls:` and `Compensating controls:` for controls classified under [Control Enforcement Boundary](mapping-rules.md#61-control-enforcement-boundary). Include only evidenced categories; a compensating-only narrative is valid. Do not emit an empty or invented `Implemented controls:` clause.
- Format eligible MID citations under [EMB3D Citation Format](#7-emb3d-citation-format); eligibility and implementation evidence are governed by [EMB3D Mitigations](mapping-rules.md#62-emb3d-mitigations).
- Add protocol, trust relationship, validation behavior, attack vector, access requirements, minimum actor, CVSS severity, likelihood, inherent risk, or mapping details only when they explain the decision.
- End a finalized risk narrative with [Treatment Evidence](#8-treatment-evidence).
- Record assumptions and missing evidence. Explain intentional `N/A` or blank fields once.
- Avoid unqualified legal safe-harbor language. Frame compliance-oriented statements as technical-documentation support or product-specific evidence pending stakeholder review.
- Use no semicolons or embedded line breaks. Let the CSV writer enclose the complete cell in double quotes.
- Never invent a control, owner, approval, transfer mechanism, or architectural fact to complete a template.

## 3. Mitigated

```plaintext
[Actor or failure mode] can [action] through [protocol, interface, or trust relationship], causing [effect]. [Protocol, component, or process] lacks [control] or relies on [validated limitation]. [Optional: The path requires [access] and the minimum capable actor is [actor] because [capability evidence].] [Optional: Implemented controls: [verified controls enforced within the assessed product or device boundary].] [Optional: Compensating controls: [controls enforced outside the assessed product or device boundary].] [Optional: EMB3D Foundational mitigation: [exact source name] ([MID-NNN]). EMB3D Intermediate mitigation: [exact source name] ([MID-NNN]). EMB3D Leading mitigation: [exact source name] ([MID-NNN]).] [Optional: Device-specific evidence: [design, configuration, test, or verified behavior evidence].] Residual risk is [level] after [controls and remaining exposure]. Treatment is [Mitigation, Acceptance, or Transfer] because [decision rationale]. [Residual-risk owner or approving stakeholder] records approval through [mechanism or pending status].
```

Omit every optional category that lacks evidence. In particular, a mitigated narrative supported only by external controls should contain `Compensating controls:` and no `Implemented controls:` clause. For `Acceptance` or `Transfer`, adapt the treatment sentence to the required [Treatment Evidence](#8-treatment-evidence).

## 4. Not Applicable

```plaintext
[Candidate scenario] does not apply because [architectural contradiction, absent capability, removed element, or out-of-scope boundary]. [Evidence] confirms that [rejected precondition or unavailable effect]. [Optional: The related weakness remains covered by threat row [Id or title] through [applicable path].]
```

Name the contradiction or eliminated element and explain why the minimum actor was considered before rejecting the path. Include the [Avoidance evidence](#8-treatment-evidence) and apply [Residual Risk](analysis-guidance.md#7-residual-risk). Do not add mitigation tiers, residual-risk ownership, or approval prose when the row has no residual risk and `Risk Approval = Not Required`.

## 5. Needs Investigation

```plaintext
[Candidate scenario and affected interface]. The row remains Needs Investigation because [specific evidence gap or conflict]. The gap prevents a defensible decision for [affected mappings, score, actor, treatment, or approval]. Resolve it with [required artifact, test, owner decision, or architecture clarification].
```

Leave unsupported review fields blank. Do not convert missing evidence into `Not Applicable`, `Mitigated`, or a speculative governance decision.

## 6. Not Started

Preserve the native source justification and apply [Field Resolution](artifact-contract.md#3-field-resolution) to enrichment and governance fields. Do not synthesize a reviewed narrative for an unreviewed row.

## 7. EMB3D Citation Format

Keep EMB3D clauses separate from the enforcement-boundary control categories. No dedicated MID column exists. For each eligible MID, copy its exact source name and source level with the `EMB3D` prefix:

| MITRE EMB3D Mitigation Level | Use in `Justification` |
| --- | --- |
| Foundational | `EMB3D Foundational mitigation: <exact source name> (MID-NNN).` |
| Intermediate | `EMB3D Intermediate mitigation: <exact source name> (MID-NNN).` |
| Leading | `EMB3D Leading mitigation: <exact source name> (MID-NNN).` |

For an implementation claim supported under [EMB3D Mitigations](mapping-rules.md#62-emb3d-mitigations), add `Device-specific evidence:` to the EMB3D clause and describe the verified within-boundary behavior separately under `Implemented controls:`. Omit MIDs when `EMB3D TID` is `N/A`; describe verified controls under their enforcement-boundary category without an EMB3D label.

## 8. Treatment Evidence

End finalized risk narratives with the applicable treatment evidence, including remaining exposure, residual risk, owner or approving stakeholder, and approval mechanism where required by [Risk Treatment Mapping](mapping-rules.md#11-risk-treatment-mapping).

| Risk Treatment | Minimum Evidence in `Justification` |
| --- | --- |
| Avoidance | Architectural record or design decision confirming the risk source has been eliminated; identify the removed or restructured system element, function, interface, data flow, or attack path. |
| Mitigation | Implemented and/or compensating controls, enforcement boundary, remaining exposure, residual risk level, residual-risk owner, and approval mechanism. |
| Acceptance | Business rationale for retention, acceptance threshold, approving stakeholder, and explicit approval mechanism. |
| Transfer | Named third party, specific contract/SLA/warranty/insurance or managed-service reference, explicit risk scope, and consequences retained by the product owner. |
