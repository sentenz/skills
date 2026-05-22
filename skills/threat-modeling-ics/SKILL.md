---
name: threat-modeling-ics
description: >-
  Performs end-to-end threat modeling for OT/ICS systems from Microsoft Threat Modeling Tool (TMT) threat-list exports (`*.csv`) and model files (`*.tm7`).
  Uses TMT and STRIDE for initial threat enumeration, then enriches each threat with OT/ICS context, MITRE ATT&CK for ICS mappings, MITRE EMB3D device-property
  threat enrichment for embedded field devices, CWE weakness classification, CVSS v4.0 scoring, Likelihood of Exploit, Risk-based Prioritization via a Risk Matrix,
  minimum-capable Threat Actor assignment, Risk Treatment decisions, and OT impact categories ranging from Denial of View to Physical Damage to Property.
metadata:
  version: "1.7.2"
---

# Threat Modeling ICS

Instructions for AI security agents reviewing Microsoft Threat Modeling Tool threat-list exports.

> [!NOTE]
> Treat the Microsoft TMT CSV as the primary artifact and as the source of record for the native threat-row inventory. Use the Microsoft TMT model (`*.tm7`), Mermaid diagrams, and external documentation as architecture evidence for trust boundaries, interfaces, attack paths, and control coverage. If those sources materially conflict about whether an interface, trust boundary, or attack path exists, document the discrepancy and ask the user how to proceed before continuing. Do not silently choose one source as globally authoritative.

- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
  - [2.1. CIA Triad](#21-cia-triad)
  - [2.2. Purdue Model](#22-purdue-model)
  - [2.3. Threat Actors](#23-threat-actors)
  - [2.4. Diagram Depth Layers](#24-diagram-depth-layers)
- [3. Frameworks](#3-frameworks)
  - [3.1. Microsoft Threat Modeling Tool](#31-microsoft-threat-modeling-tool)
  - [3.2. STRIDE](#32-stride)
  - [3.3. MITRE ATT\&CK](#33-mitre-attck)
  - [3.4. MITRE EMB3D](#34-mitre-emb3d)
  - [3.5. MITRE CWE](#35-mitre-cwe)
  - [3.6. FIRST CVSS](#36-first-cvss)
  - [3.7. BSI Likelihood of Exploit](#37-bsi-likelihood-of-exploit)
  - [3.8. Risk Treatment](#38-risk-treatment)
- [4. Workflow](#4-workflow)
  - [4.1. Preparation](#41-preparation)
  - [4.2. Review](#42-review)
  - [4.3. Deliverables](#43-deliverables)
- [5. Example](#5-example)
  - [5.1. Diagram](#51-diagram)
    - [5.1.1. Threat Model Depth Layer 0 (System)](#511-threat-model-depth-layer-0-system)
  - [5.2. Mapping](#52-mapping)
    - [5.2.1. Purdue Model Mapping](#521-purdue-model-mapping)
    - [5.2.2. Impact Mapping](#522-impact-mapping)
    - [5.2.3. Probability Mapping](#523-probability-mapping)
    - [5.2.4. Risk Matrix Mapping](#524-risk-matrix-mapping)
    - [5.2.5. Threat Actor Mapping](#525-threat-actor-mapping)
    - [5.2.6. Risk Treatment Mapping](#526-risk-treatment-mapping)
    - [5.2.7. Risk Approval Mapping](#527-risk-approval-mapping)
  - [5.3. Template](#53-template)
    - [5.3.1. Raw TMT Export CSV Template](#531-raw-tmt-export-csv-template)
    - [5.3.2. Generated TMT CSV Template](#532-generated-tmt-csv-template)
- [6. References](#6-references)

## 1. Benefits

- Proactive Defense
  > Threat modeling enables teams to identify and mitigate security risks early in the design phase, reducing the likelihood of vulnerabilities being introduced during development.

- Residual Risk
  > The remaining risk after mitigations are applied. This risk must be explicitly documented and either accepted by stakeholders or further mitigated.

- Compliance Alignment
  > Threat modeling supports the risk assessment and technical documentation expectations of frameworks such as EU CRA, ISO/IEC 27005, NIST SP 800-30, IEC 62443-3-2, and GDPR Article 25 by producing documented evidence of security due diligence, assumptions, mitigations, and residual risk.

- Evidence-based Risk Assessment
  > Threat reviews grounded in concrete system context, attack paths, and control evidence improve the consistency and defensibility of likelihood, impact, and prioritization decisions.

- Risk Treatment Traceability
  > Assigning a concrete risk treatment decision (`Mitigation`, `Transfer`, `Acceptance`, or `Avoidance`) to each finalized reviewed threat produces traceable evidence that stakeholders have deliberately addressed every risk. Recording risk treatment supports regulatory obligations, stakeholder accountability, and residual risk communication.

- Tactics, Techniques, and Procedures (TTPs)
  > Modeling realistic attack scenarios based on known adversary TTPs utilizing frameworks such as MITRE ATT&CK ensures that mitigations are effective against actual threats rather than hypothetical ones.

## 2. Principles

### 2.1. CIA Triad

Focus on Confidentiality, Integrity, and Availability to ensure comprehensive security coverage.

- Confidentiality
  > Prevent unauthorized disclosure of process data, engineering parameters, network topology, and authentication credentials.

- Integrity
  > Ensure that control commands, setpoints, ladder logic, and historian records have not been altered without authorization.

- Availability
  > Maintain uninterrupted operation of control systems and communications so that operators can monitor and adjust the process at all times.

### 2.2. Purdue Model

The Purdue Model (ISA-95 / IEC 62264) partitions an industrial automation environment into hierarchical zones with distinct functional roles and communication boundaries. Each zone defines a trust perimeter and a characteristic attack surface that determines which STRIDE categories apply and which mitigations are feasible.

| Purdue Level | Zone Label                | Representative Assets                                                           |
| ------------ | ------------------------- | ------------------------------------------------------------------------------- |
| L5           | Enterprise                | ERP, Active Directory, email, cloud services                                    |
| L4           | Business Logistics        | Plant data historian, remote access gateway, IT/OT bridge                       |
| DMZ          | ICS/IT Demilitarized Zone | Reverse proxy, data diode, firewall, jump server                                |
| L3           | Site Operations           | SCADA server, application server, batch management, HMI servers                 |
| L2           | Area Supervisory          | Operator HMIs, engineering workstations (EWS), domain controllers               |
| L1           | Basic Control             | PLCs, PACs, RTUs, SIS (Safety Instrumented Systems)                             |
| L0           | Field Process             | Sensors (temperature, pressure, flow), actuators, variable-speed drives, valves |

### 2.3. Threat Actors

Threat actors are individuals, groups, or organizations with the motivation and capability to carry out attacks against systems, data, or infrastructure.

| #   | Threat Actor        | Skill Level | Resources | Persistence | Detection Difficulty | Primary Motivation                                      | Common Targets                                                            | Typical TTPs                                                                               |
| --- | ------------------- | ----------- | --------- | ----------- | -------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| 1   | Nation-State Actor  | Very High   | Very High | Very High   | Very High            | Espionage, Geopolitical Dominance, Strategic Objectives | Government, Defense, Critical Infrastructure, Research, Financial Systems | Zero-days, Supply Chain Attacks, Living-off-the-Land (LOTL), Lateral Movement, SIGINT      |
| 2   | Insider Threat      | Low–High    | Low–High  | Low–High    | Very High            | Greed, Grievance, Coercion, or Negligence / Human Error | Employer's Sensitive Systems & Data                                       | Data Exfiltration, Sabotage, Privilege Abuse, Misconfiguration, Unauthorized Data Transfer |
| 3   | Cybercriminal       | Low–High    | Low–High  | Low–High    | Low–High             | Financial Gain                                          | Individuals, SMBs, Enterprises, Banks, Healthcare                         | Ransomware-as-a-Service, Phishing, BEC, Carding, Credential Theft, Identity Fraud          |
| 4   | Hacktivist          | Low–Medium  | Low       | Low–Medium  | Low–Medium           | Political, Social, or Ideological Cause                 | Governments, Corporations, Media Outlets                                  | DDoS, Website Defacement, Doxing, Data Leaks                                               |
| 5   | Thrill Seeker       | Low–Medium  | Low       | Low         | Low                  | Curiosity, Notoriety, Thrill, or Mischief               | Random / Opportunistic Systems                                            | Pre-built Exploit Kits, DDoS-for-Hire, Unauthorized Vulnerability Discovery, Defacement    |

- Nation-State Actor
  > State-sponsored actors conduct long-duration, multi-stage campaigns targeting critical infrastructure for geopolitical objectives: espionage, pre-positioning for disruption, or physical sabotage. They invest significant resources in custom tooling, zero-day exploits, and supply-chain compromise to penetrate defense-in-depth architectures and reach Level 0 field devices.

- Insider Threat
  > Insiders hold privileged physical or logical access to control systems without requiring an initial intrusion phase. Malicious insiders may intentionally manipulate setpoints, corrupt configuration files, introduce rogue commands, or disable safety interlocks. Negligent insiders introduce risk by bypassing security controls or mishandling engineering-level credentials.

- Cybercriminal
  > Financially motivated actors deploy ransomware or extortion campaigns that pivot across the IT/OT boundary. By encrypting historian databases, engineering workstations, or SCADA servers they force operators to halt processes or pay ransom to restore visibility and control. OT-targeting ransomware groups increasingly understand industrial protocol semantics.

- Hacktivist
  > Hacktivists target publicly visible OT assets to advance political or ideological agendas. They exploit internet-exposed HMIs, Shodan-indexed SCADA web interfaces, or default credentials to post proof-of-access, deface operator displays, or make coarse setpoint changes for publicity rather than sustained operational damage.

- Thrill Seeker
  > Unskilled actors (e.g., Script Kiddies) opportunistically attack exposed OT services using pre-built exploit kits, default credential lists, or DDoS-for-hire services. They typically cause low-impact disruption or defacement without a specific target in mind.

### 2.4. Diagram Depth Layers

Use Microsoft [diagram depth layers](https://learn.microsoft.com/en-us/training/modules/tm-provide-context-with-the-right-depth-layer/1b-depth-layers) when creating or validating the threat model diagram.

- Layer 0 (`System`)
  > System layer for high-level architecture and trust boundaries between major zones or subsystems.

- Layer 1 (`Process`)
  > Process layer for process-level data flows in each major part.

- Layer 2 (`Subprocess`)
  > Subprocess layer for critical system subparts.

- Layer 3 (`Lower-Level`)
  > Lower-Level layer for highly critical or firmware-level and driver-level detail.

## 3. Frameworks

### 3.1. Microsoft Threat Modeling Tool

Microsoft Threat Modeling Tool (TMT) is a tool for identifying and categorizing potential security threats in software and system designs.

- STRIDE-based Threat Enumeration
  > TMT generates an initial list of threats based on the STRIDE categories, which provides a structured starting point for the review process.

- Source of Record
  > The exported TMT CSV is the working dataset and the source of record for the native row set.

### 3.2. STRIDE

STRIDE is the foundational threat classification scheme for understanding each threat statement and for guiding the review process.

- Spoofing
  > Illegitimate use of an identity, endpoint, process, or trust relationship.

- Tampering
  > Unauthorized modification of data, messages, logic, configuration, or execution inputs.

- Repudiation
  > Inability to prove an action, source, or responsibility.

- Information Disclosure
  > Exposure of information to an unauthorized party.

- Denial Of Service
  > Interruption, degradation, blocking, or exhaustion affecting availability.

- Elevation Of Privilege
  > Gain of permissions beyond the intended security boundary.

### 3.3. MITRE ATT&CK

[MITRE ATT&CK (Adversarial Tactics, Techniques, and Common Knowledge)](https://attack.mitre.org/) provides the technique taxonomy for threat enrichment.

1. Domains and Categories

    - ICS
      > Covers tactics and techniques targeting industrial control systems (ICS) and operational technology (OT) environments.

2. Concepts and Components

    - [Matrix](https://attack.mitre.org/matrices/ics/)
      > A tabular representation of tactics (columns) and techniques (rows) that allows users to explore how specific techniques are used to achieve tactical objectives.

    - [Tactics](https://attack.mitre.org/tactics/ics/)
      > The adversary's tactical goal or objective, such as initial access, persistence, or exfiltration.

    - [Techniques](https://attack.mitre.org/techniques/ics/)
      > A specific method used by adversaries to achieve a tactic, such as spearphishing, credential dumping, or data staging.

    - [Mitigations](https://attack.mitre.org/mitigations/ics/)
      > Security controls that can prevent or detect techniques, such as multi-factor authentication, network segmentation, or data loss prevention.

### 3.4. MITRE EMB3D

[MITRE EMB3D (Embedded Device Threat Model)](https://emb3d.mitre.org/) is a MITRE-developed knowledge base of cyber threats and associated mitigations for embedded devices found in critical infrastructure, IoT, automotive, healthcare, and manufacturing environments. EMB3D aligns with MITRE ATT&CK, CWE, and CVE to provide a property-based threat model that maps device features to specific threats and recommends mitigations tiered by implementation maturity.

> [!NOTE]
> Use EMB3D when the modeled asset is, contains, or depends on an embedded device: PLC, PAC, RTU, SIS controller, HMI appliance, gateway, industrial edge node, drive, intelligent sensor, actuator, or embedded communication module. Do not use EMB3D as a substitute for ATT&CK for ICS; use both layers when evidence supports both.

1. Domains and Categories

    - Embedded Devices
      > Covers a wide range of embedded systems, including IoT devices, industrial control systems, automotive electronics, medical devices, and consumer electronics.

2. Concepts and Components

    - [Device Properties](https://emb3d.mitre.org/properties-list/)
      > Describe the hardware and software features of a device, including physical hardware, network services and protocols, software, and firmware. Each property is mapped to a set of threats, enabling enumeration of threat exposure based on known device features.

    - [Threats](https://emb3d.mitre.org/threats)
      > Embedded-device threat entries identify how a threat actor can achieve a specific objective or effect on the device. Each threat entry describes the targeted technical features, the required threat actions, the resulting impact, and the associated CWE weaknesses.

      - [Hardware](https://emb3d.mitre.org/threats/hardware)
        > Threats targeting physical hardware components such as processors, memory, and interfaces.

      - [System Software](https://emb3d.mitre.org/threats/system-software)
        > Threats targeting operating systems, firmware, and bootloaders.

      - [Application Software](https://emb3d.mitre.org/threats/application-software)
        > Threats targeting application-layer software running on the device.

      - [Networking](https://emb3d.mitre.org/threats/networking)
        > Threats targeting network services, protocols, and communication interfaces of the device.

    - [Mitigations](https://emb3d.mitre.org/mitigations)
      > Security mechanisms for each threat, categorized by implementation maturity level. Mitigations are intended for device vendors to implement at design time and for asset owners to evaluate during device acquisition.

      - [Foundational](https://emb3d.mitre.org/mitigations/foundational)
        > Baseline controls applicable to all devices, addressing the most common embedded device threats.

      - [Intermediate](https://emb3d.mitre.org/mitigations/intermediate)
        > Enhanced controls addressing more complex threats, potentially requiring moderate design changes or additional device resources.

      - [Leading](https://emb3d.mitre.org/mitigations/leading)
        > Advanced controls targeting sophisticated threats, potentially requiring significant design changes or emerging security technologies.

### 3.5. MITRE CWE

[MITRE CWE](https://cwe.mitre.org/) (Common Weakness Enumeration) is a comprehensive catalog of software and design weaknesses that can lead to security vulnerabilities. CWE provides a standardized way to classify and describe the underlying issues that enable threats, which can inform mitigation strategies and secure design practices.

### 3.6. FIRST CVSS

[FIRST CVSS v4.0](https://www.first.org/cvss/) to score the technical severity of the threat based on the modeled attack scenario and its consequences.

- [CVSS Calculation](https://www.first.org/cvss/calculator/4.0)
  > Use the CVSS v4.0 calculator to determine the base score, severity, and vector based on the modeled attack scenario and review rationale.

- CVSS-B Score
  > Record the CVSS v4.0 base score as a numeric value between `0,0` and `10,0` when the evidence supports a defensible score.

- CVSS Severity
  > Record the CVSS v4.0 severity category (`None`, `Low`, `Medium`, `High`, `Critical`) when a base score is recorded.

- CVSS Vector
  > Record the CVSS v4.0 vector string (`CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:N/SA:N`) when a base score is recorded.

### 3.7. BSI Likelihood of Exploit

[BSI Dringlichkeit / Eintrittspotenzial](https://www.bsi.bund.de/DE/Service-Navi/Abonnements/Newsletter/Buerger-CERT-Abos/Buerger-CERT-Sicherheitshinweise/Risikostufen/risikostufen.html) to assess the likelihood of exploit based on the current state of the vulnerability and the style of exploitation.

1. Concepts and Components

    - Exploitation Method
      > The style of attack required to exploit the vulnerability, which affects the likelihood of exploitation.

      - Manual (Manuell)
        > The attacker must perform non-automatable steps to adapt the attack to the target. Requires skill and effort.

      - Automated (Automatisch)
        > The exploit can be run using a script or tool against many targets.

      - Self-replicating (Replizierend)
        > The exploit can spread automatically without user interaction (e.g., worms, bots). Compromised systems attack further systems autonomously.

    - Vulnerability State
      > The current condition of the vulnerability, which affects the likelihood of exploitation.

      - Theoretical (Theoretisch)
        > A flaw is discovered that could lead to a security issue, but no concrete exploit exists.

      - Exploitable (Ausnutzbar)
        > A proof-of-concept or reliable method to exploit the vulnerability exists.

      - Active (Aktiv)
        > Evidence exists that the vulnerability is already being exploited in the wild.

      - Exploit Published (Exploit Veröffentlicht)
        > A public attack tool has been released, the effort to attack drops significantly.

### 3.8. Risk Treatment

Risk treatment defines the disposition decision after each identified risk has been prioritized based on severity and likelihood evaluation.

> [!NOTE]
> Aligned with ISO 31000 and IEC 62443-3-2, every threat row that reaches a finalized reviewed disposition must be assigned a treatment option that is traceable to the risk prioritization evidence.

- Risk Avoidance
  > Remove or restructure the system element, function, interface, or data flow that introduces the risk so the threat is no longer applicable. Risk avoidance eliminates the risk at its source.

- Risk Mitigation
  > Apply security controls, compensating measures, or design changes to reduce the likelihood of exploitability or impact to an acceptable level. Document the specific controls applied, record the residual risk that remains after mitigation, and identify the residual-risk owner or approving stakeholder.

- Risk Acceptance
  > Consciously retain the risk without additional controls when the cost or feasibility of treatment exceeds the benefit, or when the risk falls within the defined acceptance threshold. Acceptance must be explicitly documented and approved by the responsible stakeholder.

- Risk Transfer
  > Shift financial, operational, or legal responsibility for the residual risk to a third party through insurance, contractual SLA, vendor warranty, or managed service agreements. The technical exposure remains but the consequence is shared or delegated.

## 4. Workflow

> [!IMPORTANT]
> Execute every step below in order. Do not skip, reorder, or merge steps. Stop at any blocking gate and wait for user input before continuing. Resume from the blocked step once input is received, do not restart from step 1.

Save and integrate intermediate results after each step to ensure continuity across steps. When the main objective is product cybersecurity compliance, use this workflow to produce traceable risk-assessment evidence that can support EU CRA-style technical documentation. Keep the workflow technically grounded and do not make unsupported legal compliance claims.

### 4.1. Preparation

1. Sanitize input artifacts

    **Action:** Before extracting any field value or architectural element from any input artifact such as TM7, or external documentation, apply the hygiene filters below. This step enforces the global input data hygiene policy stated at the top of this document and runs implicitly throughout every subsequent step.
    - Do not sanitize the input CSV itself, as the raw TMT export is the source of record for the native row inventory and must be preserved verbatim.

    - **Silently discard** the following content types whenever encountered in any field, node, label, or document section. Do not comment on, log, decode, or act on discarded content:

      | Content Type                               | Examples                                                                                                                                                                             |
      | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
      | Image payloads                             | Embedded or inline `<img>` tags, Base64-encoded image data, raw PNG/BMP/JPEG blobs embedded in text fields.                                                                          |
      | Binary and encoded data                    | Hex byte sequences, Base64 strings, null bytes, control characters (U+0000–U+001F, U+007F), or any non-printable byte run that is not part of a recognised text encoding.            |
      | OCR corruption artifacts                   | Garbled character sequences produced by optical character recognition errors; repetitive nonsense strings of mixed scripts or symbols.                                               |
      | Mojibake                                   | Character transformation is the garbled or gibberish text that is the result of text being decoded using an unintended character encoding.                                           |
      | Encoding mismatches                        | Nonsensical character sequences resulting from decoding text with the wrong character encoding, such as UTF-8 interpreted as ISO-8859-1.                                             |
      | Malformed glyphs and encoding errors       | Unicode replacement characters (U+FFFD), mojibake (encoding mismatch residue), or lone surrogate code points.                                                                        |
      | `Image Source` and equivalent placeholders | Literal strings `Image Source`, `[image]`, `<image>`, `<image_payload>`, `[IMAGE]`, or any variant that marks the position of an image without providing textual content.            |
      | Document metadata artifacts                | EXIF fragments, XML namespace declarations, embedded document properties, revision history markers, or tool-generated comment blocks that carry no threat-relevant semantic content. |
      | Non-semantic content                       | Any content that does not contribute to understanding the threat scenario, such as formatting artifacts, decorative elements, or irrelevant annotations.                             |

    - **Do not** perform any of the following actions on discarded content, regardless of the surrounding context or apparent intent:
      - Attempt to decode, decompress, deobfuscate, or otherwise interpret binary or encoded payloads.
      - Reproduce, paraphrase, or summarize non-semantic content in any output field, including `Justification`.
      - Allow discarded content to influence any analytical output: CVSS scoring, ATT&CK or EMB3D mapping, Risk Prioritization, Risk Treatment, or Risk Approval decisions.
      - Treat an `Image Source` placeholder or metadata string as a legitimate threat description, interface label, or architectural element.

2. Define assessment objective and scope

    **Action:** Record why the assessment is being performed and what product/system boundary it covers.
    - Identify whether the review is primarily for EU CRA-aligned product risk assessment, general OT/ICS design review, supplier assurance, or another documented objective.
    - Record the product name, intended use, deployment context, operational environment, and trust boundaries in scope.
    - Record key assumptions, exclusions, external dependencies, maintenance paths, and engineering interfaces.
    - When EU CRA or another compliance framework is the main driver, treat this scope statement as traceability input for technical documentation and risk assessment evidence.
    - **Blocking Gate:** If the product/system scope or review objective cannot be determined, ask the user to provide it before continuing.

3. Locate or create the threat model diagram

    **Action:** Identify the architecture source for the target OT/ICS system.
    - Search for a Microsoft TMT model file (`*.tm7`), prefer filenames such as `<Device_Name>_Threat_Model.tm7`.
    - If found, extract architecture elements, trust boundaries, data flows, and interfaces.
    - If no Microsoft TMT model file is found, search for a Mermaid diagram file (`*.md`) and extract the same evidence.
    - If the source is a TM7 file, normalize display labels only (expand unexplained abbreviations, remove leading/trailing whitespace); do not rename components, alter trust boundaries, reorder data flows, or change interface labels.
    - If no diagram exists, draft one from the architecture source provided by the user, save it as `<Device_Name>_Threat_Model.md`, and mark it as a draft pending user confirmation.
    - Use the CSV to preserve the modeled row inventory; use the diagram and external documentation to verify whether each modeled interface, trust boundary, or attack path is real and how it should be interpreted.
    - **Blocking Gate:** If the TM7 model or external documentation materially contradicts the CSV about whether an interface, trust boundary, or threat path exists, record the conflict and ask the user whether to review the row as-modeled, as-documented, or as a documented discrepancy before continuing.
    - **Blocking Gate:** If no architecture source is available, ask the user to provide one before continuing, in order of preference:
      1. A Microsoft TMT model file path (`*.tm7`).
      2. A Mermaid diagram file path (`*.md`).
      3. External documentation or links describing the system architecture.
      4. A textual description of the system components and trust relationships.

4. Locate and classify the input CSV

    **Action:** Locate the TMT export CSV and determine its review status.
    - Prefer filenames such as `<Device_Name>_Threat_Model.csv` or `<Device_Name>_Threat_Model_Generated.csv`, but rely on the header and row content to determine artifact type.
    - Classify using the following observable signals:
      - `Raw TMT export`: comma-delimited header containing only native TMT columns.
    - **Blocking Gate:** If no CSV is available, ask the user to provide the exported TMT CSV before continuing.

5. Detect native TMT columns

    **Action:** Verify and note the native TMT columns confirmed in the input CSV header.
    - Confirm that the header row contains all native TMT fields:
      - `Id`, `Title`, `Category`, `Diagram`, `Interaction`, `Priority`, `State`, `Changed By`, `Description`, `Justification`, `Last Modified`
    - **Blocking Gate:** If any expected native TMT column is absent from the header, report the missing field(s) to the user before continuing.
    - If the header contains columns beyond the native TMT fields (e.g., enrichment columns from a partially reviewed file), note them as pre-existing review columns and carry their values forward unchanged for any already-reviewed rows.

6. Establish preservation constraints

    **Action:** Define the column contract for the output file `<Device_Name>_Threat_Model_Generated.csv` before beginning the row-by-row review.
    - Do not delete any columns.
    - Do not edit the original `<Device_Name>_Threat_Model.csv` file — treat it as immutable evidence.
    - **Preserve** (copy verbatim from source to output, never modify, even if the source value appears to contain a typo or formatting difference): `Id`, `Title`, `Category`, `Diagram`, `Interaction`, `Changed By`, `Description`, `Last Modified`.
    - **Update** (may be revised based on analyst review): `State`, `Priority`, `Justification`.
    - **Append** (add to the output only; not present in the raw TMT export): `ATT&CK ID`, `EMB3D TID`, `CWE ID`, `CVSS v4.0 Vector`, `CVSS-B v4.0 Score`, `CVSS v4.0 Severity`, `Likelihood of Exploit`, `Risk Prioritization`, `Threat Actor`, `Risk Treatment`, `Risk Approval`.
    - Every row in the output must trace back to exactly one row in the source CSV, identified by its native `Id` value.

7. Conflict Gathering

    **Action:** Before beginning the review, gather any known conflicts or discrepancies in the architecture evidence that may impact how specific rows are interpreted.
    - Incorporate contents from additional sources as supplementary architectural, operational, and control evidence. Use this material to validate assumptions, identify missing trust boundaries, assess control coverage, and detect inconsistencies between the documented architecture and the existing threat model.
    - For example, if the TM7 model shows interface, trust boundary, or attack path data flow between two components but the diagram and external documentation do not, record this conflict as a known discrepancy.
    - When a conflict is encountered during the row-by-row review, refer back to this list of known discrepancies to determine whether to review the row as-modeled, as-documented, or as a documented discrepancy.
    - **Blocking Gate:** If the architecture evidence contains material conflicts that impact how specific rows should be reviewed, ask the user to clarify how to review those rows before continuing.

### 4.2. Review

1. Row-by-Row

    **Action:** For every row in the dataset, read all native TMT fields together as a single unit before forming any judgment.
    - `Title`
      > The initial threat statement generated by TMT. Interpret together with `Description`.
    - `Category`
      > The STRIDE classification assigned by TMT. Use it to anchor the threat type.
    - `Interaction`
      > The data flow or trust relationship associated with the threat. Use it to determine the attack vector and applicable controls.
    - `Description`
      > Additional detail about the threat consequences and high-level mitigations. Read together with `Category` and `Title`.
    - `Priority`
      > The initial priority assigned by TMT.
    - `State`
      > The initial review status assigned by TMT.
    - Record assumptions and missing evidence in the `Justification` field when the native TMT fields do not fully determine the threat decision.
    - When the assessment objective is compliance-oriented, treat each row as a traceable product risk statement tied to a concrete interface, trust relationship, or maintenance path.

    > [!NOTE]
    > Perform steps 2–13 for every row before proceeding to section 4.3.

2. MITRE ATT&CK

    **Action:** Populate the `ATT&CK ID` field for each row when a concrete ATT&CK for ICS technique can be supported by the TMT threat fields, see [MITRE ATT&CK](#33-mitre-attck).
    - Record the most relevant MITRE ATT&CK Techniques IDs for ICS.
    - Store MITRE technique IDs in the dedicated `ATT&CK ID` column.
    - In `Justification`, describe the specific technique behavior that supports the mapping; avoid duplicating technique IDs already captured in `ATT&CK ID`.
    - Record `N/A` when no ICS-specific ATT&CK technique applies to the finalized reviewed row.
    - Leave the field blank only when the ATT&CK mapping remains unresolved because the review is incomplete or blocked.

    **Data source:** `assets/attack/` directory contains structured MITRE ATT&CK data files with technique IDs, descriptions, mitigations, and detection methods.
    - Consult these files when populating the `ATT&CK ID` column.

3. MITRE EMB3D

    **Action:** Populate the `EMB3D TID` and apply [MITRE EMB3D](#34-mitre-emb3d) to determine the embedded-device exposure and mitigation family that best explains the row.
    - Use EMB3D especially for PLC, PAC, RTU, field-device, firmware, maintenance-port, removable-media, and device-identity scenarios.
    - Store the matched [EMB3D Threats](https://emb3d.mitre.org/threats) Enumeration TID(s) in the dedicated `EMB3D TID` column. Apply EMB3D [Device Properties](https://emb3d.mitre.org/properties-list/) Mapper to support the justification for the TID selection.
    - Use comma-separated values when more than one TID applies (e.g., `TID-116, TID-119`).
    - Record `N/A` when the reviewed row has no applicable EMB3D threat mapping.
    - Leave the field blank only when the mapping remains unresolved because the review is incomplete or blocked.
    - In `Justification`, describe the mapped device property or missing control; avoid duplicating TIDs already captured in `EMB3D TID`.
    - When the `Interaction` names a hardware or embedded-software interface (JTAG, UART, RS-232, RS-485, SPI, I²C, GPIO, USB, Modbus RTU, proprietary serial, or a firmware update path), cross-reference the MITRE EMB3D [Properties Mapper](https://emb3d.mitre.org/properties-mapper/) to identify device-property-mapped threats (TIDs) and their associated CWE IDs before finalizing the `CWE ID` assignment in step 4.

    **Data source:** `assets/emb3d/` directory contains structured MITRE EMB3D data files with threat IDs, descriptions, associated device properties, and mitigations.
    - Consult these files when populating the `EMB3D TID` column.

4. MITRE CWE

    **Action:** Populate the `CWE ID` field for each row when the root weakness is identifiable from the TMT threat fields, see [3.5. MITRE CWE](#35-mitre-cwe).
    - Prefer the most specific CWE that fits the described weakness.
    - Use comma-separated values when the finding depends on more than one concrete weakness (e.g., `CWE-290, CWE-345`).
    - Store CWE identifiers in the dedicated `CWE ID` column. In `Justification`, prefer weakness name or exploit behavior wording unless repeating the ID is required for disambiguation.
    - Record `N/A` when the reviewed row has no applicable underlying weakness to record.
    - Leave the field blank only when the root weakness remains unresolved because the review is incomplete or blocked.

    **Data source:** `assets/cwe/` directory contains structured MITRE CWE data files with weakness IDs, descriptions, and mitigations.
    - Consult these files when populating the `CWE ID` column.

    > [!NOTE]
    > Prefer the most specific CWE that fits the described weakness. When the root weakness is identifiable from the TMT threat fields (`Title`, `Category`, `Interaction`, `Description`), load the relevant `assets/cwe/` file to confirm the CWE definition and associated mitigation guidance before recording the identifier.

5. FIRST CVSS v4.0

    **Action:** Populate the CVSS v4.0 Base Metrics `CVSS v4.0 Vector`, `CVSS v4.0 Severity`, and `CVSS-B v4.0 Score` together for each row, see [3.6. FIRST CVSS](#36-first-cvss).
    - All three fields must be populated together. Do NOT record a severity without a vector. Do NOT record a vector without a score.
    - Record a zero-impact CVSS assessment (`0,0` / `None`) when the reviewed row has a valid attack path but the impact is effectively zero due to architectural controls, compensating measures, or mitigations.
    - Leave the trio blank only when the scoring analysis remains unresolved because the review is incomplete or blocked.
    - Derive the recorded score from the [CVSS v4.0 calculator](https://www.first.org/cvss/calculator/4.0) using the CVSS Base Metrics informed by the native TMT threat fields (`Title`, `Category`, `Interaction`, `Description`), the MITRE ATT&CK technique, and the EMB3D device exposure as input.
    - Reference the [5.2.2. Impact Mapping](#522-impact-mapping) section for guidance on mapping STRIDE categories to CVSS impact metrics.

    **Data source:** `assets/cvss/` directory contains the CVSS v4.0 JSON Schema for validating recorded vector, score, and severity fields.
    - Consult this schema to validate CVSS v4.0 column values; derive scoring from the CVSS calculator and specification, not from this schema file.

6. BSI Likelihood of Exploit

    **Action:** Populate the `Likelihood of Exploit` column using the BSI `Dringlichkeit / Eintrittspotenzial` logic, see [3.7. BSI Likelihood of Exploit](#37-bsi-likelihood-of-exploit).
    - Leave the field blank only when the likelihood assessment remains unresolved because the review is incomplete or blocked.
    - Do not record `N/A` for finalized reviewed rows. Zero-impact outcomes (`CVSS-B v4.0 Score = 0,0`, `CVSS v4.0 Severity = None`) still require a mapped likelihood value.
    - Reference the [5.2.3. Probability Mapping](#523-probability-mapping) section for guidance on mapping CVSS metrics and TMT statements to BSI likelihood categories.

7. Risk Prioritization

    **Action:** Populate the `Risk Prioritization` column using the combined information from `CVSS v4.0 Severity` and `Likelihood of Exploit` for each row.
    - Leave the field blank only when either `CVSS v4.0 Severity` or `Likelihood of Exploit` remains unresolved because the review is incomplete or blocked.
    - Do not record `N/A` for finalized reviewed rows. When `CVSS v4.0 Severity = None`, still evaluate the risk matrix using the derived likelihood value.
    - Reference the [5.2.4. Risk Matrix Mapping](#524-risk-matrix-mapping) section for guidance on combining the impact and probability assessments into a final risk prioritization category.

8. Threat Actor

    **Action:** Populate the `Threat Actor` column by assigning the minimum capable `Threat Actor` for each row using the standardized labels from [Threat Actors](#23-threat-actors).
    - Use exactly one standardized `Threat Actor` label per reviewed CSV row.
    - Record the minimum required actor, not the most severe or most newsworthy actor.
    - Base the decision on the modeled attack path, required access, exploit maturity, and the amount of OT-specific knowledge required.
    - Evaluate the assignment against all three selection criteria together:
      - **Capability:** tooling maturity, exploit sophistication, and ability to chain multiple steps.
      - **Access Path:** internet-reachable, adjacent industrial network, local workstation, maintenance path, or physical access requirement.
      - **Operational Knowledge:** generic IT tradecraft, OT protocol familiarity, process-specific engineering knowledge, or privileged insider context.
    - Escalate to a more capable actor only when the attack path cannot reasonably succeed with a less capable one.
    - Do not assign multiple actors in one row. If several actors could plausibly perform the attack, record the minimum actor that can realistically achieve the described effect.
    - Reference the [5.2.5. Threat Actor Mapping](#525-threat-actor-mapping) section for common actor selections from attack-path characteristics.

9. TMT State

    **Action:** Revise the `State` field for each row using the full analytical context: TMT threat fields, MITRE ATT&CK technique, EMB3D device exposure, CWE root weakness, CVSS severity, Risk Prioritization, and assigned Threat Actor.
    - State selection guidance: Select the state decision that best fits the evidence and rationale.
      - `Not Started`: Default/export state for rows that have not yet been reviewed. Use this only to indicate genuinely unreviewed work remaining in a partially completed CSV. Once a row has been analyzed in this step, move it out of `Not Started` and assign the best-fit reviewed state below.
      - `Not Applicable`: The attack path is architecturally impossible (e.g., analog-only interface, passive sensor with no network exposure, human actor rather than a machine endpoint with no independent execution context), or the risk source has been structurally eliminated.
        - In `Justification`, name the specific architectural contradiction or eliminated element. Keep the required `Threat Actor` value and explain why that actor was the minimum candidate considered before the path was rejected.
      - `Mitigated`: One or more security controls, compensating measures, or design changes are confirmed in place and reduce the risk to an accepted level. The applied control, measure, residual risk, and what residual attack surface remains for the assigned threat actor after those controls are applied must be identified in `Justification`.
      - `Needs Investigation`: Critical evidence is missing, a key assumption cannot be validated, or the attack path cannot be closed without additional architecture information or clarification. The specific evidence gap or unanswered question must be named in `Justification`, including whether the unknowns affect the assigned threat actor.

10. TMT Priority

    **Action:** Revise the `Priority` field for each row. Use the derived `Risk Prioritization` as the primary signal and adjust only when the modeled context provides a specific reason to deviate.
    - Assign one of the following three priority values.
      - `Low`
        > The threat is accepted with minimal concern. No immediate action is required, but it should be monitored for changes.
      - `Medium`
        > Mitigation planning should be initiated, and the threat should be tracked in the security backlog.
      - `High`
        > The threat is significant and requires prompt mitigation. It should be prioritized in the security backlog and may require escalation.

11. TMT Justification

    **Action:** Write a concise, technically precise analyst statement in the `Justification` field for each row, synthesizing all prior enrichment steps. The justification provides the evidence-based rationale that supports the assigned `State`, explains the assigned `Threat Actor`, and informs the `Risk Treatment` decision in the next step.
    - State the evidence-based rationale that supports the assigned `State`.
    - Reference the modeled protocol, interface, trust relationship, validation behavior, or compensating control that informs the decision.
    - Reference the *behavior or name* of the assigned MITRE ATT&CK technique, EMB3D threat, CWE weakness, CVSS severity, and Threat Actor where they support the rationale.
    - **Do NOT repeat technique/threat/weakness IDs** (e.g., `T0*`, `TID-*`, `CWE-*`) in the `Justification` column, those identifiers belong exclusively in their dedicated columns (`ATT&CK ID`, `EMB3D TID`, `CWE ID`).
    - State why the chosen actor is the minimum capable adversary by describing the required access path and operational knowledge.
    - When a reviewed row intentionally uses `N/A` in an appended identifier column that has no applicable mapping (for example `ATT&CK ID`, `EMB3D TID`, or `CWE ID`), or leaves a review column blank because the review is incomplete or blocked, state the architectural or evidentiary reason once in `Justification` rather than leaving the omission implicit.
    - When `State` is `Not Applicable`, name the specific architectural contradiction or eliminated element (e.g., passive sensor, analog signal path, human actor rather than machine endpoint, or no independent execution context).
    - When `State` is `Mitigated`, identify the applied security control, compensating measure, or design change. State the residual risk level if exposure is not fully eliminated.
    - When `State` is `Needs Investigation`, state the most important evidence gap or assumption that must be resolved before a decision can be made.
    - When `Risk Treatment` is `Mitigation` or `Acceptance`, identify in `Justification` the residual-risk owner or approving stakeholder (role or name) and the approval mechanism, or state that approval is pending if it is not yet available.
    - When `Risk Treatment` is `Transfer`, identify in `Justification` the named organization, contract, SLA, or insurance policy responsible for the transferred risk.

    > [!IMPORTANT]
    > The justification is the most critical part of the security review. It is written last so it can synthesize the full analytical picture.

12. Risk Treatment

    **Action:** Populate the `Risk Treatment` column by assigning a risk treatment decision to each row based on the derived `Risk Prioritization`, see [Risk Treatment](#38-risk-treatment).
    - Do not use `Acceptance` or `Transfer` to work around missing technical evidence.
    - Reference the [5.2.6. Risk Treatment Mapping](#526-risk-treatment-mapping) section for selecting risk treatment based on mandatory constraints for each `Risk Prioritization` level.
    - Verify that `Justification` contains the minimum evidence for the selected treatment before proceeding to next step.
    - Leave the field blank only when the treatment decision remains unresolved because the review is incomplete or blocked.

13. Risk Approval

    **Action:** Populate the `Risk Approval` column by recording the minimum required approval authority role for each row.
    - Derive the required approval authority using the [5.2.7. Risk Approval Mapping](#527-risk-approval-mapping) table.
    - Record exactly one of the standardized role labels.
    - Leave the field blank only when the approval assessment remains unresolved because the review itself is incomplete or blocked.

### 4.3. Deliverables

1. Generate CSV

    **Action:** Validate the analyst decisions, then write the complete enriched dataset to the output file `<Device_Name>_Threat_Model_Generated.csv`.
    - Generate a semicolon delimited output CSV format.
    - Any field containing the delimiter character (semicolon) or line breaks must be enclosed in double quotes per CSV conventions.
    - Verify each output row against its source row to confirm no enrichment values were dropped or overwritten.
    - Retain native TMT columns in their source order and append the review columns in the order defined in section [4.1. Preparation](#41-preparation).
    - Verify that all native TMT columns are present and unmodified in the output before saving.
    - Verify that every reviewed row has exactly one allowed `Threat Actor` label.
    - Perform a final column-scope consistency check: keep IDs and score artifacts in dedicated columns, and keep `Justification` as narrative rationale.
    - Reject rows where `Justification` is only an identifier token or parenthetical code reference.
    - Verify that the output supports traceability from raw TMT threat statement to analyst decision, supporting evidence, assumptions, residual risk posture, and threat actor selection decision.

2. Review Summary

    **Action:** Write a Markdown summary file `<Device_Name>_Threat_Model_Summary.md` of the review that lists the highest-risk interactions, the main assumptions, rows marked `Not Applicable` by rationale category, the main evidence gaps that keep rows in `Needs Investigation`, and the residual risks that remain after documented mitigations.

    **Compliance Traceability Guidance:**
    - When the main objective is EU CRA or another product compliance framework, structure the summary so it can be reused as risk-assessment evidence and as an input to technical documentation.
    - Capture product scope, intended use, assessment assumptions, open evidence gaps, and residual risks — each risk claim must reference at minimum one threat row `Id`.

    **Recommended Summary Sections:**
    - Assessment Objective and Product Scope
    - Executive Summary with threat counts by state, risk level, and threat actor
    - Highest Risk Findings table with ID, Threat, Interface, CVSS, Risk Prioritization, Threat Actor
    - Primary Attack Vectors with techniques, impact, and risk treatment
    - Threat Actor Distribution with key access-path and knowledge assumptions
    - Not Applicable Rationale Summary by pattern category
    - MITRE ATT&CK for ICS Mapping table
    - CWE Weakness Classification summary
    - Assumptions and Evidence Gaps
    - Conflict Gathering Summary
    - Residual Risk Summary and Unresolved Decisions
    - Residual-Risk Approval and Ownership Notes (if applicable)
    - Risk Treatment Summary with counts and rationale by treatment option
    - Risk Approval Status Summary with counts by approval label and pending approver roles
    - Recommended Mitigations by priority (High, Medium, Low)

## 5. Example

### 5.1. Diagram

#### 5.1.1. Threat Model Depth Layer 0 (System)

- `<Device_Name>_Threat_Model.md`
  > A depth layer 0 (system) architecture diagram showing major zones, trust boundaries, and data flows.

  > [!IMPORTANT]
  > Be precise in technical labeling of components, interfaces, and data flows to support accurate threat review and mapping.

  ```mermaid
  flowchart TD
    %% Layer 0 (System) - External Entities
    subgraph External_Entities [External Entities]
        PLC((PLC))
        USER((Operator))
        DEBUGGER((Debugger))
    end

    %% Layer 0 (System) - Engineering Workstation
    subgraph Management_Zone [Engineering Workstation]
        CFG[Configurator Software]
        DB[(Device Modules)]
    end

    %% Layer 0 (System) - Device Trust Boundary
    subgraph Device_Boundary [Trust Boundary `Device Name`]
        DEVICE[Positioner / Actuator]
    end

    %% Layer 0 (System) - Physical Process
    subgraph Physical_Process [Physical Environment]
        VALVE[Control Valve]
    end

    %% Data Flows
    USER --> CFG
    CFG <--> |"Proprietary (RS-232)"| DEVICE
    PLC <--> |"Modbus RTU (RS-485)"| DEVICE
    DEBUGGER <--> |"JTAG"| DEVICE
    USER --> DEVICE
    DEVICE --- VALVE
  ```

### 5.2. Mapping

#### 5.2.1. Purdue Model Mapping

Use this table to identify the Purdue zone of each asset from `Interaction` or `Diagram`, and to validate that the modeled threat surface is consistent with the zone's prevalent STRIDE categories. Do not use this table to override the `Category` values assigned by TMT.

| Purdue Level | Zone        | Asset Type                                 | Examples                                                          | Prevalent STRIDE Categories                                                            |
| ------------ | ----------- | ------------------------------------------ | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Level 4–5    | Enterprise  | SCADA Server / Historian                   | OSIsoft PI, AVEVA System Platform, Wonderware                     | Information Disclosure, Repudiation, Denial of Service, Elevation of Privilege         |
| Level 3      | Operations  | Engineering Workstation / OPC Server       | Siemens TIA Portal, Rockwell Studio 5000, OPC UA Server           | Spoofing, Tampering, Information Disclosure, Denial of Service, Elevation of Privilege |
| Level 2      | Supervisory | HMI / Operator Station                     | Siemens WinCC, FactoryTalk View SE, Inductive Automation Ignition | Spoofing, Tampering, Information Disclosure, Denial of Service                         |
| Level 1      | Control     | PLC / PAC                                  | Siemens S7, Allen-Bradley ControlLogix, Schneider Modicon         | Tampering, Denial of Service, Elevation of Privilege                                   |
| Level 0      | Field       | Sensors / Actuators / RTUs / Field Devices | Transmitters, positioners, motor drives, RTUs                     | Tampering, Denial of Service                                                           |

#### 5.2.2. Impact Mapping

Categorize the impact of the STRIDE categories using CVSS v4.0 Impact Metrics.

- Exploitability Metrics
  > Select the appropriate attack vector based on the physical and logical access requirements of the modeled interface.

  | Attack Vector     | OT/ICS Scenarios                                                                       | Example Interfaces                       |
  | ----------------- | -------------------------------------------------------------------------------------- | ---------------------------------------- |
  | `AV:N` (Network)  | IP-connected devices, remote SCADA, cloud-connected gateways                           | Modbus/TCP, EtherNet/IP, OPC UA, MQTT    |
  | `AV:A` (Adjacent) | Shared industrial bus, field network segment, same VLAN                                | Modbus RTU (RS-485), PROFIBUS, CAN       |
  | `AV:L` (Local)    | Workstation software, HMI application, locally-executed software or configuration tool | Engineering software, local DB           |
  | `AV:P` (Physical) | Direct cable connection, removable debug port, hardware tampering                      | RS-232, JTAG, SWD, USB, hardware buttons |

- Vulnerable System Impact Metrics
  > Map STRIDE categories to CVSS v4 Impact Metrics using the primary impact metrics to determine the base score and severity, and the secondary impact metrics to inform the justification and vector details. Metric abbreviations: `VC` = Vulnerable System Confidentiality Impact, `VI` = Vulnerable System Integrity Impact, `VA` = Vulnerable System Availability Impact.

  | STRIDE Category        | Primary Impact Metric | Secondary Impact Metric | Confidence  | Rationale                                                                                                                                                                                                                                                                                                                                                                                               |
  | ---------------------- | --------------------- | ----------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | Spoofing               | VI                    | VC                      | Medium      | Identity impersonation primarily corrupts trust and authorization decisions, which is best represented as integrity impact. Confidentiality is often a follow-on effect when impersonation grants access to protected data.                                                                                                                                                                             |
  | Tampering              | VI                    | VA, VC                  | High        | Unauthorized modification is directly an integrity impact. Availability and confidentiality may also be affected when tampering disrupts operation or alters protection controls.                                                                                                                                                                                                                       |
  | Repudiation            | VI                    | VC                      | Medium-Low  | CVSS has no explicit non-repudiation or auditability metric. Repudiation is therefore best represented through integrity harm to logs, records, and transaction evidence, with occasional secondary confidentiality implications.                                                                                                                                                                       |
  | Information Disclosure | VC                    | VI                      | High        | Unauthorized exposure of information is directly a confidentiality impact. Integrity is only indirect or downstream.                                                                                                                                                                                                                                                                                    |
  | Denial of Service      | VA                    | VI                      | High        | Service degradation or outage is directly an availability impact. Integrity may be secondarily affected where incomplete processing or inconsistent state results.                                                                                                                                                                                                                                      |
  | Elevation of Privilege | VI                    | VC, VA                  | Medium-High | Privilege gain commonly enables unauthorized modification and unauthorized access, making integrity and confidentiality primary. Availability is often a secondary consequence when elevated rights permit shutdown, deletion, or resource exhaustion. The primary impact depends on the privileges gained: <br>• _Read_ access → `VC`<br>• _Write_ access → `VI`<br>• _Admin/Execution_ access → `VA`. |

- Subsequent System Impact Metrics for OT/ICS
  > In OT/ICS environments, compromising one component often affects downstream systems. Use SC/SI/SA to capture cascading effects on the physical process, safety systems, or connected devices. Metric abbreviations: `SC` = Subsequent System Confidentiality Impact, `SI` = Subsequent System Integrity Impact, `SA` = Subsequent System Availability Impact. Values: `N` = None, `H` = High.

  | Scenario                                         | SC  | SI  | SA  | Rationale                                                                                                                      |
  | ------------------------------------------------ | --- | --- | --- | ------------------------------------------------------------------------------------------------------------------------------ |
  | Compromised PLC affects downstream actuators     | N   | H   | H   | PLC compromise enables unauthorized control of physical process, affecting integrity and availability of actuators and valves. |
  | Firmware tampering enables lateral movement      | H   | H   | H   | Compromised device can be used to attack other devices on same network segment.                                                |
  | Debug interface exposes firmware secrets         | H   | N   | N   | Extracted credentials or keys may compromise other devices using shared secrets.                                               |
  | DoS on communication interface                   | N   | N   | H   | Loss of communication causes upstream PLC to trigger fault handling or fail-safe mode.                                         |
  | Configuration change via engineering workstation | N   | H   | N   | Modified setpoints propagate to field devices, affecting process integrity.                                                    |

- Zero-Impact Assessment
  > Use a zero-impact CVSS outcome when the finalized reviewed scenario leaves no modeled impact.

  - `State = Not Applicable`: the attack path is impossible or structurally eliminated; pair this with `Risk Treatment = Avoidance`.
  - `State = Mitigated`: documented controls reduce the remaining impact to zero; pair this with `Risk Treatment = Mitigation` and explain the control in `Justification`.
  - Zero-impact does not make `Likelihood of Exploit` or `Risk Prioritization` inapplicable. For finalized reviewed rows, populate both columns from the mapping tables. When `State = Not Applicable`, treat the vulnerability state as `Theoretical` unless stronger exploit-maturity evidence exists, then derive likelihood from the CVSS exploitability metrics and derive prioritization from the `None` severity row in the risk matrix.

#### 5.2.3. Probability Mapping

Categorize the likelihood of exploit using the BSI `Dringlichkeit / Eintrittspotenzial` logic, which combines the exploitation method and vulnerability state to determine the overall likelihood category.

- Exploitation Method
  > Determine the exploitation method (columns) based on the modeled attack scenario and CVSS Exploitability Metrics.

  | Method                          | CVSS Exploitability Metrics              | Description                                                                                                      |
  | ------------------------------- | ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
  | Manual (Manuell)                | `AV:P`                                   | Requires direct physical device access. Any `AV:P` attack qualifies as Manual regardless of other metric values. |
  | Automated (Automatisch)         | `AV:A` or `AV:L`, `AC:L`, `AT:N`, `UI:N` | Adjacently or locally exploitable with low complexity and no user interaction.                                   |
  | Self-Replicating (Replizierend) | `AV:N`, `AC:L`, `AT:N`, `PR:N`, `UI:N`   | Network-reachable with zero friction and the scenario describes autonomous propagation behavior.                 |

  > [!NOTE]
  > `PR` (Privileges Required) is independent of the exploitation method in most cases. Do not change the method classification based on `PR` alone. Self-Replicating typically implies `PR:N` because autonomous propagation rarely depends on pre-existing credentials. For `AV:N` threats that do not explicitly describe autonomous propagation behavior, classify as `Automated`, not `Self-Replicating`.

- Vulnerability State
  > Determine the vulnerability state (rows) based on evidence of exploit maturity, which may come from the `Justification` field or from external sources such as threat intelligence, public exploit databases, or observed attack activity.

  | State                                      | CVSS Threat Metrics | Description                                                                                                                                                            |
  | ------------------------------------------ | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | Theoretical (Theoretisch)                  | `E:U`               | No known exploit; attack is conceptually possible but unverified.                                                                                                      |
  | Exploitable (Ausnutzbar)                   | `E:P`               | Proof-of-concept exists or the technique is documented and reproducible.                                                                                               |
  | Active (Aktiv)                             | `E:A`               | Active exploitation observed in the wild or in targeted campaigns.                                                                                                     |
  | Exploit Published (Exploit Veröffentlicht) | `E:A`               | Public exploit code or tooling is freely available. Prefer Exploit Published over Active when a public exploit tool or module is directly usable without modification. |

- Likelihood Matrix

  | State / Method                             | Manual (Manuell)   | Automated (Automatisch) | Self-Replicating (Replizierend) |
  | ------------------------------------------ | ------------------ | ----------------------- | ------------------------------- |
  | Theoretical (Theoretisch)                  | Info (sehr gering) | Low (gering)            | Medium (mittel)                 |
  | Exploitable (Ausnutzbar)                   | Low (gering)       | Medium (mittel)         | High (hoch)                     |
  | Active (Aktiv)                             | Medium (mittel)    | High (hoch)             | High (hoch)                     |
  | Exploit Published (Exploit Veröffentlicht) | Medium (mittel)    | High (hoch)             | Critical (sehr hoch)            |

#### 5.2.4. Risk Matrix Mapping

The risk matrix provides a mapping of impact severity and likelihood to a risk prioritization category. Use this as a guide to assign the appropriate prioritization level based on the combined assessment of impact severity and likelihood.

  > [!NOTE]
  > Combine information from `BSI Likelihood of Exploit` (Probability) and `CVSS v4.0 Severity` (Impact) to determine a risk prioritization level for each threat.

  | Probability \ Impact | None   | Low    | Medium | High     | Critical |
  | -------------------- | ------ | ------ | ------ | -------- | -------- |
  | Info                 | Info   | Info   | Low    | Low      | Medium   |
  | Low                  | Info   | Low    | Low    | Medium   | High     |
  | Medium               | Low    | Low    | Medium | High     | High     |
  | High                 | Low    | Medium | High   | High     | Critical |
  | Critical             | Medium | High   | High   | Critical | Critical |

#### 5.2.5. Threat Actor Mapping

Normalize the `Threat Actor` decision from common OT/ICS threat-path characteristics. Always pick the minimum actor that satisfies the required access, capability, and process knowledge, and only reassess upward when the modeled path requires capabilities beyond the currently selected label.

> [!NOTE]
> Actor capability order from lowest to highest: `Thrill Seeker` → `Hacktivist` → `Cybercriminal` → `Insider Threat` → `Nation-State Actor`.

| Minimum Threat Actor | Attack Path / Scenario                                                                                                                                | Key Indicators                                                                                                                                                                                                                          |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Thrill Seeker`      | Internet-exposed service with public exploit, default credentials, or unauthenticated interface                                                       | `AV:N`, `AC:L`; pre-built tooling; no plant-specific knowledge; opportunistic targeting or commodity compromise path                                                                                                                    |
| `Hacktivist`         | Internet-exposed HMI, SCADA web UI, or public-facing OT asset targeted for ideological messaging, defacement, or symbolic proof-of-access             | `AV:N`; visible, high-profile target; protest or propaganda objective; short-lived campaign; no persistent access sought                                                                                                                |
| `Cybercriminal`      | Internet-exposed service or IT/OT boundary exploited for financial gain: ransomware staging, credential theft, extortion, or fraud                    | IT-to-OT pivot; commodity or affiliate malware; stolen or phished credentials; business disruption for payment                                                                                                                          |
| `Cybercriminal`      | Compromised vendor tooling, update service, or MSP remote-management channel reused for scalable extortion or ransomware deployment                   | Third-party trust dependency; monetized supply-chain reuse; commodity ransomware payload; no mission-specific objective                                                                                                                 |
| `Insider Threat`     | Trusted maintenance path, local engineering workstation, removable media, direct cable or debug interface, or privileged badge access                 | `AV:P` or `AV:L` only when initial access is a local or physical session, not a post-exploitation pivot from prior network access; trusted plant or engineering access; process familiarity; maintenance tooling or insider credentials |
| `Nation-State Actor` | Trojanized engineering software, signed firmware package, or tainted vendor update used for covert pre-positioning or mission-specific sabotage       | Supply-chain compromise; custom or signed tooling; covert persistence objective; strategic or safety-critical target                                                                                                                    |
| `Nation-State Actor` | Bespoke multi-stage intrusion against a segmented ICS requiring custom tooling, zero-day exploits, covert lateral movement, or deep process expertise | Custom tradecraft; zero-days; long-dwell access; strategic high-value target; objective is disruption, sabotage, or pre-positioning                                                                                                    |

> [!NOTE]
> When supply-chain compromise is the modeled vector: choose `Cybercriminal` when the payload is commodity ransomware or the objective is financial extortion; choose `Nation-State Actor` when tooling is custom-signed or the objective is strategic pre-positioning or sabotage.

#### 5.2.6. Risk Treatment Mapping

The Risk Treatment Mapping translates the `Risk Prioritization` level into a default treatment decision and defines which alternative treatments are acceptable and under what conditions. It is the bridge between the technical risk score and the governance disposition recorded in the `Risk Treatment` column.

> [!NOTE]
> Rows where `Risk Treatment = Avoidance` (risk source structurally eliminated) bypass this mapping: no residual risk remains, `Risk Approval = Not Required`, and no further treatment evidence is needed beyond the architectural record in `Justification`.

- Treatment Decision Guidance
  > Select the **Default Treatment** for the row's `Risk Prioritization` level. Deviate to an **Acceptable Alternative** only when documented evidence supports the deviation and the rationale is recorded in `Justification`. Conditions that prohibit certain treatments are mandatory constraints.

  | Risk Prioritization | Default Treatment | Acceptable Alternatives | Conditions and Constraints                                                                                                                                                                                                    |
  | ------------------- | ----------------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | Info                | Avoidance         | Acceptance              | Attack path is architecturally impossible, structurally eliminated, or no longer present in the assessed design. Risk is negligible. No security control investment is warranted.                                             |
  | Low                 | Acceptance        | Avoidance, Mitigation   | Low-cost compensating controls are encouraged. Transfer is not warranted at this level. Risk remains intentionally retained without additional controls.                                                                      |
  | Medium              | Mitigation        | Acceptance, Transfer    | Controls must address the root weakness. Controls or compensating measures reduce the risk to an acceptable residual level. Transfer requires named SLA or policy. Consequence ownership is formally shifted to a third party |
  | High                | Mitigation        | Avoidance, Transfer     | Acceptance is restricted to exceptional cases with CPSO approval and written justification. Avoidance is preferred when structurally feasible.                                                                                |
  | Critical            | Avoidance         | Mitigation, Transfer    | Acceptance is prohibited unless approved by Executive / Management with documented rationale. Uncontrolled residual risk is not permitted at this level.                                                                      |

- Treatment Evidence Requirements
  > The following evidence types are required in `Justification` to support the selected `Risk Treatment`. This evidence must be present before recording the `Risk Approval` column.

  | Risk Treatment | Minimum Evidence in `Justification`                                                                                                |
  | -------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
  | Avoidance      | Architectural record or documented design decision confirming the risk source has been eliminated; no stakeholder sign-off needed. |
  | Mitigation     | The residual risk level after controls are applied, and the approval mechanism.                                                    |
  | Acceptance     | Written business rationale for retention, and the acceptance mechanism.                                                            |
  | Transfer       | Named third party, the specific contract, SLA, warranty, or insurance policy reference, and its explicit risk scope.               |

#### 5.2.7. Risk Approval Mapping

The minimum required approval authority is determined by combining the `Risk Prioritization` level with the `Risk Treatment` decision. The `Risk Approval` column records the required **approver role label**. Consult this section to look up the required authority and record the corresponding role label in the column.

- Risk Approval
  > Select the cell at the intersection of the `Risk Prioritization` (rows) and `Risk Treatment` (columns) to identify the minimum required approval authority. Record the role label directly in the `Risk Approval` column.

  | Prioritization / Treatment | Avoidance    | Mitigation       | Acceptance       | Transfer         |
  | -------------------------- | ------------ | ---------------- | ---------------- | ---------------- |
  | Info                       | Not Required | Lead Security    | Lead Security    | Lead Security    |
  | Low                        | Not Required | Lead Security    | Lead Security    | Lead Security    |
  | Medium                     | Not Required | Product Security | Product Security | Product Security |
  | High                       | Not Required | CPSO             | CPSO             | CPSO             |
  | Critical                   | Not Required | Executive        | Executive        | Executive        |

- Approval Authority Roles
  > Define the following stakeholder roles for risk approval.

  | Role Label       | Typical Title or Function                                                                        |
  | ---------------- | ------------------------------------------------------------------------------------------------ |
  | Not Required     | Risk structurally eliminated, no residual risk remains.                                          |
  | Lead Security    | Technical lead, security engineer, or equivalent responsible for the design area.                |
  | Product Security | Product security officer, security architect, or equivalent with cross-functional authority.     |
  | CPSO             | CPSO, or equivalent with organizational risk management authority.                               |
  | Executive        | C-level executive, risk committee, or board-level function with final risk acceptance authority. |

### 5.3. Template

Use these templates for Microsoft TMT CSV intake and review.

#### 5.3.1. Raw TMT Export CSV Template

- `<Device_Name>_Threat_Model.csv`
  > The raw export from Microsoft TMT in comma delimited CSV format.

  ```csv
  Id,Title,Category,Diagram,Interaction,Priority,State,Changed By,Description,Justification,Last Modified
  0,Spoofing the MCU Process,Spoofing,<Device_Name>,Debugger to MCU over JTAG,High,Not Started,,MCU may be spoofed by an attacker and this may lead to information disclosure by Debugger Probe. Consider using a standard authentication mechanism to identify the destination process.,,Generated
  11,Spoofing the RS-485 Interface Process,Spoofing,<Device_Name>,PLC to RS-485 (Modbus RTU),High,Not Started,,RS-485 Interface may be spoofed by an attacker and this may lead to information disclosure by PLC. Consider using a standard authentication mechanism to identify the destination process.,,Generated
  38,Data Flow MCU to CFG over Modbus RTU (RS-232) Is Potentially Interrupted,Denial Of Service,<Device_Name>,MCU to CFG over Modbus RTU (RS-232),High,Not Started,,An external agent interrupts data flowing across a trust boundary in either direction.,,Generated
  72,Elevation Using Impersonation,Elevation Of Privilege,<Device_Name>,Operator to MCU over Switches (GPIO),High,Not Started,,MCU may be able to impersonate the context of Operator in order to gain additional privilege.,,Generated
  ```

#### 5.3.2. Generated TMT CSV Template

- `<Device_Name>_Threat_Model_Generated.csv`
  > The completed security review of the raw TMT export in semicolon delimited CSV format with appended columns.

  ```csv
  Id;Title;Category;Diagram;Interaction;Priority;State;Changed By;Description;Justification;Last Modified;ATT&CK ID;EMB3D TID;CWE ID;CVSS v4.0 Vector;CVSS-B v4.0 Score;CVSS v4.0 Severity;Likelihood of Exploit;Risk Prioritization;Threat Actor;Risk Treatment;Risk Approval
  0;Spoofing the MCU Process;Spoofing;<Device_Name>;Debugger to MCU over JTAG;Low;Not Applicable;;MCU may be spoofed by an attacker and this may lead to information disclosure by Debugger Probe. Consider using a standard authentication mechanism to identify the destination process.;"The MCU firmware is the target of the JTAG debug session, not a process with an identity to spoof. Evidence for Threat Actor classification is physical debug-port dependency, requirement for direct maintenance access, and absence of any remote network precondition. That profile matches Insider Threat as the minimum actor because trusted local access is required.";Generated;T0843;TID-116, TID-119;CWE-1191;CVSS:4.0/AV:P/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:N/SA:N;"0,0";None;Info;Info;Insider Threat;Avoidance;Not Required
  11;Spoofing the RS-485 Interface Process;Spoofing;<Device_Name>;PLC to RS-485 (Modbus RTU);Medium;Needs Investigation;;RS-485 Interface may be spoofed by an attacker and this may lead to information disclosure by PLC. Consider using a standard authentication mechanism to identify the destination process.;Modbus RTU on RS-485 has no built-in authentication mechanism and spoofing is feasible from the same bus segment. Evidence for Threat Actor classification is protocol-level OT knowledge requirement with no need for plant-specific sabotage tradecraft, which maps to Cybercriminal as the minimum actor. Whether the RS-485 module is installed and physically reachable is still unknown, so treatment and approval remain unresolved until deployment evidence confirms scope.;Generated;T0802;TID-118;CWE-287;CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N;"4,3";Medium;Medium;Medium;Cybercriminal;Mitigation;Product Security
  38;Data Flow MCU to CFG over Modbus RTU (RS-232) Is Potentially Interrupted;Denial Of Service;<Device_Name>;MCU to CFG over Modbus RTU (RS-232);Low;Mitigated;;"An external agent interrupts data flowing across a trust boundary in either direction.";"This RS-232 interruption affects a local maintenance session more than the primary control function. Evidence for Threat Actor classification is direct cable proximity, maintenance-port handling, and local physical access constraints, which makes Insider Threat the minimum actor. Baseline mitigation includes physical port isolation and cable shielding, and residual risk remains Low with closure via design-review sign-off.";Generated;T0814;TID-118;CWE-693;CVSS:4.0/AV:P/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:L;"2,4";Low;Low;Low;Insider Threat;Mitigation;Lead Security
  72;Elevation Using Impersonation;Elevation Of Privilege;<Device_Name>;Operator to MCU over Switches (GPIO);Low;Not Applicable;;"MCU may be able to impersonate the context of Operator in order to gain additional privilege.";"The dry-contact GPIO path has no machine-to-machine trust boundary the MCU can impersonate and no device property enables software privilege escalation on this passive signal path. Evidence for Threat Actor classification is that only local operator-side interaction could influence the interface, which maps to Insider Threat as the minimum actor under constraints access. Treatment remains Avoidance by keeping the interface free of machine-authenticated trust assumptions.";Generated;N/A;N/A;N/A;CVSS:4.0/AV:P/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:N/SA:N;"0,0";None;Info;Info;Insider Threat;Avoidance;Not Required
  ```

## 6. References

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
