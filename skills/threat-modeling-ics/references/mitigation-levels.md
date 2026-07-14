# Mitigation Levels

- [1. Purpose](#1-purpose)
- [2. Canonical Values](#2-canonical-values)
- [3. Selection Rules](#3-selection-rules)
- [4. Separation of Concerns](#4-separation-of-concerns)
- [5. Evidence Requirements](#5-evidence-requirements)
- [6. Examples](#6-examples)
- [7. References](#7-references)

## 1. Purpose

This document defines the mitigation-level convention used by the `threat-modeling-ics` skill.

There is no universal, framework-independent convention named **Mitigation Levels**. Similar labels in security frameworks classify different properties, such as control baselines, assurance depth, implementation groups, or technology maturity. This skill therefore uses a local reporting convention while preserving MITRE EMB3D terminology exactly.

> [!IMPORTANT]
> `Baseline` is a skill-specific label and is **not** a MITRE EMB3D tier. MITRE EMB3D defines only `Foundational`, `Intermediate`, and `Leading` mitigation tiers.

The values classify the controls that are confirmed to mitigate a threat row. They do not, by themselves, indicate implementation status, control effectiveness, residual risk, risk treatment, or approval status.

## 2. Canonical Values

| Value | Meaning | Assignment Rule |
| ----- | ------- | --------------- |
| Blank | The mitigation evidence is unresolved or the row has not been reviewed. | Leave blank for `Not Started`, `Needs Investigation`, or evidence-gated rows. |
| `N/A` | No mitigation classification applies because the threat path is structurally eliminated, outside scope, or otherwise not applicable. | Use only with `State = Not Applicable` and normally `Risk Treatment = Avoidance`. |
| `Baseline` | A confirmed minimum, common, compensating, environmental, or operational control materially reduces the threat, but the control is not being claimed as an implemented EMB3D mitigation. | Use for controls such as protected deployment boundaries, physical access restrictions, segmentation, monitoring, backup, fail-safe behavior, or generic validation when no evidenced EMB3D MID is assigned. |
| `Foundational` | One or more confirmed MITRE EMB3D Tier 0 mitigations materially address the mapped EMB3D threat. | Assign only from implemented and evidenced EMB3D mitigation records whose `level` is `foundational`. |
| `Intermediate` | One or more confirmed MITRE EMB3D Tier 1 mitigations materially address the mapped EMB3D threat. | Assign only from implemented and evidenced EMB3D mitigation records whose `level` is `intermediate`. |
| `Leading` | One or more confirmed MITRE EMB3D Tier 2 mitigations materially address the mapped EMB3D threat. | Assign only from implemented and evidenced EMB3D mitigation records whose `level` is `leading`. |

The canonical display order is:

`Baseline` → `Foundational` → `Intermediate` → `Leading`

This ordering is for consistent reporting. It must not be interpreted as a universal assurance scale. In particular, a `Baseline` control may be operational or environmental, while EMB3D tiers describe mitigation maturity and implementation difficulty for device-integrated security mechanisms.

## 3. Selection Rules

1. Identify the controls that materially address the modeled attack path.
2. Record only controls that are confirmed implemented or otherwise evidenced for the assessed product or deployment. Record planned or recommended controls in `Justification` or the summary, not in `Mitigation Level`.
3. Use `Baseline` when confirmed controls reduce the threat but no implemented EMB3D mitigation is being claimed.
4. Use `Foundational`, `Intermediate`, or `Leading` only when the applicable EMB3D mitigation identifier and its official `level` are confirmed from the local EMB3D assets.
5. When implemented mitigations span multiple EMB3D tiers:
   - Record all materially contributing levels, comma-separated in canonical order, when the mitigations are complementary.
   - Record only the implemented higher tier when it demonstrably supersedes the lower-tier mitigation, and document the supersession in `Justification`.
6. Do not assume that a higher EMB3D tier automatically includes lower-tier coverage. Higher-tier mitigations may complement or replace lower-tier mitigations depending on the threat and design.
7. Use `N/A` only when the finalized threat row is `Not Applicable`. Do not use `N/A` merely because mitigation has not been implemented.
8. Leave the field blank when evidence is missing, the row is unresolved, or the applicable mitigation cannot be verified.

## 4. Separation of Concerns

| Field or Concept | Question Answered |
| ---------------- | ----------------- |
| `Mitigation Level` | What category or EMB3D tier is represented by the confirmed controls? |
| Implementation status | Is the control proposed, planned, implemented, or verified? |
| Control effectiveness | How completely does the control interrupt the modeled attack path? |
| Residual risk | What risk remains after the confirmed controls are applied? |
| `Risk Treatment` | Is the risk avoided, mitigated, accepted, or transferred? |
| `Risk Approval` | Which role must approve the resulting disposition? |

A row may therefore record `Mitigation Level = Foundational` while retaining `Residual Risk = High`, or record `Risk Treatment = Acceptance` after baseline controls reduce exposure but do not eliminate the risk.

## 5. Evidence Requirements

For each populated mitigation level, `Justification` should identify:

- The implemented control or security mechanism.
- The architecture element, interface, or attack-path segment protected by the control.
- The implementation or verification evidence.
- The applicable EMB3D MID when an EMB3D tier is recorded.
- Whether multiple mitigations are complementary or whether a higher-tier mitigation supersedes a lower-tier mitigation.
- The remaining exposure and residual risk.

Do not infer an EMB3D tier from a control name alone. Confirm the MID-to-level mapping in:

- [`assets/emb3d/mitigations_threat_mappings_2.0.1.json`](../assets/emb3d/mitigations_threat_mappings_2.0.1.json)
- [`assets/emb3d/threats_properties_mitigations_mappings_2.0.1.json`](../assets/emb3d/threats_properties_mitigations_mappings_2.0.1.json)

## 6. Examples

| Scenario | Mitigation Level | Rationale |
| -------- | ---------------- | --------- |
| An isolated RS-485 segment, locked cabinet, and PLC fail-safe behavior reduce exposure, with no device-integrated EMB3D mitigation claimed. | `Baseline` | Confirmed environmental and operational controls reduce the threat. |
| Production JTAG is disabled using MID-057. | `Foundational` | MID-057 is an EMB3D Foundational mitigation. |
| Hardware-backed bootloader authentication using MID-002 replaces software-only bootloader authentication for the same protection objective. | `Intermediate` | The implemented Intermediate mitigation supersedes the lower-tier mechanism. |
| MID-057 disables production debug access and an Intermediate hardware isolation control protects a separate portion of the same threat. | `Foundational, Intermediate` | The controls are complementary and both materially contribute. |
| A suggested secure tunnel is not yet implemented. | Blank | Planned controls are recommendations, not confirmed mitigation evidence. |
| The modeled spoofing path has no identity-bearing endpoint and is structurally inapplicable. | `N/A` | No mitigation classification is required for an avoided, non-applicable threat. |

## 7. References

- MITRE EMB3D [Mitigations](https://emb3d.mitre.org/mitigations/) catalog.
- MITRE, [The EMB3D Threat Model for Embedded Devices](https://emb3d.mitre.org/assets/EMB3D_Paper_09-23-24.pdf), section 3.3.2, Mitigation Tiers.
- NIST [Security Control Baseline](https://csrc.nist.gov/glossary/term/security_control_baseline) glossary definition.
- NIST SP 800-53B, [Control Baselines for Information Systems and Organizations](https://csrc.nist.gov/pubs/sp/800/53/b/upd1/final).