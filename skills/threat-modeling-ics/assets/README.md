# `assets/`

- [1. Details](#1-details)
- [2. References](#2-references)

## 1. Details

- [attack/](attack/)
  > MITRE ATT&CK for ICS 19.2 STIX snapshot from the [ATT&CK STIX dataset](https://github.com/mitre-attack/attack-stix-data/blob/master/ics-attack/ics-attack-19.2.json). Contains techniques, tactics, mitigations, relationships, and lifecycle flags. Treat it as programmatic input only, use `scripts/query_attack.py` for bounded lookup and `scripts/validate_output.py` for complete-output validation.

- [cwe/](cwe/)
  > Versioned MITRE CWE 4.20 projection derived from the [CWE JSON API](https://github.com/CWE-CAPEC/REST-API-wg/tree/main/json_repo). Contains all weakness IDs plus abstraction, status, mapping notes, relationships, candidate mitigations, and selected discovery views. Treat it as programmatic input only, use `scripts/query_cwe.py` for bounded lookup and `scripts/validate_output.py` for complete-output validation.

- [emb3d/](emb3d/)
  > MITRE EMB3D 2.0.1 JSON files derived from the [EMB3D knowledge base](https://github.com/mitre/emb3d/tree/main/_data). The base and combined files contain the same threat set, while the combined file enriches threat references and the property- and mitigation-centric files remain authoritative for their respective records. Treat them as programmatic input only, use `scripts/query_emb3d.py` for bounded joined lookup and `scripts/validate_output.py` for complete-output validation.

- [cvss/](cvss/)
  > CVSS v4.0 [JSON Schema](https://www.first.org/cvss/cvss-v4.0.json) for validating vector string format and metric enumerations. Keep it as programmatic validation input, use `scripts/calculate_cvss.py` and `scripts/validate_cvss.py` for scoring and output checks rather than adding a query layer.

  > [!NOTE]
  > Does NOT contain scoring data, scores are computed using the [CVSS v4.0 calculator](https://www.first.org/cvss/calculator/4.0).

## 2. References

- GitHub [MITRE ATT&CK](https://github.com/mitre-attack/attack-stix-data) repository.
- GitHub [MITRE CWE](https://github.com/CWE-CAPEC/REST-API-wg) repository.
- GitHub [MITRE EMB3D](https://github.com/mitre/emb3d) repository.
- FIRST [CVSS](https://www.first.org/cvss/data-representations) website.
