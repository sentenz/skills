---
name: threat-modeling-ics
description: >-
  Performs end-to-end threat modeling for OT/ICS systems from Microsoft Threat
  Modeling Tool (TMT) threat-list exports (`*.csv`) and model files (`*.tm7`).
  Uses TMT and STRIDE for initial threat enumeration, then enriches each threat
  with OT/ICS context, MITRE ATT&CK for ICS mappings, CWE weakness
  classification, CVSS v4.0 scoring, Likelihood of Exploit, Risk-based
  Prioritization, minimum-capable Threat Actor assignment, Risk Treatment
  decisions, STRIDE to Mitigation mapping for SCADA, PLC, PAC, and HMI assets,
  and OT impact categories ranging from Denial of View to Physical Damage to
  Property.
metadata:
  version: "1.5.0"
  activation:
    implicit: true
    priority: 1
    triggers:
      - "microsoft tmt"
      - "threat model"
      - "threat modeling"
      - "stride"
      - "mitre att&ck"
      - "cwe"
      - "cvss"
      - "likelihood"
      - "risk treatment"
      - "threat review"
      - "security review"
    match:
      languages: ["markdown", "csv"]
      paths:
        - "**/*.tm7"
        - "**/*threat-model*.csv"
        - "**/*threat-model*.md"
      prompt_regex: "(?i)(microsoft tmt|threat modeling|stride|mitre att&ck|cwe|cvss|likelihood|risk treatment|threat review|security review)"
  usage:
    load_on_prompt: true
    autodispatch: true
---

# Threat Modeling ICS

Instructions for AI security agents reviewing Microsoft Threat Modeling Tool threat-list exports.

> [!NOTE]
> Treat the Microsoft TMT CSV as the primary artifact. When a Mermaid diagram is absent, a Microsoft TMT model file (`*.tm7`) is an acceptable architecture source. Extract system elements, trust boundaries, interfaces, and data flows from the model before reviewing the CSV.

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
  - [3.4. CWE](#34-cwe)
  - [3.5. CVSS](#35-cvss)
  - [3.6. BSI Likelihood of Exploit](#36-bsi-likelihood-of-exploit)
  - [3.7. Risk Treatment](#37-risk-treatment)
- [4. Workflow](#4-workflow)
  - [4.1. Preparation](#41-preparation)
  - [4.2. Review](#42-review)
  - [4.3. Deliverables](#43-deliverables)
- [5. Example](#5-example)
  - [5.1. Diagram](#51-diagram)
    - [5.1.1. Threat Model Depth Layer 0 (System)](#511-threat-model-depth-layer-0-system)
  - [5.2. Mapping](#52-mapping)
    - [5.2.1. Purdue Model Mapping](#521-purdue-model-mapping)
    - [5.2.2. STRIDE Mapping](#522-stride-mapping)
    - [5.2.3. MITRE ATT\&CK Mapping](#523-mitre-attck-mapping)
    - [5.2.4. CVSS v4.0 Mapping](#524-cvss-v40-mapping)
    - [5.2.5. Likelihood of Exploit Mapping](#525-likelihood-of-exploit-mapping)
    - [5.2.6. Risk Prioritization Mapping](#526-risk-prioritization-mapping)
    - [5.2.7. Threat Actor Mapping](#527-threat-actor-mapping)
  - [5.3. Template](#53-template)
    - [5.3.1. Raw TMT Export CSV Template](#531-raw-tmt-export-csv-template)
    - [5.3.2. Reviewed TMT CSV Template](#532-reviewed-tmt-csv-template)
- [6. References](#6-references)

## 1. Benefits

- Proactive Defense
  > Threat modeling enables teams to identify and mitigate security risks early in the design phase, reducing the likelihood of vulnerabilities being introduced during development.

- Residual Risk
  > The remaining risk after mitigations are applied. This risk must be explicitly documented and either accepted by stakeholders or further mitigated.

- Compliance Alignment
  > Threat modeling supports the risk assessment and technical documentation expectations of frameworks such as EU CRA, ISO/IEC 27005, NIST SP 800-30, IEC 62443-3-2, and GDPR Article 25 by producing documented evidence of security due diligence, assumptions, mitigations, and residual risk.

- Risk Treatment Traceability
  > Assigning a concrete risk treatment decision (`Mitigation`, `Transfer`, `Acceptance`, or `Avoidance`) to each identified threat produces traceable evidence that stakeholders have deliberately addressed every risk. Recording risk treatment supports regulatory obligations, stakeholder accountability, and residual risk communication.

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

Threat modeling must assign the minimum-capable adversary type relevant to the OT/ICS attack path.
Use canonical threat actor classes aligned with common CISA and NIST threat-source terminology so the `Threat Actor` field records actor type rather than campaign style, access vector, or tooling maturity.

- Use exactly one standardized `Threat Actor` label per reviewed CSV row. Allowed labels are:
  - `Nation-State Actor`
  - `Cybercriminal`
  - `Insider Threat`
  - `Hacktivist`
- Do not use `APT`, `Ransomware Operator`, `Supply Chain Attacker`, or `Script Kiddie` as standalone labels. Treat those as supporting context that helps justify one of the four canonical actor classes listed above.

- Nation-State Actor
  > State-sponsored actors conduct long-duration, multi-stage campaigns targeting critical infrastructure for geopolitical objectives: espionage, pre-positioning for disruption, or physical sabotage. They invest significant resources in custom tooling, zero-day exploits, and supply-chain compromise to penetrate defense-in-depth architectures and reach Level 0 field devices.

- Cybercriminal
  > Financially motivated actors deploy ransomware or extortion campaigns that pivot across the IT/OT boundary. By encrypting historian databases, engineering workstations, or SCADA servers they force operators to halt processes or pay ransom to restore visibility and control. OT-targeting ransomware groups increasingly understand industrial protocol semantics.

- Insider Threat
  > Insiders hold privileged physical or logical access to control systems without requiring an initial intrusion phase. Malicious insiders may intentionally manipulate setpoints, corrupt configuration files, introduce rogue commands, or disable safety interlocks. Negligent insiders introduce risk by bypassing security controls or mishandling engineering-level credentials.

- Hacktivist
  > Hacktivists target publicly visible OT assets to advance political or ideological agendas. They exploit internet-exposed HMIs, Shodan-indexed SCADA web interfaces, or default credentials to post proof-of-access, deface operator displays, or make coarse setpoint changes for publicity rather than sustained operational damage.

### 2.4. Diagram Depth Layers

Use Microsoft [diagram depth layers](https://learn.microsoft.com/en-us/training/modules/tm-provide-context-with-the-right-depth-layer/1b-depth-layers) when creating or validating the threat model diagram.

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

Microsoft Threat Modeling Tool (TMT) is the source of truth for the initial threat inventory.

- Source of Record
  > The exported TMT CSV is the working dataset.

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

MITRE ATT&CK for ICS to map a TMT threat to realistic adversary behavior affecting industrial environments.

- [Tactics](https://attack.mitre.org/tactics/ics/)
  > The adversary's tactical goal or motivation for the attack (e.g., `TA0043: Impact`).

- [Techniques](https://attack.mitre.org/techniques/ics/)
  > The specific adversary behavior or method used to achieve the tactic (e.g., `T0855: Unauthorized Command Message`).

### 3.4. CWE

- [MITRE CWE](https://cwe.mitre.org/)
  > The underlying software or design weakness that enables the threat (e.g., `CWE-20: Improper Input Validation`).

### 3.5. CVSS

[FIRST CVSS v4.0](https://www.first.org/cvss/) to score the technical severity of the threat based on the modeled attack scenario and its consequences.

- [CVSS Calculation](https://www.first.org/cvss/calculator/4.0)
  > Use the CVSS v4.0 calculator to determine the base score, severity, and vector based on the modeled attack scenario and review rationale.

- CVSS-B Score
  > Record the CVSS v4.0 base score as a numeric value between `0,0` and `10,0` when the evidence supports a defensible score.

- CVSS Severity
  > Record the CVSS v4.0 severity category (`None`, `Low`, `Medium`, `High`, `Critical`) when a base score is recorded.

- CVSS Vector
  > Record the CVSS v4.0 vector string (`CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:N/SA:N`) when a base score is recorded.

### 3.6. BSI Likelihood of Exploit

[BSI Dringlichkeit / Eintrittspotenzial](https://www.bsi.bund.de/DE/Service-Navi/Abonnements/Newsletter/Buerger-CERT-Abos/Buerger-CERT-Sicherheitshinweise/Risikostufen/risikostufen.html) to assess the likelihood of exploit based on the current state of the vulnerability and the style of exploitation.

- Exploitation Method
  - Manual (Manuell)
    > The attacker must perform non-automatable steps to adapt the attack to the target. Requires skill and effort.

  - Automated (Automatisch)
    > The exploit can be run using a script or tool against many targets.

  - Self-replicating (Replizierend)
    > The exploit can spread automatically without user interaction (e.g., worms, bots). Compromised systems attack further systems autonomously.

- Vulnerability State
  - Theoretical (Theoretisch)
    > A flaw is discovered that could lead to a security issue, but no concrete exploit exists.

  - Exploitable (Ausnutzbar)
    > A proof-of-concept or reliable method to exploit the vulnerability exists.

  - Active (Aktiv)
    > Evidence exists that the vulnerability is already being exploited in the wild.

  - Exploit Published (Exploit Veröffentlicht)
    > A public attack tool has been released, the effort to attack drops significantly.

### 3.7. Risk Treatment

Risk treatment defines the disposition decision after each identified risk has been prioritized based on severity and likelihood evaluation.

> [!NOTE]
> Aligned with ISO 31000 and IEC 62443-3-2, every threat row must be assigned a treatment option that is traceable to the risk prioritization evidence.

- Risk Avoidance
  > Remove or restructure the system element, function, interface, or data flow that introduces the risk so the threat is no longer applicable. Risk avoidance eliminates the risk at its source.

- Risk Mitigation
  > Apply security controls, compensating measures, or design changes to reduce the likelihood of exploitability or impact to an acceptable level. Document the specific controls applied and record the residual risk that remains after mitigation.

- Risk Acceptance
  > Consciously retain the risk without additional controls when the cost or feasibility of treatment exceeds the benefit, or when the risk falls within the defined acceptance threshold. Acceptance must be explicitly documented and approved by the responsible stakeholder.

- Risk Transfer
  > Shift financial, operational, or legal responsibility for the residual risk to a third party through insurance, contractual SLA, vendor warranty, or managed service agreements. The technical exposure remains but the consequence is shared or delegated.

## 4. Workflow

> [!IMPORTANT]
> Execute every step below in order. Do not skip, reorder, or merge steps. Stop at any blocking gate and wait for user input before continuing. Resume from the blocked step once input is received, do not restart from step 1.

> [!NOTE]
> Save and integrate intermediate results after each step to ensure continuity across steps.

> [!NOTE]
> When the main objective is product cybersecurity compliance, use this workflow to produce traceable risk-assessment evidence that can support EU CRA-style technical documentation. Keep the workflow technically grounded and do not make unsupported legal compliance claims.

### 4.1. Preparation

1. Define assessment objective and scope

    **Action:** Record why the assessment is being performed and what product/system boundary it covers.
    - Identify whether the review is primarily for EU CRA-aligned product risk assessment, general OT/ICS design review, supplier assurance, or another documented objective.
    - Record the product name, intended use, deployment context, operational environment, and trust boundaries in scope.
    - Record key assumptions, exclusions, external dependencies, maintenance paths, engineering interfaces, and other security-relevant entry points.
    - When EU CRA or another compliance framework is the main driver, treat this scope statement as traceability input for technical documentation and risk assessment evidence.
    - **Blocking Gate:** If the product/system scope or review objective cannot be determined, ask the user to provide it before continuing.

2. Locate or create the threat model diagram

    **Action:** Identify the architecture source for the target OT/ICS system.
    - Search for a Microsoft TMT model file (`*.tm7`), prefer filenames such as `<Device_Name>_Threat_Model.tm7`.
    - If found, extract architecture elements, trust boundaries, data flows, and interfaces.
    - If no Microsoft TMT model file is found, search for a Mermaid diagram file (`*.md`) and extract the same evidence.
    - If the source is a TM7 file, normalize names and labels only enough to make the diagram readable, but preserve the modeled trust boundaries, interfaces, and flow directions.
    - If no diagram exists, draft one from the provided input and save it as `<Device_Name>_Threat_Model.md`.
    - **Blocking Gate:** If no architecture source is available, ask the user to provide one before continuing:
      - A Mermaid diagram file path.
      - A Microsoft TMT model file path (`*.tm7`).
      - External documentation or links describing the system architecture.
      - A textual description of the system components and trust relationships.

3. Locate and classify the input CSV

    **Action:** Locate the TMT export CSV and determine its review status.
    - Prefer filenames such as `<Device_Name>_Threat_Model.csv` or `<Device_Name>_Threat_Model_Generated.csv`, but rely on the header row to determine artifact type.
    - Classify as one of: raw TMT export, partially reviewed file, or completed review file.
    - **Blocking Gate:** If no CSV is available, ask the user to provide the exported TMT CSV before continuing.

4. Detect native TMT columns

    **Action:** Immutably record the native TMT columns present in the input CSV header.
    - Confirm that the header row contains native TMT fields:
      - `Id`, `Title`, `Category`, `Diagram`, `Interaction`, `Priority`, `State`, `Changed By`, `Description`, `Justification`, `Last Modified`

5. Establish preservation constraints

    **Action:** Define column mutability rules before beginning the row-by-row review.
    - Do not delete any columns.
    - Do not edit the original `<Device_Name>_Threat_Model.csv` file — treat it as immutable evidence.
    - Immutably preserve values in: `Id`, `Title`, `Category`, `Diagram`, `Interaction`, `Changed By`, `Description`, `Last Modified`.
    - Mutably update `State`, `Priority`, and `Justification` in the output file `<Device_Name>_Threat_Model_Generated.csv`.
    - Preserve the original source and review lineage so the generated output remains traceable to the raw TMT export for audit and compliance evidence purposes.

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
    - Record assumptions and missing evidence when the native TMT fields do not fully resolve the threat decision.
    - When the assessment objective is compliance-oriented, treat each row as a traceable product risk statement tied to a concrete interface, trust relationship, or maintenance path.

    > [!NOTE]
    > Perform steps 2–11 for every row before proceeding to section 4.3.

2. MITRE ATT&CK

    **Action:** Populate the `MITRE ID` field for each row when a concrete ATT&CK for ICS technique can be supported by the TMT threat fields, see [MITRE ATT&CK](#33-mitre-attck).
    - Record the most relevant MITRE IDs for ICS (e.g., `TA0043, T0856`).
    - Store MITRE technique IDs in the dedicated `MITRE ID` column.
    - Avoid duplicating the same MITRE ID string in `Justification` when the `MITRE ID` column is populated. In `Justification`, prefer technique name or behavior wording unless repeating the ID is necessary for disambiguation.
    - Leave the field blank when the threat statement is ambiguous.
    - Reference the [MITRE ATT&CK for ICS Mapping](#523-mitre-attck-mapping) section for common technique mappings based on STRIDE categories.

3. MITRE CWE

    **Action:** Populate the `CWE ID` field for each row when the root weakness is identifiable from the TMT threat fields, see [MITRE CWE](#34-cwe).
    - Prefer the most specific CWE that fits the described weakness.
    - Use comma-separated values when the finding depends on more than one concrete weakness (e.g., `CWE-290, CWE-345`).
    - Store CWE identifiers in the dedicated `CWE ID` column. In `Justification`, prefer weakness name or exploit behavior wording unless repeating the ID is required for disambiguation.
    - Do not assign a CWE when the row is generic but the underlying weakness is still unclear after reviewing the modeled interaction.
    - Leave the field blank when the evidence is insufficient.

4. CVSS v4.0

    **Action:** Populate the CVSS v4.0 Base Metrics `CVSS v4.0 Vector`, `CVSS v4.0 Severity`, and `CVSS-B v4.0 Score` together for each row, see [CVSS](#35-cvss).
    - All three fields must be populated together or left blank together. Do not record a severity without a vector. Do not record a vector without a score.
    - Keep raw CVSS artifacts in dedicated columns (`CVSS v4.0 Vector`, `CVSS-B v4.0 Score`, `CVSS v4.0 Severity`) rather than duplicating them in `Justification`.
    - Derive the score from the [CVSS v4.0 calculator](https://www.first.org/cvss/calculator/4.0) using the native TMT threat fields (`Title`, `Category`, `Interaction`, `Description`) and the MITRE ATT&CK technique as input.
    - Reference the [CVSS v4.0 Mapping](#524-cvss-v40-mapping) section for guidance on mapping STRIDE categories to CVSS impact metrics.

5. Likelihood of Exploit

    **Action:** Populate the `Likelihood of Exploit` using the BSI `Dringlichkeit / Eintrittspotenzial` logic, see [BSI Likelihood of Exploit](#36-bsi-likelihood-of-exploit).
    - Add or update a `Likelihood of Exploit` column in the review CSV rather than creating duplicate fields.
    - Reference the [Likelihood of Exploit Mapping](#525-likelihood-of-exploit-mapping) section for guidance on mapping CVSS exploitability metrics and TMT statements to BSI likelihood categories.

6. Risk Prioritization

    **Action:** Populate Risk-Based Vulnerability Prioritization by combining `CVSS v4.0 Severity` and `Likelihood of Exploit` for each row.
    - Add or update a `Risk Prioritization` column in the review CSV rather than creating duplicate fields.
    - Only assign `Risk Prioritization` when both `CVSS v4.0 Severity` and `Likelihood of Exploit` are present.
    - Reference the [Risk Prioritization Mapping](#526-risk-prioritization-mapping) section for guidance on combining severity and likelihood into prioritization category.

7. Threat Actor

    **Action:** Assign the minimum capable `Threat Actor` for each row using the standardized labels from [Threat Actors](#23-threat-actors).
    - Add or update a `Threat Actor` column in the review CSV rather than creating duplicate fields.
    - Use exactly one standardized `Threat Actor` label per reviewed CSV row.
    - Choose the minimum required actor, not the most severe or most newsworthy actor.
    - Base the decision on the modeled attack path, required access, exploit maturity, and the amount of OT-specific knowledge required.
    - Evaluate the assignment against all three selection criteria together:
      - **Capability:** tooling maturity, exploit sophistication, and ability to chain multiple steps.
      - **Access Path:** internet-reachable, adjacent industrial network, local workstation, maintenance path, or physical access requirement.
      - **Operational Knowledge:** generic IT tradecraft, OT protocol familiarity, process-specific engineering knowledge, or privileged insider context.
    - Prefer the least capable actor that can still plausibly execute the threat end-to-end.
    - Escalate to a more capable actor only when the attack path cannot reasonably succeed with a less capable one.
    - Do not assign multiple actors in one row. If several actors could plausibly perform the attack, record the minimum actor that can realistically achieve the described effect.
    - Reference the [Threat Actor Mapping](#527-threat-actor-mapping) section for common actor selections from attack-path characteristics.

8. TMT State

    **Action:** Revise the `State` field for each row using the full analytical context: TMT threat fields, MITRE ATT&CK technique, CWE root weakness, CVSS severity, Risk Prioritization, and assigned Threat Actor.
    - State selection guidance: Select the state decision that best fits the evidence and rationale.
      - `Not Started`: Default/export state for rows that have not yet been reviewed. Use this only to indicate genuinely unreviewed work remaining in a partially completed CSV. Once a row has been analyzed in this step, move it out of `Not Started` and assign the best-fit reviewed state below.
      - `Not Applicable`: The attack path is architecturally impossible (e.g., analog-only interface, passive sensor with no network exposure, human actor rather than a machine endpoint with no independent execution context), or the risk source has been structurally eliminated.
        - In `Justification`, name the specific architectural contradiction or eliminated element. Keep the required `Threat Actor` value and explain why that actor was the minimum candidate considered before the path was rejected.
      - `Mitigated`: One or more security controls, compensating measures, or design changes are confirmed in place and reduce the risk to an accepted level. The applied control, measure, residual risk, and how those controls constrain the assigned threat actor must be identified in `Justification`.
      - `Needs Investigation`: Critical evidence is missing, a key assumption cannot be validated, or the attack path cannot be closed without additional architecture information or clarification. The specific evidence gap or unanswered question must be named in `Justification`, including whether the unknowns affect the assigned threat actor, and do not leave a row in `Needs Investigation` without identifying the blocker.

9. TMT Priority

    **Action:** Revise the `Priority` field for each row. Use the derived `Risk Prioritization` as the primary signal and adjust only when the modeled context provides a specific reason to deviate.
    - Use the priority vocabulary already present in the file.
      - `Low`
        > The threat is accepted with minimal concern. No immediate action is required, but it should be monitored for changes.
      - `Medium`
        > Mitigation planning should be initiated, and the threat should be tracked in the security backlog.
      - `High`
        > The threat is significant and requires prompt mitigation. It should be prioritized in the security backlog and may require escalation.

10. TMT Justification

    **Action:** Write a concise, technically precise analyst statement in the `Justification` field for each row, synthesizing all prior enrichment steps. The justification provides the evidence-based rationale that supports the assigned `State`, explains the assigned `Threat Actor`, and informs the `Risk Treatment` decision in the next step.
    - State the evidence-based rationale that supports the assigned `State`.
    - Reference the modeled protocol, interface, trust relationship, validation behavior, or compensating control that informs the decision.
    - Reference the assigned MITRE ATT&CK technique, CWE weakness, CVSS severity, Risk Prioritization, and Threat Actor where they support the rationale. Prefer technique name and behavior phrasing over repeating raw MITRE IDs that are already captured in `MITRE ID`.
    - State why the chosen actor is the minimum capable adversary by describing the required access path and operational knowledge.
    - When `State` is `Not Applicable`, name the specific architectural contradiction or eliminated element (e.g., passive sensor, analog signal path, human actor rather than machine endpoint, or no independent execution context).
    - When `State` is `Mitigated`, identify the applied security control, compensating measure, or design change. State the residual risk level if exposure is not fully eliminated. If risk ownership is formally transferred to a third party, identify the named organization, contract, or SLA.
    - When `State` is `Needs Investigation`, state the most important evidence gap or assumption that must be resolved before a decision can be made.

    > [!IMPORTANT]
    > The justification is the most critical part of the security review. It is written last so it can synthesize the full analytical picture.


11. Risk Treatment

    **Action:** Assign a risk treatment decision to each row based on the derived `Risk Prioritization`, see [Risk Treatment](#37-risk-treatment).
    - Add or update a `Risk Treatment` column in the review CSV rather than creating duplicate fields.
    - Preserve `Risk Treatment` as the final decision column in the reviewed CSV.
    - Treatment selection guidance: Select one of the following risk treatment preferences based on the order of priority:
      - `Avoidance`: apply if it is documented how the system element, interface, or data flow is removed or restructured to eliminate the risk.
      - `Mitigation`: apply if security controls or compensating measures that lower the risk are documented. Residual risk must be explicitly approved by a responsible stakeholder.
      - `Acceptance`: document the business rationale, residual risk level, and the responsible stakeholder who approves retention.
      - `Transfer`: identify the third party, contract, SLA, or insurance policy that accepts the risk.

### 4.3. Deliverables

1. Reviewed CSV

    **Action:** Validate the analyst decisions, then write the complete enriched dataset to the output file `<Device_Name>_Threat_Model_Generated.csv`.
    - Generate a semicolon-delimited output CSV format.
    - Review each row from the source before saving.
    - Check that identical scores across many rows are defensible from the modeled scenario and not simply inherited from the STRIDE category.
    - Preserve the delimiter, quoting style, encoding, and header order from the source file.
    - Verify that all native TMT columns are present and unmodified in the output before saving.
    - Perform a final column-scope consistency check: keep IDs and score artifacts in dedicated columns, and keep `Justification` as narrative rationale.
    - Verify that every reviewed row has exactly one allowed `Threat Actor` label.
    - Verify that the review columns are appended immediately after the native TMT columns and that the tail-column order, using the semicolon CSV delimiter, is `Likelihood of Exploit;Risk Prioritization;Threat Actor;Risk Treatment`.
    - Reject rows where `Justification` is only an identifier token or parenthetical code reference.
    - Verify that the output supports traceability from raw TMT threat statement to analyst decision, supporting evidence, assumptions, residual risk posture, threat actor selection, and risk treatment decision.

2. Review Summary

    **Action:** A short Markdown `<Device_Name>_Threat_Model_Summary.md` summary file of the review that lists the highest-risk interactions, the main assumptions, rows marked `Not Applicable` by rationale category, the main evidence gaps that keep rows in `Needs Investigation`, and the residual risks that remain after documented mitigations.

    **Compliance Traceability Guidance:**
    - When the main objective is EU CRA or another product compliance framework, structure the summary so it can be reused as risk-assessment evidence and as an input to technical documentation.
    - Capture product scope, intended use, assessment assumptions, open evidence gaps, and residual risks in terms that remain traceable to the reviewed threat rows.

    **Recommended Summary Sections:**
    - Assessment Objective and Product Scope
    - Executive Summary with threat counts by state, risk level, and threat actor
    - Highest Risk Findings table with ID, Threat, Interface, CVSS, Risk Factor, Threat Actor
    - Primary Attack Vectors with techniques, impact, and mitigations
    - Threat Actor Distribution with key access-path and knowledge assumptions
    - Not Applicable Rationale Summary by pattern category
    - MITRE ATT&CK for ICS Mapping table
    - CWE Weakness Classification summary
    - Assumptions and Evidence Gaps
    - Residual Risk Summary and Unresolved Decisions
    - Risk Treatment Summary with counts and rationale by treatment option
    - Recommended Mitigations by priority (Immediate, Short-Term, Long-Term)

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

Classify ICS assets by Purdue zone before assigning STRIDE categories or selecting mitigations. Each zone has a characteristic threat surface and a primary set of STRIDE categories.

| Purdue Level | Zone        | Asset Type                                 | Examples                                                          | Primary STRIDE Categories                                      |
| ------------ | ----------- | ------------------------------------------ | ----------------------------------------------------------------- | -------------------------------------------------------------- |
| Level 4–5    | Enterprise  | SCADA Server / Historian                   | OSIsoft PI, AVEVA System Platform, Wonderware                     | Information Disclosure, Repudiation, Elevation of Privilege    |
| Level 3      | Operations  | Engineering Workstation / OPC Server       | Siemens TIA Portal, Rockwell Studio 5000, OPC UA Server           | Spoofing, Tampering, Elevation of Privilege                    |
| Level 2      | Supervisory | HMI / Operator Station                     | Siemens WinCC, FactoryTalk View SE, Inductive Automation Ignition | Spoofing, Tampering, Information Disclosure, Denial of Service |
| Level 1      | Control     | PLC / PAC                                  | Siemens S7, Allen-Bradley ControlLogix, Schneider Modicon         | Tampering, Denial of Service, Elevation of Privilege           |
| Level 0      | Field       | Sensors / Actuators / RTUs / Field Devices | Transmitters, positioners, motor drives, RTUs                     | Tampering, Denial of Service                                   |

> [!NOTE]
> PAC (Programmable Automation Controller) occupies Level 1 alongside PLCs but typically provides broader I/O handling (higher module count, protocol diversity, or distributed I/O over EtherNet/IP or PROFINET) and higher processing capacity. Treat PAC threats identically to PLC threats unless the PAC exposes additional network-facing services (e.g., built-in web server, RESTful API, OPC UA endpoint, or MQTT client) that expand the attack surface beyond standard fieldbus communication.

#### 5.2.2. STRIDE Mapping

STRIDE to Mitigation reference for OT/ICS assets. Use these mappings to populate the `Justification` field, to select compensating controls, and to populate the Recommended Mitigations section of the review summary.

> [!NOTE]
> Reference section [5.2.1. Purdue Model Mapping](#521-purdue-model-mapping) to identify the asset type and Purdue zone. Reference section [5.2.3. MITRE ATT&CK Mapping](#523-mitre-attck-mapping) to identify the OT-specific consequence before selecting mitigations.

- Spoofing
  > Identity impersonation of SCADA servers, PLCs, PACs, or HMI stations allows attackers to inject unauthorized commands or intercept control traffic.

  | Asset Type               | OT Impact                    | Key Mitigations                                                                                                                                               |
  | ------------------------ | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | SCADA Server / Historian | Manipulation of View         | PKI certificates for OPC UA client/server authentication; mutual TLS for historian replication; remove default vendor accounts; enforce named user logins.    |
  | Engineering Workstation  | Manipulation of Control      | Multi-factor authentication (MFA) for engineering software; signed project file verification; dedicated VLAN for engineering zone.                            |
  | HMI / Operator Station   | Denial of View, Loss of View | Named operator accounts with MFA; session lock-out on idle; HMI certificate-based authentication for server connections.                                      |
  | PLC / PAC                | Unauthorized Command         | DNP3 Secure Authentication v5 (SAv5) or IEC 62351-5; Modbus function code allow-listing; physical network isolation; rack-level access control.               |
  | Field Devices / RTUs     | Unauthorized Command         | Physical bus isolation; point-to-point wiring where feasible; tamper-evident enclosures; restrict bus access to known master addresses where protocol allows. |

- Tampering
  > Unauthorized modification of configurations, firmware, register values, or historian records can cause unsafe process states ranging from equipment damage to physical injury.

  | Asset Type               | OT Impact                                            | Key Mitigations                                                                                                                                                                             |
  | ------------------------ | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | SCADA Server / Historian | Manipulation of View, Physical Damage to Property    | File integrity monitoring on historian databases; alarm configuration change management; signed backup archives; write-protect critical alarm setpoints.                                    |
  | Engineering Workstation  | Manipulation of Control                              | Project file signing and version control; configuration change auditing; restrict USB/removable media.                                                                                      |
  | HMI / Operator Station   | Denial of View, Manipulation of View                 | Setpoint change confirmation dialogs with secondary operator acknowledgement; change logging with timestamp and user ID; read-only default HMI mode.                                        |
  | PLC / PAC                | Manipulation of Control, Physical Damage to Property | Strict register range and type validation in firmware; physical write-protect relay/switch on critical registers; CRC-verified configuration blocks; safe-state fallback on invalid inputs. |
  | Field Devices / RTUs     | Physical Damage to Property, Environmental Release   | Input range clamping; analog signal plausibility checks; hardware over-range protection; failsafe spring-return actuators.                                                                  |

- Repudiation
  > Lack of audit trails in OT environments prevents attribution of unauthorized changes and impedes incident response across SCADA, HMI, and control layers.

  | Asset Type               | OT Impact               | Key Mitigations                                                                                                                                                                                                                                                                                                                    |
  | ------------------------ | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | SCADA Server / Historian | Manipulation of View    | Centralized syslog with tamper-evident log storage; operator session recording; immutable event historian with time-stamped entries.                                                                                                                                                                                               |
  | Engineering Workstation  | Manipulation of Control | Version-controlled project repository with signed commits; change management workflow with approvals; workstation activity logs forwarded to SIEM.                                                                                                                                                                                 |
  | HMI / Operator Station   | Loss of View            | Named user accounts (no shared/generic logins); HMI action log capturing user ID, timestamp, and changed value; export logs to off-device storage.                                                                                                                                                                                 |
  | PLC / PAC                | Unauthorized Command    | PLC audit log for configuration and program changes (where firmware supports); upstream SCADA event capture for all command transactions; NTP time synchronization.                                                                                                                                                                |
  | Field Devices / RTUs     | Unauthorized Command    | RTU event log with timestamped command receipt; where protocol selection is still possible, prefer DNP3 with Application Layer Sequence Numbers (ALSN) enabled; for legacy Modbus RTU deployments, implement gateway-level sequence validation or anomaly detection; out-of-band monitoring for unexpected register state changes. |

  > [!NOTE]
  > DNP3 Application Layer Sequence Numbers (ALSN) prevent replay attacks and out-of-order command injection by ensuring each request-response pair carries a unique, incrementing sequence value. Enable this feature to provide repudiation evidence at the field device level.

- Information Disclosure
  > Unencrypted industrial protocols and unrestricted physical access expose process data that adversaries use for reconnaissance and to plan subsequent attacks.

  | Asset Type               | OT Impact               | Key Mitigations                                                                                                                                                  |
  | ------------------------ | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | SCADA Server / Historian | Manipulation of View    | OPC UA with message signing and encryption; role-based access control (RBAC) limiting historian read to authorized roles; data classification labels on exports. |
  | Engineering Workstation  | Loss of Control         | Encrypted project file storage; network micro-segmentation between engineering and control zones; no internet connectivity on workstation.                       |
  | HMI / Operator Station   | Denial of View          | Screen lock on idle; remote HMI access over encrypted VPN only; display only process values necessary for the operator role (least-information principle).       |
  | PLC / PAC                | Manipulation of Control | Modbus/TCP over IPsec or VPN tunnel; physical RS-485 cable shielding and routing through conduit; firewall allow-list for communication partners.                |
  | Field Devices / RTUs     | Manipulation of View    | Shielded cables and conduit routing; physical bus segregation per zone; passive network tap detection; restrict bus access to authorized master addresses.       |

- Denial of Service
  > Availability loss in OT/ICS environments can progress from Loss of View (operator blindness) to Loss of Control and, in safety-critical systems, to Physical Damage to Property.

  | Asset Type               | OT Impact                                    | Key Mitigations                                                                                                                                                 |
  | ------------------------ | -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | SCADA Server / Historian | Loss of View, Denial of View                 | Redundant SCADA servers (active/standby); watchdog monitoring with automated failover; graceful degradation to local HMI panels on server unavailability.       |
  | Engineering Workstation  | Loss of Control                              | Separate engineering workstation from real-time control path; workstation failure must not affect running PLC programs.                                         |
  | HMI / Operator Station   | Denial of View, Loss of Control              | Redundant HMI stations per critical area; local operator panel with hardwired status indicators as backup; uninterruptible power supply (UPS) for HMI hardware. |
  | PLC / PAC                | Loss of Control, Physical Damage to Property | Communication timeout with safe-state fallback; watchdog timer supervision of control loop; industrial firewall with rate limiting; bus load monitoring.        |
  | Field Devices / RTUs     | Physical Damage to Property                  | Fail-safe spring-return or de-energize-to-trip actuator selection; hardware interlocks independent of communication state; physical over-travel limit switches. |

- Elevation of Privilege
  > Privilege escalation in OT/ICS environments allows attackers to transition from operator-level read access to engineer-level write access, ultimately reaching unrestricted control of the process.

  | Asset Type               | OT Impact                                            | Key Mitigations                                                                                                                                                                                     |
  | ------------------------ | ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | SCADA Server / Historian | Manipulation of Control, Physical Damage to Property | RBAC with least-privilege accounts; privileged access workstations (PAWs) for admin operations; periodic access review; remove all default vendor accounts.                                         |
  | Engineering Workstation  | Manipulation of Control                              | Dedicated engineering accounts with no internet access; host-based application allow-listing; OS hardening baseline (CIS benchmarks for ICS).                                                       |
  | HMI / Operator Station   | Unauthorized Command, Loss of Control                | Operator/administrator role separation; mandatory session timeout; physical key-switch for mode change (operator → engineer); prevent USB-based privilege tools.                                    |
  | PLC / PAC                | Manipulation of Control, Physical Damage to Property | Physical write-protect switch for firmware and critical parameter blocks; function code restrictions (deny program download in run mode); maintenance mode protection requiring physical keyswitch. |
  | Field Devices / RTUs     | Physical Damage to Property, Environmental Release   | Restrict parameterization access to engineering network only; firmware update requires physical presence and signed package; hardware jumper to lock configuration.                                 |

#### 5.2.3. MITRE ATT&CK Mapping

MITRE ATT&CK technique reference for OT/ICS threat scenarios. Use these mappings to populate the `MITRE ID` field with specific adversary behaviors.

| Technique ID | Technique Name                        | Scenarios                                                                                                        |
| ------------ | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| T0801        | Monitor Process State                 | Passive eavesdropping on unencrypted industrial protocols (Modbus RTU/TCP, PROFIBUS, proprietary serial).        |
| T0813        | Denial of Control                     | Legitimate control commands blocked or discarded; process cannot be adjusted during upsets.                      |
| T0814        | Denial of Service                     | Bus contention, frame flooding, communication disruption on serial or network interfaces.                        |
| T0827        | Loss of Control                       | Operators unable to send control commands to field devices; manual override may be the only option.              |
| T0828        | Environmental Release                 | Unauthorized release of hazardous materials or contamination events triggered by control manipulation.           |
| T0829        | Loss of View (Denial)                 | Operators blinded by corrupted, suppressed, or replayed HMI/SCADA displays and alarm outputs.                    |
| T0829        | Loss of View (Availability)           | Process visibility lost due to HMI or SCADA server unavailability; operators cannot monitor state.               |
| T0831        | Manipulation of Control               | Issuing unauthorized setpoint changes or mode transitions via compromised HMI or protocol injection.             |
| T0832        | Manipulation of View                  | False process data injected into historian records or displayed on HMI to mislead operators.                     |
| T0842        | Hardware Debug                        | Exploiting JTAG, SWD, or UART debug interfaces for firmware extraction or modification.                          |
| T0843        | Program Download / Code Injection     | Exploiting firmware update mechanisms, buffer overflows, or protocol parsing vulnerabilities for code execution. |
| T0852        | Screen Capture / Replay               | Capturing and replaying valid protocol messages when no sequence numbers or timestamps exist.                    |
| T0855        | Unauthorized Command Message          | Sending malformed or out-of-range values via industrial protocols to manipulate process variables.               |
| T0859        | Valid Accounts / Unauthorized Command | Spoofing PLC/HMI identity on unauthenticated protocols (Modbus, DNP3). Device accepts commands from any source.  |
| T0879        | Physical Damage to Property           | Physical destruction of machinery or infrastructure caused by out-of-range commands or safety bypass.            |
| T0880        | Personnel Safety Risk                 | Conditions created that endanger human operators or maintenance personnel.                                       |

> [!NOTE]
> T0829 covers two distinct impact categories. **Denial of View** is intentional blinding (e.g., alarm suppression, display injection). **Loss of View** results from availability failure (e.g., server crash, network outage). Distinguish the root cause in the `Justification` field by stating whether the origin is adversarial manipulation or system unavailability.

#### 5.2.4. CVSS v4.0 Mapping

- Exploitability Metrics
  > Select the appropriate attack vector based on the physical and logical access requirements of the modeled interface.

  | Attack Vector     | OT/ICS Scenarios                                                  | Example Interfaces                       |
  | ----------------- | ----------------------------------------------------------------- | ---------------------------------------- |
  | `AV:N` (Network)  | IP-connected devices, remote SCADA, cloud-connected gateways      | Modbus/TCP, EtherNet/IP, OPC UA, MQTT    |
  | `AV:A` (Adjacent) | Shared industrial bus, field network segment, same VLAN           | Modbus RTU (RS-485), PROFIBUS, CAN       |
  | `AV:L` (Local)    | Workstation software, HMI application, local file access          | Engineering software, local DB           |
  | `AV:P` (Physical) | Direct cable connection, removable debug port, hardware tampering | RS-232, JTAG, SWD, USB, hardware buttons |

- Vulnerable System Impact Metrics
  > Map STRIDE categories to CVSS v4 Impact Metrics using the primary impact metrics to determine the base score and severity, and the secondary impact metrics to inform the justification and vector details.

  | STRIDE Category        | Primary CVSS v4 | Secondary CVSS v4 | Confidence  | Rationale                                                                                                                                                                                                                                                                                                                                                                                                                       |
  | ---------------------- | --------------- | ----------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | Spoofing               | VI              | VC                | Medium      | Identity impersonation primarily corrupts trust and authorization decisions, which is best represented as integrity impact. Confidentiality is often a follow-on effect when impersonation grants access to protected data.                                                                                                                                                                                                     |
  | Tampering              | VI              | VA, VC            | High        | Unauthorized modification is directly an integrity impact. Availability and confidentiality may also be affected when tampering disrupts operation or alters protection controls.                                                                                                                                                                                                                                               |
  | Repudiation            | VI              | VC                | Medium-Low  | CVSS has no explicit non-repudiation or auditability metric. Repudiation is therefore best represented through integrity harm to logs, records, and transaction evidence, with occasional secondary confidentiality implications.                                                                                                                                                                                               |
  | Information Disclosure | VC              | VI                | High        | Unauthorized exposure of information is directly a confidentiality impact. Integrity is only indirect or downstream.                                                                                                                                                                                                                                                                                                            |
  | Denial of Service      | VA              | VI                | High        | Service degradation or outage is directly an availability impact. Integrity may be secondarily affected where incomplete processing or inconsistent state results.                                                                                                                                                                                                                                                              |
  | Elevation of Privilege | VI, VC, VA      | None              | Medium-High | Privilege gain commonly enables unauthorized modification and unauthorized access, making integrity and confidentiality primary. Availability is often a secondary consequence when elevated rights permit shutdown, deletion, or resource exhaustion. The primary impact depends on the privileges gained: <br>• _Read_ access → Confidentiality<br>• _Write_ access → Integrity<br>• _Admin/Execution_ access → Availability. |

- Subsequent System Impact Metrics for OT/ICS
  > In OT/ICS environments, compromising one component often affects downstream systems. Use SC/SI/SA to capture cascading effects on the physical process, safety systems, or connected devices.

  | Scenario                                         | SC  | SI  | SA  | Rationale                                                                                                                      |
  | ------------------------------------------------ | --- | --- | --- | ------------------------------------------------------------------------------------------------------------------------------ |
  | Compromised PLC affects downstream actuators     | N   | H   | H   | PLC compromise enables unauthorized control of physical process, affecting integrity and availability of actuators and valves. |
  | Firmware tampering enables lateral movement      | H   | H   | H   | Compromised device can be used to attack other devices on same network segment.                                                |
  | Debug interface exposes firmware secrets         | H   | N   | N   | Extracted credentials or keys may compromise other devices using shared secrets.                                               |
  | DoS on communication interface                   | N   | N   | H   | Loss of communication causes upstream PLC to trigger fault handling or fail-safe mode.                                         |
  | Configuration change via engineering workstation | N   | H   | N   | Modified setpoints propagate to field devices, affecting process integrity.                                                    |

#### 5.2.5. Likelihood of Exploit Mapping

The BSI Likelihood of Exploit categorizes the probability of a threat being successfully exploited. It considers both the technical feasibility and the availability of exploit techniques.

> [!NOTE]
> Map the `CVSS v4.0 Exploitability Metrics` to BSI likelihood categories. The Vulnerable/Subsequent System Impact Metrics are excluded since likelihood derives from exploit feasibility, not consequence severity.

- Exploitation Method
  > Determine the exploitation method (columns) based on the modeled attack scenario and CVSS Exploitability Metrics.

  | Method                          | CVSS Exploitability Metrics                                       | Description                                                                                        |
  | ------------------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
  | Manual (Manuell)                | `AV:P` and at least one of `AC:H`, `AT:P`, `PR:H`, `UI:P`, `UI:A` | Requires physical presence, user participation, high complexity, or explicit attack prerequisites. |
  | Automated (Automatisch)         | `AV:A` or `AV:L`, `AC:L`, `AT:N`, `PR:N`, `PR:L`, `UI:N`          | Remotely or adjacently exploitable with low complexity and no user interaction.                    |
  | Self-Replicating (Replizierend) | `AV:N`, `AC:L`, `AT:N`, `PR:N`, `UI:N`                            | Network-reachable with zero friction and the scenario describes autonomous propagation behavior.   |

  > [!NOTE]
  > `PR` (Privileges Required) is independent of the exploitation method in most cases. Do not change the method classification based on `PR` alone. Self-Replicating typically implies `PR:N` because autonomous propagation rarely depends on pre-existing credentials.

- Vulnerability State
  > Determine the vulnerability state (rows) based on evidence of exploit maturity, which may come from the `Justification` field or from external sources such as threat intelligence, public exploit databases, or observed attack activity.

  | State                                      | CVSS Threat Metrics | Description                                                                                                                                |
  | ------------------------------------------ | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
  | Theoretical (Theoretisch)                  | `E:U`               | No known exploit,  attack is conceptually possible but unverified.                                                                         |
  | Exploitable (Ausnutzbar)                   | `E:P`               | Proof-of-concept exists or the technique is documented and reproducible.                                                                   |
  | Active (Aktiv)                             | `E:A`               | Active exploitation observed in the wild or in targeted campaigns.                                                                         |
  | Exploit Published (Exploit Veröffentlicht) | `E:A`               | Public exploit code or tooling is freely available. CVSS does not distinguish from Active, apply when public availability amplifies reach. |

- Likelihood Matrix

  | State / Method                             | Manual (Manuell)   | Automated (Automatisch) | Self-Replicating (Replizierend) |
  | ------------------------------------------ | ------------------ | ----------------------- | ------------------------------- |
  | Theoretical (Theoretisch)                  | Info (sehr gering) | Low (gering)            | Medium (mittel)                 |
  | Exploitable (Ausnutzbar)                   | Low (gering)       | Medium (mittel)         | High (hoch)                     |
  | Active (Aktiv)                             | Medium (mittel)    | High (hoch)             | High (hoch)                     |
  | Exploit Published (Exploit Veröffentlicht) | Medium (mittel)    | High (hoch)             | Critical (sehr hoch)            |

#### 5.2.6. Risk Prioritization Mapping

- Risk Prioritization
  > Combine `CVSS v4.0 Severity` and `Likelihood of Exploit` to determine an overall risk prioritization level for each threat.

  | Likelihood \ Severity | None   | Low    | Medium | High     | Critical |
  | --------------------- | ------ | ------ | ------ | -------- | -------- |
  | Info                  | Info   | Info   | Low    | Low      | Medium   |
  | Low                   | Info   | Low    | Low    | Medium   | High     |
  | Medium                | Low    | Low    | Medium | High     | High     |
  | High                  | Low    | Medium | High   | High     | Critical |
  | Critical              | Medium | High   | High   | Critical | Critical |

#### 5.2.7. Threat Actor Mapping

Normalize the `Threat Actor` decision from common OT/ICS threat-path characteristics. Always pick the minimum actor that satisfies the required access, capability, and process knowledge, and only reassess upward when the modeled path requires capabilities beyond the currently selected label.

| Threat-path characteristics                                                                 | Minimum Threat Actor                  | Selection logic                                                                                           |
| -------------------------------------------------------------------------------------------- | ------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Internet-exposed HMI, VPN, web service, or remote access path exploited with commodity tooling for extortion, fraud, or monetized access | `Cybercriminal` | Choose this label when the differentiator in the modeled row is financial gain, fraud, or scalable criminal reuse. |
| Internet-exposed HMI, VPN, web service, or remote access path exploited for publicity, protest, or symbolic disruption | `Hacktivist` | Choose this label when the differentiator in the modeled row is ideological messaging, defacement, or proof-of-access rather than monetization. |
| Extortion, ransomware staging, or financially motivated IT/OT pivoting                      | `Cybercriminal`                       | Use when commodity or affiliate-operated intrusion tradecraft is enough to disrupt operations for payment or fraud. |
| Trusted maintenance path, engineering workstation misuse, badge access, or privileged misuse | `Insider Threat`                      | Use when success depends on privileged local access, physical presence, or direct operational familiarity. |
| Trojanized engineering software, malicious firmware, or a tainted vendor update used for covert pre-positioning or sabotage | `Nation-State Actor` | The same supplier-channel path can support other actors, but choose this label when the modeled objective is covert pre-positioning or mission-specific sabotage. Example: a trojanized engineering software update that quietly establishes long-term access to safety controllers. |
| Compromised vendor tooling, update service, or MSP remote-management channel reused for broad extortion or monetized access | `Cybercriminal` | The same supplier-channel path can support other actors, but choose this label when the modeled objective is scalable extortion, fraud, or ransomware deployment. Example: a compromised remote management platform reused to deploy ransomware across multiple customer sites. |
| Coordinated multi-stage intrusion needing custom tooling, stealth, or deep process expertise | `Nation-State Actor`                  | Use only when lower-tier actors cannot plausibly achieve the path without advanced tradecraft or mission-specific OT knowledge. |

> [!NOTE]
> The presence of high impact alone does not justify a more capable actor. Terms such as `APT`, `Ransomware Operator`, `Supply Chain Attacker`, and `Script Kiddie` may appear in justification text, but not as `Threat Actor` labels.
>
> When an internet-exposed path could support both financially motivated and ideologically motivated abuse, choose the actor that best matches the modeled objective in the row. Default to `Cybercriminal` when the scenario emphasizes monetization or reusable unauthorized access; choose `Hacktivist` when the primary effect is messaging, protest, or public proof-of-access.
>
> The same supplier-channel path can support different actor classes. When vendor tooling, firmware distribution, or MSP access is involved, still record exactly one canonical label based on the modeled campaign objective: sabotage or covert pre-positioning maps to `Nation-State Actor`, while monetized reuse maps to `Cybercriminal`.

### 5.3. Template

Use these templates for Microsoft TMT CSV intake and review.

#### 5.3.1. Raw TMT Export CSV Template

- `<Device_Name>_Threat_Model.csv`
  > The raw export from Microsoft TMT in comma delimited CSV format.

  ```csv
  Id,Title,Category,Diagram,Interaction,Priority,State,Changed By,Description,Justification,Last Modified
  0,Spoofing the MCU Process,Spoofing,<Device_Name>,Debugger to MCU over JTAG,High,Not Started,,MCU may be spoofed by an attacker and this may lead to information disclosure by Debugger Probe. Consider using a standard authentication mechanism to identify the destination process.,,Generated
  38,Data Flow MCU to CFG over Modbus RTU (RS-232) Is Potentially Interrupted,Denial Of Service,<Device_Name>,MCU to CFG over Modbus RTU (RS-232),High,Not Started,,An external agent interrupts data flowing across a trust boundary in either direction.,,Generated
  72,Elevation Using Impersonation,Elevation Of Privilege,<Device_Name>,Operator to MCU over Switches (GPIO),High,Not Started,,MCU may be able to impersonate the context of Operator in order to gain additional privilege.,,Generated
  ```

#### 5.3.2. Reviewed TMT CSV Template

- `<Device_Name>_Threat_Model_Generated.csv`
  > The completed analyst review of the TMT export in semicolon-delimited CSV format with review columns appended. The required tail-column order is `Likelihood of Exploit;Risk Prioritization;Threat Actor;Risk Treatment`.

  ```csv
  Id;Title;Category;Diagram;Interaction;Priority;State;Changed By;Description;Justification;Last Modified;MITRE ID;CWE ID;CVSS v4.0 Vector;CVSS-B v4.0 Score;CVSS v4.0 Severity;Likelihood of Exploit;Risk Prioritization;Threat Actor;Risk Treatment
  0;Spoofing the MCU Process;Spoofing;<Device_Name>;Debugger to MCU over JTAG;Medium;Needs Investigation;;"MCU may be spoofed by an attacker and this may lead to information disclosure by Debugger Probe. Consider using a standard authentication mechanism to identify the destination process.";"The physical JTAG maintenance path makes Insider Threat the minimum actor because physical service access and debug familiarity are required. A rogue interposer or substituted board could impersonate the MCU and capture debug traffic. Treatment is Mitigation through authenticated debug unlock and production-time debug lockout; residual risk owner remains product security.";Generated;T0842;CWE-1191;CVSS:4.0/AV:P/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N;"6,7";Medium;Medium;Medium;Insider Threat;Mitigation
  38;Data Flow MCU to CFG over Modbus RTU (RS-232) Is Potentially Interrupted;Denial Of Service;<Device_Name>;MCU to CFG over Modbus RTU (RS-232);Low;Mitigated;;"An external agent interrupts data flowing across a trust boundary in either direction.";"This RS-232 interruption affects a local maintenance session more than the primary control function. Insider Threat is the minimum actor because the attack requires direct physical or maintenance-port access. The actuator remains locally autonomous with fail-safe behavior, so residual impact is low. Treatment is Acceptance with monitoring.";Generated;T0814;CWE-693;CVSS:4.0/AV:P/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:L;"2,4";Low;Low;Low;Insider Threat;Acceptance
  72;Elevation Using Impersonation;Elevation Of Privilege;<Device_Name>;Operator to MCU over Switches (GPIO);Low;Not Applicable;;"MCU may be able to impersonate the context of Operator in order to gain additional privilege.";"Insider Threat is the minimum candidate because only local operator-side access is in scope, but this dry-contact GPIO path has no machine-to-machine trust boundary the MCU can impersonate. Treatment is Avoidance by keeping the interface free of machine-authenticated trust.";Generated;;;;;;;;Insider Threat;Avoidance
  ```

## 6. References

- Microsoft [Threat Modeling Tool](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool) documentation.
- Microsoft [Threat Modeling Fundamentals](https://learn.microsoft.com/en-us/training/paths/tm-threat-modeling-fundamentals/) training.
- STRIDE [Threat Modeling](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats) guide.
- MITRE [ATT&CK for ICS](https://attack.mitre.org/matrices/ics/) matrix.
- MITRE [CWE](https://cwe.mitre.org/) page.
- FIRST [CVSS v4.0 Specification](https://www.first.org/cvss/v4.0/specification-document) page.
- FIRST [CVSS v4.0 Calculator](https://www.first.org/cvss/calculator/4.0) page.
- BSI [Risk Prioritization](https://www.bsi.bund.de/DE/Service-Navi/Abonnements/Newsletter/Buerger-CERT-Abos/Buerger-CERT-Sicherheitshinweise/Risikostufen/risikostufen.html) page.
- IEC [62443 Industrial Automation and Control Systems Security](https://www.iec.ch/cyber-security) standards.
- ISO [31000 Risk Management](https://www.iso.org/iso-31000-risk-management.html) standard.
- NIST [SP 800-30 Guide for Conducting Risk Assessments](https://csrc.nist.gov/publications/detail/sp/800-30/rev-1/final) publication.
- NIST [SP 800-82 Guide to OT Security](https://csrc.nist.gov/publications/detail/sp/800-82/rev-3/final) publication.
- CISA [Nation-State Threats](https://www.cisa.gov/topics/cyber-threats-and-advisories/nation-state-cyber-actors) page.
- CISA [Defining Insider Threats](https://www.cisa.gov/topics/physical-security/insider-threat-mitigation/defining-insider-threats) page.
