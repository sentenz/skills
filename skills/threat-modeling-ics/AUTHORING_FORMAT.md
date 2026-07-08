# Threat Modeling ICS Skill Authoring Format

This guide captures the style and structure conventions for keeping the `threat-modeling-ics` skill readable, deterministic, and reviewable as the skill grows.

## Desired file split

Keep `SKILL.md` as the short execution contract. Move large reference material into companion files that are easier to review and maintain.

| File | Purpose | Content style |
| --- | --- | --- |
| `SKILL.md` | Agent execution contract | Short imperative rules and ordered workflow |
| `REVIEW_CONTRACT.md` | Output schema and validation contract | Canonical tables and validation checklist |
| `MAPPINGS.md` | Framework and scoring lookup tables | Dense lookup matrices and deterministic mappings |
| `EXAMPLES.md` | Raw and generated examples | Fenced CSV and Mermaid examples |
| `REFERENCES.md` | External framework references | Links, local asset versions, and provenance notes |

## Recommended `SKILL.md` structure

A compact agent skill should follow this order:

1. Purpose and scope
2. Required inputs
3. Required outputs
4. Non-negotiable invariants
5. Blocking gates
6. Ordered workflow
7. Deliverable checklist
8. References to companion files

The main file should answer what the agent must do. Companion files should answer how to classify, score, map, or format the details.

## Voice and style

Use direct, operational instructions.

| Prefer | Avoid |
| --- | --- |
| `Preserve native TMT fields byte-for-byte.` | Long explanatory paragraphs before the rule |
| `Leave the field blank only when review is blocked.` | Ambiguous terms such as `when appropriate` without criteria |
| `Record exactly one threat actor label.` | Multiple synonymous instructions in different sections |
| `Stop at this blocking gate.` | Soft suggestions for conditions that must halt the review |

Explanatory context is valuable, but it should live outside the critical execution path unless the agent must use it to decide.

## Admonition policy

Reserve Markdown admonitions for high-signal control points.

| Admonition | Use for |
| --- | --- |
| `[!IMPORTANT]` | Non-negotiable execution rules, preservation invariants, and blocking gates |
| `[!NOTE]` | Clarifying rationale that prevents predictable misinterpretation |
| `[!WARNING]` | Conditions that may corrupt evidence, produce unsafe assumptions, or invalidate traceability |

Do not use admonitions for general background, framework introductions, or examples that can be expressed as normal prose.

## Table policy

Use inline tables only when they directly support an execution decision in the same section. Move wide or dense tables to companion files.

| Keep inline | Move out |
| --- | --- |
| Native column preservation contract | Full generated CSV examples |
| Blocking condition table | Large risk matrices |
| Allowed value table for one output field | Purdue, threat-actor, or framework reference tables |
| Short deliverable checklist | Long mapping examples or scenario catalogs |

## CSV formatting policy

Keep CSV examples in fenced code blocks and avoid Markdown tables for long row examples.

```csv
Id;Title;Category;Diagram;Interaction;Priority;State;Changed By;Description;Justification;Last Modified
1;Example threat;Tampering;Device;PLC to Device;High;Mitigated;;"Description";"Justification";Generated
```

Rules:

- Use `csv` fenced blocks for copyable examples.
- Keep generated examples semicolon-delimited when the output contract requires semicolon CSV.
- Quote long narrative fields such as `Description` and `Justification`.
- Keep explanatory row notes outside the fenced CSV block.
- Do not mix comma-decimal and dot-decimal scoring in the same analytical schema.

## Determinism rules

Every instruction should help an agent produce repeatable results.

- Define allowed values before asking the agent to populate a column.
- State when `N/A` is valid and when a blank field is valid.
- Separate evidence gathering from decision-making.
- Avoid duplicate rules in multiple sections unless one section explicitly delegates to the other.
- Keep framework identifiers in dedicated columns, not only in narrative text.
- Use one canonical section for output-column order.

## Suggested refactor sequence

The safest way to slim the current skill is incremental.

1. Add companion files without altering existing workflow behavior.
2. Move output schema and validation checklist into `REVIEW_CONTRACT.md`.
3. Move large mapping tables into `MAPPINGS.md`.
4. Move Mermaid and CSV examples into `EXAMPLES.md`.
5. Replace moved sections in `SKILL.md` with concise references.
6. Re-run a documentation diff review to confirm no execution rule was lost.

## Review checklist for future edits

Before merging changes to this skill:

- The main workflow remains ordered and unambiguous.
- Blocking gates are easy to find.
- Native TMT row-preservation rules are still explicit.
- Output fields have one canonical schema definition.
- Examples are copyable and fenced.
- Large lookup matrices are not duplicated across files.
- Terminology is consistent across state, priority, risk treatment, and approval.
- Companion files do not contradict `SKILL.md`.
