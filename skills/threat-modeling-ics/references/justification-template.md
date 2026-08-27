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

- For `Mitigated` rows, move from the concrete scenario to the protocol or control limitation, required access and actor when material, CWE root-cause evidence when a CWE is populated, applied controls, residual risk, and treatment.
- For `Not Applicable` rows, use a shorter contradiction narrative that identifies the impossible or eliminated attack path.
- Include only the control tiers that apply. Do not emit empty Foundational, Intermediate, or Leading clauses.
- Treat Basic controls as product-specific physical, procedural, or implementation controls, not as a MITRE EMB3D mitigation level.

Do not treat omissions in an example row as permission to omit evidence required by the current output contract or mapping rules.

## 2. Universal Rules

- State the decision rationale before supporting framework details.
- Describe ATT&CK and EMB3D behavior without repeating their dedicated-column identifiers unless disambiguation requires it.
- When `CWE ID` is populated, add exactly one `CWE root-cause evidence: CWE-NNN — ...` clause for each mapped CWE. The clause must state affirmative product, architecture, design, implementation, configuration, or verified behavioral evidence that satisfies the weakness definition. A STRIDE category, ATT&CK technique, EMB3D threat, attack vector, attacker capability, exploitation prerequisite, technical impact, CVSS metric, or recommended mitigation is not root-cause evidence by itself.
- When multiple CWEs are mapped, repeat the root-cause evidence clause for every ID and provide separately sufficient evidence for each weakness. Do not list ancestors, descendants, alternative hypotheses, or plausible causes merely because they are related to the threat outcome.
- When retaining a CWE marked `Allowed-with-Review` or `Discouraged`, add `CWE mapping rationale: ...` with the supporting evidence and why no more-specific `Allowed` entry fits. This is additional to, not a replacement for, the root-cause evidence clause.
- Treat CWE `potential_mitigations` as candidate treatments. Translate an applicable candidate into a product-specific, testable engineering control and identify verification evidence before claiming implementation, effectiveness, or residual-risk reduction. Omit inapplicable candidate mitigations rather than presenting the CWE catalog text as a requirement.
- Include an MID only when row evidence supports the mitigation and the mitigation asset maps it to at least one TID in the row. Copy its exact source name and Foundational, Intermediate, or Leading level. Distinguish implemented controls from recommendations. Omit MIDs when `EMB3D TID` is `N/A`. No dedicated MID column exists.
- Add attack vector, access requirements, minimum actor, CVSS severity, likelihood, or inherent risk only when they explain the decision.
- End a finalized risk narrative with the treatment-specific evidence: remaining exposure, residual risk, owner or approving stakeholder, and approval mechanism where required.
- Use no semicolons or embedded line breaks. Let the CSV writer enclose the complete cell in double quotes.
- Never invent a weakness, control, owner, approval, transfer mechanism, or architectural fact to complete a template.

## 3. Mitigated

```plaintext
[Actor or failure mode] can [action] through [protocol, interface, or trust relationship], causing [effect]. [Protocol, component, or process] lacks [control] or relies on [validated limitation]. [Optional: The path requires [access] and the minimum capable actor is [actor] because [capability evidence].] [When CWE is populated: CWE root-cause evidence: CWE-NNN — [product-specific evidence satisfying the weakness definition]. Repeat once for each mapped CWE.] Applied controls include [confirmed controls]. [Optional: Foundational mitigation: [name] ([MID-NNN]). Intermediate mitigation: [name] ([MID-NNN]). Leading mitigation: [name] ([MID-NNN]).] Residual risk is [level] after [controls and remaining exposure]. Treatment is [Mitigation, Acceptance, or Transfer] because [decision rationale]. [Residual-risk owner or approving stakeholder] records approval through [mechanism or pending status].
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

Leave unsupported review fields blank. Do not convert missing root-cause evidence into a CWE mapping, `Not Applicable`, `Mitigated`, or a speculative governance decision.

## 6. Not Started

Preserve the native source justification and leave enrichment and governance fields blank. Do not synthesize a reviewed narrative for an unreviewed row.
