---
name: tm7-threat-model
description: 'Create, inspect, and modify Microsoft Threat Modeling Tool (.tm7) files with data flow diagrams and STRIDE threats. Use when a threat model must be delivered as .tm7, when adapting an existing .tm7 model, or when modeling software, embedded devices, or industrial interfaces using the bundled examples.'
---

# Microsoft Threat Modeling Tool (.tm7)

Produce a diagram and STRIDE threats using the WCF `DataContractSerializer` structure
demonstrated by the bundled exports. Treat XML well-formedness, model consistency, and
successful opening in Microsoft Threat Modeling Tool as separate validation levels.

## Select the reference

Read [example patterns](./references/example-patterns.md) before adapting either export.

| Resource | Use |
|----------|-----|
| [Example_Threat_Model.tm7](./references/Example_Threat_Model.tm7) | Full embedded-device example: generic stencils, trust borders, scope properties, directional interfaces, and generated STRIDE threats; SDL TM Knowledge Base (Core) `4.1.0.11`, model `Version` `4.3`. |
| [example-minimal.tm7](./assets/example-minimal.tm7) | Smaller diagram with two stencils, one connector, and one threat; Azure Threat Model Template `1.0.0.33`. Use its own catalog and serialization layout. |

For modifications, use the supplied model as the base and preserve its catalog and layout.
For new models, select the bundled export whose stencil and threat catalog fits the system.
Inspect relevant XML subtrees programmatically; avoid loading the entire knowledge base into
context. Use the references to learn serialization and modeling patterns, not to inherit
device names, scope decisions, security settings, priorities, or mitigation claims.

## Workflow

1. **Inventory the architecture.** Identify processes, stores, external actors, trust zones,
   directed interfaces, and scope assumptions. Record the payload or action and protocol
   for each flow. Separate confirmed facts from unresolved assumptions.
2. **Select one base export.** Preserve its root children, member order, namespaces,
   `KnowledgeBase`, and `Profile`. Do not combine the Azure and Core catalogs or copy a
   threat `TypeId` from one into the other.
3. **Build the diagram.** Clone complete compatible stencil/property blocks. Assign a new
   lowercase UUID to each new surface, stencil, boundary, and connector; retain existing
   identities when modifying a model. Update dictionary keys and all references together.
4. **Set properties and scope.** Select list values by their actual option text and index.
   Give exclusions a reason on each affected element and flow. Populate metadata from
   known facts; leave unknown ownership fields empty rather than inventing people.
5. **Lay out the model.** Position components without overlap, size borders around the
   intended zones, and preserve or recalculate connector endpoint and handle coordinates.
   Use separate connectors for independently modeled directions, as in the JTAG and QSPI
   examples. A visual border does not set `Out Of Scope` properties.
6. **Assess interactions.** Review applicable STRIDE categories for each in-scope flow and
   its endpoints. Use threat types from the selected catalog. Adapt descriptions to the
   architecture and record proposed controls without asserting that they are implemented.
7. **Serialize and validate.** Follow the checks below, write compact UTF-8 XML without an
   XML declaration to match the examples, and reparse the saved file. Open and save it in
   Microsoft Threat Modeling Tool when available; otherwise report that application
   validation remains unperformed.

## Serialization contract

Preserve namespace URIs and in-scope prefix bindings, including prefixes used inside
`i:type` values. Prefix spellings are aliases; changing them without updating QName-valued
attributes can break deserialization. XML declarations and indentation are not themselves
proof of corruption; use the bundled compact style to minimize unnecessary changes.

| Alias used here | Namespace URI | Purpose |
|-----------------|---------------|---------|
| `m` / default | `http://schemas.datacontract.org/2004/07/ThreatModeling.Model` | Root, drawing surfaces, model members |
| `d` | `http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts` | Inherited stencil members |
| `a` | `http://schemas.microsoft.com/2003/10/Serialization/Arrays` | Dictionary and array wrappers |
| `b` | `http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase` | Attribute objects, catalog, threat members |
| `i` | `http://www.w3.org/2001/XMLSchema-instance` | `type` and `nil` attributes |
| `z` | `http://schemas.microsoft.com/2003/10/Serialization/` | Object identities and references |
| `c` | `http://www.w3.org/2001/XMLSchema` | Primitive type names |

Read namespaces locally: the exports rebind `a` to the KnowledgeBase namespace inside
`KnowledgeBase`; it does not always denote Arrays.

### Root members

Preserve the sequence of the selected export; these are two observed layouts, not a rule
to merge their optional members:

| Export | Root children in document order |
|--------|---------------------------------|
| Core example | `DrawingSurfaceList`, `MetaInformation`, `Notes`, `ThreatInstances`, `ThreatGenerationEnabled`, `Validations`, `Version`, `KnowledgeBase`, `Profile` |
| Minimal Azure example | `DrawingSurfaceList`, `MetaInformation`, `Notes`, `ThreatInstances`, `ThreatMetaData`, `KnowledgeBase`, `Profile` |

Keep `KnowledgeBase` as a root-level sibling before `Profile`, never inside
`ThreatMetaData`. Preserve the separate catalog-level `KnowledgeBase/ThreatMetaData`.
Keep `<PromptedKb xmlns=""/>` in `Profile`. Do not infer a tool release number from the
Core example's model `Version` value `4.3`.

### Stencils and connectors

Keep stencils in `DrawingSurfaceModel/Borders` and connectors in `Lines`, each wrapped
in an Arrays `KeyValueOfguidanyType` containing `Key` and `Value`. Set `Key` equal to
the object's Abstracts `Guid`. Preserve the Abstracts namespace and member order of
`GenericTypeId`, `Guid`, `Properties`, `TypeId`, and geometry members.

| Element | `i:type` | Core example `GenericTypeId` | Core example `TypeId` |
|---------|----------|------------------------------|-----------------------|
| Process | `StencilEllipse` | `GE.P` | `GE.P` |
| Data store | `StencilParallelLines` | `GE.DS` | `GE.DS` |
| External actor | `StencilRectangle` | `GE.EI` | `GE.EI` or `SE.EI.TMCore.User` |
| Trust border | `BorderBoundary` | `GE.TB.B` | `GE.TB.B` |
| Directed flow | `Connector` | `GE.DF` | `GE.DF` |

Resolve generic identifiers against `KnowledgeBase/GenericElements` and specialized
identifiers against `StandardElements`. Do not replace a complete specialized stencil
with a generic block by changing only its `TypeId`; its property definitions also differ.
Use `GE.TB.B` for the demonstrated border, not the unsupported shorthand `GE.TB`.

For each connector, resolve Abstracts `SourceGuid` and `TargetGuid` to stencils on the
same surface. Preserve `HandleX`, `HandleY`, `SourceX`, `SourceY`, `TargetX`, and
`TargetY` along with the direction. Do not assign all endpoint coordinates zero by default.

Preserve existing `z:Id` attributes and allocate fresh identifiers for cloned objects,
including nested objects. Scan the entire document, including the catalog, for collisions.
Resolve every `z:Ref` to an existing identity. Do not add `z:Id` to every XML node or
regenerate catalog identifiers as if they were diagram UUIDs.

### Typed properties

Keep complete Arrays `anyType` blocks with KnowledgeBase members:

| Attribute type | Representation |
|----------------|----------------|
| `HeaderDisplayAttribute` | `DisplayName`, `Name`, and nil `Value` |
| `StringDisplayAttribute` | `Value` typed as XML Schema `string` |
| `BooleanDisplayAttribute` | `Value` typed as XML Schema `boolean` |
| `ListDisplayAttribute` | Arrays string options in `Value`, plus zero-based `SelectedIndex` |

Preserve property `Name` identifiers and option order. Never assume `0` means `No` or
`1` means `Yes`: the Core example's `Source Authenticated` options are `Not Selected`,
`No`, `Yes`, while `Destination Authenticated` has `No`, `Yes`. See the
[property examples](./references/example-patterns.md#typed-properties-and-scope).

If a control is unconfirmed, select `Not Selected` when available. If the catalog only
offers `No` and `Yes`, document a conservative `No` as an assumption that credits no
control pending confirmation, rather than presenting it as an observed implementation fact.

### Threat instances

Use Arrays `KeyValueOfstringThreatpc_P0_PhOB` wrappers in `ThreatInstances`. Preserve
the selected export's KnowledgeBase `Value` member order, including nil members.
Construct identities from the interaction, not from a hard-coded `TH` prefix:

```text
TypeId         = an Id in the selected KnowledgeBase/ThreatTypes
dictionary Key = TypeId + SourceGuid + FlowGuid + TargetGuid
InteractionKey = SourceGuid + ":" + FlowGuid + ":" + TargetGuid
```

The Core example uses identifiers such as `S2`, `T1`, and `E7`; the Azure template uses
identifiers such as `TH117`. Keep numeric threat `Id` values unique and separate from
`TypeId` and dictionary keys. Resolve `DrawingSurfaceGuid`, both endpoint GUIDs, and
`FlowGuid` within the intended surface. Keep the interaction consistent with the selected
flow and assessed direction; do not blindly copy the minimal example's threat endpoints.

Store display content in `Properties` using Arrays `KeyValueOfstringstring` entries.
The Core example demonstrates `Title`, `UserThreatCategory`,
`UserThreatShortDescription`, `UserThreatDescription`, `InteractionString`, and
`Priority`; its top-level `Title` and `UserThreat*` members remain nil. Keep the
top-level and property `Priority` values consistent. Preserve catalog category spellings,
including `Denial Of Service` and `Elevation Of Privilege` in the Core example.

Use `AutoGenerated` for newly generated, unreviewed threats as demonstrated by the Core
example. Preserve existing review states when editing. Set `Mitigated` only with evidence
of implemented controls and a recorded justification; suggested controls alone do not
establish mitigation. Add properties only when supported by the selected catalog's
`ThreatMetaData`; do not invent `<Mitigations>` or `<SecurityGaps>` elements.

## Validation and delivery

Perform these checks on the saved file:

1. Parse XML with namespaces and verify the selected root layout and member order.
   Resolve namespace prefixes inside `i:type` values, not only element tag names.
2. Check unique surface/stencil/connector UUIDs, matching dictionary keys and `Guid`
   members, unique `z:Id` values, and resolvable `z:Ref` attributes.
3. Resolve connector endpoints and threat surface/flow/endpoint references. Reconstruct
   threat dictionary and interaction keys and check unique numeric threat IDs.
4. Resolve stencil and threat types against the selected knowledge base. Check every
   list index is within its own option array and selects the intended value.
5. Review names, metadata, exclusions and their reasons, directional flows, boundary
   placement, and connector geometry. Require STRIDE review of in-scope interactions;
   do not force six threats per flow or copy the example's threat count.
6. Confirm descriptions and states reflect available evidence. Reopen in Microsoft
   Threat Modeling Tool when available and inspect both diagram and analysis views.

Deliver the `.tm7` file with a short account of the modeled scope, assumptions, and checks
actually performed. Do not claim application compatibility solely from XML parsing or
reference checks.
