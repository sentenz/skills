# Analysis Guidance

Analytical requirements for assessment context, native TMT evidence, framework enrichment, and row disposition. [Mapping Rules](mapping-rules.md) owns the classification and decision tables; [Artifact Contract](artifact-contract.md) and [Justification Templates](justification-template.md) own output requirements. Sequencing and tool invocation belong to [SKILL.md](../SKILL.md).

- [1. Assessment Context](#1-assessment-context)
- [2. Architecture and Native Row Evidence](#2-architecture-and-native-row-evidence)
- [3. ATT&CK for ICS](#3-attck-for-ics)
- [4. EMB3D Threat Mapping](#4-emb3d-threat-mapping)
- [5. TMT State](#5-tmt-state)
- [6. TMT Priority](#6-tmt-priority)
- [7. Residual Risk](#7-residual-risk)
- [8. References](#8-references)

## 1. Assessment Context

Use the assessment to identify threats and mitigations before exploitation, quantify remaining risk after controls and design changes, and produce evidence for engineering review, product-security governance, and compliance-oriented technical documentation. Ground likelihood, impact, and prioritization in architecture, attack paths, asset characteristics, and verified controls. Link treatment to inherent prioritization, residual risk, controls, ownership, and approval evidence. Use ATT&CK for ICS and EMB3D to relate adversary behavior and embedded-device threats to the modeled architecture.

Record why the assessment is being performed and what product/system boundary it covers.

- Identify whether the review is for EU CRA-aligned product risk assessment, general OT/ICS design review, supplier assurance, or another objective.
- Record the assessed product or device boundary. State whether enclosures, companion software, gateways, workstations, installation components, and operator procedures are inside or outside that boundary.
- Record product name, intended use, deployment context, operational environment, trust boundaries, assumptions, exclusions, external dependencies, maintenance paths, and engineering interfaces.

For product cybersecurity compliance, produce traceable risk-assessment evidence that can support EU CRA-style technical documentation without making unsupported legal compliance claims.

## 2. Architecture and Native Row Evidence

Treat the Microsoft TMT CSV as the primary artifact and source of record for the native threat-row inventory.

- Use Microsoft TMT model files (`*.tm7`), Mermaid diagrams, and external documentation as architecture evidence for trust boundaries, interfaces, attack paths, and control coverage.
- Do not silently choose one source as globally authoritative.
- Do not rename components, alter trust boundaries, reorder data flows, or change interface labels when normalizing TM7 display labels.

Use TMT's STRIDE enumeration as the starting point, not as the final analytical decision. Architecture diagrams support identification of missing or misrepresented interfaces, trust boundaries, and attack paths; they do not replace the native TMT row inventory.

Interpret all native TMT fields as a single unit.

- Interpret `Title` together with `Description`.
- Use `Category` as the STRIDE anchor.
- Use `Interaction` to determine attack vector, trust relationship, and applicable controls.
- Use `Priority` and `State` only as initial TMT signals.
- Classify each confirmed control by its enforcement point using [Control Classification and EMB3D Mitigations](mapping-rules.md#6-control-classification-and-emb3d-mitigations).
- When the assessment objective is compliance-oriented, treat each row as a traceable product risk statement tied to a concrete interface, trust relationship, or maintenance path.

Classify each connection by path (`Direct` or `Indirect`), type (`Logical` or `Physical`), and target (`Device` or `Network`) using [Connection-Path Scope Classification](mapping-rules.md#1-connection-path-scope-classification). Determine whether each connection is in-scope or out-of-scope for the modeled threat. Evaluate confidentiality, integrity, and availability using [CIA Impact Reference](mapping-rules.md#2-cia-impact-reference), and classify assets and validate their zone-specific exposure using [Purdue Model Mapping](mapping-rules.md#4-purdue-model-mapping). Apply [STRIDE Classification](mapping-rules.md#5-stride-classification) to TMT `Category`; do not infer STRIDE from ATT&CK, EMB3D, or CWE mappings, or infer a TMT `Category` solely from a Purdue zone.

## 3. ATT&CK for ICS

ATT&CK for ICS provides an adversary-behavior taxonomy, technique-specific mitigation relationships, and detection strategies and analytics for enrichment, control derivation, and telemetry requirements.

Populate `ATT&CK ID` only when a concrete active ATT&CK for ICS technique matches the adversary behavior described by the TMT row and architecture evidence.

- Record the most relevant technique ID(s) in `ATT&CK ID`.
- Use `N/A` when no ICS-specific ATT&CK technique applies to a finalized row.

Validate every selected technique against the active, non-revoked, non-deprecated technique set in the pinned asset.

## 4. EMB3D Threat Mapping

Populate `EMB3D TID` when the modeled asset is, contains, or depends on an embedded device such as a PLC, PAC, RTU, SIS controller, HMI appliance, gateway, edge node, drive, intelligent sensor, actuator, embedded communication module, firmware path, maintenance port, removable-media path, or device-identity mechanism.

- Use EMB3D in addition to ATT&CK when evidence supports both. Do not use EMB3D as a substitute for ATT&CK for ICS.
- Record matched TID(s) in `EMB3D TID`.
- Use `N/A` when no EMB3D threat mapping applies to a finalized row.

Treat `resolved: false` properties as evidence gaps. Apply [Control Classification and EMB3D Mitigations](mapping-rules.md#6-control-classification-and-emb3d-mitigations) to control and implementation claims.

## 5. TMT State

Revise `State` using the full analytical context: TMT row, ATT&CK technique, EMB3D exposure, CWE weakness, CVSS severity, inherent risk prioritization, and threat actor.

| State | Use When |
| --- | --- |
| `Not Started` | Row has not yet been reviewed. |
| `Not Applicable` | Attack path is architecturally impossible, outside scope, or structurally eliminated. |
| `Mitigated` | Confirmed implemented controls, compensating controls, or design changes reduce risk to an accepted level. |
| `Needs Investigation` | Critical evidence is missing or a key assumption cannot be validated. |

State-specific narrative evidence is defined in [Justification Templates](justification-template.md); field handling is defined in [Field Resolution](artifact-contract.md#3-field-resolution).

Do not use `Not Applicable` to downgrade a real weakness that merely has compensating controls, environmental restrictions, or an accepted residual risk.

## 6. TMT Priority

Revise `Priority` using `Risk Prioritization` as the primary signal and adjust only when modeled context provides a specific reason to deviate.

| Priority | Meaning                                                                      |
| -------- | ---------------------------------------------------------------------------- |
| `Low`    | Minimal concern. No immediate action required, monitor for changes.          |
| `Medium` | Mitigation planning should be initiated and tracked in the security backlog. |
| `High`   | Significant threat requiring prompt mitigation and possible escalation.      |

## 7. Residual Risk

Assess residual risk for `Justification`.

- Use one of `None`, `Info`, `Low`, `Medium`, `High`, or `Critical`.
- For `Not Applicable`, record `None` when the attack path is structurally eliminated or outside scope.
- For `Mitigated`, record the remaining risk after confirmed implemented controls, compensating controls, environmental constraints, or design changes are applied.
- For `Needs Investigation` or unresolved rows, leave blank and record the evidence gap in `Justification`.
- Do not use residual risk to lower `CVSS-B v4.0 Score`, `CVSS v4.0 Severity`, or `Risk Prioritization`.

## 8. References

- Microsoft [Threat Modeling Tool](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool) documentation.
- Microsoft [Threat Modeling Fundamentals](https://learn.microsoft.com/en-us/training/paths/tm-threat-modeling-fundamentals/) training.
- STRIDE [Threat Modeling](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats) guide.
- MITRE [ATT&CK for ICS](https://attack.mitre.org/matrices/ics/) matrix.
- MITRE [CWE](https://cwe.mitre.org/) page.
- MITRE [EMB3D](https://emb3d.mitre.org/) page.
- FIRST [CVSS v4.0 Specification](https://www.first.org/cvss/v4.0/specification-document) page.
- FIRST [CVSS v4.0 Calculator](https://www.first.org/cvss/calculator/4.0) page.
- BSI [Risk Prioritization](https://www.bsi.bund.de/DE/Service-Navi/Abonnements/Newsletter/Buerger-CERT-Abos/Buerger-CERT-Sicherheitshinweise/Risikostufen/risikostufen.html) page.
- IEC [62443](https://www.iec.ch/cyber-security) standards.
