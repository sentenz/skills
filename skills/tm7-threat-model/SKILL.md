---
name: tm7-threat-model
description: 'Creates and modifies Microsoft Threat Modeling Tool (.tm7) files using SDL TM Knowledge Base (Core). Use when asked to generate or edit a .tm7 threat model, or perform STRIDE threat modeling with a .tm7 deliverable.'
---

# Microsoft Threat Modeling Tool (.tm7) Generator

Translate a system description into a diagram and STRIDE threats in Microsoft Threat
Modeling Tool's WCF `DataContractSerializer` XML format. Preserve the serialization
structure, member order, namespaces, and embedded knowledge base from the Core assets.

> [!NOTE]
> Generates and modifies Microsoft Threat Modeling Tool (.tm7) files using the **SDL TM Knowledge Base (Core)**.

- [1. Workflow](#1-workflow)
- [2. Core reference assets](#2-core-reference-assets)
- [3. Serialization format](#3-serialization-format)
  - [3.1. Namespaces and qualified types](#31-namespaces-and-qualified-types)
  - [3.2. Object identity](#32-object-identity)
- [4. Stencils and boundaries](#4-stencils-and-boundaries)
  - [4.1. Common Core `TypeId` values](#41-common-core-typeid-values)
- [5. Data flow lines](#5-data-flow-lines)
- [6. Property attribute types](#6-property-attribute-types)
- [7. Threat instances](#7-threat-instances)
- [8. Validation checklist](#8-validation-checklist)

## 1. Workflow

When asked to produce a `.tm7` file:

1. **Model the system.** Identify processes, data stores, external interactors, trust
   boundaries, and unidirectional data flows. Represent a bidirectional connection, such as
   Request and Response, with two opposite unidirectional flows. Select their types from the
   embedded Core catalog.
2. **Assign unique lowercase UUIDs** to every new drawing surface, stencil, and flow.
   Preserve existing UUIDs when editing a model. Use real UUIDs such as
   `148ade68-5c80-40f3-8e1f-4e2cabdb5991`, rather than component names.
3. **Lay out coordinates** using the [TMT Style Guide](./references/tmt-style-guide.md):
   retain default stencil sizes, use facing connection points, and apply its flow naming convention.
   Keep stencils readable, boundary membership correct, and connector endpoints on their shapes.
   Preserve supplied export geometry and keep bundled examples within the style guide's
   conservative coordinate envelope; verify larger layouts in TMT before delivery.
4. **Generate STRIDE threats** for applicable interactions, using Core threat types and
   their generation filters. Place them in `ThreatInstances`; include architecture-specific
   descriptions and proposed mitigations without claiming that proposed controls are implemented.
5. **Serialize** by adapting [assets/example-minimal.tm7](./assets/example-minimal.tm7).
   Read it first. Use [references/Example_Threat_Model.tm7](./references/Example_Threat_Model.tm7)
   for populated stencil, connector, property, and threat blocks.
6. **Validate** references, catalog identifiers, properties, and serialization with the
   checklist below and `python scripts/validate_tm7.py path/to/model.tm7` (resolve the script
   relative to this skill). Correct failures before delivery.
7. **Write without an XML declaration or added pretty-print indentation.** Preserve existing
   whitespace inside catalog descriptions and user text; the supplied asset contains such text.

## 2. Core reference assets

| Asset                                 | Role                                                                                                                    | Core manifest version             |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| `assets/example-minimal.tm7`          | Authoritative blank generation skeleton supplied by the user: one empty drawing surface, no stencils, flows, or threats | `4.1.0.11`                        |
| `references/Example_Threat_Model.tm7` | Labeled populated Core example: 10 border entries, 10 labeled connectors, 50 threats                                    | `4.1.0.11`                        |
| `references/core-xml-examples.md`     | Complete, namespace-qualified example blocks and a connected worked model                                               | Uses the blank skeleton's catalog |
| `references/core-worked-example.tm7`  | Bidirectional connection (Request and Response): two stencils, two connectors, one illustrative request-side threat     | `4.1.0.11`                        |
| `references/tmt-style-guide.md`       | Diagram patterns, stencil sizes, connector attachment geometry, and naming conventions                                  | Applies to Core `4.1.0.11`        |

Both exports use model `Version` **`4.3`**, distinct from the knowledge-base version and
the application's version. Their manifest name is **`SDL TM Knowledge Base (Core)`** and
manifest ID is **`cc62ebae-3748-431e-b1df-f4220dc9003f`**. Both use Core **`4.1.0.11`**.
Their generic/standard element IDs, threat type IDs, and configurable attribute lists agree.
Their catalogs match apart from the `KnowledgeBase` object's `z:Id` (`i2` in the blank
asset, `i22` in the populated reference). That ID is serializer identity, not catalog content.
Keep the chosen export's entire `KnowledgeBase` intact when copying populated blocks.

The blank asset has no populated blocks to duplicate. Read the populated reference when
adding diagram elements or threats. For changes to an existing Core model, preserve its
catalog and existing serialization unless a catalog change is explicitly requested. Validate
against that model's original export with `--template original.tm7`.

## 3. Serialization format

Start with this root, with no XML declaration:

```xml
<ThreatModel xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
```

The root's children appear in this exact order in both Core assets:

1. `DrawingSurfaceList`
2. `MetaInformation`
3. `Notes`
4. `ThreatInstances`
5. `ThreatGenerationEnabled` (`true` in the assets)
6. `Validations` (empty, with the KnowledgeBase namespace binding in the assets)
7. `Version` (`4.3`)
8. `KnowledgeBase`
9. `Profile`

`ThreatMetaData` belongs **inside `KnowledgeBase`**, after `ThreatCategories` and before
`ThreatTypes`. There is no root-level `ThreatMetaData` in these exports. Keep `KnowledgeBase`
as a root-level sibling after `Version` and before `Profile`.

`MetaInformation` children are `Assumptions`, `Contributors`, `ExternalDependencies`,
`HighLevelSystemDescription`, `Owner`, `Reviewer`, `ThreatModelName`, in that order.
The drawing surface's members are `GenericTypeId`, `Guid`, `Properties`, `TypeId`,
`Borders`, `Header`, `Lines`, `Zoom`, in that order. Its generic and concrete type IDs
are both `DRAWINGSURFACE`. Preserve the profile's `<PromptedKb xmlns=""/>` child.

Do not invent XML elements such as `SecurityGaps` or `Mitigations`. Store threat details
in the Core properties described below.

### 3.1. Namespaces and qualified types

| Conventional prefix | URI                                                                      | Role                                                      |
| ------------------- | ------------------------------------------------------------------------ | --------------------------------------------------------- |
| default             | `http://schemas.datacontract.org/2004/07/ThreatModeling.Model`           | Root, drawing surface, concrete shape type names          |
| `i`                 | `http://www.w3.org/2001/XMLSchema-instance`                              | `type`, `nil`                                             |
| `z`                 | `http://schemas.microsoft.com/2003/10/Serialization/`                    | Object `Id`, `Ref`                                        |
| `a`                 | `http://schemas.microsoft.com/2003/10/Serialization/Arrays`              | Dictionary wrappers, keys, values, collections            |
| `b`                 | `http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase`   | Display attributes and threat members                     |
| `c`                 | `http://www.w3.org/2001/XMLSchema`                                       | Primitive value types                                     |
| local default       | `http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts` | Inherited stencil, connector, and drawing-surface members |

Prefix names are local aliases: the same prefix can bind a different URI in another scope.
For example, `a` binds the KnowledgeBase URI on the catalog but the Arrays URI on dictionaries.
Preserve bindings where `i:type` values use them. `i:type="b:ListDisplayAttribute"` must
resolve to the KnowledgeBase URI; `i:type="a:ArrayOfstring"` must resolve to Arrays.
An XML serializer that rewrites element prefixes may leave QName-valued `i:type` strings
unbound; verify them explicitly. Namespace URIs, rather than the spellings `i` or `xsi`,
determine XML meaning. Retain the asset's aliases for predictable output.

### 3.2. Object identity

Dictionary `<a:Key>` and inherited `<Guid>` must match for each stencil and connector.
UUIDs identify model objects. `z:Id` strings identify serializer objects; these are separate
identities. Preserve the template's existing `z:Id` values and assign unused ones to cloned
reference-tracked objects, including nested objects when present. In the blank skeleton,
`i1` is the drawing surface and `i2` is the knowledge base, so start new objects at `i3`.
Every present `z:Id` must be unique and every `z:Ref` must resolve; ordinary untracked
objects, including the exported threat values, do not require invented `z:Id` attributes.

## 4. Stencils and boundaries

Each entry in a drawing surface's `Borders` is an Arrays
`KeyValueOfguidanyType` containing an Arrays `Key` and `Value`. The value has an
`i:type` in the Model namespace and these inherited members in the Abstracts namespace:

`GenericTypeId`, `Guid`, `Properties`, `TypeId`, `Height`, `Left`, `StrokeDashArray`,
`StrokeThickness`, `Top`, `Width`, in that order for the exported border shapes.

| Component                | `i:type`                           | `GenericTypeId` |
| ------------------------ | ---------------------------------- | --------------- |
| Process                  | `StencilEllipse`                   | `GE.P`          |
| Data store               | `StencilParallelLines`             | `GE.DS`         |
| External interactor      | `StencilRectangle`                 | `GE.EI`         |
| Enclosing trust boundary | `BorderBoundary`                   | `GE.TB.B`       |
| Trust line boundary      | Obtain from a matching Core export | `GE.TB.L`       |

`GE.TB.B` and `GE.TB.L` are separate Core generic types. The populated reference demonstrates
enclosing boundaries in `Borders`. The catalog calls the line representation `LineBoundary`,
but neither bundled export contains a serialized instance proving its concrete `i:type` or
members. Obtain its block from a matching Core export before adding one; do not infer a
serializer type from the catalog representation. The bundled checker supports the demonstrated
enclosing boundary format and reports line boundaries as unsupported pending such an export.

### 4.1. Common Core `TypeId` values

Generic stencils may use their `GenericTypeId` as `TypeId`. Specialized stencils inherit
their generic family through the catalog's `ParentId` chain.

| `TypeId`                    | Component                     |
| --------------------------- | ----------------------------- |
| `SE.P.TMCore.OSProcess`     | OS Process                    |
| `SE.P.TMCore.WebApp`        | Web Application               |
| `SE.P.TMCore.WebSvc`        | Web Service                   |
| `SE.P.TMCore.Win32Service`  | Win32 Service                 |
| `SE.DS.TMCore.SQL`          | SQL Database                  |
| `SE.DS.TMCore.NoSQL`        | Non Relational Database       |
| `SE.DS.TMCore.CloudStorage` | Cloud Storage                 |
| `SE.DS.TMCore.Cache`        | Cache                         |
| `SE.EI.TMCore.Browser`      | Browser                       |
| `SE.EI.TMCore.User`         | Human User                    |
| `SE.EI.TMCore.WebSvc`       | External Web Service          |
| `SE.TB.B.TMCore.CorpNet`    | CorpNet Trust Boundary        |
| `SE.TB.B.TMCore.Sandbox`    | Sandbox Trust Boundary Border |
| `SE.TB.L.TMCore.Internet`   | Internet Boundary             |

Only use identifiers actually present in the chosen catalog. For architecture components
without a specialized Core type, choose the appropriate generic type and give it a specific
display name. Rebuild configurable properties when changing types; changing only `TypeId`
can retain incompatible inherited attributes.

## 5. Data flow lines

`Lines` uses the same Arrays `KeyValueOfguidanyType` wrapper, with `i:type="Connector"`,
`GenericTypeId` `GE.DF`, and a catalog-backed `TypeId`. Use `GE.DF` for a generic flow or
Core protocol types such as `SE.DF.TMCore.HTTP`, `SE.DF.TMCore.HTTPS`,
`SE.DF.TMCore.Binary`, or `SE.DF.TMCore.NamedPipe`.

Connector members, all in Abstracts, occur in this order:

`GenericTypeId`, `Guid`, `Properties`, `TypeId`, `HandleX`, `HandleY`, `PortSource`,
`PortTarget`, `SourceGuid`, `SourceX`, `SourceY`, `TargetGuid`, `TargetX`, `TargetY`.

Treat an **individual data flow** as one unidirectional transfer from `SourceGuid` to
`TargetGuid`, represented by one `Connector`. Treat a **bidirectional connection**
as two opposite unidirectional flows between the same stencils: for example, Request from
Client to Service and Response from Service to Client.
The connection is a conceptual grouping, not an additional Core object or a single connector
with two arrowheads. A protocol name or a combined `Request/Response` label does not create
the reverse flow.

For each new direction, assign a distinct UUID and unused serializer ID. Preserve the UUID
and serializer ID of an existing connector. Give each direction its own name and applicable
properties. Reverse the source and target for the response. Use supported ports from the
populated reference and the attachment and handle conventions from the
[TMT Style Guide](./references/tmt-style-guide.md#4-data-flow-connections); endpoints must
resolve on the same drawing surface and coordinates must match their attachment ports.
Use the exported five-unit inset for the bundled 100 × 100 cardinal attachment points.
Serialize connector coordinates as integers. Use midpoint handles for straight one-way
flows and opposing handle offsets for bidirectional connections, as in the worked example.
Do not add a response to a genuinely one-way transfer. If a return path is omitted from
scope, record that limitation explicitly instead of implying that one connector models both.

Evaluate threats independently for each direction using the Core generation filters.
Keep each finding's `FlowGuid`, `SourceGuid`, `TargetGuid`, `InteractionKey`, and threat
dictionary key consistent with its connector. Use that connector's directional Name in the
`InteractionString` property. Do not clone request threats onto a response without checking
applicability. Authentication properties are relative to each connector's source and
destination, so reassess them when reversing endpoints.

## 6. Property attribute types

Inherited `Properties` contains Arrays `anyType` items. Each item's `DisplayName`, `Name`,
`Value`, and optional `SelectedIndex` are in the KnowledgeBase namespace.

| `i:type`                       | Value representation                                                                                       |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| `b:HeaderDisplayAttribute`     | `Value i:nil="true"`                                                                                       |
| `b:StringDisplayAttribute`     | `Value i:type="c:string"`                                                                                  |
| `b:BooleanDisplayAttribute`    | `Value i:type="c:boolean"`                                                                                 |
| `b:ListDisplayAttribute`       | `Value i:type="a:ArrayOfstring"` containing Arrays `string` values, followed by zero-based `SelectedIndex` |
| `b:StaticListDisplayAttribute` | Same list representation for a specialized static attribute, as in Human User's `type` property            |

Copy the exported common properties (Name, Out Of Scope, Reason For Out Of Scope, and
Dataflow Order where present, including the reference's border boundaries) and their internal names/IDs. For configurable attributes,
use the chosen element's `Attributes` plus inherited parent attributes, respecting specialized
overrides. Preserve each `Name` and ordered `AttributeValues`. An index is meaningful only
with its exact value list. Do not infer a universal index for Yes, No, or Not Selected.

Examples include `authenticatesItself` for external interactors and `authenticatesSource`,
`authenticatesDestination`, `providesConfidentiality`, and `providesIntegrity` for flows.
Selected values affect Core threat-generation filters, so record only supported assumptions.

## 7. Threat instances

Use the Arrays dictionary wrapper **`KeyValueOfstringThreatpc_P0_PhOB`**. Its `Value`
contains KnowledgeBase members, in the order demonstrated by the populated Core export:

`ChangedBy`, `DrawingSurfaceGuid`, `FlowGuid`, `Id`, `InteractionKey`, `InteractionString`,
`ModifiedAt`, `Priority`, `Properties`, `SourceGuid`, `State`, `StateInformation`,
`TargetGuid`, `Title`, `TypeId`, `Upgraded`, `UserThreatCategory`, `UserThreatDescription`,
`UserThreatShortDescription`, `Wide`.

- `TypeId` resolves to an exact ID in `KnowledgeBase/ThreatTypes`: for example `S3`, `T3`,
  `R1`, `I2`, `D2`, or `E7`. Select by meaning, `Category`, and `GenerationFilters`;
  the category letter alone is not a threat type. The catalog also contains dotted IDs
  such as `S7.1` and a UUID ID; do not assume every ID has one letter and one digit.
- The dictionary key is `TypeId + SourceGuid + FlowGuid + TargetGuid`, with no separators.
  For `S3` it begins with `S3`; there is no added `TH` prefix.
- `Id` is a unique numeric instance ID, separate from the catalog `TypeId` and dictionary key.
- `InteractionKey` is `SourceGuid:FlowGuid:TargetGuid`. These three GUIDs must agree with
  the referenced connector's direction; `DrawingSurfaceGuid` must identify its owning surface.
- `Properties` is an Arrays `KeyValueOfstringstring` dictionary. Use the Core keys below.
  The populated reference keeps the top-level `Title`, `InteractionString`, and three
  `UserThreat*` members nil while storing their displayed values in this dictionary.
- Preserve the exported state when editing existing threats. New catalog-derived findings
  can use the reference's `AutoGenerated` state; do not set `Mitigated` merely because a
  proposed mitigation has been written. Use `StateInformation` for a supported justification.

| Core property key            | Content                                                                                     |
| ---------------------------- | ------------------------------------------------------------------------------------------- |
| `Title`                      | Concrete threat title, adapting the catalog `ShortTitle`                                    |
| `UserThreatCategory`         | Exact category name resolved from the threat type's `Category` ID                           |
| `UserThreatShortDescription` | Category short description from the catalog                                                 |
| `UserThreatDescription`      | Context-specific threat description and proposed controls, adapting the catalog description |
| `InteractionString`          | Human-readable interaction or flow label                                                    |
| `Priority`                   | `High`, `Medium`, or `Low`; agree with the threat's top-level `Priority`                    |
| `StateInformation`           | Optional justification when applicable; keep consistent with the corresponding member       |

Core's global property metadata is at `KnowledgeBase/ThreatMetaData/PropertiesMetaData`;
per-type metadata is under each `ThreatType/PropertiesMetaData`. Use those definitions
rather than introducing properties absent from Core, such as `PossibleMitigations` or
`SDLPhase`. Keep proposed mitigation text in `UserThreatDescription`.

Core's STRIDE category names are **Spoofing**, **Tampering**, **Repudiation**,
**Information Disclosure**, **Denial Of Service**, and **Elevation Of Privilege**.
The catalog additionally defines Abuse; its presence does not change the STRIDE workflow.

Read [references/core-xml-examples.md](./references/core-xml-examples.md) for complete
stencil, connector, list-property, and threat XML blocks with resolving identifiers.

## 8. Validation checklist

1. Root and member order match the chosen Core skeleton, including `Header`, `Zoom`,
   `ThreatGenerationEnabled`, `Validations`, `Version`, and `Profile`.
2. The complete embedded knowledge base and manifest are preserved. `ThreatMetaData`
   remains inside it. Stencil and threat types resolve to that catalog.
3. Dictionary wrappers and namespace URIs match the assets; every QName in `i:type`
   has an in-scope binding. Inherited members remain in Abstracts.
4. UUIDs are valid, unique, and lowercase; dictionary keys match their object's GUID.
   All present serializer IDs are unique and serializer references resolve.
5. Flow endpoints and threat references resolve on the correct drawing surface.
   Threat dictionary keys, numeric IDs, and interaction keys are consistent.
   Each modeled bidirectional connection has two separately identified opposite connectors;
   request/response labels and threat directions agree with their source and target GUIDs.
6. Properties match the chosen type and inherited catalog values; every list selection
   is in range. Threat categories, descriptions, priority, and property keys match Core.
7. Output has no XML declaration or added formatting. Existing text whitespace is preserved.
   Review sizes, connection points, handle separation, and naming against the style guide; these visual and naming
   conventions are separate from the script's structural checks.
8. Run `python scripts/validate_tm7.py model.tm7`. All bundled models validate against the
   blank asset's Core `4.1.0.11` catalog. The checker excludes the knowledge base object's
   serializer ID from catalog-content comparison and validates its uniqueness separately.
   Static checks validate the bundled serialization contract and consistency;
   an application open/save check is additional evidence when the tool is available.

The checker's regression tests run with `python -B scripts/validate_tm7_test.py`.
See [scripts/README.md](./scripts/README.md) for script usage, output, and validation limits.
