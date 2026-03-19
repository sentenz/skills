---
name: threat-modeling
description: Automates threat modeling tasks for OT/ICS and general software systems using STRIDE, MITRE ATT&CK, CWE, and CVSS v4.0. Use when creating threat models, performing security reviews, mapping threats to MITRE ATT&CK and CWE, or calculating CVSS scores. Applicable to any system architecture with data flows, trust boundaries, and external entities.
metadata:
  version: "1.0.0"
  activation:
    implicit: true
    priority: 1
    triggers:
      - "threat model"
      - "threat modeling"
      - "STRIDE"
      - "security review"
      - "MITRE ATT&CK"
      - "CWE"
      - "CVSS"
      - "attack surface"
      - "trust boundary"
      - "data flow diagram"
    match:
      languages: []
      paths: ["**/*.csv", "**/*.md", "**/*.vpp"]
      prompt_regex: "(?i)(threat model|stride|security review|mitre att&ck|cwe|cvss|attack surface|trust boundary|data flow diagram)"
  usage:
    load_on_prompt: true
    autodispatch: true
---

# Threat Modeling

Instructions for AI coding agents on automating threat modeling tasks for OT/ICS and general software systems.

- [1. Skills](#1-skills)
  - [1.1. Prompt for Model](#11-prompt-for-model)
  - [1.2. Prompt for Security Review](#12-prompt-for-security-review)
  - [1.3. Prompt for MITRE ATT\&CK and CWE Mapping](#13-prompt-for-mitre-attck-and-cwe-mapping)
  - [1.4. Prompt for CVSS](#14-prompt-for-cvss)
- [2. Architecture Model](#2-architecture-model)

## 1. Skills

### 1.1. Prompt for Model

Goal: Produce a complete STRIDE threat model and a render-ready Mermaid diagram for the SAMSON Type 3374 electrical actuator together with the TROVIS-VIEW configuration software.

Deliverables:

1. A Mermaid diagram (include the `%%{init:...}%%` block) modeling:
    - External entities: Engineer/Technician PC (TROVIS-VIEW), PLC/SCADA, portable storage (USB/Memory pen).
    - Management zone: TROVIS-VIEW, local config files (.vpp), USB/Serial adapter.
    - Communication bridge: USB<->RS-232 or USB<->RS-485 adapter, RS-485/Serial interface (SSP/Modbus RTU) on the actuator.
    - Device boundary: Type 3374 positioner logic/firmware, EEPROM/flash configuration storage, local UI (LCD & keys), motor & mechanical fail-safe, sensors and valve.
    - Physical process: Valve and process media.
    - Directed data flows with stable IDs (DF1, DF2, ...), and trust boundaries (management vs device vs physical).

2. A STRIDE mapping: for each relevant component or data flow list applicable STRIDE categories (Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege), one-sentence attack example, severity (High/Medium/Low), and a concise mitigation (one line).

3. A short prioritized mitigation checklist (3–6 items) and any assumptions made (1–2 lines if a public detail is missing).

Formatting & constraints:

- Provide the Mermaid code block first (render-ready). Use `classDef` to differentiate trust boundaries and threats, and annotate threat-prone nodes/flows visually.
- Use clear DF IDs in the diagram so the STRIDE mapping can reference them directly.
- Keep Mermaid output under ~300 lines. Keep textual findings concise (1–2 sentences each).
- If a product detail is not public, state a reasonable assumption in one sentence and continue.

Reference guidance: Use the SAMSON Type 3374 product page and TROVIS-VIEW software page for interface and behavior context.

Example instruction line to the model: "If a detail is not public, state a reasonable assumption in one line and continue."

See reference:

- https://www.samsongroup.com/en/products/actuators/3374/
- https://www.samsongroup.com/en/downloads/software-drivers/trovis-view/

### 1.2. Prompt for Security Review

Conduct a security review of the threats identified in the `.csv` threat modeling file. Update the dataset by refining the State, Priority levels and generate new, actionable Justification descriptions based on the specific threats, interactions (such as data flow communication), and standard operational technology (OT) security risks.

Role: Act as a Senior OT (Operational Technology) Security Architect.

Task: Perform a row-by-row security review of the provided threat-model `.csv` and update only `Priority`, `State`, and `Justification`.

Objective:

- Reassess each threat using OT context (industrial safety, process availability, integrity of setpoints, serial/Modbus risks, weak or absent authentication, insecure engineering workstations, removable media exposure).
- Produce consistent and actionable output that can be written back to the same `.csv` without changing schema.

Tech Stack:

- Microsoft TMT (Threat Modeling Tool)
- STRIDE

Input assumptions:

- The `.csv` contains threat entries with fields such as `Category`, `Interaction`, `Description`, and existing `Priority`, `State`, `Justification`.
- `Interaction` refer to specific data flow communication paths (for example USB, RS-485, Modbus RTU, firmware/config file transfer, Pub/Sub, Request/Response, local HMI/manual override).

Update rules (required):

1. Refine `Priority`
    - Use `Category`, `Interaction`, and `Description` together.
    - Assign `High` when exploitation could plausibly cause unsafe actuator movement, loss of control, major production disruption, or persistent compromise.
    - Assign `Medium` when impact is operationally meaningful but bounded/recoverable.
    - Assign `Low` when impact is limited, compensating controls are strong, or exploitation is unlikely in the current architecture.

2. Refine `State`
   The available states are `Not Started`, `Not Applicable`, `Needs Investigation` and `Mitigated`.
    - Assign `Not Started` when the threat has not yet been reviewed or assessed.
    - Assign `Needs Investigation` when the threat is credible but requires further analysis to confirm exploitability or impact.
    - Assign `Mitigated` when there is a clear, actionable control that can be implemented to reduce risk to an acceptable level.
    - Avoid `Not Applicable` unless the threat truly cannot occur in this context (for example, a web-based attack vector on a non-networked device).

3. Regenerate `Justification`
    - Write 1-2 concise sentences.

Output constraints (strict):

- Preserve all original rows and row order.
- Do not add or remove columns.
- Modify only `Priority`, `State`, and `Justification`.
- Use exact `Priority` values: `High`, `Medium`, `Low`.
- Use exact `State` values: `Needs Investigation`, `Mitigated` or `Not Applicable`.
- Keep language technical and concise.

Quality check before finalizing:

- Verify each `Justification` references a specific mechanism from the row context.
- Verify each mitigation is actionable and relevant to OT/ICS environments.
- Verify `State` is consistent with the final `Priority` for every row.

### 1.3. Prompt for MITRE ATT&CK and CWE Mapping

Map the identified threats from the `.csv` threat modeling file to relevant MITRE ATT&CK techniques and CWE weaknesses. Update the dataset by adding two new columns: `MITRE ID` and `CWE ID`, populated with the most applicable entries based on the threat descriptions and interactions.

1. Reference

    - MITRE [ATT&CK](https://attack.mitre.org/) page.
    - MITRE [ATT&CK Matrix for ICS](https://attack.mitre.org/matrices/ics/) page.
    - MITRE [ATT&CK Tactics for ICS](https://attack.mitre.org/tactics/ics/) page.
    - MITRE [ATT&CK Techniques for ICS](https://attack.mitre.org/techniques/ics/) page.
    - MITRE [CWE](https://cwe.mitre.org/index.html) page.

2. Example

Derive from Markdown example.

- https://attack.mitre.org/techniques/T0814/
- https://cwe.mitre.org/data/definitions/400.html

| MITRE ID | CWE ID  |
| :------- | :------ |
| T0814    | CWE-400 |
| T0832    | CWE-294 |

### 1.4. Prompt for CVSS

Calculate CVSS scores for each identified threat in the `.csv` threat modeling file based on the provided descriptions, interactions, and potential impacts. Update the dataset by adding a new column for `CVSS v4.0 Score`, `CVSS v4.0 Severity` and `CVSS v4.0 Vector`, populated with the calculated score for each threat.

- Generate Vectors from each row's Category, Interaction, Priority, State, Description, and Justification.
- Compute Scoring using a CVSS v4.0-capable library and validated as parsable vectors.

1. Reference

    - FIRST [CVSS v4.0 Calculator](https://www.first.org/cvss/calculator/4.0) page.

2. Example

Derive from Markdown example.

- https://www.first.org/cvss/calculator/4.0#CVSS:4.0/AV:A/AC:H/AT:P/PR:H/UI:N/VC:H/VI:L/VA:L/SC:L/SI:L/SA:L
- https://www.first.org/cvss/calculator/4.0#CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H
- https://www.first.org/cvss/calculator/4.0#CVSS:4.0/AV:P/AC:H/AT:P/PR:H/UI:A/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N

| CVSS v4.0 Score | CVSS v4.0 Severity | CVSS v4.0 Vector                                                   |
| --------------: | :----------------: | :----------------------------------------------------------------- |
|             5.8 |       Medium       | CVSS:4.0/AV:A/AC:H/AT:P/PR:H/UI:N/VC:H/VI:L/VA:L/SC:L/SI:L/SA:L |
|             9.5 |      Critical      | CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H |
|             1.0 |        Low         | CVSS:4.0/AV:P/AC:H/AT:P/PR:H/UI:A/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N |

## 2. Architecture Model

The architecture model describes the system components, trust boundaries, and data flows used in the threat model. Use the following structure as a reference when producing the Mermaid diagram.

- External entities
  > Actors outside the system boundary that interact with the system (e.g., Engineer/Technician PC, PLC/SCADA, portable storage).

- Management zone
  > The software and configuration layer used to manage the device (e.g., TROVIS-VIEW, local config files, USB/Serial adapter).

- Communication bridge
  > Physical and protocol adapters that connect the management zone to the device (e.g., USB<->RS-232, RS-485/Serial interface, SSP/Modbus RTU).

- Device boundary
  > The embedded system under analysis, including firmware, configuration storage, local UI, motor control, and sensors.

- Physical process
  > The physical output of the device and its interaction with the process environment (e.g., valve position, process media).
