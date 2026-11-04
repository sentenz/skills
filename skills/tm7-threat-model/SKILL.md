---
name: tm7-threat-model
description: 'Creates valid Microsoft Threat Modeling Tool (.tm7) files compatible with the Microsoft Threat Modeling Tool v7.3+. Use this skill whenever asked to create, generate, or modify a .tm7 threat model file, or when performing STRIDE threat modeling that should output a .tm7 file that opens cleanly in the Microsoft Threat Modeling Tool.'
---

# Microsoft Threat Modeling Tool (.tm7) Generator

You generate **valid `.tm7` files** for the Microsoft Threat Modeling Tool (v7.3+). A `.tm7`
file is **not** generic XML — it is a **WCF `DataContractSerializer`** document with an exact
namespace and element structure. If the structure is wrong, the tool refuses to open the file
with:

> "File is not an actual threat model or the threat model may be corrupted."

Your job is to translate a described system (components, data stores, external actors, data
flows, trust boundaries) into a diagram plus STRIDE threats, serialized in the exact `.tm7`
format described below.

## Workflow

When asked to produce a `.tm7` file:

1. **Model the system.** Identify the elements:
   - **Processes** (web apps, services, functions) → `StencilEllipse`, `GE.P`
   - **Data stores** (databases, caches, queues, blobs) → `StencilParallelLines`, `GE.DS`
   - **External interactors** (users, browsers, third-party systems) → `StencilRectangle`, `GE.EI`
   - **Trust boundaries** → `BorderBoundary`, `GE.TB.B`
   - **Data flows** connecting the above → `Connector`, `GE.DF`
2. **Assign a unique lowercase UUID** (e.g. `148ade68-5c80-40f3-8e1f-4e2cabdb5991`) to every
   stencil and every flow. Never use human-readable ids like `users-browser`.
3. **Lay out coordinates** (`Left`/`Top`/`Width`/`Height`) so stencils don't overlap.
4. **Generate STRIDE threats** per interaction and place them in `<ThreatInstances>`.
   Adapt descriptions, priorities, and mitigations to the architecture; do not inherit example
   threat states or claim a mitigation is implemented without evidence.
5. **Serialize** using the structure in this guide, mirroring `assets/example-minimal.tm7`.
6. **Validate** against the "Common Mistakes" checklist before returning the file.
7. **Write the file with no XML declaration and no added pretty-print indentation.**
   Preserve existing text whitespace in the reused KnowledgeBase.

Always open [`assets/example-minimal.tm7`](./assets/example-minimal.tm7) first and adapt it — reuse its exact
serialization skeleton and KnowledgeBase. It contains an empty diagram and no threats;
take populated stencil, connector, and threat blocks from
[`references/Example_Threat_Model.tm7`](./references/Example_Threat_Model.tm7), checking their
types and properties against the baseline catalog before adapting them.

For device interfaces, paired flows, trust boundaries, or a larger STRIDE example, read
[`references/example-patterns.md`](./references/example-patterns.md). It explains how to use
[`references/Example_Threat_Model.tm7`](./references/Example_Threat_Model.tm7) selectively while
retaining the minimal template's serialization skeleton and KnowledgeBase.

## CRITICAL: Serialization format

TM7 files use **WCF `DataContractSerializer` XML** with specific namespaces and contracts.

The file MUST start with this exact root element — **no `<?xml?>` declaration**:

```xml
<ThreatModel xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
```

**Preserve the baseline conventions:**
- Omit `<?xml version="1.0" encoding="utf-8"?>` and added formatting whitespace.
- Keep the template's namespace bindings, including prefixes used inside `i:type` values.
  Do not rename a prefix without updating its QName-valued references.
- Do not invent elements such as `<SecurityGaps>` or `<Mitigations>` — they do not exist in the
  TM7 schema.

> **Note:** `<MetaInformation>` (with children like `<Owner>`, `<Contributors>`,
> `<Reviewer>`, `<Assumptions>`, `<ExternalDependencies>`, `<HighLevelSystemDescription>`,
> `<ThreatModelName>`), `<Notes>`, and `<KnowledgeBase>` **are** part of the real schema and
> are emitted by the tool — keep them (see the structure below and `assets/example-minimal.tm7`).
> Just don't invent elements that the tool never produces.

## Required namespace prefixes

| Prefix | URI | Used for |
|--------|-----|----------|
| (default) | `http://schemas.datacontract.org/2004/07/ThreatModeling.Model` | Root `ThreatModel` |
| `xmlns:i` | `http://www.w3.org/2001/XMLSchema-instance` | Type attributes |
| `xmlns:z` | `http://schemas.microsoft.com/2003/10/Serialization/` | Reference ids (`z:Id`) |
| `xmlns:a` | `http://schemas.microsoft.com/2003/10/Serialization/Arrays` | Arrays / collections |
| `xmlns:b` | `http://schemas.datacontract.org/2004/07/ThreatModeling.KnowledgeBase` | Stencil properties |
| `xmlns:c` | `http://www.w3.org/2001/XMLSchema` | Primitive type values |

## File structure (correct order)

The minimal template contains, in this order: `DrawingSurfaceList`, `MetaInformation`, `Notes`,
`ThreatInstances`, `ThreatGenerationEnabled`, `Validations`, `Version`, `KnowledgeBase`, and
`Profile`. Both bundled files use this sequence, with `ThreatGenerationEnabled=true` and
document `Version=4.3`. Preserve these fields and the baseline's empty `Validations` element.

The embedded catalog versions differ; see
[example comparison](./references/example-patterns.md#serialization-differences).

```xml
<ThreatModel xmlns="..." xmlns:i="...">
  <DrawingSurfaceList>
    <DrawingSurfaceModel z:Id="i1" xmlns:z="...">
      <GenericTypeId xmlns="...Abstracts">DRAWINGSURFACE</GenericTypeId>
      <Guid xmlns="...Abstracts">{guid}</Guid>
      <Properties xmlns="...Abstracts" xmlns:a="...Arrays">...</Properties>
      <TypeId xmlns="...Abstracts">DRAWINGSURFACE</TypeId>
      <Borders xmlns:a="...Arrays">
        <!-- Stencil elements: processes, data stores, external entities, boundaries -->
      </Borders>
      <Header>Diagram 1</Header>
      <Lines xmlns:a="...Arrays">
        <!-- Data flow lines connecting stencils -->
      </Lines>
      <Zoom>1</Zoom>
    </DrawingSurfaceModel>
  </DrawingSurfaceList>
  <MetaInformation>
    <!-- Owner, Contributors, Reviewer, Assumptions, ThreatModelName, etc. -->
  </MetaInformation>
  <Notes xmlns:a="...Arrays"/>
  <ThreatInstances>
    <!-- Threat entries -->
  </ThreatInstances>
  <ThreatGenerationEnabled>true</ThreatGenerationEnabled>
  <Validations/>
  <Version>4.3</Version>
  <KnowledgeBase z:Id="i2" xmlns:a="...ThreatModeling.KnowledgeBase" xmlns:z="...">
    <!-- SDL Core catalog, including its own ThreatMetaData collection -->
  </KnowledgeBase>
  <Profile>
    <PromptedKb xmlns=""/>
  </Profile>
</ThreatModel>
```

> The `<KnowledgeBase>` (the template's stencil/threat catalog) is large but **required** —
> the tool uses it to resolve every stencil `TypeId`. It is a **top-level sibling** placed after
> `Version` and before `Profile`. `ThreatMetaData` belongs inside the catalog, not at the root.
> Reuse the KnowledgeBase verbatim
> from `assets/example-minimal.tm7`; only add stencils whose `TypeId` already appears in that
> KnowledgeBase.

## Stencil elements

Each stencil in `<Borders>` is wrapped in `<a:KeyValueOfguidanyType>`:

```xml
<a:KeyValueOfguidanyType>
  <a:Key>{guid}</a:Key>
  <a:Value z:Id="i3" i:type="StencilEllipse">
    <GenericTypeId xmlns="...Abstracts">GE.P</GenericTypeId>
    <Guid xmlns="...Abstracts">{guid}</Guid>
    <Properties xmlns="...Abstracts">
      <a:anyType i:type="b:HeaderDisplayAttribute" xmlns:b="...KnowledgeBase">
        <b:DisplayName>Web Application</b:DisplayName>
        <b:Name/>
        <b:Value i:nil="true"/>
      </a:anyType>
      <a:anyType i:type="b:StringDisplayAttribute" xmlns:b="...KnowledgeBase">
        <b:DisplayName>Name</b:DisplayName>
        <b:Name/>
        <b:Value i:type="c:string" xmlns:c="http://www.w3.org/2001/XMLSchema">My Component</b:Value>
      </a:anyType>
      <!-- Out Of Scope, Reason, configurable attributes -->
    </Properties>
    <TypeId xmlns="...Abstracts">SE.P.TMCore.WebApp</TypeId>
    <Height xmlns="...Abstracts">100</Height>
    <Left xmlns="...Abstracts">400</Left>
    <StrokeDashArray i:nil="true" xmlns="...Abstracts"/>
    <StrokeThickness xmlns="...Abstracts">1</StrokeThickness>
    <Top xmlns="...Abstracts">200</Top>
    <Width xmlns="...Abstracts">100</Width>
  </a:Value>
</a:KeyValueOfguidanyType>
```

### Stencil shape types

| Shape | `i:type` | `GenericTypeId` | Description |
|-------|----------|-----------------|-------------|
| Process (circle) | `StencilEllipse` | `GE.P` | Processes, web apps, services |
| Data store (parallel lines) | `StencilParallelLines` | `GE.DS` | Databases, storage, caches |
| External interactor (rectangle) | `StencilRectangle` | `GE.EI` | Users, external systems |
| Trust boundary | `BorderBoundary` | `GE.TB.B` | Trust boundaries |

### Common `TypeId` values (baseline KnowledgeBase)

| `TypeId` | Component |
|----------|-----------|
| `GE.P` | Generic Process |
| `GE.DS` | Generic Data Store |
| `GE.EI` | Generic External Interactor |
| `GE.DF` | Generic Data Flow |
| `GE.TB.B` | Generic Trust Border Boundary |
| `SE.P.TMCore.WebApp` | Web Application |
| `SE.P.TMCore.WebSvc` | Web Service |
| `SE.DS.TMCore.SQL` | SQL Database |
| `SE.EI.TMCore.Browser` | Browser |
| `SE.EI.TMCore.User` | Human User |

Use the SDL Core catalog's definitions and configurable attributes for each selected type.
Do not reuse Azure-only IDs or property metadata from an earlier template.

## Data flow lines

Lines in `<Lines>` also use `<a:KeyValueOfguidanyType>`, with `i:type="Connector"`:

```xml
<a:KeyValueOfguidanyType>
  <a:Key>{line-guid}</a:Key>
  <a:Value z:Id="i10" i:type="Connector">
    <GenericTypeId xmlns="...Abstracts">GE.DF</GenericTypeId>
    <Guid xmlns="...Abstracts">{line-guid}</Guid>
    <Properties xmlns="...Abstracts">...</Properties>
    <TypeId xmlns="...Abstracts">GE.DF</TypeId>
    <HandleX xmlns="...Abstracts">0</HandleX>
    <HandleY xmlns="...Abstracts">0</HandleY>
    <SourceGuid xmlns="...Abstracts">{source-stencil-guid}</SourceGuid>
    <SourceX xmlns="...Abstracts">0</SourceX>
    <SourceY xmlns="...Abstracts">0</SourceY>
    <TargetGuid xmlns="...Abstracts">{target-stencil-guid}</TargetGuid>
    <TargetX xmlns="...Abstracts">0</TargetX>
    <TargetY xmlns="...Abstracts">0</TargetY>
  </a:Value>
</a:KeyValueOfguidanyType>
```

## Property attribute types

Properties use typed `<a:anyType>` elements:

| `i:type` | Purpose | Value |
|----------|---------|-------|
| `b:HeaderDisplayAttribute` | Section header | `i:nil="true"` |
| `b:StringDisplayAttribute` | Text value (Name, Reason) | `i:type="c:string"` |
| `b:BooleanDisplayAttribute` | Boolean (Out Of Scope) | `i:type="c:boolean"` |
| `b:ListDisplayAttribute` | Dropdown list | Has `<b:SelectedIndex>` |

## Threat instances

Threats go in `<ThreatInstances>` using `<a:KeyValueOfstringThreatpc_P0_PhOB>` (note the exact
`PhOB` suffix). Unlike stencils, the threat `<a:Value>` fields are **`b:`-prefixed** (the
`ThreatModeling.KnowledgeBase` namespace), and the `<a:Key>` is the literal concatenation
`<TypeId> + <SourceGuid> + <FlowGuid> + <TargetGuid>` (without separators). The minimal
template has no threat instances; the device reference uses SDL Core IDs such as `S2` and `E7`.
Use a threat `TypeId` defined in the output's KnowledgeBase; never transfer IDs between
catalogs without checking their definitions:

```xml
<ThreatInstances xmlns:a="...Arrays">
  <a:KeyValueOfstringThreatpc_P0_PhOB>
    <a:Key>S2{source-guid}{flow-guid}{target-guid}</a:Key>
    <a:Value xmlns:b="...KnowledgeBase">
      <b:ChangedBy/>
      <b:DrawingSurfaceGuid>{drawing-surface-guid}</b:DrawingSurfaceGuid>
      <b:FlowGuid>{flow-guid}</b:FlowGuid>
      <b:Id>32</b:Id>
      <b:InteractionKey>{source-guid}:{flow-guid}:{target-guid}</b:InteractionKey>
      <b:InteractionString i:nil="true"/>
      <b:ModifiedAt>2025-01-01T00:00:00</b:ModifiedAt>
      <b:Priority>High</b:Priority>
      <b:Properties>
        <a:KeyValueOfstringstring>
          <a:Key>Title</a:Key>
          <a:Value>Spoofing the destination process</a:Value>
        </a:KeyValueOfstringstring>
        <a:KeyValueOfstringstring>
          <a:Key>UserThreatCategory</a:Key>
          <a:Value>Spoofing</a:Value>
        </a:KeyValueOfstringstring>
        <a:KeyValueOfstringstring>
          <a:Key>UserThreatShortDescription</a:Key>
          <a:Value>Spoofing is when a process or entity is something other than its claimed identity.</a:Value>
        </a:KeyValueOfstringstring>
        <a:KeyValueOfstringstring>
          <a:Key>UserThreatDescription</a:Key>
          <a:Value>An attacker may impersonate the destination process and obtain data from the source.</a:Value>
        </a:KeyValueOfstringstring>
        <a:KeyValueOfstringstring>
          <a:Key>StateInformation</a:Key>
          <a:Value>Proposed: authenticate the destination process. Implementation is unverified.</a:Value>
        </a:KeyValueOfstringstring>
        <a:KeyValueOfstringstring>
          <a:Key>InteractionString</a:Key>
          <a:Value>{flow-name}</a:Value>
        </a:KeyValueOfstringstring>
        <a:KeyValueOfstringstring>
          <a:Key>Priority</a:Key>
          <a:Value>High</a:Value>
        </a:KeyValueOfstringstring>
      </b:Properties>
      <b:SourceGuid>{source-stencil-guid}</b:SourceGuid>
      <b:State>AutoGenerated</b:State>
      <b:StateInformation i:nil="true"/>
      <b:TargetGuid>{target-stencil-guid}</b:TargetGuid>
      <b:Title i:nil="true"/>
      <b:TypeId>S2</b:TypeId>
      <b:Upgraded>false</b:Upgraded>
      <b:UserThreatCategory i:nil="true"/>
      <b:UserThreatDescription i:nil="true"/>
      <b:UserThreatShortDescription i:nil="true"/>
      <b:Wide>false</b:Wide>
    </a:Value>
  </a:KeyValueOfstringThreatpc_P0_PhOB>
</ThreatInstances>
```

Use `S2` only for applicable destination-process spoofing; check the catalog's description
and generation filters. Store proposed mitigations and review rationale in the supported
`StateInformation` property (Justification), distinct from the nullable field of the same name.
Do not add Azure-specific `PossibleMitigations` or `SDLPhase` properties to the Core template.

**Every GUID must resolve:** `SourceGuid` and `TargetGuid` must equal `<a:Key>` values of real
stencils in `<Borders>`, and `FlowGuid` must equal the `<a:Key>` of a real connector in
`<Lines>`. Dangling references produce a model that opens with missing diagram elements.

Use the standard STRIDE categories for `UserThreatCategory`: **S**poofing, **T**ampering,
**R**epudiation, **I**nformation Disclosure, **D**enial of Service, **E**levation of Privilege.

## Common mistakes that break TM7 files

1. **Adding an `<?xml version="1.0"?>` declaration** — keep the baseline's declaration-free output convention.
2. **Changing namespace bindings without updating QName values** — preserve bindings used in `i:type` attributes.
3. **Using simple element names** like `<Border>`, `<Line>`, `<Stencil>` — you must use the
   DataContract wrapper types such as `<a:KeyValueOfguidanyType>`.
4. **Inventing elements the tool never emits** like `<SecurityGaps>` or `<Mitigations>` — these
   are not in the schema. (`<MetaInformation>`, `<Notes>`, and `<KnowledgeBase>` **are** valid
   and must be preserved.)
5. **Using human-readable GUIDs** like `users-browser` instead of real UUIDs
   (e.g. `148ade68-5c80-40f3-8e1f-4e2cabdb5991`).
6. **Dangling references** — a `Line`, threat `SourceGuid`/`TargetGuid`, or threat `FlowGuid`
   that points to a stencil/flow GUID that isn't actually defined in `<Borders>`/`<Lines>`.
   Every reference must resolve to an included element.
7. **Missing or duplicated `z:Id` reference attributes** — preserve these attributes where
   the template uses them; each `z:Id` (e.g. `i1`, `i2`, `i10`) must be **unique** across the whole file.
   When you duplicate a template block to add an element, always renumber its `z:Id` (and any
   nested ones) to values not used elsewhere; reusing an id creates duplicate DataContract
   object ids and makes deserialization fail.
8. **Missing the `xmlns` on child elements** — each `GenericTypeId`, `Guid`, `Properties`,
   `TypeId`, etc. must carry its own
   `xmlns="http://schemas.datacontract.org/2004/07/ThreatModeling.Model.Abstracts"`.
9. **Adding pretty-print indentation** — serialize compactly while preserving existing
   text whitespace in the reused catalog.

Also check drawing-surface references, catalog membership for stencil and threat `TypeId`
values, and consistency between each threat key, interaction key, and GUID fields. Report
structural checks separately from an actual open/save check in Microsoft Threat Modeling
Tool; parsing XML alone does not establish application compatibility.

## Reference asset

Always use [`assets/example-minimal.tm7`](./assets/example-minimal.tm7) in this skill's
directory as the structural reference. It contains one empty drawing surface and the SDL Core
KnowledgeBase, with no stencils, flows, or threat instances. Use the populated device example
for record shapes, then adapt stencil types, names, properties,
coordinates, data flows, and threats to the user's architecture, but **never** change the
serialization format or namespace structure, and only use stencil `TypeId` values that already
appear in its bundled `KnowledgeBase`. After generating, mentally diff your output's skeleton
against the example to confirm every namespace, wrapper element, and GUID reference matches.
