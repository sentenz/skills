# CSV Contract

CSV intake and generation rules for Microsoft TMT threat-model review artifacts.

- [1. Input Contract](#1-input-contract)
- [2. Output Contract](#2-output-contract)
- [3. CSV Writer Requirements](#3-csv-writer-requirements)
- [4. Field Validation](#4-field-validation)
- [5. Spreadsheet Safety](#5-spreadsheet-safety)
- [6. Templates](#6-templates)

## 1. Input Contract

The raw Microsoft TMT export is immutable source-of-record evidence.

- Prefer `<Device_Name>_Threat_Model.csv` as the raw TMT export.
- Classify the file by header and row content rather than filename alone.
- Do not edit the original input CSV.
- Required native fields: `Id`, `Title`, `Category`, `Diagram`, `Interaction`, `Priority`, `State`, `Changed By`, `Description`, `Justification`, `Last Modified`.
- Preserve raw native values verbatim unless the field is explicitly designated as a native review field.

## 2. Output Contract

The generated review artifact is `<Device_Name>_Threat_Model_Generated.csv`.

- Use semicolon-delimited CSV.
- Retain native TMT columns in source order.
- Preserve native source fields verbatim: `Id`, `Title`, `Category`, `Diagram`, `Interaction`, `Changed By`, `Description`, `Last Modified`.
- Update native review fields only after analyst review: `State`, `Priority`, `Justification`.
- Append review columns in this order: `ATT&CK ID`, `EMB3D TID`, `CWE ID`, `CVSS v4.0 Vector`, `CVSS-B v4.0 Score`, `CVSS v4.0 Severity`, `Likelihood of Exploit`, `Risk Prioritization`, `Threat Actor`, `Risk Treatment`, `Risk Approval`.
- Every output row must trace back to exactly one source row by native `Id`.
- If enrichment columns already exist, carry their values forward unchanged for already-reviewed rows unless the user explicitly requests re-review.

## 3. CSV Writer Requirements

> [!IMPORTANT]
> Do not hand-concatenate CSV rows. Use a standards-compliant CSV writer.

| Setting         | Required Value                                                                                          |
| --------------- | -------------------------------------------------------------------------------------------------------- |
| Delimiter       | Semicolon (`;`)                                                                                          |
| Quote character | Double quote (`"`)                                                                                      |
| Quoting         | Quote fields as required by the CSV writer. Quoting all fields is acceptable when consistency is needed. |
| Embedded quotes | Escape by doubling (`""`).                                                                             |
| Newlines        | Preserve only when correctly quoted.                                                                     |
| Encoding        | UTF-8.                                                                                                   |

Do not rely on narrative restrictions such as avoiding semicolons to make CSV valid. Any field can contain delimiters, quotes, line breaks, or spreadsheet formula triggers and must be handled by the writer.

## 4. Field Validation

Validate analyst decisions before writing the generated CSV.

| Field Group                | Validation Rule                                                                                                                        |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Source fields              | Verify every generated row matches exactly one source row by `Id`.                                                                     |
| Framework identifiers      | Keep identifiers in dedicated columns. Do not use identifier-only `Justification` values.                                               |
| CVSS trio                  | Populate `CVSS v4.0 Vector`, `CVSS-B v4.0 Score`, and `CVSS v4.0 Severity` together or leave all three blank when unresolved.          |
| CVSS score                 | Record with exactly one decimal digit and comma as decimal separator, e.g., `0,0`, `2,4`, `5,2`, `7,0`, `10,0`.                       |
| Finalized likelihood       | Do not record `N/A` for `Likelihood of Exploit` on finalized reviewed rows.                                                            |
| Finalized prioritization   | Do not record `N/A` for `Risk Prioritization` on finalized reviewed rows.                                                              |
| Threat actor               | Record exactly one standardized actor label.                                                                                           |
| Treatment and approval     | Reject rows where `State`, `CVSS v4.0 Severity`, `Risk Prioritization`, `Risk Treatment`, or `Risk Approval` contradict mapping rules. |
| Legal or regulatory claims | Reject rows that use legal or regulatory shorthand as the sole rationale for acceptance, transfer, mitigation, or avoidance.            |

## 5. Spreadsheet Safety

The generated CSV is source-of-record output and must preserve reviewed values unchanged.

- When a generated CSV cell begins with `=`, `+`, `-`, `@`, tab, or carriage return, preserve the value in the generated CSV and document the spreadsheet formula injection risk in the summary.
- If a spreadsheet-safe viewing copy is required, generate it as a separate derivative artifact.
- Name derivative viewing copies so they cannot be mistaken for source-of-record evidence, for example `<Device_Name>_Threat_Model_Generated_SpreadsheetSafe.csv`.

## 6. Templates

### 6.1. Raw TMT Export CSV Template

- `<Device_Name>_Threat_Model.csv`
  > Raw Microsoft TMT export in comma-delimited CSV format.

  ```csv
  Id,Title,Category,Diagram,Interaction,Priority,State,Changed By,Description,Justification,Last Modified
  1,Potential Lack of Input Validation for [Target],Tampering,<Device_Name>,PLC to [Target] via Modbus RTU (RS-485),High,Not Started,,Data flowing across PLC to [Target] via Modbus RTU (RS-485) may be tampered with by an attacker.,,Generated
  ```

### 6.2. Generated TMT CSV Template

- `<Device_Name>_Threat_Model_Generated.csv`
  > Completed review in semicolon-delimited CSV format with appended enrichment columns.

  ```csv
  Id;Title;Category;Diagram;Interaction;Priority;State;Changed By;Description;Justification;Last Modified;ATT&CK ID;EMB3D TID;CWE ID;CVSS v4.0 Vector;CVSS-B v4.0 Score;CVSS v4.0 Severity;Likelihood of Exploit;Risk Prioritization;Threat Actor;Risk Treatment;Risk Approval
  1;Potential Lack of Input Validation for [Target];Tampering;<Device_Name>;PLC to [Target] via Modbus RTU (RS-485);High;Mitigated;;"Data flowing across PLC to [Target] via Modbus RTU (RS-485) may be tampered with by an attacker.";"The protocol lacks authentication or integrity protection. Adjacent-bus injection can alter commands sent to the target. Controls reduce but do not eliminate residual exposure, and approval remains product-specific.";Generated;T1692.001;N/A;CWE-20;CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:L/SA:N;7,1;High;Medium;High;Cybercriminal;Acceptance;CPSO
  ```

> [!NOTE]
> Template rows are generalized, vendor-neutral patterns. Replace bracketed placeholders with product-specific values and validate all mappings against `MAPPING_RULES.md` before reuse.
