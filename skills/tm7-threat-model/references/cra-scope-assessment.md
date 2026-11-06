# Example Device: CRA data-connection scope assessment

Assessed 6 November 2026. Model: [Example_Threat_Model.tm7](Example_Threat_Model.tm7).
Covers every stencil (10) and connection (10); UUIDs are the stable audit references.

## Basis and decision semantics

Article 2(1) concerns products with digital elements supplied on the Union market whose
intended or reasonably foreseeable use includes a direct or indirect logical or physical
data connection. Article 3(8)-(10) defines logical, physical and indirect connections;
Article 3(1), (22)-(24) informs product, market and use boundaries. A component's inclusion
in this threat model does not independently establish its regulatory status.

Apply the supplied `mapping-rules.md`, section 1: distinguish deliberately encoded digital
information from power, analog quantities and trigger-only states. C1/C3 mean direct
logical/physical device paths. Candidate C5/C7 mean device access via an intermediary;
no indirect or network path is established here. Directness is relative to the endpoints
shown. A logical protocol and its physical bearer are different aspects of the same edge,
not extra connectors. This is a documented engineering assessment, conditional on the
model's accuracy, rather than a final product applicability determination.

- **In analysis:** retain digital interfaces for assessment; `Out Of Scope=false`.
- **Unresolved:** evidence missing/conflicting; retain in analysis with the flag false.
- **Out of scope:** exclude only the stated assessed role/path, with conditional or
  provisional assumptions explicit; retain the stencil/edge and rationale. A non-data
  edge does not exempt its endpoint or the whole connected product.
- **Context only:** diagram boundary, not an independently regulated product or data
  connection. The Core boundary block has no scope flag; its classification is in model
  Assumptions and this record. Boundary membership is not a legal conclusion.

## Stencil inventory

| UUID | Stencil / Core family | Classification | Connectivity and rationale |
| --- | --- | --- | --- |
| `eb7fcab6-6c6f-4057-805e-8263102d5a6e` | Debug Probe / `GE.EI` | In analysis | Direct logical device session (C1); physical bearer unverified (candidate C3). JTAG is an explicit digital protocol claim. Probe is an external dependency; its separate market status and service access require confirmation. |
| `1cd50465-88c8-4d5a-9fe8-86ba82b78968` | Trust Boundary Example Device / `GE.TB.B` | Context only | No connection of its own. A diagram boundary is not a product or data channel. Retained to describe the example device context; enclosure does not establish CRA scope. |
| `b12efa5e-d565-4d97-970c-0f16f0efcdbe` | MCU / `GE.P` | In analysis | Direct logical JTAG/QSPI device interactions (C1); QSPI physical attachment (C3). Digital processing and QSPI/JTAG paths are explicitly modeled. External network access through a probe or PLC is unproven; do not infer C6/C8. |
| `68f7ea80-2b40-443c-97d0-8afdb8fb9f5b` | Flash Memory (NVM) with Bootloader / `GE.DS` | In analysis | Direct logical/physical QSPI device path (C1/C3). Flash/bootloader data exchange is modeled. Indirect access through MCU firmware (candidate C5/C7) requires a demonstrated forwarding path; separate marketing is unknown. |
| `cea9ef0a-d9bd-46c5-8c96-6dbce2b58a07` | Magnetoresistive Position Sensor / `GE.P` | Unresolved; retained in analysis | Claimed direct I2C device path (candidate C1/C3); passive-transducer description conflicts. Do not exclude the sensor while an I2C digital path is claimed. Obtain part number, circuit and encoding evidence; a passive-only transducer would instead be contextual. |
| `2c04f557-30f1-4fde-9527-2b190e6b2d7c` | Operator / `GE.EI` | Out of scope; context | Human interaction via buttons and LED; not a device/network data endpoint. The operator is a person, not a product with digital elements. Retained for misuse, local-access and safety scenarios. |
| `5f4312a0-1972-49c0-adf1-b7207b1aee33` | PLC / DCS / `GE.EI` | Unresolved; retained in analysis | Direct physical 4-20 mA interface; digital encoding and indirect network access unproven. The diagram does not establish digital exchange on this loop. The PLC/DCS may have other digital interfaces, but none is evidenced here; its product scope cannot be decided from its name. |
| `6bd55692-9166-48ab-a7ab-45815087d674` | Uninterruptible Power Supply (UPS 12-36 V DC) / `GE.EI` | Out of scope for modeled role; conditional | Direct physical power dependency only; no established data path. Only 12-36 V DC power delivery is modeled. Retain for availability risks. A management interface, telemetry or digital overlay would require reassessment of the UPS product. |
| `fafd48d9-90dd-4e9c-8daf-bf2efb3ac46a` | Control Valve / Actuator / `GE.P` | Out of scope for modeled role; conditional | Direct mechanical linkage only; no established digital symbols. The stated role is passive mechanical actuation. Retain for process/safety effects. A smart actuator or encoded feedback interface would change this assessment. |
| `71c124e0-039b-4be4-8f31-32192932da6b` | Context boundary (scope varies) / `GE.TB.B` | Context only | No connection of its own. Grouping boundary, not an independently assessed CRA product. Membership is contextual and does not exclude the unresolved sensor; geometry remains unchanged. |

## Connection inventory

Each UUID is one unidirectional connector. Reverse flows remain separate.

| UUID | Directional flow | Classification | Connectivity and rationale |
| --- | --- | --- | --- |
| `9d4afcea-3e67-4aa2-abf9-4e4514946c6b` | MCU to Debug Probe via JTAG response (transport unspecified, unencrypted, unauthenticated) | In analysis | Direct logical device response (C1); physical bearer unverified (candidate C3). JTAG response carries digitally encoded information if the declared interface is accurate. Workstation access via a probe (candidate C5/C7) needs evidence, not an invented model edge. |
| `552b907e-0d26-4e70-92c9-e0b4df52e9bf` | Debug Probe to MCU via JTAG request (transport unspecified, unencrypted, unauthenticated) | In analysis | Direct logical device request (C1); physical bearer unverified (candidate C3). JTAG request is an explicit digital exchange claim. Confirm production availability, intended maintenance/debug use and reasonably foreseeable service access. |
| `3ea05cdd-2a10-419e-a3df-a0bc3bf98680` | PLC / DCS to MCU via 4-20 mA power and signal (two-wire loop, analog-only assumed) | Out of scope as data connection; provisional | Direct electrical loop; analog-only assumed, no C1-C8 digital path established. Assume continuous 4-20 mA signaling and power only. No encoded digital overlay is evidenced. Confirm HART/other modulation, diagnostics and foreseeable use before final exclusion. |
| `1dd4151c-3b0f-414b-8d77-e92441b51b47` | Uninterruptible Power Supply (UPS 12-36 V DC) to MCU via 12-36 V DC supply (two-wire power, out of scope) | Out of scope as data connection; conditional | Direct physical power dependency, not demonstrated data communication. 12-36 V DC supply is used solely for power as modeled. No telemetry or power-line data scheme is evidenced; retain power-loss and interference dependencies. |
| `9ac0f863-3849-4fe2-befd-fa32dce6fea1` | Operator to MCU via pushbuttons selector/confirm (physical input, trigger-only assumed) | Out of scope as data connection; provisional | Direct physical user control; trigger-only assumed, encoding unresolved. Assume selector/confirm contacts solely trigger functions. Binary voltage states do not prove communication. Confirm whether firmware reads deliberately encoded states or a defined symbol/command scheme. |
| `fe9683fb-3eaf-4898-b9c6-2fd1aab24dc7` | Magnetoresistive Position Sensor to MCU via I2C measurement (wire, unencrypted, unauthenticated) | Unresolved; retained in analysis | Claimed direct logical/physical I2C device exchange (candidate C1/C3). I2C would carry encoded digital transactions, but the passive/non-electronic sensor description conflicts. Retain for analysis until interface and decoding evidence resolves the contradiction. |
| `3f4ff8e3-29b3-4d50-988f-590b63a01bb3` | MCU to Flash Memory (NVM) with Bootloader via QSPI request (wire, unencrypted, unauthenticated) | In analysis | Direct logical and physical device request (C1/C3). QSPI requests explicitly model command/address/data exchange. No network or intermediary is shown; MCU-mediated external access remains a separate unverified indirect path. |
| `55ff5bd2-fdb9-4e83-b229-0744938845fb` | MCU to Operator via LED status display red/green (physical output, human indication assumed) | Out of scope as data connection; provisional | Direct physical human-visible indication; no demonstrated device/network receiver. Assume red/green human status indication only. Do not infer optical digital communication from LED states. Confirm coded blinking, machine reading or foreseeable automated decoding. |
| `fdfd398d-f6d8-4fb4-a772-d0d15168e4a9` | Flash Memory (NVM) with Bootloader to MCU via QSPI response (wire, unencrypted, unauthenticated) | In analysis | Direct logical and physical device response (C1/C3). QSPI response explicitly models digitally encoded flash data. It is assessed independently from the request; network reachability is not established. |
| `cb59d018-06d7-4803-9217-f168963da421` | Magnetoresistive Position Sensor to Control Valve / Actuator via linear/rotary motion lever/follower (mechanical linkage, protection not modeled) | Out of scope as data connection; conditional | Direct physical mechanical transfer; no demonstrated encoded data scheme. Lever/follower motion is described as passive actuation, not deliberate digital symbols sent to a decoder. Mechanical interfaces can carry data in other designs; reassess if encoded position feedback exists. |

## Evidence still required

1. Define the product supplied on the Union market, components sold separately and any
   applicable exclusion; identify manufacturer instructions and reasonably foreseeable
   technical/service uses. A schematic alone cannot establish these facts.
2. Confirm JTAG access in production, debug-probe bearer and service/workstation topology.
   Presence of a PLC or probe is insufficient evidence of an external network path.
3. Resolve the sensor contradiction with a part number, schematic and transaction trace:
   passive transducer versus I2C peripheral. Until resolved, both sensor and I2C edge are
   retained in analysis despite the legacy context boundary.
4. Confirm whether 4–20 mA is analog-only or has HART/another digital overlay. Do not
   infer an overlay, a PLC network, or its absence as a product-wide fact.
5. Document what selector/confirm states mean and how they are read; establish whether
   they solely trigger a function or encode information deliberately interpreted as data.
   Confirm the LED's recipient and any coded blinking or machine-readable use.
6. Confirm UPS monitoring/management capabilities and actuator feedback. Power-only and
   passive-mechanical assumptions apply solely to the depicted roles.

## Preservation and consequences

All 10 stencils, 10 connections, 50 threat records, original exported geometry, UUIDs,
serializer identities, endpoint directions and the embedded catalog are retained. Scope
flags and reason properties use existing Core fields. The ambiguous sensor/I2C exclusion
is cleared pending evidence. Operator, UPS and passive actuator are contextual; the analog,
trigger, human-indication, power and mechanical edges carry explicit exclusion assumptions.
The legacy `Out of Scope` boundary is renamed `Context boundary (scope varies)` without
moving it. No new XML properties, network edges or response flows are introduced.

Existing findings remain available for contextual attack, misuse, availability and safety
analysis. Scope flags may affect TMT filtering or future generation; they do not mean a
finding is mitigated or that a contextual interface cannot affect an in-scope component.
Threat states and descriptions have not been rewritten as compliance conclusions.

## Sources

- [Regulation (EU) 2024/2847, Article 2(1) and Article 3](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R2847).
- Supplied `mapping-rules.md`, section 1 (Data Connection), including C1-C8 taxonomy.
- [Commission publication of guidance C(2026) 5252](https://digital-strategy.ec.europa.eu/en/library/commission-publishes-new-guidance-support-timely-cyber-resilience-act-implementation).
  The supplied mapping attributes its encoding test to section 2.5, paragraphs 26-28.
  The official annex download could not be retrieved during this assessment; that wording
  is applied from the supplied rules, not represented as independently verified annex text.
- Model evidence: stencil descriptions, endpoint GUIDs, interface labels and existing
  configurable properties. No datasheets, firmware traces or manufacturer use statements
  were supplied.
