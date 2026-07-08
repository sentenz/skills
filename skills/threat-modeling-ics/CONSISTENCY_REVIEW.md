# Threat Modeling ICS Consistency Review

This note captures the hardening recommendations identified during review of `skills/threat-modeling-ics/SKILL.md`. It is intentionally scoped to consistency, over-prescription, and defensibility risks in the sample mappings so that future changes to the skill can be applied without weakening the source-of-record model or the traceability contract.

## Review focus

The existing skill is structurally strong: it preserves the raw Microsoft TMT CSV as the source of record, appends enrichment columns, and requires local ATT&CK for ICS, EMB3D, CWE, and CVSS assets before recording identifiers. The principal risks are not coverage gaps. They are consistency and defensibility risks introduced by deterministic governance language and by example rows whose state, treatment, and evidence columns do not always agree.

## Emerging consistency concerns

### 1. State and treatment combinations drift in the examples

Several generated CSV rows use `State = Mitigated` while the `Risk Treatment` remains `Acceptance`. This is defensible only when the justification clearly distinguishes implemented controls from the residual-risk governance decision. Otherwise it reads as if a row can be both fully mitigated and accepted because mitigation is unavailable.

Recommended rule:

- Use `State = Mitigated` only when controls are confirmed and residual exposure is reduced to an accepted level.
- Use `Risk Treatment = Acceptance` only when the residual risk is intentionally retained and the business or product-security approval basis is documented.
- If controls exist but residual risk is intentionally retained because the protocol weakness cannot be removed, require the justification to say: `Controls reduce exposure but do not remove the inherent protocol weakness. Residual risk is accepted pending the named approval mechanism.`

### 2. Avoidance is used while the state remains mitigated

Rows involving production removal or permanent disabling of debug or removable-media paths use `Risk Treatment = Avoidance` but still carry `State = Mitigated`. If the interface is structurally removed from production scope, `Not Applicable` or a clearly documented eliminated-risk state is more consistent than `Mitigated`.

Recommended rule:

- `Risk Treatment = Avoidance` requires evidence that the risk source is removed, disabled, or no longer present in the assessed design.
- When avoidance is achieved by a design change, the state should either be `Not Applicable` or the justification must explicitly state that the row is reviewed as a pre-change design risk whose treatment is avoidance.

### 3. Not Applicable rows retain positive framework mappings

Rows marked `Not Applicable` still include ATT&CK, EMB3D, and CWE mappings in places. This creates ambiguity: it is unclear whether the identifiers are supported mappings, rejected candidates, or evidence for a different threat row.

Recommended rule:

- For `State = Not Applicable`, use `N/A` in ATT&CK, EMB3D, and CWE columns unless the mapped behavior remains applicable to the rejected path.
- If a rejected candidate mapping is useful, record it only in the justification as a rejected alternative, not in the dedicated identifier columns.
- If the mapped behavior belongs to a different row, reference the related row by `Id` in the justification rather than duplicating the mapping.

### 4. CVSS Base severity is sometimes treated as residual risk

Some examples appear to use zero-impact CVSS outcomes when controls or contextual constraints reduce the practical risk. This can blur the distinction between intrinsic technical severity and residual risk after controls.

Recommended rule:

- `CVSS-B v4.0 Score`, `CVSS v4.0 Severity`, and `CVSS v4.0 Vector` should describe the intrinsic modeled weakness and attack path.
- Residual exposure should be recorded in `Justification`, `Risk Prioritization`, `Risk Treatment`, and `Risk Approval` rather than by zeroing the base score.
- A zero-impact base score should be reserved for rows where the modeled weakness or attack path is architecturally impossible or structurally eliminated.

### 5. Numeric score format is inconsistent

The skill describes scores with comma decimal separators, but examples mix values such as `7,1`, `5,2`, `2,4`, `0`, and `7`.

Recommended rule:

- Normalize all populated scores to one explicit format. If comma decimal format is required, write integer scores as `7,0` and zero as `0,0`.
- Reject generated CSV rows where a score is present without a matching valid vector and severity.

## Emerging over-prescription concerns

### 1. Blocking gates can halt useful best-effort analysis

The current workflow is strict and audit-friendly, but repeated blocking gates can make agent execution brittle for incomplete design packages.

Recommended rule:

- Keep the existing strict workflow for audit mode.
- Add a best-effort mode in which the agent continues with explicit assumptions, leaves unresolved fields blank, and records `Needs Investigation` where evidence is missing.
- Preserve blocking behavior only for missing source CSV, missing required native columns, or conflicts that would materially change whether a threat path exists.

### 2. CRA wording is too deterministic in sample rows

Sample rows repeatedly frame acceptance as being under CRA Recital 55 and conditioned on a trusted environment. This risks implying a legal safe harbor from a technical mapping alone.

Recommended rule:

- Avoid treating CRA language as a deterministic risk-treatment rule.
- Replace `Acceptance under CRA Recital 55` with neutral wording such as `Acceptance based on documented product-context and interoperability rationale, pending product-security or legal review`.
- Require any compliance-oriented claim to be traceable to product scope, intended use, deployment assumptions, and an approving role.

### 3. STRIDE-to-CVSS mappings should remain guidance, not a formula

The current mappings are useful, but direct STRIDE-to-CVSS translation can overfit examples. Repudiation, spoofing, and elevation of privilege often need scenario-specific impact analysis.

Recommended rule:

- Treat STRIDE-to-CVSS mappings as defaults requiring confirmation from the modeled asset, trust boundary, and consequence chain.
- Require justification when the mapping uses secondary or subsequent-system impact metrics.
- For low-confidence mappings, prefer `Needs Investigation` over a fully populated score.

### 4. Threat actor ordering is not always linear

The minimum-capable actor concept is strong, but strict capability ordering can obscure cases where motivation and access dominate skill.

Recommended rule:

- Retain the minimum-capable actor rule.
- Add a caveat that physical access does not automatically imply `Insider Threat`; it can also represent contractor, opportunistic physical attacker, or vendor-maintenance misuse depending on evidence.
- Require the justification to explain both access path and motivation when the actor is elevated above the least capable plausible class.

## Defensibility risks in sample maps

### Rows 1-4: Modbus RTU acceptance language

Concern: The rows describe protocol weaknesses as inherent and repeatedly justify `Acceptance under CRA Recital 55`. This can read as a compliance conclusion rather than a product-security decision.

Suggested adjustment:

- Replace the CRA-specific phrase with product-context acceptance language.
- Ensure each row identifies the actual approving role, mechanism, and deployment assumption.
- Distinguish implemented exposure-reducing controls from the residual accepted weakness.

### Rows 5-6: JTAG avoidance with mitigated state

Concern: The rows use `Risk Treatment = Avoidance` for burning fuse bits or disabling JTAG while retaining `State = Mitigated`. This undercuts the difference between eliminating a risk source and reducing its exploitability.

Suggested adjustment:

- If JTAG is disabled in production, use a state/rationale pattern that indicates structural removal.
- If JTAG remains present but protected by enclosure, lock bits, or secure boot, keep `State = Mitigated` and use `Risk Treatment = Mitigation`.

### Row 8: removable-media avoidance

Concern: Permanent removal of removable-media support is avoidance, but the row also describes firmware validation controls. The example mixes design elimination with compensating controls.

Suggested adjustment:

- Split the example into either `Mitigation` with validation and administrative disablement, or `Avoidance` with a documented production design decision removing the feature.

### Rows 10-11: Not Applicable with retained identifiers

Concern: A `Not Applicable` row should not normally carry positive ATT&CK, EMB3D, or CWE identifiers. This weakens downstream analytics and may inflate mapping counts.

Suggested adjustment:

- Use `N/A` for dedicated mapping fields when the threat path is rejected.
- Move candidate or alternative mappings into the justification only when they explain why the row was rejected or superseded.

### Row 12: repudiation acceptance

Concern: The row asserts acceptance under CRA language for a protocol logging limitation. Repudiation may still require system-level controls such as gateway logs, PLC-side audit trails, signed engineering changes, or historian correlation.

Suggested adjustment:

- Do not state that the threat cannot be mitigated at the protocol layer as a complete treatment conclusion.
- Record whether compensating system-level evidence exists. If not, keep the row in `Needs Investigation` or require explicit acceptance approval.

## Proposed validation checks

A generated CSV should fail validation when any of the following conditions are true:

1. A populated CVSS vector lacks a score or severity.
2. A score is present but does not match the expected decimal format.
3. `State = Not Applicable` and ATT&CK, EMB3D, or CWE columns contain concrete identifiers without justification explaining why a valid mapping remains applicable.
4. `Risk Treatment = Avoidance` and the justification does not identify the eliminated interface, data flow, feature, or design element.
5. `Risk Treatment = Acceptance` and the justification lacks an approval mechanism or owner role.
6. `State = Mitigated` and the justification does not identify a confirmed control and residual exposure.
7. CRA, IEC 62443, ISO, GDPR, or other compliance language is used as a conclusion rather than as traceability context.
8. A row marked `Needs Investigation` contains final approval or treatment language.
9. A row marked `Not Started` contains enrichment values.
10. A CSV row cannot round-trip through a semicolon-delimited parser with quoted fields preserved.

## Preferred next patch to `SKILL.md`

1. Add a compact validation subsection under `4.3. Deliverables`.
2. Add an allowed-combinations table for `State`, `Risk Treatment`, and `Risk Approval` under `5.2.7`.
3. Replace deterministic CRA sample wording with neutral product-context acceptance language.
4. Normalize sample CVSS score formatting to the documented decimal convention.
5. Convert positive mappings in `Not Applicable` rows to `N/A`, unless the skill explicitly introduces separate rejected-candidate mapping columns.
