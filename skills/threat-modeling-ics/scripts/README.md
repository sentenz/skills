# `scripts/`

- [1. Details](#1-details)
- [2. References](#2-references)

## 1. Details

- [calculate_cvss.py](calculate_cvss.py)
  > Calculates a CVSS vector and returns compact JSON. Supports CVSS v2, v3, and v4 formats. Primarily used to populate the `CVSS v4.0` columns.

    ```bash
    python ./scripts/calculate_cvss.py --vector 'CVSS:4.0/AV:P/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N'
    ```

- [validate_cvss.py](validate_cvss.py)
  > Validates all CVSS vectors in the `CVSS v4.0` columns and compares the calculated score with the stored score.

    ```bash
    python ./scripts/validate_cvss.py --csv 'input.csv'
    ```

## 2. References

- GitHub [CVSS](https://github.com/RedHatProductSecurity/cvss) repository.
- Agent Skills [Using Scripts](https://agentskills.io/skill-creation/using-scripts) page.
