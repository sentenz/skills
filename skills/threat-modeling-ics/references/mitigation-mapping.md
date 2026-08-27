# Cross-Framework Mitigation Mapping

Use this reference after ATT&CK for ICS, EMB3D, and CWE mappings have been selected for a threat row and before revising TMT `State`, residual risk, `Risk Treatment`, `Risk Approval`, or `Justification`.

Mitigation mapping converts source-backed framework guidance into row-level candidate controls, then separates applicability, implementation, and validated effect. Framework mitigation guidance is evidence for **what may address a threat**; product evidence is required to establish **what is actually implemented and effective in the assessed design**.

- [1. Source Roles](#1-source-roles)
- [2. Mitigation Evidence States](#2-mitigation-evidence-states)
- [3. Mapping Procedure](#3-mapping-procedure)
- [4. Control-Effect Classification](#4-control-effect-classification)
- [5. Decision Boundaries](#5-decision-boundaries)
- [6. Justification Use](#6-justification-use)

## 1. Source Roles

Treat each source as a different analytical view. Do not collapse framework recommendations into proof of product implementation.

| Source | Mapping Anchor | Mitigation Role | Source Validation | Prohibited Inference |
| ------ | -------------- | --------------- | ----------------- | -------------------- |
| MITRE ATT&CK for ICS | Selected ATT&CK technique in `ATT&CK ID` | Behavior-oriented countermeasure that can prevent, constrain, or otherwise reduce success of the mapped adversary technique. | The bounded ATT&CK query returns an active mitigation through an active `mitigates` relationship to the selected technique. | A technique-to-mitigation relationship does not prove that the assessed product implements the mitigation. |
| MITRE CWE | Selected weakness in `CWE ID` | Root-cause engineering guidance intended to prevent, remove, or reduce the underlying weakness. | The bounded CWE query returns the entry under `potential_mitigations`; preserve phase, strategy, effectiveness, and effectiveness notes when material. | A source-listed potential mitigation does not prove implementation, effectiveness, or residual-risk reduction. |
| MITRE EMB3D | Selected `EMB3D TID` | Embedded-device/property-specific mitigation taxonomy. | The mitigation-centric EMB3D query returns the exact MID name, source level, and association to at least one TID in the row. | A valid MID/TID relationship does not prove implementation or control effectiveness. |
| Product Evidence | TMT row, architecture, design, implementation, configuration, verification, and operational evidence | Establishes whether a candidate mitigation is present in the assessed design and what effect it has on the modeled threat. | Evidence identifies the concrete control, its enforcement point or scope, and the threat condition it changes. | A policy statement, framework recommendation, deployment assumption, or control name alone does not establish implementation or effectiveness. |

> [!IMPORTANT]
> ATT&CK detections are separate from ATT&CK mitigations. A detection relationship or detection strategy is not automatically a preventive mitigation. When detection contributes to the risk posture, classify it as `Detection only` unless separate evidence shows a preventive or constraining effect.

## 2. Mitigation Evidence States

Classify each material mitigation or normalized product control claim using the strongest state supported by evidence.

| Evidence State | Meaning | Minimum Evidence | Permitted Analytical Use |
| -------------- | ------- | ---------------- | ------------------------ |
| `Candidate` | A framework source recommends or associates a mitigation with the mapped technique, weakness, or device threat. | Valid source relationship or source-listed mitigation from the bounded query. | Candidate-control discovery and remediation guidance only. |
| `Applicable` | The candidate mitigation addresses the actual attack path, root weakness, device property, or consequence represented by the row. | Candidate evidence plus architecture/scenario evidence showing relevance to the row. | Control selection and remediation planning. Does not prove implementation. |
| `Implemented` | The assessed product or deployment contains a concrete control corresponding to the applicable mitigation. | Architecture, design, code, configuration, product documentation, or equivalent product-specific evidence identifying the control and enforcement point. | Establishes control presence. Does not by itself prove that the control changes the modeled threat sufficiently to reduce residual risk. |
| `Validated` | Evidence shows that the implemented control materially changes the modeled attack prerequisite, path, exploitability, privilege, impact, detection posture, or recovery capability. | Implementation evidence plus verification, test, analysis, or otherwise defensible evidence of the control effect for the row. | May support `State = Mitigated`, residual-risk reduction, and `Risk Treatment = Mitigation` when the remaining exposure, owner, and approval evidence are also complete. |

Do not skip states by inference. In particular, `Candidate` or `Applicable` must never be described as an applied control, and `Implemented` must not be treated as validated when the effectiveness of the control is material to the decision but unverified.

## 3. Mapping Procedure

Apply this procedure once per reviewed row after ATT&CK, EMB3D, and CWE identifiers are resolved.

1. **Anchor to supported framework mappings.**
   - Use only ATT&CK techniques already supported by the row and architecture evidence.
   - Use only EMB3D TIDs already supported by the device/property evidence.
   - Use only CWE weaknesses already supported under the CWE mapping rules.
   - If a framework mapping is `N/A`, do not invent a mitigation from that framework for the row.

2. **Retrieve bounded source-backed mitigation guidance.**
   - ATT&CK: inspect the selected technique with `uv run ./scripts/query_attack.py --id 'TNNNN' --include mitigations` and accept only active mitigation objects connected by the active `mitigates` relationship returned by the asset.
   - CWE: inspect the selected weakness with `uv run ./scripts/query_cwe.py --id 'CWE-NNN' --include mitigations` and retain relevant `potential_mitigations` attributes such as phase, strategy, effectiveness, and effectiveness notes.
   - EMB3D: inspect the selected threat with `uv run ./scripts/query_emb3d.py --tid 'TID-NNN' --include mitigations`. For a selected mitigation, verify the exact source name, level, and TID associations with `uv run ./scripts/query_emb3d.py --mid 'MID-NNN' --include threats`.

3. **Filter for row-level applicability.**
   Reject source guidance that does not address the concrete interface, trust relationship, attack prerequisite, root weakness, device property, or consequence represented by the row. A generally sound security practice is not automatically applicable mitigation evidence.

4. **Normalize overlapping recommendations into product control claims.**
   Multiple frameworks may recommend conceptually equivalent controls such as authentication, authorization, signed firmware, input validation, network segmentation, or least privilege. Treat the product control as one control claim with multiple source alignments rather than as several independent controls.

5. **Establish implementation evidence.**
   Identify the product-specific control and where it is enforced. Examples include authenticated maintenance mode, authorization checks, signed-update verification, secure-boot verification, protocol input validation, debug-lock configuration, network allowlists, physical interlocks, or tested rate limiting. Do not infer implementation from a framework recommendation.

6. **Establish the control effect.**
   Apply [Control-Effect Classification](#4-control-effect-classification) and state exactly what changes in the modeled scenario. Evidence should identify the affected prerequisite, attack vector, privilege boundary, weakness, consequence, detection path, or recovery path.

7. **Determine remaining exposure.**
   Record what attack path, bypass condition, credential compromise, privileged misuse, physical-access path, downstream effect, detection gap, or recovery limitation remains after the validated control.

8. **Carry the result forward.**
   - Use validated controls and remaining exposure when revising TMT `State`.
   - Use remaining exposure when determining residual risk.
   - Keep CVSS Base severity and `Risk Prioritization` intrinsic and pre-treatment.
   - Use the control evidence, residual risk, owner, and approval evidence when selecting `Risk Treatment` and `Risk Approval`.
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

Keep mitigation mapping, technical state, and governance disposition separate.

- **Mitigation Mapping** answers: Which controls address the mapped threat, which are actually implemented, and what effect is validated?
- **`State = Mitigated`** answers: Do confirmed and validated controls reduce the modeled threat to an accepted residual level?
- **`Risk Treatment = Mitigation`** answers: Is mitigation the governance disposition for the inherent risk, with the required residual-risk ownership and approval evidence?

Apply these constraints:

- Framework guidance at `Candidate` or `Applicable` state cannot support `State = Mitigated`, residual-risk reduction, or a claim that treatment has been implemented.
- An `Implemented` control whose material effect is not established must not be used to lower residual risk. When that uncertainty blocks the state or treatment decision, use `Needs Investigation` under the selected execution mode.
- A `Validated` control may support `State = Mitigated` only when remaining exposure and residual risk are also assessed and the required ownership/approval evidence is available.
- An applicable but unimplemented framework mitigation is remediation guidance or backlog input, not an applied control.
- Multiple framework sources aligning to the same product control increase traceability, not control count or control effectiveness.
- Do not lower `CVSS-B v4.0 Score`, `CVSS v4.0 Severity`, or inherent `Risk Prioritization` solely because a mitigation exists or is implemented.
- Regulation, trusted-environment assumptions, deployment restrictions, organizational policy, or intended-use statements are not standalone technical mitigations. Tie them to enforceable architecture or control evidence when they materially constrain the threat.
- Do not describe detection-only or recovery-only controls as if they remove the root weakness or prevent the attack.

## 6. Justification Use

The final `Justification` should present an evidence chain rather than a framework inventory:

`scenario → framework behavior/weakness/device threat → applicable control → implementation evidence → validated control effect → remaining exposure → residual risk → treatment → approval`

- Lead with the concrete threat scenario and product evidence.
- Mention a framework mitigation only when it materially explains why a control is relevant or why a remediation recommendation was selected.
- Distinguish source-backed recommendations from implemented and validated controls explicitly.
- For ATT&CK mitigation alignment, use the exact mitigation name and identifier returned by the bounded ATT&CK query only when it has an active `mitigates` relationship to a technique in the row.
- For CWE mitigation alignment, prefer the source strategy, phase, or engineering behavior rather than inventing a stable mitigation identifier when the source does not provide one.
- For EMB3D, preserve the existing MID rules: exact source name, exact Foundational/Intermediate/Leading level, and association to at least one TID in the row.
- Do not dump every candidate mitigation into `Justification`; record only evidence that explains state, residual risk, treatment, or a material remediation gap.
