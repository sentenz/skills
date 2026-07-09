# Mapping Rules

Canonical mapping rules for OT/ICS threat enrichment, scoring, prioritization, threat actor selection, treatment, and approval.

- [1. Framework Enrichment](#1-framework-enrichment)
- [2. CVSS v4.0 Scoring](#2-cvss-v40-scoring)
- [3. Probability Mapping](#3-probability-mapping)
- [4. Risk Matrix Mapping](#4-risk-matrix-mapping)
- [5. Threat Actor Mapping](#5-threat-actor-mapping)
- [6. Risk Treatment Mapping](#6-risk-treatment-mapping)
- [7. Risk Approval Mapping](#7-risk-approval-mapping)

## 1. Framework Enrichment

### 1.1. MITRE ATT&CK for ICS

**Action:** Populate `ATT&CK ID` when a concrete ATT&CK for ICS technique is supported by the TMT row and architecture evidence.

- Record the most relevant technique ID(s) in `ATT&CK ID`.
- Use `N/A` when no ICS-specific ATT&CK technique applies to a finalized row.
- In `Justification`, describe the behavior that supports the mapping without repeating IDs.

### 1.2. MITRE EMB3D

**Action:** Populate `EMB3D TID` when the modeled asset is, contains, or depends on an embedded device such as a PLC, PAC, RTU, SIS controller, HMI appliance, gateway, edge node, drive, intelligent sensor, actuator, embedded communication module, firmware path, maintenance port, removable-media path, or device-identity mechanism.

- Use EMB3D in addition to ATT&CK when evidence supports both. Do not use EMB3D as a substitute for ATT&CK for ICS.
- Record matched TID(s) in `EMB3D TID`, comma-separated when needed.
- Use `N/A` when no EMB3D threat mapping applies to a finalized row.
- When `Interaction` names JTAG, UART, RS-232, RS-485, SPI, I²C, GPIO, USB, Modbus RTU, proprietary serial, or a firmware update path, cross-reference the EMB3D Properties Mapper before finalizing `EMB3D TID` and `CWE ID`.
- In `Justification`, describe the mapped device property or missing control without repeating TIDs.

### 1.3. MITRE CWE

**Action:** Populate `CWE ID` when the root weakness is identifiable from the TMT row, architecture evidence, ATT&CK behavior, or EMB3D device-property threat.

- Prefer the most specific CWE that fits the described weakness.
- Use comma-separated values when multiple concrete weaknesses are required.
- Use `N/A` when no underlying weakness applies to a finalized row.
- In `Justification`, prefer weakness name or exploit behavior wording unless repeating the ID is required for disambiguation.

## 2. CVSS v4.0 Scoring

**Action:** Populate `CVSS v4.0 Vector`, `CVSS-B v4.0 Score`, and `CVSS v4.0 Severity` together.

- Do not record a severity without a vector and score.
- Do not record a vector without a score and severity.
- Record `CVSS-B v4.0 Score` with exactly one decimal digit and comma as decimal separator, e.g., `0,0`, `2,4`, `5,2`, `7,0`, `10,0`.
- Leave the trio blank only when scoring remains unresolved.
- Derive the score with the CVSS v4.0 calculator using the native TMT row, ATT&CK technique, EMB3D exposure, and OT/ICS impact context.
- Do not lower the intrinsic CVSS Base score solely because compensating controls or risk-acceptance decisions reduce residual business exposure.

> [!IMPORTANT]
> `CVSS v4.0 Vector` stores the Base vector only. `Likelihood of Exploit` uses a separate evidence-based vulnerability-state decision: `Theoretical`, `Exploitable`, `Active`, or `Exploit Published`. Do not append CVSS Threat metric `E` to the Base vector unless a separate threat-vector column is introduced.

### 2.1. Zero-Impact

Use a zero-impact CVSS outcome only when the finalized reviewed scenario leaves no modeled impact because the attack path or weakness is not real in the assessed design.

- `State = Not Applicable`: the attack path is impossible or structurally eliminated. Pair with `Risk Treatment = Avoidance`.
- `State = Mitigated`: do not reduce the CVSS Base score to zero solely because controls reduce residual exposure.
- Zero-impact does not make `Likelihood of Exploit` or `Risk Prioritization` inapplicable. For finalized reviewed rows, populate both columns from the mapping tables.
- When `State = Not Applicable`, treat vulnerability state as `Theoretical` unless stronger exploit-maturity evidence exists, then derive likelihood from CVSS exploitability metrics and prioritization from the `None` severity row in the risk matrix.

### 2.2. Exploitability Metrics

| Attack Vector   | OT/ICS Scenarios                                                            | Example Interfaces                     |
| --------------- | --------------------------------------------------------------------------- | -------------------------------------- |
| `AV:N` Network  | IP-connected devices, remote SCADA, cloud-connected gateways.               | Modbus/TCP, EtherNet/IP, OPC UA, MQTT. |
| `AV:A` Adjacent | Shared industrial bus, field network segment, same VLAN.                    | Modbus RTU, PROFIBUS, CAN.             |
| `AV:L` Local    | Workstation software, HMI application, locally executed configuration tool. | Engineering software, local database.  |
| `AV:P` Physical | Direct cable connection, removable debug port, hardware tampering.          | RS-232, JTAG, SWD, USB, buttons.       |

> [!NOTE]
> Use `AV:A` when the attacker can transmit or observe traffic from an already-connected node on the same fieldbus or adjacent segment. Use `AV:P` when exploitation requires opening an enclosure, tapping conductors, attaching a probe, manipulating termination points, or touching the device or cabling. Actor assignment follows the access precondition, not the protocol name alone.

### 2.3. Vulnerable System Impact Metrics

Metric abbreviations: `VC` = Vulnerable System Confidentiality Impact, `VI` = Vulnerable System Integrity Impact, `VA` = Vulnerable System Availability Impact.

| STRIDE Category        | Primary Impact Metric | Secondary Impact Metric | Confidence  | Rationale                                                                                                                                                                        |
| ---------------------- | --------------------- | ----------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spoofing               | VI                    | VC                      | Medium      | Identity impersonation primarily corrupts trust and authorization decisions. Confidentiality can follow when impersonation grants access to protected data.                      |
| Tampering              | VI                    | VA, VC                  | High        | Unauthorized modification is directly an integrity impact. Availability and confidentiality may follow when tampering disrupts operation or alters protection controls.          |
| Repudiation            | VI                    | VC                      | Medium-Low  | CVSS has no explicit non-repudiation metric. Represent auditability harm through integrity impact to logs, records, and transaction evidence.                                    |
| Information Disclosure | VC                    | VI                      | High        | Unauthorized exposure is directly a confidentiality impact. Integrity is usually indirect or downstream.                                                                         |
| Denial of Service      | VA                    | VI                      | High        | Degradation or outage is directly an availability impact. Integrity can follow where inconsistent processing results.                                                            |
| Elevation of Privilege | VI                    | VC, VA                  | Medium-High | Privilege gain enables unauthorized modification, access, and potentially shutdown or execution. Read access maps to `VC`, write access to `VI`, admin/execution access to `VA`. |

### 2.4. Subsequent System Impact Metrics

Use `SC`, `SI`, and `SA` to capture cascading effects on the physical process, safety systems, or connected devices. Values: `N` = None, `L` = Low, `H` = High.

| Scenario                                         | SC  | SI  | SA  | Rationale                                                                    |
| ------------------------------------------------ | --- | --- | --- | ---------------------------------------------------------------------------- |
| Compromised PLC affects downstream actuators     | N   | H   | H   | PLC compromise enables unauthorized physical-process control.                |
| Firmware tampering enables lateral movement      | H   | H   | H   | Compromised device can attack other devices on the same segment.             |
| Debug interface exposes firmware secrets         | H   | N   | N   | Extracted credentials or keys may compromise other devices.                  |
| DoS on communication interface                   | N   | N   | H   | Loss of communication can trigger upstream fault handling or fail-safe mode. |
| Configuration change via engineering workstation | N   | H   | N   | Modified setpoints propagate to field devices and affect process integrity.  |

## 3. Probability Mapping

Categorize likelihood of exploit using BSI `Dringlichkeit / Eintrittspotenzial` logic. Combine exploitation method with vulnerability state.

### 3.1. Exploitation Method

| Method                          | CVSS Exploitability Metrics                                      | Description                                                                                                                                      |
| ------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Manual (Manuell)                | `AV:P`                                                           | Direct physical device access. Any `AV:P` attack qualifies as Manual regardless of other metrics.                                                |
| Automated (Automatisch)         | `AV:A` or `AV:L`, `AC:L`, `AT:N`, `UI:N`                         | Adjacent or local exploitation with low complexity and no user interaction. Also use for `AV:N` threats without autonomous propagation behavior. |
| Self-Replicating (Replizierend) | `AV:N`, `AC:L`, `AT:N`, `PR:N`, `UI:N` plus propagation behavior | Network-reachable, low-friction, and scenario describes autonomous spread.                                                                       |

> [!NOTE]
> `PR` (Privileges Required) is independent of exploitation method in most cases. Do not change method classification based on `PR` alone.

### 3.2. Vulnerability State

| State                                      | CVSS Threat Metric Reference | Description                                                                                                   |
| ------------------------------------------ | ---------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Theoretical (Theoretisch)                  | `E:U`                        | No known exploit. Attack is conceptually possible but unverified.                                             |
| Exploitable (Ausnutzbar)                   | `E:P`                        | Proof-of-concept exists or the technique is documented and reproducible.                                      |
| Active (Aktiv)                             | `E:A`                        | Active exploitation observed in the wild or targeted campaigns.                                               |
| Exploit Published (Exploit Veröffentlicht) | `E:A`                        | Public exploit code or tooling is freely available. Prefer over Active when a public tool is directly usable. |

### 3.3. Likelihood Matrix

| State / Method                             | Manual (Manuell)   | Automated (Automatisch) | Self-Replicating (Replizierend) |
| ------------------------------------------ | ------------------ | ----------------------- | ------------------------------- |
| Theoretical (Theoretisch)                  | Info (sehr gering) | Low (gering)            | Medium (mittel)                 |
| Exploitable (Ausnutzbar)                   | Low (gering)       | Medium (mittel)         | High (hoch)                     |
| Active (Aktiv)                             | Medium (mittel)    | High (hoch)             | High (hoch)                     |
| Exploit Published (Exploit Veröffentlicht) | Medium (mittel)    | High (hoch)             | Critical (sehr hoch)            |

## 4. Risk Matrix Mapping

Combine `Likelihood of Exploit` and `CVSS v4.0 Severity` to determine `Risk Prioritization`.

| Probability \ Impact | None   | Low    | Medium | High     | Critical |
| -------------------- | ------ | ------ | ------ | -------- | -------- |
| Info                 | Info   | Info   | Low    | Low      | Medium   |
| Low                  | Info   | Low    | Low    | Medium   | High     |
| Medium               | Low    | Low    | Medium | High     | High     |
| High                 | Low    | Medium | High   | High     | Critical |
| Critical             | Medium | High   | High   | Critical | Critical |

## 5. Threat Actor Mapping

Normalize `Threat Actor` from common OT/ICS threat-path characteristics. Always select the minimum actor that satisfies required access, capability, and process knowledge. Reassess upward only when the modeled path requires capabilities beyond the selected label.

> [!NOTE]
> Actor capability order from lowest to highest: `Thrill Seeker` → `Hacktivist` → `Cybercriminal` → `Insider Threat` → `Nation-State Actor`.

| Minimum Threat Actor | Attack Path / Scenario                                                                                                                       | Key Indicators                                                                                                        |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `Thrill Seeker`      | Internet-exposed service with public exploit, default credentials, or unauthenticated interface.                                             | `AV:N`, `AC:L`, pre-built tooling, no plant-specific knowledge, opportunistic path.                                   |
| `Hacktivist`         | Internet-exposed HMI, SCADA web UI, or public-facing OT asset targeted for ideological messaging or symbolic proof-of-access.                | Visible high-profile target, protest objective, short-lived campaign, no persistence sought.                          |
| `Cybercriminal`      | Internet-exposed service or IT/OT boundary exploited for financial gain.                                                                     | Ransomware staging, credential theft, extortion, affiliate malware, stolen or phished credentials.                    |
| `Cybercriminal`      | Compromised vendor tooling, update service, or MSP channel reused for scalable extortion or ransomware.                                      | Monetized supply-chain reuse, commodity payload, no mission-specific objective.                                       |
| `Insider Threat`     | Trusted maintenance path, local engineering workstation, removable media, direct cable/debug interface, or privileged badge access.          | `AV:P` or `AV:L` local/physical session, plant access, maintenance tooling, process familiarity, insider credentials. |
| `Nation-State Actor` | Trojanized engineering software, signed firmware package, or tainted vendor update for covert pre-positioning or sabotage.                   | Custom or signed tooling, covert persistence, strategic or safety-critical target.                                    |
| `Nation-State Actor` | Bespoke multi-stage intrusion against segmented ICS requiring custom tooling, zero-days, covert lateral movement, or deep process expertise. | Long-dwell access, strategic high-value target, disruption, sabotage, or pre-positioning objective.                   |

> [!NOTE]
> When supply-chain compromise is the modeled vector, choose `Cybercriminal` for commodity ransomware or financial extortion, and `Nation-State Actor` for custom-signed tooling, strategic pre-positioning, or sabotage.

## 6. Risk Treatment Mapping

Risk treatment records the governance disposition for the remaining risk after prioritization.

> [!NOTE]
> `State` records the technical review result. `Risk Treatment` records the governance disposition. `Mitigated` may pair with `Acceptance` only when controls are in place and inherent residual risk is intentionally retained with documented approval.

### 6.1. Defensibility Checks

| Concern            | Check                                                                                                                                                                           |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Consistency        | `State`, CVSS severity, prioritization, treatment, and approval describe the same residual-risk posture.                                                                        |
| Overprescription   | Example rows are generalized patterns. Replace actor, score, treatment, and approval when product evidence differs.                                                             |
| Defense Risk       | Do not cite regulation, deployment restrictions, or trusted-environment assumptions as standalone mitigations. Tie each claim to controls, architecture, and approval evidence. |
| Identifier Hygiene | Do not populate ATT&CK, EMB3D, or CWE identifiers for `Not Applicable` rows unless the row explicitly documents a retained discrepancy.                                         |
| CVSS Defensibility | Keep CVSS Base scoring intrinsic. Document compensating controls and acceptance decisions outside the Base vector.                                                              |

### 6.2. Treatment Decision Guidance

Select the default treatment for the row's `Risk Prioritization`. Deviate to an acceptable alternative only when documented evidence supports the deviation and the rationale is recorded in `Justification`.

| Risk Prioritization | Default Treatment | Acceptable Alternatives         | Conditions and Constraints                                                                                                                  |
| ------------------- | ----------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Info                | Avoidance         | Acceptance                      | Attack path is impossible, structurally eliminated, or no longer present. Risk is negligible.                                               |
| Low                 | Acceptance        | Avoidance, Mitigation           | Low-cost controls are encouraged. Transfer is not warranted. Risk may be intentionally retained.                                            |
| Medium              | Mitigation        | Acceptance, Transfer            | Controls must address the root weakness. Transfer requires named SLA, policy, warranty, insurance, or equivalent mechanism.                 |
| High                | Mitigation        | Avoidance, Transfer, Acceptance | Acceptance is restricted to exceptional cases with CPSO approval and written justification. Do not use acceptance for unresolved evidence.  |
| Critical            | Avoidance         | Mitigation, Transfer, Acceptance | Acceptance requires explicit executive risk acceptance and written rationale. Do not use acceptance as a substitute for unresolved evidence. |

### 6.3. State and Treatment Compatibility

| TMT State             | Compatible Risk Treatment | Consistency Requirements                                                                                                          |
| --------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `Not Started`         | Blank                     | Row has not yet been reviewed. Leave enrichment and governance fields blank except preserved source values.                       |
| `Needs Investigation` | Blank                     | Evidence gap remains. Do not assign treatment or approval until resolved.                                                         |
| `Not Applicable`      | Avoidance                 | Attack path or risk source is impossible, structurally eliminated, or outside scope. Identifier columns should normally be `N/A`. |
| `Mitigated`           | Mitigation                | Controls reduce risk to an accepted residual level. Identify control, remaining exposure, owner, and approval mechanism.          |
| `Mitigated`           | Acceptance                | Use only when controls reduce exposure but residual risk is intentionally retained with documented approval.                      |
| `Mitigated`           | Transfer                  | Use only when controls and a named third-party mechanism share or delegate residual consequence.                                  |

### 6.4. Treatment Evidence Requirements

| Risk Treatment | Minimum Evidence in `Justification`                                                             |
| -------------- | ----------------------------------------------------------------------------------------------- |
| Avoidance      | Architectural record or design decision confirming the risk source has been eliminated.         |
| Mitigation     | Control(s), residual risk level, residual-risk owner, and approval mechanism.                   |
| Acceptance     | Business rationale for retention, approving stakeholder, and acceptance mechanism.              |
| Transfer       | Named third party, specific contract/SLA/warranty/insurance reference, and explicit risk scope. |

## 7. Risk Approval Mapping

`Risk Approval` records the minimum required approver role label from the intersection of `Risk Prioritization` and `Risk Treatment`.

| Prioritization / Treatment | Avoidance    | Mitigation       | Acceptance       | Transfer         |
| -------------------------- | ------------ | ---------------- | ---------------- | ---------------- |
| Info                       | Not Required | Lead Security    | Lead Security    | Lead Security    |
| Low                        | Not Required | Lead Security    | Lead Security    | Lead Security    |
| Medium                     | Not Required | Product Security | Product Security | Product Security |
| High                       | Not Required | CPSO             | CPSO             | CPSO             |
| Critical                   | Not Required | Executive        | Executive        | Executive        |

| Role Label       | Typical Title or Function                                                                        |
| ---------------- | ------------------------------------------------------------------------------------------------ |
| Not Required     | Risk structurally eliminated, no residual risk remains.                                          |
| Lead Security    | Technical lead, security engineer, or equivalent responsible for the design area.                |
| Product Security | Product security officer, security architect, or equivalent with cross-functional authority.     |
| CPSO             | CPSO, or equivalent with organizational risk management authority.                               |
| Executive        | C-level executive, risk committee, or board-level function with final risk acceptance authority. |
