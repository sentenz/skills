# Justification Templates

Use these templates after completing review steps 1–14. Select the template from the final `State`, replace every bracketed placeholder with row-specific evidence, and omit optional clauses when evidence does not support them. Write the result as one paragraph in the generated CSV cell.

- [1. Baseline-Derived Structure](#1-baseline-derived-structure)
- [2. Universal Rules](#2-universal-rules)
- [3. Mitigated](#3-mitigated)
- [4. Not Applicable](#4-not-applicable)
- [5. Needs Investigation](#5-needs-investigation)
- [6. Not Started](#6-not-started)

## 1. Baseline-Derived Structure

Use the completed SERIAL baseline as evidence for narrative shape, not as text to copy:

- For `Mitigated` rows, move from the concrete scenario to the protocol or control limitation, required access and actor when material, applied controls and their validated effect, residual risk, and treatment.
- For `Not Applicable` rows, use a shorter contradiction narrative that identifies the impossible or eliminated attack path.
- Include only the control tiers that apply. Do not emit empty Foundational, Intermediate, or Leading clauses.
- Treat Basic controls as product-specific physical, procedural, or implementation controls, not as a MITRE EMB3D mitigation level.

Do not treat omissions in an example row as permission to omit evidence required by the current output contract or mapping rules.

## 2. Universal Rules

- State the decision rationale before supporting framework details.
- Describe behavior and evidence rather than repeating `ATT&CK ID`, `EMB3D TID`, `CWE ID`, the full CVSS vector, or other dedicated-column values.
- When retaining a CWE marked `Allowed-with-Review` or `Discouraged`, add `CWE mapping rationale: ...` with the supporting evidence and why no more-specific `Allowed` entry fits.
- Treat ATT&CK mitigation relationships, CWE `potential_mitigations`, and EMB3D mitigations as source-backed candidate guidance. A framework source match does not prove that the product implements the control or that the control reduces residual risk.
- For an applied control, lead with product-specific implementation evidence and state the validated control effect. Optionally identify an exact ATT&CK mitigation or CWE mitigation strategy when it materially explains the control rationale. Do not count the same product control as multiple independent controls merely because several frameworks recommend it.
- Include an MID only when row evidence supports the mitigation and the mitigation asset maps it to at least one TID in the row. Copy its exact source name and Foundational, Intermediate, or Leading level. Distinguish implemented controls from recommendations. Omit MIDs when `EMB3D TID` is `N/A`. No dedicated MID column exists.
- Describe detection-only and recovery-only controls as detection or recovery. Do not present them as prevention, root-cause remediation, or elimination of an attack path unless separate evidence supports that effect.
- Add attack vector, access requirements, minimum actor, CVSS severity, likelihood, or inherent risk only when they explain the decision.
- End a finalized risk narrative with the treatment-specific evidence: remaining exposure, residual risk, owner or approving stakeholder, and approval mechanism where required.
- Use no semicolons or embedded line breaks. Let the CSV writer enclose the complete cell in double quotes.
- Never invent a control, owner, approval, transfer mechanism, or architectural fact to complete a template.

## 3. Mitigated

```plaintext
[Actor or failure mode] can [action] through [protocol, interface, or trust relationship], causing [effect]. [Protocol, component, or process] lacks [control] or relies on [validated limitation]. [Optional: The path requires [access] and the minimum capable actor is [actor] because [capability evidence].] Applied controls include [confirmed controls], validated by [implementation or verification evidence], which [eliminate a prerequisite, constrain the attack vector or privileges, prevent exploitation, contain impact, detect the behavior, or support recovery]. [Optional: Source-backed alignment: ATT&CK mitigation [name] ([Mxxxx]); CWE mitigation [strategy or phase]; Foundational mitigation [name] ([MID-NNN]); Intermediate mitigation [name] ([MID-NNN]); Leading mitigation [name] ([MID-NNN]).] Remaining exposure is [remaining attack path or consequence]. Residual risk is [level]. Treatment is [Mitigation, Acceptance, or Transfer] because [decision rationale]. [Residual-risk owner or approving stakeholder] records approval through [mechanism or pending status].
```

For `Acceptance`, replace the control-focused treatment sentence with the business rationale, acceptance threshold, approving stakeholder, and explicit approval mechanism. For `Transfer`, identify the named third party, contract, SLA, warranty, insurance policy, or managed service and state which consequences remain with the product owner.

## 4. Not Applicable

```plaintext
[Candidate scenario] does not apply because [architectural contradiction, absent capability, removed element, or out-of-scope boundary]. [Evidence] confirms that [rejected precondition or unavailable effect]. [Optional: The related weakness remains covered by threat row [Id or title] through [applicable path].]
```

Name the architectural record or design decision when `Risk Treatment = Avoidance`. Do not add mitigation tiers, residual-risk ownership, or approval prose when the row has no residual risk and `Risk Approval = Not Required`.

## 5. Needs Investigation

```plaintext
[Candidate scenario and affected interface]. The row remains Needs Investigation because [specific evidence gap or conflict]. The gap prevents a defensible decision for [affected mappings, mitigation implementation or effect, score, actor, treatment, or approval]. Resolve it with [required artifact, test, owner decision, or architecture clarification].
```

Leave unsupported review fields blank. Candidate framework mitigations may be recorded as remediation guidance, but do not convert an unverified recommendation into an applied control, `Not Applicable`, `Mitigated`, or a speculative governance decision.

## 6. Not Started

Preserve the native source justification and leave enrichment and governance fields blank. Do not synthesize a reviewed narrative for an unreviewed row.
