---
name: threat-modeling-ics
description: >-
  Performs end-to-end threat modeling for OT/ICS systems from Microsoft Threat Modeling Tool (TMT) threat-list exports (`*.csv`) and model files (`*.tm7`). Uses TMT and
  STRIDE for initial threat enumeration, then enriches each threat with OT/ICS context, MITRE ATT&CK for ICS mappings, MITRE EMB3D device-property threat enrichment for
  embedded field devices, CWE weakness classification, CVSS v4.0 scoring, Likelihood of Exploit, Risk-based Prioritization via a Risk Matrix, minimum-capable Threat Actor
  assignment, inherent and residual risk traceability, Risk Treatment decisions, and OT impact categories ranging from Denial of View to Physical Damage to Property.
metadata:
  version: "1.7.33"
  python-package: "cvss==3.6"
allowed-tools: Bash(python:*) Bash(uv:*)
---

# Threat Modeling ICS

Authoritative workflow for reviewing Microsoft Threat Modeling Tool (TMT) threat-list exports. Execute every foundation, preparation, review, and deliverable step in order. Do not skip, reorder, or merge steps. Save and integrate intermediate results after each step, and evaluate blocking gates throughout the workflow using the selected execution mode.

- [1. Supporting Responsibilities](#1-supporting-responsibilities)
- [2. Foundation](#2-foundation)
  - [2.1. Field Resolution](#21-field-resolution)
  - [2.2. Execution Mode](#22-execution-mode)
  - [2.3. Mode-aware Blocking Gates](#23-mode-aware-blocking-gates)
  - [2.4. Artifact Hygiene](#24-artifact-hygiene)
  - [2.5. Source of Record](#25-source-of-record)
- [3. Assessment](#3-assessment)
  - [3.1. Preparation](#31-preparation)
  - [3.2. Framework Data Access](#32-framework-data-access)
  - [3.3. Review](#33-review)
- [4. Deliverables](#4-deliverables)

## 1. Supporting Responsibilities

Load only the applicable subsection of Mapping Rules when linked by the current step; do not load the full reference by default.

| Resource | Responsibility | Workflow Use |
| --- | --- | --- |
| [Analysis Guidance](references/analysis-guidance.md) | Assessment context, native-row interpretation, ATT&CK and EMB3D enrichment, state, priority, and residual-risk decisions. | Preparation and the corresponding review steps. |
| [Mapping Rules](references/mapping-rules.md) | Canonical classification, scoring, likelihood, prioritization, actor, treatment, and approval rules. | The linked subsection at each analytical step. |
| [Threat Depth Layers](references/threat-depth-layers.md) | Canonical depth definitions and architecture examples. | Architecture visualization and validation. |
| [Artifact Contract](references/artifact-contract.md) | Input integrity, field resolution, generated CSV, baseline, and summary specifications. | Foundation, preparation, and deliverables. |
| [Justification Templates](references/justification-template.md) | Narrative requirements, state patterns, control and MID citation syntax, and treatment evidence. | Final justification and output validation. |
| [Asset Catalog](assets/README.md) | Dataset versions, provenance, and record authority. | Framework input checks. |
| [Script Catalog](scripts/README.md) | Utility capabilities and output descriptions. | The invocations in this workflow. |
| [Raw Example](references/Example_Threat_Model.csv) and [Generated Example](references/Example_Threat_Model_Generated.csv) | Source and completed output examples. | Preparation's baseline check. |

## 2. Foundation

### 2.1. Field Resolution

Read [Field Resolution](references/artifact-contract.md#3-field-resolution) and apply it throughout the review.

### 2.2. Execution Mode

Select the mode before starting the review. Apply the mode's unresolved-field requirements in [Field Resolution](references/artifact-contract.md#3-field-resolution).

| Execution Mode | Use When | Blocking Gate Behavior |
| --- | --- | --- |
| Strict | The assessment is interactive or compliance-oriented and user clarification is available. | Stop at blocking gates and request the missing decision or evidence. |
| Best-effort | The user explicitly requests unattended analysis, draft output, or partial completion. | Continue only when the unresolved item can be isolated and documented. |
| Batch | Large CSV review requires completion of all rows before discussion. | Mark affected rows `Needs Investigation` and continue with the next row. |

### 2.3. Mode-aware Blocking Gates

Always evaluate the gates. Unattended modes do not permit invented framework mappings, score values, treatment decisions, approval roles, or compliance conclusions.

| Gate Condition | Strict | Best-effort | Batch |
| --- | --- | --- | --- |
| Scope or objective missing | Stop and request scope or objective. | Continue only if the row-level effect is isolated and documented. | Mark affected rows `Needs Investigation` and continue. |
| No architecture source | Stop and request TM7, Mermaid, documentation, or description. | Draft architecture assumptions only when explicitly requested; mark them pending confirmation. | Mark affected rows `Needs Investigation` unless the CSV row alone contains enough architecture evidence. |
| No TMT export CSV | Stop and request the exported TMT CSV. | Stop; the native TMT row inventory cannot be reconstructed safely. | Stop; batch review cannot proceed without the row inventory. |
| Native TMT column missing | Stop and report missing fields. | Continue only if the missing field is not needed for the affected rows; document the limitation. | Mark affected rows `Needs Investigation` when the missing field affects interpretation. |
| Material architecture conflict | Stop and ask whether to review as modeled, documented, or discrepancy. | Document the conflict and review only rows whose interpretation is unaffected. | Mark affected rows `Needs Investigation` and continue with unaffected rows. |
| Framework asset unavailable, inaccessible, stale, or missing | Stop and request updated assets. | Apply [unresolved-field requirements](references/artifact-contract.md#3-field-resolution); mark the row `Needs Investigation` when the missing asset affects the decision. | Mark affected rows `Needs Investigation`, apply [unresolved-field requirements](references/artifact-contract.md#3-field-resolution), and continue with the next row. |
| Approval owner or mechanism missing | Stop when treatment requires approval. | Apply the pending-approval requirements in [Field Resolution](references/artifact-contract.md#3-field-resolution). | Mark affected rows `Needs Investigation` when approval is required for the selected disposition. |

### 2.4. Artifact Hygiene

Apply [Artifact Hygiene](references/artifact-contract.md#2-artifact-hygiene) to all input and generated artifacts.

### 2.5. Source of Record

Establish the source inventory and architecture evidence under [Input Contract](references/artifact-contract.md#1-input-contract) and [Architecture and Native Row Evidence](references/analysis-guidance.md#2-architecture-and-native-row-evidence).

Create a Mermaid diagram from the TM7 model using [Threat Depth Layers](references/threat-depth-layers.md) to visualize the architecture and confirm that the TMT row inventory is complete. Start with the mandatory Layer 0 view. Use the diagram to identify missing or misrepresented interfaces, trust boundaries, and attack paths.

If sources materially conflict about whether an interface, trust boundary, or attack path exists, document the discrepancy and apply the [blocking gates](#23-mode-aware-blocking-gates).

## 3. Assessment

### 3.1. Preparation

1. **Define assessment objective and scope.** Record the assessment context and product boundary required by [Assessment Context](references/analysis-guidance.md#1-assessment-context) before classifying controls.
2. **Check the input contract.** Classify and check the supplied TMT export against [Input Contract](references/artifact-contract.md#1-input-contract).
3. **Establish the output contract.** Read [Generated CSV Contract](references/artifact-contract.md#4-generated-csv-contract).
4. **Check the output baseline.** Read [Example_Threat_Model_Generated.csv](references/Example_Threat_Model_Generated.csv) before row-by-row review. Compare the planned output's column order, delimiter, quoting, score format, and narrative pattern against [Example Baseline](references/artifact-contract.md#7-example-baseline) and its linked requirements. Correct and report any baseline inconsistency before relying on it.
5. **Gather conflicts.** Record architecture-evidence discrepancies that may affect row interpretation and apply the selected execution mode's [blocking gates](#23-mode-aware-blocking-gates).

### 3.2. Framework Data Access

Apply these access constraints when invoking the corresponding review step. Required local ATT&CK, EMB3D, CWE, and CVSS assets are gating inputs under [Mode-aware Blocking Gates](#23-mode-aware-blocking-gates).

- Do not read or print raw ATT&CK, EMB3D, or CWE JSON into model context. Use the bounded query scripts in the review steps; the scripts read the complete datasets in-process.
- Treat the FIRST CVSS schema as programmatic format-validation input. Do not load it during normal row processing or derive scores from it; use the calculator and validators below without adding a schema query layer.
- Run the commands below from the skill directory. The [Script Catalog](scripts/README.md) describes each utility's interface and output.

### 3.3. Review

Perform steps 1–14 for every row before proceeding to [Deliverables](#4-deliverables).

1. **Analyze the native row.** Read all native fields together and apply [Architecture and Native Row Evidence](references/analysis-guidance.md#2-architecture-and-native-row-evidence), including its linked scope, CIA, Purdue, STRIDE, and control-classification rules.

2. **Map ATT&CK for ICS.** Apply [ATT&CK for ICS](references/analysis-guidance.md#3-attck-for-ics).
   - Discover active techniques with `uv run ./scripts/query_attack.py --search '<terms>' --top 5`.
   - Inspect selected IDs with `uv run ./scripts/query_attack.py --id 'TNNNN'`; request `--include description,tactics,platforms,mitigations,detections,relationships` only for one selected ID.

3. **Map EMB3D.** Apply [EMB3D Threat Mapping](references/analysis-guidance.md#4-emb3d-threat-mapping) and [Control Classification and EMB3D Mitigations](references/mapping-rules.md#6-control-classification-and-emb3d-mitigations).
   - Discover threats, properties, and mitigations with `uv run ./scripts/query_emb3d.py --search '<terms>' --top 5`; narrow discovery with `--kind threat`, `--kind property`, or `--kind mitigation` when needed.
   - Inspect one selected identifier with `uv run ./scripts/query_emb3d.py --tid 'TID-NNN'`, `--pid 'PID-NN'`, or `--mid 'MID-NNN'`; request only applicable `--include properties,mitigations,threats,hierarchy` fields.
   - When `Interaction` names JTAG, UART, RS-232, RS-485, SPI, I²C, GPIO, USB, Modbus RTU, proprietary serial, or a firmware update path, cross-reference the EMB3D Properties Mapper before finalizing `EMB3D TID` and `CWE ID`.

4. **Map CWE.** Apply [MITRE CWE Mapping Rules](references/mapping-rules.md#13-mitre-cwe-mapping-rules).
   - Discover candidates with `uv run ./scripts/query_cwe.py --search '<terms>' --top 5`.
   - Inspect selected IDs with `uv run ./scripts/query_cwe.py --id 'CWE-NNN'`; request `--include description,mapping-notes,related,mitigations` only for one selected ID.

5. **Calculate CVSS v4.0.** Apply [Impact Mapping](references/mapping-rules.md#7-impact-mapping) and its exploitability, vulnerable-system, and subsequent-system metric tables. Populate the CVSS fields under [Generated CSV Contract](references/artifact-contract.md#4-generated-csv-contract).
   - Run `uv run ./scripts/calculate_cvss.py --vector '<CVSS:4.0/...>'` to compute the Base score and severity using the [CVSS v4.0 calculator](https://www.first.org/cvss/calculator/4.0) methodology.

6. **Determine likelihood of exploit.** Apply [Probability Mapping](references/mapping-rules.md#8-probability-mapping): classify the exploitation method, classify the vulnerability state, then combine them using the likelihood matrix.

7. **Determine inherent risk prioritization.** Apply [Risk Matrix Mapping](references/mapping-rules.md#9-risk-matrix-mapping).

8. **Assign the threat actor.** Apply [Capability Boundaries](references/mapping-rules.md#101-capability-boundaries) and [Scenario Mapping](references/mapping-rules.md#102-scenario-mapping).

9. **Revise TMT state.** Apply [TMT State](references/analysis-guidance.md#5-tmt-state).

10. **Revise TMT priority.** Apply [TMT Priority](references/analysis-guidance.md#6-tmt-priority).

11. **Assess residual risk.** Apply [Residual Risk](references/analysis-guidance.md#7-residual-risk) after revising state and priority and before selecting governance treatment.

12. **Select risk treatment.** Apply [Treatment Semantics](references/mapping-rules.md#111-treatment-semantics), select the default or evidence-supported alternative under [Treatment Decision Guidance](references/mapping-rules.md#112-treatment-decision-guidance), verify [State and Treatment Compatibility](references/mapping-rules.md#113-state-and-treatment-compatibility), and record [Treatment Evidence](references/justification-template.md#8-treatment-evidence).

13. **Determine risk approval.** Apply [Risk Approval Mapping](references/mapping-rules.md#12-risk-approval-mapping).

14. **Write the TMT justification.** After steps 1–13, read [Justification Templates](references/justification-template.md), select the pattern for the final state, and write the narrative under its universal and treatment-specific requirements.

## 4. Deliverables

1. **Generate and validate the CSV.** Validate analyst decisions against [Decision Consistency](references/artifact-contract.md#5-decision-consistency), then write the artifact specified by [Generated CSV Contract](references/artifact-contract.md#4-generated-csv-contract). Verify each output row against its source row.
   - Run `uv run ./scripts/validate_csv.py --source '<Device_Name>_Threat_Model.csv' --artifact '<Device_Name>_Threat_Model_Generated.csv'` for complete CSV, active ATT&CK, mappable CWE, control terminology, cited EMB3D mitigation, and source-traceability checks with actual-versus-expected findings.
   - Run `uv run ./scripts/validate_cvss.py --csv '<Device_Name>_Threat_Model_Generated.csv'` to validate all CVSS vectors and compare calculated and stored scores.
2. **Write the review summary.** Produce the Markdown artifact specified by [Review Summary](references/artifact-contract.md#6-review-summary).
