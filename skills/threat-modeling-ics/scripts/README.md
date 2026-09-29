# Script Catalog

Utility reference for the [workflow](../SKILL.md). Invocation timing, command examples, and data-access restrictions are owned by [SKILL.md](../SKILL.md#32-framework-data-access).

| Utility | Capability and Output | Workflow |
| --- | --- | --- |
| [calculate_cvss.py](calculate_cvss.py) | Calculates a CVSS vector and returns compact JSON. Supports CVSS v2, v3, and v4; the ICS workflow populates the CVSS v4.0 columns. | [Review, step 5](../SKILL.md#33-review) |
| [query_attack.py](query_attack.py) | Searches the complete ATT&CK for ICS STIX snapshot in-process; returns bounded active-technique candidates or single-technique details with a 30,000-character ceiling. | [Review, step 2](../SKILL.md#33-review) |
| [query_cwe.py](query_cwe.py) | Searches the complete versioned CWE projection in-process; returns bounded candidates or single-record details with a 30,000-character ceiling, keeping the raw dataset out of model context. | [Review, step 4](../SKILL.md#33-review) |
| [query_emb3d.py](query_emb3d.py) | Searches and joins versioned EMB3D threat, property, and mitigation assets in-process; returns bounded candidates or single-record mappings with a 30,000-character ceiling. | [Review, step 3](../SKILL.md#33-review) |
| [validate_csv.py](validate_csv.py) | Checks the generated CSV output contract, control terminology, active ATT&CK techniques, mappable CWE weaknesses, source-backed EMB3D mitigation citations, and optional raw-TMT source traceability; reports findings with actual-versus-expected diffs. | [Deliverables, step 1](../SKILL.md#4-deliverables) |
| [validate_cvss.py](validate_cvss.py) | Validates CVSS vectors in the CVSS v4.0 columns and compares calculated and stored scores. | [Deliverables, step 1](../SKILL.md#4-deliverables) |

## References

- GitHub [CVSS](https://github.com/RedHatProductSecurity/cvss) repository.
- Agent Skills [Using Scripts](https://agentskills.io/skill-creation/using-scripts) page.
