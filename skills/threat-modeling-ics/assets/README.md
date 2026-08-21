# `assets/`

- [1. Details](#1-details)
- [2. References](#2-references)

## 1. Details

- [attack/](attack/)
  > MITRE ATT&CK for ICS 19.2 STIX snapshot from the [ATT&CK STIX dataset](https://github.com/mitre-attack/attack-stix-data/blob/master/ics-attack/ics-attack-19.2.json). Contains techniques, tactics, mitigations, relationships, and lifecycle flags. **Used to validate** active technique IDs when populating the `ATT&CK ID` column.

- [cwe/](cwe/)
  > Versioned MITRE CWE 4.20 projection derived from the [CWE JSON API](https://github.com/CWE-CAPEC/REST-API-wg/tree/main/json_repo). Contains all weakness IDs plus abstraction, status, mapping notes, relationships, candidate mitigations, and selected discovery views. Treat it as programmatic input only: use `scripts/query_cwe.py` for bounded lookup and `scripts/validate_output.py` for complete-output validation.

- [emb3d/](emb3d/)
  > MITRE EMB3D JSON data files derived from the [EMB3D knowledge base](https://github.com/mitre/emb3d/tree/main/_data). Contains threat IDs, device properties, threat actions, and mitigation levels. **Used to look up** threat details when populating the `EMB3D TID` column.

- [cvss/](cvss/)
  > CVSS v4.0 [JSON Schema](https://www.first.org/cvss/cvss-v4.0.json) for validating vector string format and metric enumerations. **Used to validate** that recorded vector, score, and severity fields are well-formed when populating the `CVSS v4.0` columns.

  > [!NOTE]
  > Does NOT contain scoring data, scores are computed using the [CVSS v4.0 calculator](https://www.first.org/cvss/calculator/4.0).

## 2. References

- GitHub [MITRE ATT&CK](https://github.com/mitre-attack/attack-stix-data) repository.
- GitHub [MITRE CWE](https://github.com/CWE-CAPEC/REST-API-wg) repository.
- GitHub [MITRE EMB3D](https://github.com/mitre/emb3d) repository.
- FIRST [CVSS](https://www.first.org/cvss/data-representations) website.
