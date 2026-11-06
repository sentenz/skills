# `scripts/`

- [1. Details](#1-details)
- [2. References](#2-references)

## 1. Details

Run the examples from the `tm7-threat-model/` skill directory. Both scripts use only the
Python standard library. The commands follow the repository's `uv run` convention;
replace `uv run` with `python -B` to use an existing Python installation directly.

- [validate_tm7.py](validate_tm7.py)
  > Validates Core TM7 serialization structure, namespace bindings, catalog identifiers, UUIDs, serializer identities, connector endpoints, threat interactions, and property values against a trusted Core export. Prints `PASS` with model counts or `FAIL` with findings for each file. Returns exit code `0` when all files pass and `1` when any file fails.

    ```bash
    uv run ./scripts/validate_tm7.py ./assets/example-minimal.tm7
    uv run ./scripts/validate_tm7.py ./references/core-worked-example.tm7 ./references/Example_Threat_Model.tm7
    uv run ./scripts/validate_tm7.py model.tm7 --template original.tm7
    ```

    The default template is `assets/example-minimal.tm7`, containing SDL TM Knowledge
    Base (Core) `4.1.0.11`. Use `--template` with an unchanged, trusted Core export when
    validating edits against another catalog. Catalog comparison excludes the knowledge
    base object's serializer ID; serializer IDs are checked separately for uniqueness.

    These are static consistency checks. The script does not evaluate threat-generation
    expressions, prove architecture coverage, or perform an application open/save check.
    Enclosing trust boundaries are supported; trust-line boundary serialization requires
    a populated Core export and is reported as unsupported by this checker.

- [test_validate_tm7.py](test_validate_tm7.py)
  > Runs 23 regression tests covering the bundled Core models, documentation fragments, and deliberately corrupted models. Checks the worked request/response pair's directionality, labels, properties, and facing inset anchors and opposing handles; the populated model's directional names, matching threat labels, and integer attachment and handle geometry; acceptance of a single one-way flow; and rejection of broken references, unsupported identifiers and properties, namespace errors, fractional connector coordinates, invalid lists, inconsistent threats, changed catalog content, and malformed member order. Prints the standard unittest summary and returns a nonzero exit code on failure.

    ```bash
    uv run ./scripts/test_validate_tm7.py
    ```

    Tests write temporary fixtures and remove them after each check. Set `TM7_TEST_TMP`
    to an existing writable directory if the environment restricts its default temporary
    directory. The tests preserve the bundled assets.

## 2. References

- [Skill instructions](../SKILL.md).
- [Minimal Core export](../assets/example-minimal.tm7), the default validation template.
- [Populated Core reference](../references/Example_Threat_Model.tm7).
- [Core XML examples](../references/core-xml-examples.md) and [connected worked model](../references/core-worked-example.tm7).
- [TMT Style Guide](../references/tmt-style-guide.md) for manual size, connection geometry, layout, and naming checks.
