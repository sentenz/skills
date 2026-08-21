# Mapping Rules

Use these rules only after reading the applicable workflow step in `SKILL.md`. Treat `SKILL.md` as authoritative if a workflow instruction conflicts with this reference.

- [1. Connection-Path Scope Classification](#1-connection-path-scope-classification)
- [2. CIA Impact Reference](#2-cia-impact-reference)
- [3. Diagram Depth Layers](#3-diagram-depth-layers)
- [4. Purdue Model Mapping](#4-purdue-model-mapping)
  - [4.1. Purdue Zone Reference](#41-purdue-zone-reference)
  - [4.2. Threat-Surface Mapping](#42-threat-surface-mapping)
- [5. STRIDE Classification](#5-stride-classification)
- [6. EMB3D Mitigation Levels](#6-emb3d-mitigation-levels)
- [7. Impact Mapping](#7-impact-mapping)
  - [7.1. Exploitability Metrics](#71-exploitability-metrics)
  - [7.2. Vulnerable System Impact Metrics](#72-vulnerable-system-impact-metrics)
  - [7.3. Subsequent System Impact Metrics](#73-subsequent-system-impact-metrics)
- [8. Probability Mapping](#8-probability-mapping)
  - [8.1. Exploitation Method](#81-exploitation-method)
  - [8.2. Vulnerability State](#82-vulnerability-state)
  - [8.3. Likelihood Matrix](#83-likelihood-matrix)
- [9. Risk Matrix Mapping](#9-risk-matrix-mapping)
- [10. Threat Actor Mapping](#10-threat-actor-mapping)
  - [10.1. Capability Boundaries](#101-capability-boundaries)
  - [10.2. Scenario Mapping](#102-scenario-mapping)
- [11. Risk Treatment Mapping](#11-risk-treatment-mapping)
  - [11.1. Treatment Semantics](#111-treatment-semantics)
  - [11.2. Treatment Decision Guidance](#112-treatment-decision-guidance)
  - [11.3. State and Treatment Compatibility](#113-state-and-treatment-compatibility)
  - [11.4. Treatment Evidence Requirements](#114-treatment-evidence-requirements)
- [12. Risk Approval Mapping](#12-risk-approval-mapping)
- [13. MITRE CWE Mapping Rules](#13-mitre-cwe-mapping-rules)

## 1. Connection-Path Scope Classification

Connection paths are classified as either [direct or indirect, logical or physical data connections to a device or network](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202402847#art_2), using the linked [definitions](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202402847#art_3) for connection path, connection type, and target.

> [!NOTE]
> A **logical connection** describes the software interface, protocol session, addressing relationship or other virtual representation through which data is exchanged. A **physical connection** describes the physical means implementing the connection, including electrical, optical or mechanical interfaces, wires and radio waves. An **indirect connection** reaches the target through a larger system that is itself directly connectable to the device or network. A **direct connection** reaches the target without passing through any other directly connectable system.

| Case | Connection Path | Connection Type | Target  | Interpretation                                 | Representative                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ---- | --------------- | --------------- | ------- | ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C1   | Direct          | Logical         | Device  | Direct logical data connection to a device     | A software or protocol interaction addressed directly to a particular device or component: a Modbus RTU request/response addressed to one slave; an RS-232 or UART console session; a JTAG/SWD debug session directed to a target MCU; a managed UPS command session; a local bootloader command channel; an SPI/I²C transaction addressed to a specific EEPROM, Flash device or peripheral; or an IrDA session or device-addressed IR command, such as NEC or RC-5/RC-6. The classification concerns the protocol, commands, addressing and software-visible interface rather than the underlying electrical, optical or radio bearer.                                                                           |
| C2   | Direct          | Logical         | Network | Direct logical data connection to a network    | A software interaction directed to, or operating on, a shared network rather than exclusively to one device: a Modbus broadcast on an RS-485 segment; network-wide discovery, enumeration or diagnostic functions; maintenance software interacting with a shared serial bus; a network-management interface operating on an Ethernet, WLAN or fieldbus network; or discovery, broadcast or management over a shared IR network. The logical interaction is independent of whether the physical bearer is electrical, optical or radio.                                                                                                                                                                           |
| C3   | Direct          | Physical        | Device  | Direct physical data connection to a device    | A point-to-point physical attachment between the connecting system and the target device. **Electrical or wired:** an RS-232/UART cable, USB service cable, JTAG/SWD probe and ribbon cable, GPIO or discrete digital-I/O wiring, SPI/I²C traces, or a board-to-board electrical connection. **Optical:** a point-to-point fibre-optic link or IrDA, IR service or remote-control link. **Mechanical-interface:** a mated plug and receptacle, docking interface, card slot or board connector through which the data connection is established. **Radio-wave:** a direct NFC, Bluetooth or proprietary point-to-point RF link.                                                                                   |
| C4   | Direct          | Physical        | Network | Direct physical data connection to a network   | Direct attachment of the product to a shared physical network medium. **Electrical or wired:** an RS-485 multidrop bus, CAN bus, wired Ethernet LAN, USB bus or industrial backplane. **Optical:** fibre Ethernet, an optical fieldbus, an IR optical LAN or shared free-space optical network. **Mechanical-interface:** an Ethernet jack, fieldbus coupler, backplane slot, hub port or other mating network connector. **Radio-wave:** direct attachment through the product's own Wi-Fi, Bluetooth Mesh, Zigbee, Thread, cellular or other network radio interface.                                                                                                                                           |
| C5   | Indirect        | Logical         | Device  | Indirect logical data connection to a device   | A device-specific software or protocol interaction relayed or mediated by a larger system: a maintenance workstation sending commands through a PLC or gateway to an embedded device; an HMI request relayed by a controller; a firmware-update command passed through application software to a bootloader; EEPROM or Flash access mediated by application firmware; a remote management session entering through a gateway before invoking a device-specific command interface; or a device command relayed through an IR gateway or blaster. The IR protocol remains the logical device interface, while the intermediary makes the connection indirect.                                                       |
| C6   | Indirect        | Logical         | Network | Indirect logical data connection to a network  | Software-level access to a network through an intermediary system or service: a maintenance application using a VPN, remote desktop session or site gateway to reach a field network; a virtual COM-port or TCP-to-serial service providing access to a Modbus RTU segment; an HMI reaching a CAN or RS-485 network through a PLC acting as a protocol gateway; diagnostic software accessing a WLAN or fieldbus through a router, serial server or network-management appliance; or logical access to an IR network through an IR gateway.                                                                                                                                                                       |
| C7   | Indirect        | Physical        | Device  | Indirect physical data connection to a device  | A physical path to a device that passes through one or more intermediate components or a larger directly connectable system: a laptop connected through a USB cable, debug probe and ribbon cable to a target MCU; a workstation connected through a USB-to-RS-232 adapter to a device; a sensor or actuator connected through remote I/O, an isolator, signal conditioner or transmitter; a connection through a fibre-to-copper media converter or wireless bridge; an internal component connected through an adapter board, backplane or product-level external connector; or a device connection through a USB-to-IR or equivalent adapter. The final IR segment is an optical physical connection.          |
| C8   | Indirect        | Physical        | Network | Indirect physical data connection to a network | A physical path to a network implemented through an intermediate system or conversion stage: a maintenance workstation connected through a USB-to-RS-485 adapter or serial server to an RS-485 bus; an internal MCU connected through isolation, an RS-485 transceiver and a board connector to an external multidrop network; a device connected through a copper-to-fibre media converter to an optical network; an electrically connected device reaching a WLAN through an Ethernet-to-Wi-Fi bridge; a module connected through an industrial backplane and network coupler to a fieldbus; or network attachment through an IR adapter, access point or gateway. The IR segment is an optical network medium. |

## 2. CIA Impact Reference

The core principles of Information Security (InfoSec) are confidentiality, integrity, and availability (CIA). The CIA triad is used for evaluating the security posture of systems and data.

| CIA Principle   | Definition                                                                                            | Representative Threats                                                                                            |
| --------------- | ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Confidentiality | Ensures that information is accessible only to authorized users, systems, or processes.               | Unauthorized access, data breaches, credential theft, eavesdropping, information disclosure.                      |
| Integrity       | Ensures that information remains accurate, complete, and unaltered except through authorized actions. | Data tampering, unauthorized modification, malware, injection attacks, man-in-the-middle attacks, replay attacks. |
| Availability    | Ensures that systems, services, and data remain accessible to authorized users when required.         | Denial-of-service (DoS/DDoS), ransomware, hardware failure, power outages, resource exhaustion.                   |

## 3. Diagram Depth Layers

[Diagram depth layers](https://learn.microsoft.com/en-us/training/modules/tm-provide-context-with-the-right-depth-layer/1b-depth-layers) are used to decompose a system into hierarchical levels of detail, enabling threat modeling at varying levels of abstraction.

| Layer | Title       | Components                                                                                                                                                                                                                                                                          | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ----- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0     | System      | Embedded Device, PLC, HMI/Engineering Station, Maintenance Workstation, Debug/Flash Probe, Managed UPS, Sensors, Actuators, Remote I/O, Protocol Gateway/Serial Server, USB Host or Service Laptop                                                                                  | Mandatory initial view of the systems major parts. Represents the Embedded Device as a single process within its trust boundary and shows all relevant external entities, intermediary systems, data flows, and physical or logical connection paths. Establishes the system context and identifies the Layer 0 processes that may require further decomposition. ([Microsoft Layer 0][1])                                                                                                                                                                     |
| 1     | Process     | Controller/MCU, RS-485 Transceiver, RS-232 Transceiver, USB Interface, JTAG/SWD Interface, RJ-12/RJ-45 Connectors, GPIO Interface, Digital I/O, Analog I/O, Power Monitoring, Flash, EEPROM                                                                                         | Decomposes the Embedded Device process from Layer 0 into its principal board-level processes, interfaces, data stores, and trust boundaries. Identifies the products external physical and logical attack surfaces while retaining the Controller/MCU as a single process. Generally the appropriate minimum decomposition for evaluating an embedded product’s communication ports, field I/O, debug interface, storage, and service interfaces. ([Microsoft Layer 1][2])                                                                                     |
| 2     | Subprocess  | Application and Control Logic, Modbus RTU Stack, GPIO Driver, UART Driver, SPI Driver, I²C Driver, Digital-I/O Driver, ADC/DAC Driver, Scheduler/Interrupt Dispatch, Configuration Manager, Bootloader, Secure Boot, Firmware-Update Manager, Debug-Access Control, Memory Manager  | Decomposes the Controller/MCU process from Layer 1 into security-relevant firmware subprocesses and data flows. Focuses on protocol parsing, control decisions, privilege boundaries, interrupt handling, secure startup, firmware updates, debug authorization, configuration processing, and non-volatile-memory access. Appropriate where compromise of an internal controller function could affect device integrity, availability, process control, or connected systems. ([Microsoft Layer 2][3])                                                        |
| 3     | Lower-Level | Modbus RTU Frame Parser and Function Handlers, Boot Verification Chain, Firmware-Update State Machine, Signature Verification, Anti-Rollback Logic, UART ISR/DMA and Buffers, GPIO Interrupt/Debounce Logic, SPI/I²C Transaction State Machines, MPU Regions, Key-Handling Routines | Provides minute implementation detail for a selected critical Layer 2 subprocess rather than automatically decomposing the entire controller. Examines parser memory safety, input-validation branches, state transitions, buffer ownership, concurrency, cryptographic verification, privilege changes, key exposure, fault injection, and side-channel behavior. Reserved for security-critical, kernel-level, privileged, cryptographic, or timing-sensitive functions where Layer 2 does not provide sufficient analytical depth. ([Microsoft Layer 3][4]) |

[1]: https://learn.microsoft.com/en-us/training/modules/tm-provide-context-with-the-right-depth-layer/2-layer-0-the-system-layer "Layer 0 | The System Layer Training | Microsoft Learn"
[2]: https://learn.microsoft.com/en-us/training/modules/tm-provide-context-with-the-right-depth-layer/3-layer-1-the-process-layer "Layer 1 | The Process Layer Training | Microsoft Learn"
[3]: https://learn.microsoft.com/en-us/training/modules/tm-provide-context-with-the-right-depth-layer/4-layer-2-the-sub-process-layer "Layer 2 | The Subprocess Layer Training | Microsoft Learn"
[4]: https://learn.microsoft.com/en-us/training/modules/tm-provide-context-with-the-right-depth-layer/5-layer-3-the-lower-level-layer "Layer 3 | The Lower-Level Layer Training | Microsoft Learn"

## 4. Purdue Model Mapping

### 4.1. Purdue Zone Reference

| Purdue Level | Zone Label                | Representative Assets                                            |
| ------------ | ------------------------- | ---------------------------------------------------------------- |
| L5           | Enterprise                | ERP, Active Directory, email, cloud services.                    |
| L4           | Business Logistics        | Plant historian, remote access gateway, IT/OT bridge.            |
| DMZ          | ICS/IT Demilitarized Zone | Reverse proxy, data diode, firewall, jump server.                |
| L3           | Site Operations           | SCADA server, application server, batch management, HMI servers. |
| L2           | Area Supervisory          | Operator HMIs, engineering workstations, domain controllers.     |
| L1           | Basic Control             | PLCs, PACs, RTUs, SIS controllers.                               |
| L0           | Field Process             | Sensors, actuators, drives, valves.                              |

### 4.2. Threat-Surface Mapping

Use this table to identify the Purdue zone of each asset from `Interaction` or `Diagram`, and to validate that the modeled threat surface is consistent with the zone's prevalent STRIDE categories. Do not override TMT `Category` values solely from this table.

| Purdue Level | Zone        | Asset Type                              | Examples                                                           | Prevalent STRIDE Categories                                                             |
| ------------ | ----------- | --------------------------------------- | ------------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| Level 4–5    | Enterprise  | SCADA Server, Historian                 | OSIsoft PI, AVEVA System Platform, Wonderware.                     | Information Disclosure, Repudiation, Denial of Service, Elevation of Privilege.         |
| Level 3      | Operations  | Engineering Workstation, OPC Server     | Siemens TIA Portal, Rockwell Studio 5000, OPC UA Server.           | Spoofing, Tampering, Information Disclosure, Denial of Service, Elevation of Privilege. |
| Level 2      | Supervisory | HMI, Operator Station                   | Siemens WinCC, FactoryTalk View SE, Inductive Automation Ignition. | Spoofing, Tampering, Information Disclosure, Denial of Service.                         |
| Level 1      | Control     | PLC, PAC                                | Siemens S7, Allen-Bradley ControlLogix, Schneider Modicon.         | Tampering, Denial of Service, Elevation of Privilege.                                   |
| Level 0      | Field       | Sensors, Actuators, RTUs, Field Devices | Transmitters, positioners, motor drives, RTUs.                     | Tampering, Denial of Service.                                                           |

## 5. STRIDE Classification

STRIDE is the foundational threat classification scheme for understanding each threat statement and for guiding the review process.

| STRIDE Category        | Operational Meaning                                                                     |
| ---------------------- | --------------------------------------------------------------------------------------- |
| Spoofing               | Illegitimate use of an identity, endpoint, process, or trust relationship.              |
| Tampering              | Unauthorized modification of data, messages, logic, configuration, or execution inputs. |
| Repudiation            | Inability to prove an action, source, or responsibility.                                |
| Information Disclosure | Exposure of information to an unauthorized party.                                       |
| Denial Of Service      | Interruption, degradation, blocking, or exhaustion affecting availability.              |
| Elevation Of Privilege | Gain of permissions beyond the intended security boundary.                              |

## 6. EMB3D Mitigation Levels

Mitigation levels classify the extent and sophistication of mitigations applied to an identified threat, ranging from no implemented mitigation to comprehensive and adaptive mitigation across the relevant architectural layers.

| Level | Maturity     | General Interpretation                                                                                                | MITRE EMB3D Mitigation Level | IEC 62443 Security Level (SL) |
| ----- | ------------ | --------------------------------------------------------------------------------------------------------------------- | ---------------------------- | ----------------------------- |
| 0     | Basic        | Controls are not established, undocumented, or not evaluated.                                                         | N/A                          | SL 0                          |
| 1     | Foundational | Controls address casual, accidental, or low-complexity threats.                                                       | Foundational                 | SL 1                          |
| 2     | Intermediate | Controls address intentional attacks using simple methods and limited resources.                                      | Intermediate                 | SL 2                          |
| 3     | Intermediate | Controls are standardized, consistently implemented, and validated against sophisticated threats.                     | Intermediate                 | SL 3                          |
| 4     | Leading      | Controls continuously adapt to threat intelligence and are engineered for highly capable, well-resourced adversaries. | Leading                      | SL 4                          |

- Cite an MID only when row evidence makes the mitigation applicable and the bounded EMB3D query maps it to at least one `EMB3D TID` recorded in the row.
- Copy the mitigation's exact source name and group it under its exact source level in `Justification`.
- Treat source validation and implementation evidence separately. A valid MID, name, level, and TID association does not prove that a product implements the mitigation.
- Omit MIDs when `EMB3D TID` is `N/A`; describe verified product-specific controls without an EMB3D label instead.
- Treat Basic controls as product-specific physical, procedural, or implementation controls. `Basic` is not an EMB3D mitigation level and must not carry an MID.
- Do not derive, raise, or lower an EMB3D level from implementation maturity, adversary capability, control coverage, or an IEC 62443 Security Level.

> [!NOTE]
> EMB3D levels are source taxonomy values, not a numeric maturity scale. Use the bundled mitigation snapshot as the offline source of record through [`query_emb3d.py`](../scripts/query_emb3d.py) and [`validate_output.py`](../scripts/validate_output.py); do not read or print the raw JSON.

## 7. Impact Mapping

Categorize impact using CVSS v4.0 Base Metrics. Keep CVSS Base scoring intrinsic. Document compensating controls, residual exposure, treatment, and approval outside the Base vector.

- Zero-Impact
  > Use a zero-impact CVSS outcome only when the finalized reviewed scenario leaves no modeled impact because the attack path or weakness is not real in the assessed design.

  - `State = Not Applicable`: the attack path is impossible or structurally eliminated. Pair with `Risk Treatment = Avoidance`.
  - `State = Mitigated`: do not reduce the CVSS Base score to zero solely because controls reduce residual exposure.
  - Zero-impact does not make `Likelihood of Exploit` or `Risk Prioritization` inapplicable. For finalized reviewed rows, populate these columns from the mapping tables.
  - When `State = Not Applicable`, treat vulnerability state as `Theoretical` unless stronger exploit-maturity evidence exists, then derive likelihood from CVSS exploitability metrics and inherent prioritization from the `None` severity row in the risk matrix.

### 7.1. Exploitability Metrics

| Attack Vector   | OT/ICS Scenarios                                                            | Example Interfaces                     |
| --------------- | --------------------------------------------------------------------------- | -------------------------------------- |
| `AV:N` Network  | IP-connected devices, remote SCADA, cloud-connected gateways.               | Modbus/TCP, EtherNet/IP, OPC UA, MQTT. |
| `AV:A` Adjacent | Shared industrial bus, field network segment, same VLAN.                    | Modbus RTU, PROFIBUS, CAN.             |
| `AV:L` Local    | Workstation software, HMI application, locally executed configuration tool. | Engineering software, local database.  |
| `AV:P` Physical | Direct cable connection, removable debug port, hardware tampering.          | RS-232, JTAG, SWD, USB, buttons.       |

### 7.2. Vulnerable System Impact Metrics

Metric abbreviations: `VC` = Vulnerable System Confidentiality Impact, `VI` = Vulnerable System Integrity Impact, `VA` = Vulnerable System Availability Impact.

| STRIDE Category        | Primary Impact Metric | Secondary Impact Metric | Confidence  | Rationale                                                                                                                                                                        |
| ---------------------- | --------------------- | ----------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spoofing               | VI                    | VC                      | Medium      | Identity impersonation primarily corrupts trust and authorization decisions. Confidentiality can follow when impersonation grants access to protected data.                      |
| Tampering              | VI                    | VA, VC                  | High        | Unauthorized modification is directly an integrity impact. Availability and confidentiality may follow when tampering disrupts operation or alters protection controls.          |
| Repudiation            | VI                    | VC                      | Medium-Low  | CVSS has no explicit non-repudiation metric. Represent auditability harm through integrity impact to logs, records, and transaction evidence.                                    |
| Information Disclosure | VC                    | VI                      | High        | Unauthorized exposure is directly a confidentiality impact. Integrity is usually indirect or downstream.                                                                         |
| Denial of Service      | VA                    | VI                      | High        | Degradation or outage is directly an availability impact. Integrity can follow where inconsistent processing results.                                                            |
| Elevation of Privilege | VI                    | VC, VA                  | Medium-High | Privilege gain enables unauthorized modification, access, and potentially shutdown or execution. Read access maps to `VC`, write access to `VI`, admin/execution access to `VA`. |

### 7.3. Subsequent System Impact Metrics

Use `SC`, `SI`, and `SA` to capture cascading effects on the physical process, safety systems, or connected devices. Values: `N` = None, `L` = Low, `H` = High.

| Scenario                                         | SC  | SI  | SA  | Rationale                                                                    |
| ------------------------------------------------ | --- | --- | --- | ---------------------------------------------------------------------------- |
| Compromised PLC affects downstream actuators     | N   | H   | H   | PLC compromise enables unauthorized physical-process control.                |
| Firmware tampering enables lateral movement      | H   | H   | H   | Compromised device can attack other devices on the same segment.             |
| Debug interface exposes firmware secrets         | H   | N   | N   | Extracted credentials or keys may compromise other devices.                  |
| DoS on communication interface                   | N   | N   | H   | Loss of communication can trigger upstream fault handling or fail-safe mode. |
| Configuration change via engineering workstation | N   | H   | N   | Modified setpoints propagate to field devices and affect process integrity.  |

## 8. Probability Mapping

Categorize likelihood of exploit using BSI `Dringlichkeit / Eintrittspotenzial` logic. Combine exploitation method with vulnerability state.

- Exploitation Method
  > The exploitation method describes the degree of attacker interaction and automation required to perform the attack.

  | Method           | Description                                                                                                |
  | ---------------- | ---------------------------------------------------------------------------------------------------------- |
  | Manual           | Requires target-specific, non-automatable steps, specialized knowledge, or direct attacker interaction.    |
  | Automated        | The exploit be executed repeatedly against eligible targets using a script, tool, or repeatable procedure. |
  | Self-Replicating | Propagates autonomously from compromised systems to additional targets without continued attacker action.  |

- Vulnerability State
  > The vulnerability state describes the maturity, availability, and observed use of the exploitation method.

  | Method            | Description                                                                                                    |
  | ----------------- | -------------------------------------------------------------------------------------------------------------- |
  | Theoretical       | The weakness is conceptually exploitable, but no concrete or reproducible exploitation method is known.        |
  | Exploitable       | A proof of concept, reproducible procedure, or otherwise reliable exploitation method exists.                  |
  | Active            | Credible evidence indicates that the vulnerability or equivalent attack method is being exploited in practice. |
  | Exploit Published | Publicly available exploit code or tooling materially reduces the effort required to perform the attack.       |

### 8.1. Exploitation Method

| Method           | CVSS Exploitability Metrics                                      | Description                                                                                                                                      |
| ---------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Manual           | `AV:P`                                                           | Direct physical device access. Any `AV:P` attack qualifies as Manual regardless of other metrics.                                                |
| Automated        | `AV:A` or `AV:L`, `AC:L`, `AT:N`, `UI:N`                         | Adjacent or local exploitation with low complexity and no user interaction. Also use for `AV:N` threats without autonomous propagation behavior. |
| Self-Replicating | `AV:N`, `AC:L`, `AT:N`, `PR:N`, `UI:N` plus propagation behavior | Network-reachable, low-friction, and scenario describes autonomous spread.                                                                       |

> [!NOTE]
> `PR` (Privileges Required) is independent of exploitation method in most cases. Do not change method classification based on `PR` alone.

### 8.2. Vulnerability State

| State             | CVSS Threat Metrics | Description                                                                                                   |
| ----------------- | ------------------- | ------------------------------------------------------------------------------------------------------------- |
| Theoretical       | `E:U`               | No known exploit. Attack is conceptually possible but unverified.                                             |
| Exploitable       | `E:P`               | Proof-of-concept exists or the technique is documented and reproducible.                                      |
| Active            | `E:A`               | Active exploitation observed in the wild or targeted campaigns.                                               |
| Exploit Published | `E:A`               | Public exploit code or tooling is freely available. Prefer over Active when a public tool is directly usable. |

### 8.3. Likelihood Matrix

| State / Method    | Manual | Automated | Self-Replicating |
| ----------------- | ------ | --------- | ---------------- |
| Theoretical       | Info   | Low       | Medium           |
| Exploitable       | Low    | Medium    | High             |
| Active            | Medium | High      | High             |
| Exploit Published | Medium | High      | Critical         |

## 9. Risk Matrix Mapping

Combine `Likelihood of Exploit` and `CVSS v4.0 Severity` to determine `Risk Prioritization`.

> [!NOTE]
> `Risk Prioritization` values are the pre-treatment technical prioritization and must not be lowered by compensating controls, acceptance, transfer, or residual-risk ownership.

| Probability / Impact | None   | Low    | Medium | High     | Critical |
| -------------------- | ------ | ------ | ------ | -------- | -------- |
| Info                 | Info   | Info   | Low    | Low      | Medium   |
| Low                  | Info   | Low    | Low    | Medium   | High     |
| Medium               | Low    | Low    | Medium | High     | High     |
| High                 | Low    | Medium | High   | High     | Critical |
| Critical             | Medium | High   | High   | Critical | Critical |

## 10. Threat Actor Mapping

### 10.1. Capability Boundaries

| Threat Actor       | Typical Capability Boundary                                                                                                       |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| Thrill Seeker      | Opportunistic use of public tooling, default credentials, or exposed services.                                                    |
| Hacktivist         | Public-facing OT access used for symbolic disruption, defacement, or proof-of-access.                                             |
| Cybercriminal      | Financially motivated compromise, ransomware, extortion, credential theft, or scalable supply-chain abuse.                        |
| Insider Threat     | Trusted local, physical, engineering, maintenance, or privileged plant access.                                                    |
| Nation-State Actor | State-sponsored actors with significant resources, custom tooling, and long-duration campaigns targeting critical infrastructure. |

### 10.2. Scenario Mapping

Normalize `Threat Actor` from common OT/ICS threat-path characteristics. Always select the minimum actor that satisfies required access, capability, and process knowledge. Reassess upward only when the modeled path requires capabilities beyond the selected label.

> [!NOTE]
> Actor capability order from lowest to highest: `Thrill Seeker` → `Hacktivist` → `Cybercriminal` → `Insider Threat` → `Nation-State Actor`.

| Minimum Threat Actor | Attack Path / Scenario                                                                                                                                                                                            | Key Indicators                                                                                                                               |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `Thrill Seeker`      | Internet-exposed service with public exploit, default credentials, or unauthenticated interface.                                                                                                                  | `AV:N`, `AC:L`, pre-built tooling, no plant-specific knowledge, opportunistic path.                                                          |
| `Hacktivist`         | Internet-exposed HMI, SCADA web UI, or public-facing OT asset targeted for ideological messaging or symbolic proof-of-access.                                                                                     | Visible high-profile target, protest objective, short-lived campaign, no persistence sought.                                                 |
| `Cybercriminal`      | Internet-exposed service or IT/OT boundary exploited for financial gain.                                                                                                                                          | Ransomware staging, credential theft, extortion, affiliate malware, stolen or phished credentials.                                           |
| `Cybercriminal`      | Compromised vendor tooling, update service, or MSP channel reused for scalable extortion or ransomware.                                                                                                           | Monetized supply-chain reuse, commodity payload, no mission-specific objective.                                                              |
| `Cybercriminal`      | Adjacent OT communication segment or fieldbus reachable outside the trusted environment, including exposed Modbus RTU/RS-485 termination, compromised gateway, engineering workstation, or vendor access channel. | `AV:A` without direct plant-floor or panel access, exposed fieldbus termination, monetized intrusion, stolen credentials, commodity payload. |
| `Insider Threat`     | Trusted maintenance path, local engineering workstation, removable media, direct cable/debug interface, internal fieldbus wiring inside a controlled cabinet or enclosure, or privileged badge access.            | `AV:P`, `AV:L`, or `AV:A` that requires direct plant-floor or panel access, maintenance tooling, process familiarity, insider credentials.   |
| `Nation-State Actor` | Trojanized engineering software, signed firmware package, or tainted vendor update for covert pre-positioning or sabotage.                                                                                        | Custom or signed tooling, covert persistence, strategic or safety-critical target.                                                           |
| `Nation-State Actor` | Bespoke multi-stage intrusion against segmented ICS requiring custom tooling, zero-days, covert lateral movement, or deep process expertise.                                                                      | Long-dwell access, strategic high-value target, disruption, sabotage, or pre-positioning objective.                                          |

> [!NOTE]
> When supply-chain compromise is the modeled vector, choose `Cybercriminal` for commodity ransomware or financial extortion, and `Nation-State Actor` for custom-signed tooling, strategic pre-positioning, or sabotage.

## 11. Risk Treatment Mapping

### 11.1. Treatment Semantics

Risk treatment records the governance disposition for the inherent risk and the resulting residual risk after controls, transfer mechanisms, avoidance decisions, or acceptance decisions are applied.

| Treatment    | Purpose                                                         | Required Evidence or Condition                                                                                 |
| ------------ | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `Avoidance`  | Eliminate the risk source or make the threat inapplicable.      | Document the removed or restructured system element, function, interface, data flow, or attack path.           |
| `Mitigation` | Reduce likelihood or impact through controls or design changes. | Document the applied controls, remaining exposure, residual risk, residual-risk owner, and approval mechanism. |
| `Acceptance` | Intentionally retain the risk without further treatment.        | Document the business rationale, acceptance threshold, responsible stakeholder, and explicit approval.         |
| `Transfer`   | Shift part of the financial, operational, or legal consequence. | Identify the third party and the applicable contract, SLA, warranty, insurance policy, or managed service.     |

> [!NOTE]
> `State` records the technical review result. `Risk Prioritization` records the pre-treatment technical prioritization. `Risk Treatment` records the governance disposition. `Mitigated` may pair with `Acceptance` only when controls are in place and inherent residual risk is intentionally retained with documented approval.

- Defensibility Checks

  | Concern            | Check                                                                                                                                                                           |
  | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | Consistency        | `State`, CVSS severity, likelihood, inherent prioritization, residual risk, treatment, and approval describe a coherent risk posture.                                           |
  | Overprescription   | Example rows are generalized patterns. Replace actor, score, treatment, and approval when product evidence differs.                                                             |
  | Defense Risk       | Do not cite regulation, deployment restrictions, or trusted-environment assumptions as standalone mitigations. Tie each claim to controls, architecture, and approval evidence. |
  | Identifier Hygiene | Do not populate ATT&CK, EMB3D, or CWE identifiers for `Not Applicable` rows unless the row explicitly documents a retained discrepancy.                                         |
  | CVSS Defensibility | Keep CVSS Base scoring intrinsic. Document compensating controls and acceptance decisions outside the Base vector.                                                              |

### 11.2. Treatment Decision Guidance

Select the default treatment for the row's `Risk Prioritization`. Deviate to an acceptable alternative only when documented evidence supports the deviation and the rationale is recorded in `Justification`.

| Risk Prioritization | Default Treatment | Acceptable Alternatives          | Conditions and Constraints                                                                                                                   |
| ------------------- | ----------------- | -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Info                | Avoidance         | Acceptance                       | Attack path is impossible, structurally eliminated, or no longer present. Risk is negligible.                                                |
| Low                 | Acceptance        | Avoidance, Mitigation            | Low-cost controls are encouraged. Transfer is not warranted. Risk may be intentionally retained.                                             |
| Medium              | Mitigation        | Acceptance, Transfer             | Controls must address the root weakness. Transfer requires named SLA, policy, warranty, insurance, or equivalent mechanism.                  |
| High                | Mitigation        | Avoidance, Transfer, Acceptance  | Acceptance is restricted to exceptional cases with CPSO approval and written justification.                                                  |
| Critical            | Avoidance         | Mitigation, Transfer, Acceptance | Acceptance requires explicit executive risk acceptance and written rationale. Do not use acceptance as a substitute for unresolved evidence. |

### 11.3. State and Treatment Compatibility

| TMT State             | Compatible Risk Treatment | Consistency Requirements                                                                                                          |
| --------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `Not Started`         | Blank                     | Row has not yet been reviewed. Leave enrichment and governance fields blank except preserved source values.                       |
| `Needs Investigation` | Blank                     | Evidence gap remains. Do not assign treatment or approval until resolved.                                                         |
| `Not Applicable`      | Avoidance                 | Attack path or risk source is impossible, structurally eliminated, or outside scope. Identifier columns should normally be `N/A`. |
| `Mitigated`           | Mitigation                | Controls reduce risk to an accepted residual level. Identify control, remaining exposure, owner, and approval mechanism.          |
| `Mitigated`           | Acceptance                | Use only when controls reduce exposure but residual risk is intentionally retained with documented approval.                      |
| `Mitigated`           | Transfer                  | Use only when controls and a named third-party mechanism share or delegate residual consequence.                                  |

### 11.4. Treatment Evidence Requirements

| Risk Treatment | Minimum Evidence in `Justification`                                                             |
| -------------- | ----------------------------------------------------------------------------------------------- |
| Avoidance      | Architectural record or design decision confirming the risk source has been eliminated.         |
| Mitigation     | Control(s), residual risk level, residual-risk owner, and approval mechanism.                   |
| Acceptance     | Business rationale for retention, approving stakeholder, and acceptance mechanism.              |
| Transfer       | Named third party, specific contract/SLA/warranty/insurance reference, and explicit risk scope. |

## 12. Risk Approval Mapping

`Risk Approval` records the minimum required approver role label from the intersection of `Risk Prioritization` and `Risk Treatment`.

> [!NOTE]
> Escalate the approver when residual-risk evidence, product safety impact, or stakeholder policy requires stronger governance.

| Prioritization / Treatment | Avoidance    | Mitigation       | Acceptance       | Transfer         |
| -------------------------- | ------------ | ---------------- | ---------------- | ---------------- |
| Info                       | Not Required | Product Security | Product Security | Product Security |
| Low                        | Not Required | Product Security | Product Security | Product Security |
| Medium                     | Not Required | Lead Security    | Lead Security    | Lead Security    |
| High                       | Not Required | CPSO             | CPSO             | CPSO             |
| Critical                   | Not Required | Executive        | Executive        | Executive        |

| Role Label       | Typical Title or Function                                                                        |
| ---------------- | ------------------------------------------------------------------------------------------------ |
| Not Required     | Risk structurally eliminated, no residual risk remains.                                          |
| Product Security | Product security officer, security architect, or equivalent with cross-functional authority.     |
| Lead Security    | Technical lead, security engineer, or equivalent responsible for the design area.                |
| CPSO             | CPSO, or equivalent with organizational risk management authority.                               |
| Executive        | C-level executive, risk committee, or board-level function with final risk acceptance authority. |

## 13. MITRE CWE Mapping Rules

Use the bundled CWE 4.20 projection as the offline source of record through `scripts/query_cwe.py` and `scripts/validate_output.py`; do not read or print the raw JSON. The projection contains all weakness entries from the upstream snapshot, including status, abstraction, mapping notes, relationships, candidate mitigations, and the Software Development, Research Concepts, and Hardware Design discovery views.

- **Active set:** weakness entries whose `status` is not `Deprecated`.
- **Mappable set:** active weakness entries whose `mapping_notes.usage` is not `Prohibited`.
- Map only `CWE-*` weakness IDs. Use views to discover candidates and relationships to refine them; never emit a view or category ID in `CWE ID`.
- Reject deprecated and `Prohibited` entries. Accept `Allowed` entries when architecture evidence supports the root cause.
- Prefer `Base` or `Variant` entries when supported, but do not force a narrower mapping beyond the available evidence.
- Retain an `Allowed-with-Review` or `Discouraged` entry only when no better-supported `Allowed` entry exists.
- Use `N/A` when the row describes adversary behavior, a physical threat path, or an impact without evidence of an underlying product weakness.
- Treat `potential_mitigations` as candidate guidance. A source-listed mitigation does not prove implementation, control effectiveness, or residual-risk reduction.
