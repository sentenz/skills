# Microsoft Threat Modeling Tool (TMT) Style Guide

Guide for pattern, format, and style conventions in Microsoft Threat Modeling Tool diagrams.

- [1. Scope and application](#1-scope-and-application)
- [2. Diagram patterns](#2-diagram-patterns)
  - [Flow directionality](#flow-directionality)
- [3. Stencil size and layout](#3-stencil-size-and-layout)
  - [Default sizes](#default-sizes)
  - [Layout defaults](#layout-defaults)
- [4. Straight data flows](#4-straight-data-flows)
  - [Connector geometry](#connector-geometry)
- [5. Naming and text format](#5-naming-and-text-format)
  - [Components and boundaries](#components-and-boundaries)
  - [Data flow naming convention](#data-flow-naming-convention)
  - [Text and XML format](#text-and-xml-format)
- [6. Properties and threat presentation](#6-properties-and-threat-presentation)
- [7. Review checklist](#7-review-checklist)
- [8. References](#8-references)

## 1. Scope and application

Apply these conventions when generating or extending TMT diagrams with SDL TM Knowledge
Base (Core) `4.1.0.11`. They define this skill's diagram style. The serialization contract,
namespace rules, identifiers, and property metadata remain defined by [SKILL.md](../SKILL.md)
and the Core exports.

Use the user's architecture, terminology, and explicit presentation requirements. When editing
an existing model, apply the guide to the requested additions; preserve object identities,
catalog content, reviewed findings, and unrelated diagram content. Record uncertain protocol
or protection details as unknown rather than inventing them to complete a label.

## 2. Diagram patterns

Model the system as directed interactions among processes, data stores, and external
interactors. Use a Core type that represents the component's role in the modeled scope.

| Pattern                                    | Representation                                   | Example                                                  |
| ------------------------------------------ | ------------------------------------------------ | -------------------------------------------------------- |
| External actor interacts with a service    | External interactor -> process                   | Operator -> MCU control service                          |
| One component sends data to another        | Process -> process                               | PLC -> MCU                                               |
| A process persists or retrieves data       | Process -> data store, or data store -> process  | MCU -> configuration store; configuration store -> MCU   |
| Bidirectional connection (Request and Response)  | Two opposite unidirectional flows                | PLC -> MCU request; MCU -> PLC response                  |
| Components share a security context        | Enclosing trust boundary around those components | Device boundary around MCU and local configuration store |

The examples describe modeling roles; choose them from the actual scope. A PLC may be an
external interactor when its internals are outside scope, or a process when they are modeled.
Use separate drawing surfaces for overview and detail when a single diagram becomes hard
to read. Give each surface a distinct name, such as `Device overview` or `Firmware update`.
Keep each connector's endpoints on its owning surface.

Place a trust boundary where identity, privilege, administration, or another security context
changes. Name the boundary for that context. Boundary geometry must reflect the intended
membership and crossing relationships because Core threat-generation filters can use them.

### Flow directionality

Distinguish the transfer from the connection between components:

| Concept | Meaning | Core representation |
| ------- | ------- | ------------------- |
| Unidirectional data flow | One transfer from a source to a target | One `Connector` with its own UUID and ordered endpoints |
| Bidirectional connection | Data travels in both directions between two components | Two `Connector` objects with opposite endpoints and distinct UUIDs |

Model a request from A to B and its response from B to A separately whenever both directions
are in scope, even if they share a protocol, session, transport, or protection mechanism.
Name each direction for the data it carries: Request from A to B and Response from B to A.
Describe the pair as a bidirectional connection in model metadata; do not label a single
connector `Request/Response` as though it carries both directions.
Do not invent a bidirectional XML flag, connection object, or second arrowhead property.

Keep genuinely one-way transfers, such as an event sent without a modeled reply, as one
flow. Do not infer a response merely from the transport's ability to send data both ways.
Record an intentionally omitted return path in the model's scope or assumptions. For an
existing connection, preserve existing flow UUIDs and add only the missing modeled direction.

## 3. Stencil size and layout

### Default sizes

Keep the exported default dimensions for ordinary stencils:

| Stencil                  | Core generic type | Width           | Height          |
| ------------------------ | ----------------- | --------------- | --------------- |
| Process                  | `GE.P`            | 100             | 100             |
| Data store               | `GE.DS`           | 100             | 100             |
| External interactor      | `GE.EI`           | 100             | 100             |
| Enclosing trust boundary | `GE.TB.B`         | Fit its members | Fit its members |

The 100 × 100 dimensions are observed in the bundled populated Core export and used by
the worked example. Treat them as model-coordinate units. Preserve the native shape and
aspect ratio when selecting a specialized Core type. If a matching exported specialized
stencil has different defaults, retain those exported dimensions.

Use concise component names so labels fit. Move explanatory detail into properties or model
metadata. Do not stretch a process into an ellipse or enlarge one component merely to give
it visual emphasis. Enlarge trust boundaries to fit their contents and labels.

### Layout defaults

- Arrange the primary interaction from left to right. Use additional rows for independent
  interactions or storage access when this reduces crossings.
- Align related 100 × 100 stencils by their centerlines. A 25-unit placement grid is a useful
  starting convention; adjust positions to keep labels readable and connectors straight.
- Start with a 200-unit clear gap between ordinary stencil edges. Increase the gap for long
  flow labels. This is a spacing default, not a serialized schema constraint.
- Leave at least 50 units between a boundary and its enclosed ordinary stencils, plus room
  for the boundary title and flow labels. Maintain the intended boundary crossings.
- Keep component shapes, connector labels, and boundary titles from overlapping. Avoid
  routing a connector through an unrelated stencil or along a boundary edge.

The worked example places Client at `Left=100`, `Top=100`, and Service at `Left=900`,
`Top=100`, both sized 100 × 100. Its 700-unit clear gap accommodates the directional flow labels.

## 4. Straight data flows

Use a single straight segment for each directional data flow. Horizontal or vertical
segments are preferred; a straight diagonal is acceptable when it makes the diagram clearer.
Keep the arrow direction consistent with `SourceGuid` and `TargetGuid`.

When a line would collide with a component, label, or another flow, move the components or
use another lane or drawing surface. Keep flows straight rather than introducing curvature
or decorative bends. Do not add fictitious processes or split one interaction into extra
connectors solely to route a line.

For bidirectional connections (Request and Response), choose distinct attachment ports and
lanes so both arrows and labels remain distinguishable. Do not draw both directions on the
same segment, where one arrow or label can hide the other. Reposition the stencils if necessary. Each direction retains
its own connector, UUID, name, properties, and applicable threat interactions.

### Connector geometry

Preserve the exported connector members and accepted port values. Match `SourceX`/`SourceY`
and `TargetX`/`TargetY` to the actual attachment points on their stencils. The endpoint
coordinates must agree with `PortSource` and `PortTarget`; do not leave stale coordinates
after moving or resizing a stencil.

For this skill's straight-connector convention, place the handle at the endpoint midpoint:

```text
HandleX = (SourceX + TargetX) / 2
HandleY = (SourceY + TargetY) / 2
```

Serialize connector coordinates as integers, following the supplied Core export. Do not
write fractional values or exponent notation. Choose endpoint positions whose midpoint is
also integral, so the straight-line convention does not require fractional handles.

The worked example uses two separated horizontal lanes. Client is a rectangle and Service
is a circular process; both have center X coordinates of 150 and 950 respectively. The
request connects their North ports and the response connects their South ports.

| Member | Request: Client to Service | Response: Service to Client |
| ------ | -------------------------- | --------------------------- |
| `PortSource` | `North` | `South` |
| `PortTarget` | `North` | `South` |
| `SourceX`, `SourceY` | `150`, `100` | `950`, `200` |
| `TargetX`, `TargetY` | `950`, `100` | `150`, `200` |
| `HandleX`, `HandleY` | `550`, `100` | `550`, `200` |

Copy the supported representation from a Core export; keep geometry members in the Abstracts
namespace and in their original order. Do not invent a `Curved`, `Straight`, or `Routing`
XML property. Inspect the rendered connector in TMT when available, including after a save
and reopen. The static validator currently checks connector structure and references; it
does not verify line rendering or enforce these geometric style conventions.

## 5. Naming and text format

### Components and boundaries

Use short, stable names from the architecture: `PLC`, `MCU`, `Operator`, `Firmware service`,
or `Configuration store`. Keep acronyms consistently capitalized. Introduce an unfamiliar
acronym in model metadata rather than repeating its expansion on every stencil.

Use descriptive boundary names such as `Device trust boundary` or `Maintenance network
trust boundary`. A name must not imply a protection or trust relationship that has not been
established. Use the same component names in flow labels and threat descriptions.

### Data flow naming convention

Use this base pattern:

```text
<Source name> to <Target name> via <Protocol or interface> (<Transport>, <Protection>)
```

Use the exact source and target display names, the words `to` and `via` in lowercase,
standard protocol spelling, a comma and space between qualifiers, and no final period.
Start qualifiers with the physical or logical transport, followed by the protection detail.
If the interface already identifies the transport, do not repeat it unnecessarily.

The requested example follows the convention:

```text
PLC to MCU via Modbus RTU (RS-485, unencrypted)
```

The following are conditional examples: use their protection claims only when supported by
the modeled architecture.

| Interaction                                                      | Flow name                                                                            |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| PLC sends a Modbus request                                       | `PLC to MCU via Modbus RTU request (RS-485, unencrypted)`                            |
| MCU returns a Modbus response                                    | `MCU to PLC via Modbus RTU response (RS-485, unencrypted)`                           |
| Operator sends input through a physical interface                | `Operator to MCU via pushbuttons (physical input, unauthenticated)`                  |
| Service transfers a firmware image over a documented TLS channel | `Firmware service to MCU via HTTPS firmware download (TCP/IP, TLS encrypted)`        |
| Client protocol and controls have not been established           | `Client to Service via generic data flow (protocol unspecified, protection unknown)` |

When multiple flows use the same endpoints and protocol, add the payload or operation after
the protocol, as in `Modbus RTU request`, `Modbus RTU response`, or `HTTPS firmware download`.
Use distinct names for interactions that have different payloads, directions, privileges, or
protection assumptions. A bidirectional connection (Request and Response) always has two
directional labels with source and target reversed. Split additional flows within one direction
only when their differences matter to the threat model; do not use this grouping rule to
merge opposite directions.

Use `unencrypted`, `unauthenticated`, `TLS encrypted`, or `mutually authenticated` only for
documented properties. Encryption and authentication are separate claims. If both matter,
state both, for example `(TCP/IP, TLS encrypted, client authentication unknown)`. Keep the
label's claims consistent with the chosen Core type and configurable property selections.

Set the connector's exported **Name** display property to the full label. For new threats
on that flow, use the same label in the `InteractionString` property dictionary entry.
When renaming an existing flow, update corresponding interaction labels without changing
its UUID, threat dictionary keys, or colon-delimited `InteractionKey`.

### Text and XML format

Use sentence case for explanatory prose, preserve established acronym spelling, and keep
visible labels on one logical line. Put detailed assumptions in `MetaInformation/Assumptions`
and architectural explanation in `HighLevelSystemDescription`.

Escape XML text through a serializer or an XML escaping function. A display name containing
`&` must be serialized as `&amp;`; keep the human-readable name consistent in the tool.
Format documentation snippets for reading, and serialize the final `.tm7` using the Core
contract described in the skill: no XML declaration or added pretty-print indentation.

## 6. Properties and threat presentation

Choose catalog types and property values from the embedded Core knowledge base. A descriptive
flow label does not configure a control. For example, a label saying `unencrypted` must
agree with the model's confidentiality assumptions; do not change a list selection by copying
an index from another type's value list.

Give each threat a concrete title describing the actor, affected component or interaction,
and adverse action. For example: `Spoofed PLC sends unauthorized commands to MCU`.
Use the catalog's exact category name and short description, then adapt
`UserThreatDescription` to the interaction. Describe proposed mitigations there and keep
the threat's state tied to the evidence for those controls. Follow the Core property rules
in the skill rather than adding new XML fields for presentation.

Evaluate each direction against the Core filters independently. A response does not inherit
request findings: its source and target roles, authentication claims, payload, and applicable
threat types can differ. Keep `FlowGuid`, `SourceGuid`, `TargetGuid`, `InteractionKey`, and
the threat dictionary key consistent with the referenced connector's UUID and ordered
endpoints. Use its directional Name in the `InteractionString` property.

## 7. Review checklist

Before delivering a new or updated model:

1. Ordinary stencils retain 100 × 100 dimensions or their matching exported specialized
   defaults; enclosing boundaries fit the intended members.
2. Stencils align cleanly, labels remain readable, and boundary membership reflects the
   security contexts in the architecture.
3. Every data flow is straight, points in the correct direction, and meets its intended
   source and target. Handle coordinates follow the midpoint convention.
   Bidirectional connections contain two opposite connectors with distinct UUIDs, names,
   attachment ports, and visible lanes. One-way transfers have no invented return flow.
4. Flow names follow `Source to Target via Protocol (Transport, Protection)`, with a useful
   payload/operation qualifier when needed. Unknown details are explicit.
5. Display names, flow labels, threat interaction labels, and Core property selections agree.
   Renaming or moving objects has preserved their identities and references.
6. Run the [Core consistency checker](../scripts/README.md). Review size, geometry, naming,
   and readability separately because those style checks are currently manual.
7. Inspect the diagram in TMT when available. Report the checks actually performed.

## 8. References

- [Skill workflow and serialization contract](../SKILL.md).
- [Blank Core 4.1.0.11 export](../assets/example-minimal.tm7).
- [Populated Core reference](../references/Example_Threat_Model.tm7), which demonstrates
  ordinary stencil dimensions, integer connector coordinates, and directional flow labels.
  Its JTAG and QSPI bidirectional connections use separate Request and Response lanes;
  existing threat interaction labels match their connectors.
- [Connected worked example](../references/core-worked-example.tm7).
- [Core XML examples](../references/core-xml-examples.md).
- [Script usage and validation limits](../scripts/README.md).
