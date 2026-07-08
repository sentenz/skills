# Threat Modeling ICS Review Contract

This companion contract turns the long-form `SKILL.md` guidance into a compact, auditable checklist for generated OT/ICS threat-model review artifacts.

Use this file as the canonical schema and validation reference when enriching Microsoft Threat Modeling Tool exports for OT/ICS systems.

## Output schema

The generated CSV must preserve native TMT fields in their original order and append enrichment fields in the order below.

| Column | Source | Required | Allowed values or format | Blank allowed when |
| --- | --- | --- | --- | --- |
| `Id` | Native TMT | Yes | Source value, byte-for-byte preserved | Never |
| `Title` | Native TMT | Yes | Source value, byte-for-byte preserved | Never |
| `Category` | Native TMT | Yes | Source value, byte-for-byte preserved | Never |
| `Diagram` | Native TMT | Yes | Source value, byte-for-byte preserved | Never |
| `Interaction` | Native TMT | Yes | Source value, byte-for-byte preserved | Never |
| `Priority` | Review | Yes | `Low`, `Medium`, `High` | Review blocked |
| `State` | Review | Yes | `Not Started`, `Not Applicable`, `Mitigated`, `Needs Investigation` | Never |
| `Changed By` | Native TMT | Yes | Source value, byte-for-byte preserved | Never |
| `Description` | Native TMT | Yes | Source value, byte-for-byte preserved and quoted in semicolon CSV output | Never |
| `Justification` | Review | Yes | Plain-language analyst rationale, quoted in semicolon CSV output | Review blocked |
| `Last Modified` | Native TMT | Yes | Source value, byte-for-byte preserved | Never |
| `ATT&CK ID` | Enrichment | Yes | `T####`, `T####.###`, comma-separated list, or `N/A` | Review blocked |
| `EMB3D TID` | Enrichment | Yes | `TID-###`, comma-separated list, or `N/A` | Review blocked |
| `CWE ID` | Enrichment | Yes | `CWE-###`, comma-separated list, or `N/A` | Review blocked |
| `CVSS v4.0 Vector` | Derived | Yes when score is present | `CVSS:4.0/...` vector string | Not applicable or review blocked |
| `CVSS-B v4.0 Score` | Derived | Yes when vector is present | Decimal value from `0.0` to `10.0` | Not applicable or review blocked |
| `CVSS v4.0 Severity` | Derived | Yes when score is present | `None`, `Low`, `Medium`, `High`, `Critical` | Not applicable or review blocked |
| `Likelihood of Exploit` | Derived | Yes for finalized rows | `Info`, `Low`, `Medium`, `High`, `Critical` | Review blocked |
| `Risk Prioritization` | Derived | Yes for finalized rows | `Info`, `Low`, `Medium`, `High`, `Critical` | Review blocked |
| `Threat Actor` | Enrichment | Yes for finalized rows | `Thrill Seeker`, `Hacktivist`, `Cybercriminal`, `Insider Threat`, `Nation-State Actor` | Review blocked |
| `Risk Treatment` | Governance | Yes for finalized rows | `Avoidance`, `Mitigation`, `Acceptance`, `Transfer` | Review blocked |
| `Risk Approval` | Governance | Yes for finalized rows | `Not Required`, `Lead Security`, `Product Security`, `CPSO`, `Executive` | Review blocked |

## State and treatment semantics

Do not use `State` and `Risk Treatment` as synonyms. They answer different questions.

| Field | Meaning | Examples |
| --- | --- | --- |
| `State` | Analyst review status of the threat row | `Mitigated`, `Not Applicable`, `Needs Investigation` |
| `Risk Treatment` | Governance disposition for the resulting risk | `Avoidance`, `Mitigation`, `Acceptance`, `Transfer` |
| `Risk Approval` | Minimum authority required for the selected disposition | `Lead Security`, `CPSO`, `Executive` |

A row may be technically `Mitigated` while still requiring `Acceptance` when residual risk remains. In that case, `Justification` must name both the applied control and the residual-risk acceptance mechanism.

## CVSS applicability rules

CVSS fields must be treated as a trio: vector, score, and severity are present together or absent together.

| Scenario | CVSS handling | Required justification |
| --- | --- | --- |
| Valid attack path with measurable technical impact | Record vector, score, and severity | Explain attack path and impact metrics |
| Valid attack path with effectively zero residual impact | Record zero-impact vector, `0.0`, and `None` | Explain controls that reduce impact to zero |
| Architecturally impossible or structurally eliminated path | Leave CVSS trio blank | Explain why the path is not applicable |
| Review blocked by missing evidence | Leave CVSS trio blank | Name the missing evidence |

Prefer `0.0` decimal notation for machine interoperability. If a locale-specific CSV requires comma decimals, apply conversion as a final serialization step, not inside the analytical schema.

## OT consequence mapping

Record OT/ICS consequences in the review summary and in row-level justification whenever they materially influence severity, risk prioritization, or approval.

| OT consequence category | Typical evidence | CVSS relation |
| --- | --- | --- |
| Loss of View | HMI, historian, telemetry, or operator visibility degraded | Usually `VA` or `SA` |
| Loss of Control | Commands blocked, control loop unavailable, or actuator response lost | Usually `VA` or `SA` |
| Manipulation of Control | Unauthorized command, setpoint, recipe, logic, or configuration change | Usually `VI` or `SI` |
| Loss of Safety Function | SIS, interlock, fail-safe, or protective function impaired | Usually `SI` or `SA` |
| Physical Damage | Device, actuator, drive, vessel, or process equipment damage plausible | Usually `SI` or `SA` |
| Environmental Harm | Release, spill, emissions excursion, or containment failure plausible | Usually `SI` or `SA` plus narrative |
| Human Safety Impact | Unsafe motion, overpressure, exposure, fire, or injury scenario plausible | Usually `SI` or `SA` plus safety narrative |
| Production Loss | Degraded throughput, downtime, quality loss, or restart burden | Usually `VA` or `SA` |

## Source-version metadata

Every generated summary must include a source metadata block so reviewers can reproduce mappings.

```yaml
framework_sources:
  attack_ics: "assets/attack/ics-attack-19.1.json"
  emb3d: "assets/emb3d/threats_2.0.1.json"
  cwe: "assets/cwe/cwe.json"
  cvss_schema: "assets/cvss/cvss-v4.0.json"
  generated_at: "<ISO-8601 timestamp>"
```

If a local asset version is known to be superseded but semantically equivalent for the reviewed mappings, state that explicitly in the summary.

## Final validation checklist

Before finalizing the generated CSV and summary:

- Every generated row has the same native TMT `Id` as exactly one source row.
- Native TMT fields are preserved byte-for-byte except allowed review fields.
- Native TMT columns remain in source order.
- Appended review columns follow the canonical order in this contract.
- `CVSS v4.0 Vector`, `CVSS-B v4.0 Score`, and `CVSS v4.0 Severity` are present together or absent together.
- `Not Applicable` rows do not claim residual risk.
- `Mitigated` rows identify the specific control and residual exposure.
- `Acceptance` rows identify the approving role and acceptance mechanism.
- `Transfer` rows identify the third party and transfer instrument.
- `Risk Approval` is consistent with `Risk Prioritization` and `Risk Treatment`.
- No row uses a framework identifier only as the justification.
- The review summary includes source-version metadata and any unresolved evidence gaps.
