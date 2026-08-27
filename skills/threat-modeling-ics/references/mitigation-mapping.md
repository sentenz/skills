# Cross-Framework Mitigation Mapping

Use this reference after ATT&CK for ICS, EMB3D, and CWE mappings have been selected or explicitly resolved as `N/A`, and before revising TMT `State`, residual risk, `Risk Treatment`, `Risk Approval`, or `Justification`.

Mitigation mapping keeps two evidence dimensions separate: framework provenance identifies **what a source recommends for the mapped threat**, while product evidence establishes **what is actually implemented and what effect is validated in the assessed design**. Framework alignment strengthens traceability but is not a prerequisite for recognizing an independently evidenced product control.

- [1. Source Roles](#1-source-roles)
- [2. Mitigation Evidence Model](#2-mitigation-evidence-model)
- [3. Mapping Procedure](#3-mapping-procedure)
- [4. Control-Effect Classification](#4-control-effect-classification)
- [5. Decision Boundaries](#5-decision-boundaries)
- [6. Justification Use](#6-justification-use)

## 1. Source Roles

Treat each source as a different analytical view. Do not collapse framework recommendations into proof of product implementation, and do not treat missing framework alignment as evidence that a product control is absent.

| Source | Mapping Anchor | Mitigation Role | Source Validation | Prohibited Inference |
| ------ | -------------- | --------------- | ----------------- | -------------------- |
| MITRE ATT&CK for ICS | Selected ATT&CK technique in `ATT&CK ID` | Behavior-oriented countermeasure that can prevent, constrain, or otherwise reduce success of the mapped adversary technique. | The bounded ATT&CK query returns an active mitigation through an active `mitigates` relationship to the selected technique. | A technique-to-mitigation relationship does not prove that the assessed product implements the mitigation. |
| MITRE CWE | Selected weakness in `CWE ID` | Root-cause engineering guidance intended to prevent, remove, or reduce the underlying weakness. | The bounded CWE query returns the entry under `potential_mitigations`; preserve phase, strategy, effectiveness, and effectiveness notes when material. | A source-listed potential mitigation does not prove implementation, effectiveness, or residual-risk reduction. |
| MITRE EMB3D | Selected `EMB3D TID` | Embedded-device/property-specific mitigation taxonomy. | The mitigation-centric EMB3D query returns the exact MID name, source level, and association to at least one TID in the row. | A valid MID/TID relationship does not prove implementation or control effectiveness. |
| Product Evidence | TMT row, architecture, design, implementation, configuration, verification, and operational evidence | Independently establishes concrete product or deployment controls and their effect on the modeled threat, with or without framework alignment. | Evidence identifies the concrete control, its enforcement point or scope, and the threat condition it changes. | A policy statement, framework recommendation, deployment assumption, or control name alone does not establish implementation or effectiveness. Absence of a framework recommendation does not invalidate otherwise sufficient product evidence. |

> [!IMPORTANT]
> ATT&CK detections are separate from ATT&CK mitigations. A detection relationship or detection strategy is not automatically a preventive mitigation. When detection contributes to the risk posture, classify it as `Detection only` unless separate evidence shows a preventive or constraining effect.

## 2. Mitigation Evidence Model

Track framework guidance provenance separately from product-control implementation evidence. The familiar `Candidate` → `Applicable` → `Implemented` → `Validated` progression applies when a product control is derived from framework guidance, but the first two states are not prerequisites for independently identified product controls.

### 2.1. Framework Guidance State

| Guidance State | Meaning | Minimum Evidence | Permitted Analytical Use |
| -------------- | ------- | ---------------- | ------------------------ |
| `Candidate` | A framework source recommends or associates a mitigation with the mapped technique, weakness, or device threat. | Valid source relationship or source-listed mitigation from the bounded query. | Candidate-control discovery and remediation guidance only. |
| `Applicable` | The candidate guidance addresses the actual attack path, root weakness, device property, or consequence represented by the row. | Candidate evidence plus architecture/scenario evidence showing relevance to the row. | Control selection, framework alignment, and remediation planning. Does not prove implementation. |

### 2.2. Product Control State

| Control State | Meaning | Minimum Evidence | Permitted Analytical Use |
| ------------- | ------- | ---------------- | ------------------------ |
| `Implemented` | The assessed product or deployment contains a concrete control relevant to the row. The control may align to framework guidance or may be independently evidenced. | Architecture, design, code, configuration, product documentation, or equivalent product-specific evidence identifying the control and enforcement point. | Establishes control presence. Does not by itself prove that the control changes the modeled threat sufficiently to reduce residual risk. |
| `Validated` | Evidence shows that the implemented control materially changes the modeled attack prerequisite, path, exploitability, privilege, impact, detection posture, or recovery capability. | Implementation evidence plus verification, test, analysis, or otherwise defensible evidence of the control effect for the row. | May support `State = Mitigated` and later residual-risk reduction or `Risk Treatment = Mitigation` when the remaining exposure and treatment evidence are complete. |

Do not promote evidence by inference. In particular, `Candidate` or `Applicable` guidance must never be described as an applied control, and `Implemented` must not be treated as `Validated` when the effectiveness of the control is material to the decision but unverified. Conversely, an independently evidenced product control may be classified `Implemented` or `Validated` without inventing an ATT&CK, CWE, or EMB3D recommendation.

## 3. Mapping Procedure

Apply this procedure once per reviewed row after ATT&CK, EMB3D, and CWE identifiers are resolved.

1. **Anchor available framework mappings.**
   - Use only ATT&CK techniques already supported by the row and architecture evidence.
   - Use only EMB3D TIDs already supported by the device/property evidence.
   - Use only CWE weaknesses already supported under the CWE mapping rules.
   - If a framework mapping is `N/A`, do not invent a mitigation from that framework for the row. Continue assessing product controls independently.

2. **Retrieve bounded source-backed mitigation guidance where a framework mapping exists.**
   - ATT&CK: inspect the selected technique with `uv run ./scripts/query_attack.py --id 'TNNNN' --include mitigations` and accept only active mitigation objects connected by the active `mitigates` relationship returned by the asset.
   - CWE: inspect the selected weakness with `uv run ./scripts/query_cwe.py --id 'CWE-NNN' --include mitigations` and retain relevant `potential_mitigations` attributes such as phase, strategy, effectiveness, and effectiveness notes.
   - EMB3D: inspect the selected threat with `uv run ./scripts/query_emb3d.py --tid 'TID-NNN' --include mitigations`. For a selected mitigation, verify the exact source name, level, and TID associations with `uv run ./scripts/query_emb3d.py --mid 'MID-NNN' --include threats`.

3. **Inventory product-specific controls independently.**
   Identify controls already present in the assessed design or deployment from architecture, design, implementation, configuration, verification, or operational evidence. Do this even when no framework mitigation is available or applicable.

4. **Filter framework guidance for row-level applicability.**
   Reject source guidance that does not address the concrete interface, trust relationship, attack prerequisite, root weakness, device property, or consequence represented by the row. A generally sound security practice is not automatically applicable mitigation guidance.

5. **Normalize alignments into product control claims.**
   Multiple frameworks may recommend conceptually equivalent controls such as authentication, authorization, signed firmware, input validation, network segmentation, or least privilege. Treat the product control as one control claim with zero, one, or multiple source alignments rather than as several independent controls.

6. **Establish implementation evidence.**
   Identify the product-specific control and where it is enforced. Examples include authenticated maintenance mode, authorization checks, signed-update verification, secure-boot verification, protocol input validation, debug-lock configuration, network allowlists, physical interlocks, or tested rate limiting. Do not infer implementation from a framework recommendation.

7. **Establish the control effect.**
   Apply [Control-Effect Classification](#4-control-effect-classification) and state exactly what changes in the modeled scenario. Evidence should identify the affected prerequisite, attack vector, privilege boundary, weakness, consequence, detection path, or recovery path.

8. **Determine remaining exposure.**
   Record what attack path, bypass condition, credential compromise, privileged misuse, physical-access path, downstream effect, detection gap, or recovery limitation remains after the validated control.

9. **Carry the result forward.**
   - Use validated product controls and remaining exposure when revising TMT `State`.
   - Quantify residual risk in the later residual-risk step; do not require that later field to be populated while setting `State`.
   - Keep CVSS Base severity and `Risk Prioritization` intrinsic and pre-treatment.
   - Use the control evidence and residual risk when selecting `Risk Treatment`; complete ownership and approval evidence in their designated later steps.
   - Include only decision-relevant mitigation evidence in `Justification` and the summary.

> [!NOTE]
> Mitigation mapping is row-level analytical evidence and does not add a dedicated generated-CSV column. The material result is carried into `State`, residual risk, treatment, approval, `Justification`, and the review summary.

## 4. Control-Effect Classification

Use the most specific effect supported by the evidence. Multiple effects may apply when independently supported.

| Effect | Meaning | Example Evidence |
| ------ | ------- | ---------------- |
| `Prerequisite eliminated` | A required condition for the threat no longer exists. | Debug interface physically removed, vulnerable function removed, unauthenticated service eliminated. |
| `Attack vector constrained` | The path remains but reachable sources, interfaces, network segments, or physical access conditions are narrowed. | Network allowlist, segmentation boundary, cabinet access control, maintenance-jump-host restriction. |
| `Privilege constrained` | Authentication, authorization, least privilege, or execution policy prevents the modeled actor from performing the protected action without additional compromise. | Role check before configuration change, authenticated maintenance session, privilege-separated service. |
| `Exploitation prevented` | The root weakness or exploit condition is removed or reliably rejected. | Bounds validation, signed-update verification, anti-rollback enforcement, parser hardening, memory-protection enforcement. |
| `Impact contained` | Exploitation may remain possible but propagation or consequence is bounded. | Process isolation, fail-safe limit, safety interlock, blast-radius segmentation. |
| `Detection only` | The control provides evidence or alerting after or during attempted behavior but does not itself prevent the modeled action. | Audit logging, anomaly detection, IDS rule, command monitoring. |
| `Recovery only` | The control restores operation or integrity after compromise but does not prevent initial exploitation. | Known-good restore, recovery image, resilient backup, tested re-provisioning procedure. |

Detection and recovery can be material to residual risk, but their effect must be described precisely. Do not re-label them as prevention or root-cause remediation.

## 5. Decision Boundaries

Keep mitigation mapping, technical state, residual-risk assessment, and governance disposition separate.

- **Mitigation Mapping** answers: Which product controls address the modeled threat, what framework guidance aligns to them, which controls are implemented, and what effect is validated?
- **`State = Mitigated`** answers: Do validated product controls materially reduce the modeled threat, with the remaining exposure identified? This technical decision is made before residual risk, treatment, and approval are populated.
- **Residual Risk** answers: What risk remains after the validated controls and identified remaining exposure are considered?
- **`Risk Treatment = Mitigation`** answers: Is mitigation the governance disposition for the inherent risk, with the required residual-risk ownership and approval evidence?

Apply these constraints:

- Framework guidance at `Candidate` or `Applicable` state cannot support `State = Mitigated`, residual-risk reduction, or a claim that treatment has been implemented.
- A product control does not require ATT&CK, CWE, or EMB3D alignment to be `Implemented` or `Validated`; framework provenance is optional supporting traceability.
- An `Implemented` control whose material effect is not established must not be used to lower residual risk. When that uncertainty blocks the technical state or later treatment decision, apply `Needs Investigation` under the selected execution mode.
- A `Validated` control may support `State = Mitigated` when its effect and the remaining exposure are established. Residual risk, treatment, ownership, and approval are completed in their later workflow steps and must not be treated as prerequisites for the earlier state decision.
- An applicable but unimplemented framework mitigation is remediation guidance or backlog input, not an applied control.
- Multiple framework sources aligning to the same product control increase traceability, not control count or control effectiveness.
- Do not lower `CVSS-B v4.0 Score`, `CVSS v4.0 Severity`, or inherent `Risk Prioritization` solely because a mitigation exists or is implemented.
- Regulation, trusted-environment assumptions, deployment restrictions, organizational policy, or intended-use statements are not standalone technical mitigations. Tie them to enforceable architecture or control evidence when they materially constrain the threat.
- Do not describe detection-only or recovery-only controls as if they remove the root weakness or prevent the attack.
- If a later residual-risk, treatment, or approval step reveals an unresolved contradiction that prevents row finalization, apply the mode-aware blocking behavior rather than inventing evidence or retroactively treating framework guidance as validation.

## 6. Justification Use

The final `Justification` should present an evidence chain rather than a framework inventory:

`scenario → optional framework guidance/alignment → product control → implementation evidence → validated control effect → remaining exposure → residual risk → treatment → approval`

- Lead with the concrete threat scenario and product evidence.
- Mention a framework mitigation only when it materially explains why a control is relevant or why a remediation recommendation was selected.
- Framework alignment is optional for an implemented or validated product control. Do not invent an ATT&CK, CWE, or EMB3D mitigation merely to complete the evidence chain.
- Distinguish source-backed recommendations from implemented and validated controls explicitly.
- For ATT&CK mitigation alignment, use the exact mitigation name and identifier returned by the bounded ATT&CK query only when it has an active `mitigates` relationship to a technique in the row.
- For CWE mitigation alignment, prefer the source strategy, phase, or engineering behavior rather than inventing a stable mitigation identifier when the source does not provide one.
- For EMB3D, preserve the existing MID rules: exact source name, exact Foundational/Intermediate/Leading level, and association to at least one TID in the row.
- Do not dump every candidate mitigation into `Justification`; record only evidence that explains state, residual risk, treatment, or a material remediation gap.
