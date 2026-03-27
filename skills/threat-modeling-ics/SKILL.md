---
name: threat-modeling-ics
description: Performs end-to-end threat modeling for OT/ICS systems from Microsoft Threat Modeling Tool (TMT) threat-list exports (`*.csv`) and model files (`*.tm7`). Uses TMT and STRIDE for initial threat enumeration, then enriches each threat with OT/ICS context, MITRE ATT&CK for ICS mappings, CWE weakness classification, CVSS v4.0 scoring, and mitigation planning. Use when triaging, validating, or completing Microsoft TMT threat outputs without converting them into a separate domain-specific schema.
metadata:
  version: "1.1.0"
  activation:
    implicit: true
    priority: 1
    triggers:
      - "microsoft tmt"
      - "threat modeling"
      - "stride"
      - "mitre att&ck"
      - "cwe"
      - "cvss"
      - "threat review"
    match:
      languages: ["markdown", "csv"]
      paths:
        - "**/*.tm7"
        - "**/*threat-model*.csv"
        - "**/*threat-model*.md"
      prompt_regex: "(?i)(microsoft tmt|threat modeling|stride|mitre att&ck|cwe|cvss|threat review)"
  usage:
    load_on_prompt: true
    autodispatch: true
---

# Threat Modeling ICS

Instructions for AI security agents reviewing Microsoft Threat Modeling Tool threat-list exports.

> [!NOTE]
> Treat the Microsoft TMT CSV as the primary artifact. Preserve native TMT identifiers, titles, categories, descriptions, priorities, states, and analyst-entered notes. Perform review by appending new columns to the exported dataset rather than rewriting the model into a different structure.

> [!NOTE]
> When a Mermaid diagram is absent, a Microsoft TMT model file (`*.tm7`) is an acceptable architecture source. Extract system elements, trust boundaries, interfaces, and data flows from the model before reviewing the CSV.

- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
- [3. Frameworks](#3-frameworks)
  - [3.1. Microsoft Threat Modeling Tool](#31-microsoft-threat-modeling-tool)
  - [3.2. STRIDE](#32-stride)
  - [3.3. MITRE ATT\&CK](#33-mitre-attck)
  - [3.4. CWE](#34-cwe)
  - [3.5. CVSS](#35-cvss)
  - [3.6. BSI Likelihood of Exploit](#36-bsi-likelihood-of-exploit)
- [4. Workflow](#4-workflow)
  - [4.1. Preparation](#41-preparation)
  - [4.2. Row-by-Row Review](#42-row-by-row-review)
  - [4.3. Output](#43-output)
- [5. Deliverables](#5-deliverables)
- [6. Style Guide](#6-style-guide)
- [7. Example](#7-example)
  - [7.1. Threat Model Diagram](#71-threat-model-diagram)
    - [7.1.1. Depth Layer 0 (System)](#711-depth-layer-0-system)
    - [7.1.2. Depth Layer 1 (Process)](#712-depth-layer-1-process)
- [8. Template](#8-template)
  - [8.1. Raw TMT Export CSV Template](#81-raw-tmt-export-csv-template)
  - [8.2. Reviewed TMT CSV Template](#82-reviewed-tmt-csv-template)
- [9. References](#9-references)

## 1. Benefits

- Safety-aware analysis
  > Captures not only cyber compromise, but also the potential physical-process, human-safety, environmental, quality, and availability consequences of a successful attack.

- End-to-End Traceability
  > Connects architecture elements, trust boundaries, threats, attacker behaviors, underlying weaknesses, severity scoring, and mitigations in a single workflow.

- Prioritization
  > Produces repeatable severity and remediation guidance that can feed security backlogs, engineering changes, exception reviews, and residual-risk decisions.

## 2. Principles

- CIA Triad
  > Focus on Confidentiality, Integrity, and Availability to ensure comprehensive security coverage.

- Purdue Model
  > Use the Purdue Model to classify assets, zones, and levels for accurate OT/ICS context.

- Diagram Depth Layers
  > Use Microsoft [diagram depth layers](https://learn.microsoft.com/en-us/training/modules/tm-provide-context-with-the-right-depth-layer/1b-depth-layers) when creating or validating the threat model diagram.

  > [!NOTE]
  > Most diagrams should include at least Layers 0 and 1, use Layers 2 and 3 when system criticality and security-review requirements justify deeper decomposition.

  - Layer 0 (`System`)
    > System layer for high-level architecture and trust boundaries between major zones or subsystems interactions.

  - Layer 1 (`Process`)
    > Process layer for process-level data flows in each major part.

  - Layer 2 (`Subprocess`)
    > Subprocess layer for critical system subparts.

  - Layer 3 (`Lower-Level`)
    > Lower-Level layer for highly critical or kernel-level detail.

## 3. Frameworks

### 3.1. Microsoft Threat Modeling Tool

Use Microsoft Threat Modeling Tool (TMT) as the source of truth for the initial threat inventory.

- Source of Record
  > The exported TMT CSV is the working dataset. Do not replace the exported row structure with a custom register unless explicitly requested.

- Preservation Rule
  > Keep native TMT fields exactly as exported whenever possible, including header names, row order, identifiers, titles, category values, and descriptions.

- Review Rule
  > Review is additive. Append analyst review fields after the native export columns.

- Model Evidence Rule
  > When both `*.tm7` and CSV are available, use the TM7 model to validate whether a generated threat matches the actual architecture before assigning `Not Applicable`, CWE, CVSS, or mitigation status.

### 3.2. STRIDE

Use STRIDE as the taxonomy for the initial threat statements generated by TMT.

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

MITRE ATT&CK for ICS to map a TMT threat to realistic adversary behavior affecting industrial environments.

- [Tactics](https://attack.mitre.org/tactics/ics/) and [Techniques](https://attack.mitre.org/techniques/ics/)
  > Record the most relevant ATT&CK for ICS tactic and technique IDs for access, execution, discovery, lateral movement, command and control, impair process control, inhibit response function, and impact.

  > [!NOTE]
  > Add a MITRE technique ID only when the threat statement and justification support a concrete technique or sub-technique. Leave the MITRE field blank when the row is too generic, ambiguous, or purely design-level without a reliable ATT&CK mapping.

- Common OT/ICS Technique Mappings
  > Use these technique mappings as a reference for common OT/ICS threat scenarios.

  | Technique ID | Technique Name                        | Scenarios                                                                                                        |
  | ------------ | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
  | T0859        | Valid Accounts / Unauthorized Command | Spoofing PLC/HMI identity on unauthenticated protocols (Modbus, DNP3). Device accepts commands from any source.  |
  | T0855        | Unauthorized Command Message          | Sending malformed or out-of-range values via industrial protocols to manipulate process variables.               |
  | T0814        | Denial of Service                     | Bus contention, frame flooding, communication disruption on serial or network interfaces.                        |
  | T0843        | Program Download / Code Injection     | Exploiting firmware update mechanisms, buffer overflows, or protocol parsing vulnerabilities for code execution. |
  | T0801        | Monitor Process State                 | Passive eavesdropping on unencrypted industrial protocols (Modbus RTU/TCP, SSP, proprietary serial).             |
  | T0852        | Screen Capture / Replay               | Capturing and replaying valid protocol messages when no sequence numbers or timestamps exist.                    |
  | T0842        | Hardware Debug                        | Exploiting JTAG, SWD, or UART debug interfaces for firmware extraction or modification.                          |
  | T0831        | Manipulation of Control               | Issuing unauthorized setpoint changes or mode transitions via compromised HMI or protocol injection.             |

### 3.4. CWE

Use [MITRE CWE](https://cwe.mitre.org/) to classify the underlying weakness that enables the threat.

- Weakness Rule
  > Prefer the most specific CWE supported by the row description and analyst justification.

- Multi-CWE Rule
  > Multiple CWE IDs may be recorded when the reviewed finding depends on more than one concrete weakness.

### 3.5. CVSS

Use [FIRST CVSS v4.0](https://www.first.org/cvss/) to score each reviewed threat when a meaningful exploitability and impact assessment can be made.

- [CVSS Calculation](https://www.first.org/cvss/calculator/4.0)
  > Use the CVSS v4.0 calculator to determine the base score, severity, and vector based on the modeled attack scenario and review rationale.

- CVSS Score
  > Record the CVSS v4.0 base score as a numeric value between `0.0` and `10.0` when the evidence supports a defensible score.

- CVSS Severity
  > Record the CVSS v4.0 severity category (`None`, `Low`, `Medium`, `High`, `Critical`) when a base score is recorded.

- CVSS Vector
  > Record the CVSS v4.0 vector string (`CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:N/SA:N`) when a base score is recorded.

- Base Metrics
  > Score the intrinsic characteristics of the exploitable condition.

- Rationale Rule
  > The justification text should make the selected vector understandable from the modeled interaction and threat description.

### 3.6. BSI Likelihood of Exploit

Use the [BSI Dringlichkeit / Eintrittspotenzial](https://www.bsi.bund.de/DE/Service-Navi/Abonnements/Newsletter/Buerger-CERT-Abos/Buerger-CERT-Sicherheitshinweise/Risikostufen/risikostufen.html) logic to determine the likelihood of exploit when the dataset provides enough evidence to classify exploit status and exploitation style.

1. Exploitation Method

    - Manual (Manuell)
      > The attacker must perform non-automatable steps to adapt the attack to the target. Requires skill and effort.

    - Automated (Automatisch)
      > The exploit can be run using a script or tool against many targets.

    - Self-replicating (Replizierend)
      > The exploit can spread automatically without user interaction (e.g., worms, bots). Compromised systems attack further systems autonomously.

2. Vulnerability State

    - Theoretical (Theoretisch)
      > A flaw is discovered that could lead to a security issue, but no concrete exploit exists.

    - Exploitable (Ausnutzbar)
      > A proof-of-concept or reliable method to exploit the vulnerability exists.

    - Active (Aktiv)
      > Evidence exists that the vulnerability is already being exploited in the wild.

    - Exploit Published (Exploit Veröffentlicht)
      > A public attack tool has been released, the effort to attack drops significantly.

## 4. Workflow

> [!IMPORTANT]
> Execute every step below in order. Do not skip, reorder, or merge steps. Stop at any blocking gate and wait for user input before continuing. Resume from the blocked step once input is received; do not restart from step 1.

> [!NOTE]
> Save intermediate results after each step to ensure continuity across steps.

### 4.1. Preparation

1. Locate or create the threat model diagram

    **Action:** Locate or create the threat model diagram for the target OT/ICS system.
    - Search the current context for a Mermaid diagram file. Prefer filenames such as `<device-name>-threat-model.md`.
    - If a diagram file is found, extract architecture elements, trust boundaries, data flows, and interfaces from it.
    - If no Mermaid diagram is found, search for a Microsoft TMT model file (`*.tm7`) and extract the same architecture evidence from the model.
    - **Blocking gate:** If no diagram is available, ask the user to provide one of the following before continuing:
      - A Mermaid diagram file path.
      - A Microsoft TMT model file path (`*.tm7`).
      - External documentation or links describing the system architecture.
      - A textual description of the system components and trust relationships sufficient to draft a Mermaid diagram.
    - Draft the Mermaid diagram from the provided input if one does not already exist, and save it as `<device-name>-threat-model.md`.
    - If the source is a TM7 file, normalize names and labels only enough to make the diagram readable, but preserve the modeled trust boundaries, interfaces, and flow directions.
    - Do not proceed to step 2 until the diagram is available or the user explicitly waives this step.

2. Identify and classify the input CSV

    **Action:** Locate the input CSV and classify it before any review work begins.
    - Locate the input CSV. Prefer filenames such as `<device-name>-threat-model.csv` and `<device-name>-threat-model-review.csv`, but rely on the header row rather than the filename alone to determine artifact type.
    - Classify the artifact as one of: raw TMT export, partially reviewed file, or completed review file.
    - **Blocking gate:** If no CSV is available, ask the user to provide the exported TMT CSV before continuing.
    - Do not proceed to step 3 until the artifact type is confirmed.

3. Detect native TMT columns

    **Action:** Identify and record the native TMT column set present in the input file.
    - Confirm that the header row contains native TMT fields. Expect fields such as:
      - `Id`
      - `Title`
      - `Category`
      - `Diagram`
      - `Interaction`
      - `Priority`
      - `State`
      - `Changed By`
      - `Description`
      - `Justification`
      - `Last Modified`

    - Record the exact source header spelling and column order as found in the file. Use this record for all subsequent output.

4. Detect existing review columns

    **Action:** Determine which review columns, if any, are already appended to the native TMT columns.
    - Check whether any of the following review fields are present in the CSV identified in step 2:
      - `MITRE ID`
      - `CWE ID`
      - `CVSS v4.0 Vector`
      - `CVSS v4.0 Score`
      - `CVSS v4.0 Severity`
      - `Likelihood of Exploit`
      - `Risk Prioritization`

    - If those columns already exist, update them in place for each row rather than adding duplicate columns.
    - If they are absent, append them to the right of the last native TMT column in the output file.

5. Establish preservation constraints

    **Action:** Lock descriptive TMT columns against modification before beginning row review.
    - Do not delete any native TMT column.
    - Do not overwrite the values in `Title`, `Category`, `Description`, or `Interaction` with rewritten text.
    - The operational fields `State`, `Priority`, and `Justification` may be updated during row review (steps 8–10) as these reflect analyst decisions rather than original TMT-generated content.

6. Establish evidence thresholds

    **Action:** Define what evidence is required before filling analyst fields.
    - Do not assign `Not Applicable` unless the row conflicts with an architecture fact visible in the diagram, TM7 model, or provided documentation. Name that fact in `Justification`.
    - Do not assign MITRE ATT&CK, CWE, CVSS, or `Likelihood of Exploit` from the STRIDE category or title alone. Require support from the modeled protocol, interface behavior, privilege boundary, or component capability.
    - Do not bulk-apply a single score, likelihood, or state to every row in an interaction family without checking whether the specific row changes the target, impact path, or exploit preconditions.
    - If evidence is insufficient, prefer `Needs Investigation` and blank review fields over a templated or forced value.

    **Common Not Applicable Patterns for OT/ICS:**

    > Use these patterns as guidance for efficiently classifying structurally inapplicable threats. Always cite the specific architectural fact in the justification.

    | Pattern                                  | Applicable Threat Types                         | Justification Template                                                                                                  |
    | ---------------------------------------- | ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
    | Passive hardware (motor, valve, sensor)  | Impersonation, code execution, memory tampering | `<Component> is a passive <actuator/sensor> with no execution context or identity. Cannot <impersonate/execute code>.`  |
    | Analog signal path                       | Replay, collision, packet-based attacks         | `<Interface> transmits continuous analog signals, not discrete messages. <Threat type> requires packet-based protocol.` |
    | Point-to-point serial (RS-232, UART)     | Collision attacks, data overlap                 | `<Interface> is point-to-point serial. No packet reassembly or shared medium. Collision attacks do not apply.`          |
    | Internal device flow (MCU to peripheral) | External spoofing, network sniffing             | `Internal <bus type> flow within device boundary. No external access path for <threat type>.`                           |
    | Privilege direction mismatch             | Lower impersonating higher                      | `<Higher component> has greater privilege than <lower component>. Impersonation yields no privilege escalation.`        |
    | Local GUI interaction                    | Network sniffing, remote interruption           | `GUI interaction is local to workstation. No network data flow to intercept.`                                           |
    | Development/debug interface (production) | Debug session interruption                      | `<Debug interface> is development tool. Interruption affects development session, not production operation.`            |
    | I2C/SPI slave device                     | Master impersonation, autonomous action         | `<Slave device> responds only to master requests. No autonomous action or impersonation capability.`                    |

### 4.2. Row-by-Row Review

7. Read each row

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
      > The initial risk ranking assigned by TMT. Treat as a reference point only; the analyst review in steps 8–15 may revise it.
    - `State`
      > The current review status of the threat. Update it in step 8.

    Perform steps 8–15 for every row before proceeding to step 16. Leave review fields blank when sufficient evidence is not available; a blank is correct when the evidence is insufficient, and a forced mapping is not.

    **Interaction Family Batching:**
    > When the dataset contains many rows for the same interaction (e.g., multiple STRIDE categories for `PLC to RS-485 (Modbus RTU)`), process them as a group to maintain consistency. However, each row still requires individual assessment of:
    >
    > - Whether the specific STRIDE category applies to this interface (e.g., collision attacks may not apply to point-to-point serial)
    > - The appropriate CVSS impact metrics for this specific threat type
    > - Whether the row is `Not Applicable` due to architectural constraints

8. Review or update `State`

   **Action:** Set the `State` field for each row based on `Title`, `Category`, `Interaction`, `Description`, and the analyst's review of the threat.
   - Use the state vocabulary already present in the file.
     - `Not Started`
       > The threat has not yet been reviewed by an analyst. This is the default state for all rows in a raw TMT export.
     - `Needs Investigation`
       > The threat requires further analysis, information gathering, or clarification before a decision can be made.
     - `Mitigated`
       > The threat is accepted but mitigated through design changes, compensating controls, or operational measures.
     - `Not Applicable`
       > The threat is not relevant to the system context or is already fully addressed by existing controls.
     - `Transferred`
       > The risk is accepted but transferred to a third party (e.g., insurance, vendor responsibility).

   - Default decision rule:
     - Use `Needs Investigation` when the threat is plausible but controls, exploitability, or impact cannot yet be confirmed.
     - Use `Not Applicable` only when the row is contradicted by the architecture or by the semantics of the modeled component.

9. Set or update `Priority`

    **Action:** Revise the `Priority` field for each row based on `Title`, `Category`, `Interaction`, `Description`, and the analyst's review of the threat.
    - Use the priority vocabulary already present in the file.
     - `Low`
       > The threat is accepted with minimal concern. No immediate action is required, but it should be monitored for changes.
     - `Medium`
       > Mitigation planning should be initiated, and the threat should be tracked in the security backlog.
     - `High`
       > The threat is significant and requires prompt mitigation. It should be prioritized in the security backlog and may require escalation.

   - Do not downgrade a row to `Low` solely because the threat is physically local. In OT/ICS systems, local or adjacent access may still be operationally significant.

10. Write or update `Justification`

    **Action:** Write a concise, technically grounded analyst statement in the `Justification` field for each row.

    - State why the threat is accepted, mitigated, transferred, not applicable, or still under investigation.
    - Reference the modeled protocol, interface, trust relationship, validation behavior, or compensating control that informs the decision.
    - When using `Not Applicable`, name the specific architecture contradiction (e.g., passive sensor, analog signal path, human actor rather than machine endpoint, or no independent execution context).
    - Keep the text brief enough to remain readable in a CSV cell.

11. Map MITRE ATT&CK

    **Action:** Populate the `MITRE ID` field for each row when a concrete ATT&CK for ICS technique can be supported by the row contents and justification.
    - Record the most relevant ATT&CK for ICS tactic and technique ID (e.g., `T0856`).
    - Prefer MITRE ATT&CK for ICS techniques that describe industrial access, command messaging, engineering workstation abuse, controller compromise, inhibit response function, or impair process control.
    - Leave the field blank when the threat statement is too generic, ambiguous, or design-level to support a reliable mapping. A blank is correct; a forced mapping is not.

12. Classify CWE

    **Action:** Populate the `CWE ID` field for each row when the root weakness is identifiable from the threat statement and justification.
    - Prefer the most specific CWE that fits the described weakness.
    - Use comma-separated values when the finding depends on more than one concrete weakness (e.g., `CWE-290, CWE-345`).
    - Do not assign a CWE when the row is generic but the underlying weakness is still unclear after reviewing the modeled interaction.
    - Leave the field blank when the evidence is insufficient.

13. Score CVSS v4.0

    **Action:** Populate `CVSS v4.0 Vector`, `CVSS v4.0 Score`, and `CVSS v4.0 Severity` together for each row when the exploitability and impact can be assessed.
    - All three fields must be populated together or left blank together. Do not record a severity without a vector. Do not record a vector without a score.
    - Derive the score from the [CVSS v4.0 calculator](https://www.first.org/cvss/calculator/4.0) using the modeled attack scenario and justification as input.
    - Record the base score (`0.0`–`10.0`), the severity label (`None`, `Low`, `Medium`, `High`, `Critical`), and the full vector string (e.g., `CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:H/SA:H`).
    - Do not derive a CVSS vector from the STRIDE category alone. Confirm the actual access path (`AV`), attacker friction (`AC`, `AT`, `UI`), and safety/availability consequences from the modeled interaction.
    - When the target is a human actor, passive peripheral, or purely analog/mechanical path, only score the row if the exploit scenario and affected digital asset are still technically coherent.

    **OT/ICS Attack Vector Guidelines:**
    > Select the appropriate attack vector based on the physical and logical access requirements of the modeled interface.

    | Attack Vector     | OT/ICS Scenarios                                                  | Example Interfaces                          |
    | ----------------- | ----------------------------------------------------------------- | ------------------------------------------- |
    | `AV:N` (Network)  | IP-connected devices, remote SCADA, cloud-connected gateways      | Modbus/TCP, EtherNet/IP, OPC UA, MQTT       |
    | `AV:A` (Adjacent) | Shared industrial bus, field network segment, same VLAN           | Modbus RTU (RS-485 bus), PROFIBUS, CAN bus  |
    | `AV:L` (Local)    | Workstation software, HMI application, local file access          | TROVIS-VIEW, engineering software, local DB |
    | `AV:P` (Physical) | Direct cable connection, removable debug port, hardware tampering | RS-232, JTAG, SWD, USB, hardware buttons    |

    **Subsequent System Impact (SC/SI/SA) for OT/ICS:**
    > In OT/ICS environments, compromising one component often affects downstream systems. Use SC/SI/SA to capture cascading effects on the physical process, safety systems, or connected devices.

    | Scenario                                         | SC  | SI  | SA  | Rationale                                                                                                                      |
    | ------------------------------------------------ | --- | --- | --- | ------------------------------------------------------------------------------------------------------------------------------ |
    | Compromised PLC affects downstream actuators     | N   | H   | H   | PLC compromise enables unauthorized control of physical process, affecting integrity and availability of actuators and valves. |
    | Firmware tampering enables lateral movement      | H   | H   | H   | Compromised device can be used to attack other devices on same network segment.                                                |
    | Debug interface exposes firmware secrets         | H   | N   | N   | Extracted credentials or keys may compromise other devices using shared secrets.                                               |
    | DoS on communication interface                   | N   | N   | H   | Loss of communication causes upstream PLC to trigger fault handling or fail-safe mode.                                         |
    | Configuration change via engineering workstation | N   | H   | N   | Modified setpoints propagate to field devices, affecting process integrity.                                                    |

    **Mapping:** Map STRIDE categories to CVSS v4 Impact Metrics using the primary impact metrics to determine the base score and severity, and the secondary impact metrics to inform the justification and vector details.

    CVSS v4 Vulnerable System Impact Metrics
    - VC = Vulnerable System Confidentiality
    - VI = Vulnerable System Integrity
    - VA = Vulnerable System Availability

    | STRIDE Category            | Primary CVSS v4 Impact Metrics | Secondary CVSS v4 Impact Metrics | Confidence      | Rationale                                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | -------------------------- | ------------------------------ | -------------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | **Spoofing**               | **VI**                         | **VC**                           | **Medium**      | Identity impersonation primarily corrupts trust and authorization decisions, which is best represented as integrity impact. Confidentiality is often a follow-on effect when impersonation grants access to protected data.                                                                                                                                                                                                                 |
    | **Tampering**              | **VI**                         | **VA, VC**                       | **High**        | Unauthorized modification is directly an integrity impact. Availability and confidentiality may also be affected when tampering disrupts operation or alters protection controls.                                                                                                                                                                                                                                                           |
    | **Repudiation**            | **VI**                         | **VC**                           | **Medium-Low**  | CVSS has no explicit non-repudiation or auditability metric. Repudiation is therefore best represented through integrity harm to logs, records, and transaction evidence, with occasional secondary confidentiality implications.                                                                                                                                                                                                           |
    | **Information Disclosure** | **VC**                         | **VI**                           | **High**        | Unauthorized exposure of information is directly a confidentiality impact. Integrity is only indirect or downstream.                                                                                                                                                                                                                                                                                                                        |
    | **Denial of Service**      | **VA**                         | **VI**                           | **High**        | Service degradation or outage is directly an availability impact. Integrity may be secondarily affected where incomplete processing or inconsistent state results.                                                                                                                                                                                                                                                                          |
    | **Elevation of Privilege** | **VI, VC, VA**                 | **None**                         | **Medium-High** | Privilege gain commonly enables unauthorized modification and unauthorized access, making integrity and confidentiality primary. Availability is often a secondary consequence when elevated rights permit shutdown, deletion, or resource exhaustion. The primary impact depends on the privileges gained: <br>• _Read_ access → **Confidentiality**<br>• _Write_ access → **Integrity**<br>• _Admin/Execution_ access → **Availability**. |

14. Determine `Likelihood of Exploit`

    **Action:** Populate `Likelihood of Exploit` using the BSI `Dringlichkeit / Eintrittspotenzial` logic when the row provides enough evidence to classify exploit status and exploitation style.
    - Add or update a `Likelihood of Exploit` column in the review CSV rather than creating duplicate fields.
    - Use the BSI reference for `Eintrittspotenzial` as the basis: combine exploit status with exploitation style.
    - When the dataset does not explicitly track BSI lifecycle states such as `theoretisch`, `aktiv`, or `Exploit veröffentlicht`, treat concretely assessable threats as `ausnutzbar` unless the row justification provides stronger evidence.
    - Determine exploitation style as follows:
      - `manual` when the scenario depends on physical presence, user participation, high attack complexity, or explicit attack prerequisites. In practice this usually aligns with CVSS indicators such as `AV:P`, `UI:P`, `AC:H`, or `AT:P`.
      - `automated` when the scenario is adjacent `AV:A` or network-reachable `AV:N`, low complexity `AC:L`, and does not require additional prerequisites `AT:N` or user participation `UI:N`.
      - `self-replicating` when the attack can propagate without user interaction or additional prerequisites, often indicated by `AV:N`, `AC:L`, `AT:N`, `UI:N`, and a scenario that describes wormable or bot-like behavior.

    - Only assign `High` or `Critical` when the row justification explicitly supports a stronger BSI status such as active exploitation or a published exploit.
    - Do not infer `High` merely from severe impact, likelihood must come from exploitability evidence, not consequence severity.
    - If the evidence is insufficient to determine either exploit status or exploitation style, leave the field blank rather than forcing a value.

    **Mapping:** Map CVSS Exploitability Metrics and analyst justification to BSI Likelihood of Exploit categories. Use the following table as a reference, but prioritize the analyst justification when it conflicts with CVSS indicators. When in doubt, default to `ausnutzbar` with `manual` style unless stronger evidence is present.

    > [!NOTE]
    > The likelihood mapping uses only CVSS v4.0 exploitability metrics (`AV`, `AC`, `AT`, `UI`, `E`). Impact metrics are excluded since likelihood derives from exploit feasibility, not consequence severity. CVSS v4.0 does not distinguish `Active (Aktiv)` from `Exploit Published (Exploit Veröffentlicht)` (both map to `E:A`) so analyst justification must preserve the BSI state.

    | Status / Method                            | Manual (Manuell)                    | Automated (Automatisch)             | Self-Replicating (Replizierend)       |
    | ------------------------------------------ | ----------------------------------- | ----------------------------------- | ------------------------------------- |
    | Theoretical (Theoretisch)                  | Info<br>`AV:P/AC:H/AT:P/UI:P/E:U`   | Low<br>`AV:A/AC:L/AT:N/UI:N/E:U`    | Medium<br>`AV:N/AC:L/AT:N/UI:N/E:U`   |
    | Exploitable (Ausnutzbar)                   | Low<br>`AV:L/AC:H/AT:P/UI:P/E:P`    | Medium<br>`AV:A/AC:L/AT:N/UI:N/E:P` | High<br>`AV:N/AC:L/AT:N/UI:N/E:P`     |
    | Active (Aktiv)                             | Medium<br>`AV:L/AC:H/AT:P/UI:P/E:A` | High<br>`AV:A/AC:L/AT:N/UI:N/E:A`   | High<br>`AV:N/AC:L/AT:N/UI:N/E:A`     |
    | Exploit Published (Exploit Veröffentlicht) | Medium<br>`AV:L/AC:H/AT:P/UI:P/E:A` | High<br>`AV:A/AC:L/AT:N/UI:N/E:A`   | Critical<br>`AV:N/AC:L/AT:N/UI:N/E:A` |

15. Determine `Risk Prioritization`

    **Action:** Populate Risk-Based Vulnerability Prioritization by combining `CVSS v4.0 Severity` and `Likelihood of Exploit` severity for each row.
    - Add or update a `Risk Prioritization` column in the review CSV rather than creating duplicate fields.
    - Only assign `Risk Prioritization` when both `CVSS v4.0 Severity` and `Likelihood of Exploit` are present.
    - Prioritization levels: `Info` < `Low` < `Medium` < `High` < `Critical`.

    **Mapping:** Use this matrix as a default reference. Analyst justification may override one level up or down when strong contextual evidence supports a different operational priority.

    | Likelihood \ Severity | None   | Low    | Medium | High     | Critical |
    | --------------------- | ------ | ------ | ------ | -------- | -------- |
    | Info                  | Info   | Info   | Low    | Low      | Medium   |
    | Low                   | Info   | Low    | Low    | Medium   | High     |
    | Medium                | Low    | Low    | Medium | High     | High     |
    | High                  | Low    | Medium | High   | High     | Critical |
    | Critical              | Medium | High   | High   | Critical | Critical |

### 4.3. Output

16. Validate and produce the reviewed CSV

    **Action:** Validate the analyst decisions, then write the complete enriched dataset to the output file.

    - Review at least one representative row from each major interaction family before saving.
    - Check that `Not Applicable` rows are justified by architecture facts rather than by generic skepticism toward TMT output.
    - Check that CVSS and likelihood values are absent where evidence is weak, rather than populated with repeated template values.
    - Check that identical scores across many rows are defensible from the modeled scenario and not simply inherited from the STRIDE category.
    - Save the result as `<device-name>-threat-model-review.csv`.
    - Preserve the delimiter, quoting style, encoding, and header order from the source file.
    - Verify that all native TMT columns are present and unmodified in the output before saving.

## 5. Deliverables

When asked to perform or assist with TMT threat review, produce the following as applicable.

1. Reviewed CSV

    A completed `<device-name>-threat-model-review.csv` that preserves the native TMT export and appends or updates review fields.

2. Review Summary

    A short Markdown summary of the review that lists the highest-risk interactions, the main assumptions, rows marked `Not Applicable` by rationale category, and the main evidence gaps that keep rows in `Needs Investigation`.

    **Recommended Summary Sections:**
    - Executive Summary with threat counts by state and risk level
    - Highest Risk Findings table with ID, Threat, Interface, CVSS, Risk Factor
    - Primary Attack Vectors with techniques, impact, and mitigations
    - Not Applicable Rationale Summary by pattern category
    - MITRE ATT&CK for ICS Mapping table
    - CWE Weakness Classification summary
    - Assumptions and Evidence Gaps
    - Recommended Mitigations by priority (Immediate, Short-Term, Long-Term)

## 6. Style Guide

- Preserve native field names
  > Keep Microsoft TMT column names exactly as exported unless the user explicitly requests a renamed schema.

- Preserve native threat wording
  > Do not rewrite `Title` or `Description` into a different narrative style. Add interpretation in `Justification` instead.

- Append rather than transform
  > Prefer adding review columns over creating a parallel custom threat register.

- Be precise with mappings
  > Only add MITRE ATT&CK and CWE IDs that can be defended from the row contents and review rationale.

- Keep states recognizable
  > Use the state vocabulary already present in the file whenever possible.

- Respect incomplete evidence
  > Blank review fields are acceptable when a precise mapping or score cannot be supported.

- Keep justifications compact
  > A good justification is specific, technically grounded, and brief enough to remain readable in a CSV cell.

- Prefer architecture-backed analyst judgment over pattern matching
  > Repeated TMT rows may be reviewed efficiently, but final state, CWE, CVSS, and likelihood decisions must still be tied to the actual modeled asset, trust boundary, and exploit path.

## 7. Example

### 7.1. Threat Model Diagram

#### 7.1.1. Depth Layer 0 (System)

- `<device-name>-threat-model.md`
  > A depth layer 0 (system) architecture diagram showing major zones, trust boundaries, and data flows.

  > [!IMPORTANT]
  > Be precise in technical labeling of components, interfaces, and data flows to support accurate threat review and mapping.

  ```mermaid
  flowchart TD
      %% Layer 0 - System
      subgraph External_Entity [External Entities]
          User((Engineer / Operator))
          PLC((PLC System))
      end

      %% Layer 0 - System
      subgraph Management_Zone [Engineering Workstation]
          TV[TROVIS-VIEW Software]
          DB[(Device Module DB)]
      end

      %% Layer 0 - System
      subgraph Device_Boundary [Trust Boundary: Device]
          DEVICE[Positioner / Actuator]
      end

      %% Layer 0 - System
      subgraph Physical_Process [Physical Environment]
          VALVE[Control Valve]
      end

      %% Data Flows
      User --> TV
      TV <--> |"Proprietary (RS-232)"| DEVICE
      PLC <--> |"Modbus RTU (RS-485)"| DEVICE
      DEVICE --- VALVE
  ```

#### 7.1.2. Depth Layer 1 (Process)

- `<device-name>-threat-model.md`
  > A depth layer 1 (process) diagram showing the internal components, interfaces, and data flows within the device boundary.

  > [!IMPORTANT]
  > Be precise in technical labeling of components, interfaces, and data flows to support accurate threat review and mapping.

  ```mermaid
  graph TD
      %% Layer 0 - System
      subgraph External_Entity [External Entities]
          User((Engineer / Operator))
          PLC((PLC System))
      end

      %% Layer 0 - System
      subgraph Management_Zone [Engineering Workstation]
          TV[TROVIS-VIEW Software]
          DB[(Device Module DB)]
      end

      %% Layer 1 - Process
      subgraph Device_Boundary [Trust Boundary: Device]
          IF232[Serial RS-232 Interface]
          IF485[Serial RS-485 Interface]
          PAC[Logic Controller / Firmware]
          MEM[(Configuration Memory)]
          HMI[Local LCD/Pushbutton]
          MOT[Motor & Gear Drive]
      end

      %% Layer 0 - System
      subgraph Physical_Process [Physical Environment]
          VALVE[Control Valve]
          FLOW[Process Fluid/Steam]
      end

      %% Data Flows
      User --> TV
      User --> HMI
      TV  <--> |"Proprietary (RS-232)"| IF232
      PLC <--> |"Modbus RTU (RS-485)"| IF485
      IF232 --> |"Read/Write Registers"| PAC
      IF485 --> |"Read/Write Registers"| PAC
      PAC <--> |"Store/Retrieve"| MEM
      PAC --> |"Control Signal"| MOT
      MOT --- |"Mechanical Force"| VALVE
      HMI --> |"Manual Override"| PAC
      VALVE --- |"Regulates"| FLOW
  ```

## 8. Template

Use these templates for Microsoft TMT CSV intake and review.

### 8.1. Raw TMT Export CSV Template

- `<device-name>-threat-model.csv`
  > The raw export from Microsoft TMT before analyst review. Preserve all fields and values as exported by TMT.

  ```csv
  Id;Title;Category;Diagram;Interaction;Priority;State;Changed By;Description;Justification;Last Modified
  1;Spoofing the RS-485 Interface Process;Spoofing;<device-name>;PLC to RS-485 (Modbus RTU);High;Not Started;;RS-485 Interface may be spoofed by an attacker and this may lead to information disclosure by PLC. Consider using a standard authentication mechanism to identify the destination process.;;Generated
  2;Potential Lack of Input Validation for RS-485 Interface;Tampering;<device-name>;PLC to RS-485 (Modbus RTU);High;Not Started;;Data flowing across PLC to RS-485 (Modbus RTU) may be tampered with by an attacker. This may lead to a denial of service attack against RS-485 Interface or an elevation of privilege attack against RS-485 Interface or an information disclosure by RS-485 Interface. Failure to verify that input is as expected is a root cause of a very large number of exploitable issues. Consider all paths and the way they handle data. Verify that all input is verified for correctness using an approved list input validation approach.;;Generated
  ```

### 8.2. Reviewed TMT CSV Template

- `<device-name>-threat-model-review.csv`
  > The completed analyst review of the TMT export. Preserve all native TMT fields and values, and append or update review fields based on the analyst assessment.

  ```csv
  Id;Title;Category;Diagram;Interaction;Priority;State;Changed By;Description;Justification;Last Modified;MITRE ID;CWE ID;CVSS v4.0 Vector;CVSS v4.0 Score;CVSS v4.0 Severity;Likelihood of Exploit;Risk Prioritization
  1;Spoofing the RS-485 Interface Process;Spoofing;<device-name>;PLC to RS-485 (Modbus RTU);High;Mitigated/Transfer;;RS-485 Interface may be spoofed by an attacker and this may lead to information disclosure by PLC. Consider using a standard authentication mechanism to identify the destination process.;Modbus RTU has no native authentication. An attacker with physical or logical access to the RS-485 bus can transmit frames indistinguishable from a legitimate HMI. Compensating controls (serial tap detection, PLC input validation) partially mitigate. Establish physical perimeter security and network isolation.;16.03.2026 11:04;T0831;CWE-290;CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N;5,3;Medium;Medium;Medium
  2;Potential Lack of Input Validation for RS-485 Interface;Tampering;<device-name>;PLC to RS-485 (Modbus RTU);High;Mitigated;;Data flowing across PLC to RS-485 (Modbus RTU) may be tampered with by an attacker. This may lead to a denial of service attack against RS-485 Interface or an elevation of privilege attack against RS-485 Interface or an information disclosure by RS-485 Interface. Failure to verify that input is as expected is a root cause of a very large number of exploitable issues. Consider all paths and the way they handle data. Verify that all input is verified for correctness using an approved list input validation approach.;Modbus RTU provides no integrity protection. An attacker with bus access can perform a man-in-the-middle attack by relaying and modifying frames. No CRC16 validation beyond the Modbus CRC16 which does not prevent deliberate manipulation by an in-path adversary.;16.03.2026 11:04;;CWE-20, CWE-119;CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N;7,2;High;Medium;High
  ```

## 9. References

- Microsoft [Threat Modeling Tool](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool) documentation.
- Microsoft [Threat Modeling Fundamentals](https://learn.microsoft.com/en-us/training/paths/tm-threat-modeling-fundamentals/) training.
- STRIDE [Threat Modeling](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats) guide.
- MITRE [ATT&CK for ICS](https://attack.mitre.org/matrices/ics/) matrix.
- MITRE [CWE](https://cwe.mitre.org/) page.
- FIRST [CVSS v4.0 Specification](https://www.first.org/cvss/v4.0/specification-document) page.
- FIRST [CVSS v4.0 Calculator](https://www.first.org/cvss/calculator/4.0) page.
- BSI [Risk Prioritization](https://www.bsi.bund.de/DE/Service-Navi/Abonnements/Newsletter/Buerger-CERT-Abos/Buerger-CERT-Sicherheitshinweise/Risikostufen/risikostufen.html) page.
