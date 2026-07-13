# CVSS Calculator Script

`calculate_cvss.py` validates, normalizes, and calculates CVSS vectors for the Threat Modeling ICS Agent Skill.

The script is designed for non-interactive agent workflows. Successful records are written to standard output as JSON or JSON Lines. Diagnostics and validation summaries are written to standard error.

## Runtime

Requirements are declared through PEP 723 inline script metadata:

- Python 3.9 or later
- `uv`
- `cvss==3.6`

Run commands from the `skills/threat-modeling-ics/` skill directory so the relative script path remains stable.

## Basic Usage

Calculate one CVSS v4.0 vector:

```bash
uv run scripts/calculate_cvss.py \
  --version 4.0 \
  --include-metrics \
  --pretty \
  'CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N'
```

Calculate a CVSS v3.1 vector with automatic version detection:

```bash
uv run scripts/calculate_cvss.py \
  'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'
```

Calculate a prefixless vector by specifying its version explicitly:

```bash
uv run scripts/calculate_cvss.py \
  --version 3.1 \
  'AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'
```

## Supported Versions

- CVSS 2.0
- CVSS 3.0
- CVSS 3.1
- CVSS 4.0

Version detection uses the vector prefix when available. Prefixless CVSS 3.x and 4.0 vectors require `--version` because their metric abbreviations overlap. Prefixless CVSS 2.0 vectors can be detected through the mandatory `Au` metric.

## Input Modes

### Positional arguments

Pass one or more vectors directly:

```bash
uv run scripts/calculate_cvss.py \
  'CVSS:4.0/AV:P/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N' \
  'CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N'
```

### Input files

Use one vector per line. Blank lines and lines beginning with `#` are ignored.

```bash
uv run scripts/calculate_cvss.py \
  --input vectors.txt \
  --format jsonl
```

`--input` may be supplied multiple times.

### Standard input

```bash
cat vectors.txt | uv run scripts/calculate_cvss.py --format jsonl
```

Use `--stdin` to combine standard input with positional vectors or input files.

## Output Formats

### JSON

JSON is the default. A single input produces one object; multiple inputs produce an array.

```json
{
  "canonical_vector": "CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N",
  "input_vector": "CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N",
  "ok": true,
  "score": 7.1,
  "scores": {
    "overall": 7.1
  },
  "severity": "High",
  "severities": {
    "overall": "High"
  },
  "source": "argument",
  "version": "4.0"
}
```

Use `--pretty` for indented JSON.

### JSON Lines

JSON Lines emits one compact object per input vector and is intended for batch processing:

```bash
uv run scripts/calculate_cvss.py \
  --input vectors.txt \
  --version 4.0 \
  --format jsonl
```

Input order is preserved so each output record can be mapped deterministically to the corresponding threat row.

## Parsed Metrics

Use `--include-metrics` to include the metric abbreviations and values parsed by the CVSS library:

```bash
uv run scripts/calculate_cvss.py \
  --version 4.0 \
  --include-metrics \
  'CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N'
```

Parsed metrics confirm that the vector was interpreted as intended. They do not establish that the selected metrics are semantically correct for the modeled attack scenario.

## Error Records

Invalid vectors produce structured records:

```json
{
  "error": {
    "hint": "Supply every mandatory Base metric required by the selected CVSS version.",
    "message": "...",
    "type": "..."
  },
  "input_vector": "CVSS:4.0/AV:N",
  "ok": false,
  "source": "argument"
}
```

Use `--fail-fast` to stop after the first invalid vector. Without this option, all inputs are processed and every failure is reported.

## Exit Codes

| Exit code | Meaning |
| --- | --- |
| `0` | All vectors were calculated successfully. |
| `1` | At least one vector failed validation or calculation. |
| `2` | Command-line usage or input acquisition failed. |

## Threat Modeling Workflow Contract

The Threat Modeling ICS skill selects and justifies CVSS v4.0 Base metrics from the threat evidence. This script is responsible only for deterministic vector validation, canonicalization, score calculation, and severity calculation.

For populated threat rows:

1. Construct a complete `CVSS:4.0/` Base vector.
2. Run this script with `--version 4.0`.
3. Accept results only when `ok` is `true`, `version` is `4.0`, and `canonical_vector` begins with `CVSS:4.0/`.
4. Store `canonical_vector`, `score`, and `severity` as the authoritative CVSS values.
5. Convert a JSON score such as `7.1` to the generated CSV decimal-comma form `7,1` only during serialization.
6. Do not manually recalculate, estimate, round, or override the script result.

Before delivering a generated CSV, batch-run all populated vectors with `--format jsonl` and reject the artifact if any record fails or differs from the row values.

## Help

```bash
uv run scripts/calculate_cvss.py --help
```
