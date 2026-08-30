# `scripts/`

- [1. Details](#1-details)
- [2. References](#2-references)

## 1. Details

- [calculate_cvss.py](calculate_cvss.py)
  > Calculates a CVSS vector and returns compact JSON. Supports CVSS v2, v3, and v4 formats. Primarily used to populate the `CVSS v4.0` columns.

    ```bash
    uv run ./scripts/calculate_cvss.py --vector 'CVSS:4.0/AV:P/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N'
    ```

- [query_attack.py](query_attack.py)
  > Searches the complete ATT&CK for ICS STIX snapshot in-process and returns only bounded active-technique candidates or single-technique details with a 30,000-character ceiling.

    ```bash
    uv run ./scripts/query_attack.py --search 'remote services' --top 5
    uv run ./scripts/query_attack.py --id 'T0886' --include tactics,platforms,mitigations
    ```

- [query_cwe.py](query_cwe.py)
  > Searches the complete versioned CWE projection in-process and returns only bounded candidate or single-record detail output with a 30,000-character ceiling, preventing the raw dataset from entering model context.

    ```bash
    uv run ./scripts/query_cwe.py --search 'resource throttling' --top 5
    uv run ./scripts/query_cwe.py --id 'CWE-770' --include description,related,mitigations
    ```

- [query_emb3d.py](query_emb3d.py)
  > Searches and joins the versioned EMB3D threat, property, and mitigation assets in-process, returning bounded candidates or single-record mappings with a 30,000-character ceiling.

    ```bash
    uv run ./scripts/query_emb3d.py --search 'firmware installation' --top 5
    uv run ./scripts/query_emb3d.py --tid 'TID-211' --include properties,mitigations
    uv run ./scripts/query_emb3d.py --mid 'MID-001' --include threats
    ```

- [validate_csv.py](validate_csv.py)
  > Validates the complete generated CSV output contract, enforcement-boundary terminology, active MITRE ATT&CK techniques, mappable MITRE CWE weaknesses, source-backed EMB3D mitigation citations, and optional raw-TMT source traceability, then reports all findings with actual-versus-expected diffs.

    ```bash
    uv run ./scripts/validate_csv.py --source 'input.csv' --artifact 'generated.csv'
    ```

- [validate_cvss.py](validate_cvss.py)
  > Validates all CVSS vectors in the `CVSS v4.0` columns and compares the calculated score with the stored score.

    ```bash
    uv run ./scripts/validate_cvss.py --csv 'generated.csv'
    ```

## 2. References

- GitHub [CVSS](https://github.com/RedHatProductSecurity/cvss) repository.
- Agent Skills [Using Scripts](https://agentskills.io/skill-creation/using-scripts) page.
