# Justification Templates

Use these templates after completing review steps 1–13. Select the template from the final `State`, replace every bracketed placeholder with row-specific evidence, and omit optional clauses when evidence does not support them. Write the result as one paragraph in the generated CSV cell.

- [1. Baseline-Derived Structure](#1-baseline-derived-structure)
- [2. Universal Rules](#2-universal-rules)
- [3. Mitigated](#3-mitigated)
- [4. Not Applicable](#4-not-applicable)
- [5. Needs Investigation](#5-needs-investigation)
- [6. Not Started](#6-not-started)

## 1. Baseline-Derived Structure

Use the [completed SERIAL baseline](Example_Threat_Model_Generated.csv) as evidence for narrative shape, not as text to copy:

- For `Mitigated` rows, move from the concrete scenario to the protocol or control limitation, required access and actor when material, enforcement-boundary control categories, residual risk, and treatment.
- For `Not Applicable` rows, use a shorter contradiction narrative that identifies the impossible or eliminated attack path.

Do not treat omissions in an example row as permission to omit evidence required by the current output contract or mapping rules.

## 2. Universal Rules

- State the evidence-based rationale for `State` and the concrete scenario, architectural contradiction, or evidence gap before supporting framework details. Do not produce generic, short, or identifier-only justifications.
- Keep identifiers and score artifacts in dedicated columns. Describe the behavior supporting ATT&CK mappings and the device property or missing control supporting EMB3D mappings without repeating IDs. Prefer weakness names or exploit behavior over CWE IDs unless an ID is required for disambiguation. Describe evidence rather than repeating the full CVSS vector or other dedicated-column values.
- When retaining a CWE marked `Allowed-with-Review` or `Discouraged`, add `CWE mapping rationale: ...` with the supporting evidence and why no more-specific `Allowed` entry fits.
- Apply [Control Enforcement Boundary](mapping-rules.md#61-control-enforcement-boundary) to define the assessed boundary, split claims that span it, and distinguish `Implemented controls:` from `Compensating controls:`. Include only evidenced categories. A compensating-only mitigated narrative is valid; do not emit an empty or invented `Implemented controls:` clause.
- Keep EMB3D clauses separate from enforcement-boundary categories and apply [EMB3D Mitigations](mapping-rules.md#62-emb3d-mitigations) for MID applicability, exact source names and levels, TID associations, and device-specific implementation evidence. Record MIDs in the narrative because no dedicated MID column exists.
- Add protocol, trust relationship, validation behavior, attack vector, access requirements, minimum actor, scoring, likelihood, inherent risk, or mapping details only when they explain the decision.
- End a finalized risk narrative with the [Treatment Evidence Requirements](mapping-rules.md#114-treatment-evidence-requirements), including remaining exposure, residual risk, owner or approving stakeholder, and approval mechanism where required.
- Explain intentional `N/A` or blank fields once.
- Avoid unqualified legal safe-harbor language. Frame compliance-oriented statements as technical-documentation support or product-specific evidence pending stakeholder review.
- Use no semicolons or embedded line breaks. Let the CSV writer enclose the complete cell in double quotes.
- Never invent missing evidence, including a control, owner, approval, transfer mechanism, or architectural fact, to complete a template.

## 3. Mitigated

```plaintext
[Actor or failure mode] can [action] through [protocol, interface, or trust relationship], causing [effect]. [Protocol, component, or process] lacks [control] or relies on [validated limitation]. [Optional: The path requires [access] and the minimum capable actor is [actor] because [capability evidence].] [Optional: Implemented controls: [verified controls enforced within the assessed product or device boundary].] [Optional: Compensating controls: [controls enforced outside the assessed product or device boundary].] [Optional: EMB3D Foundational mitigation: [exact source name] ([MID-NNN]). EMB3D Intermediate mitigation: [exact source name] ([MID-NNN]). EMB3D Leading mitigation: [exact source name] ([MID-NNN]).] [Optional: Device-specific evidence: [design, configuration, test, or verified behavior evidence].] Residual risk is [level] after [controls and remaining exposure]. Treatment is [Mitigation, Acceptance, or Transfer] because [decision rationale]. [Residual-risk owner or approving stakeholder] records approval through [mechanism or pending status].
```

Omit optional clauses according to the [Universal Rules](#2-universal-rules). For `Acceptance`, replace the control-focused treatment sentence with the business rationale, acceptance threshold, approving stakeholder, and explicit approval mechanism. For `Transfer`, identify the named third party, contract, SLA, warranty, insurance policy, or managed service and state which consequences remain with the product owner.

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
