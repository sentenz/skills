# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "cvss==3.6",
# ]
# ///

"""
Validate a CVSS vector and emit a compact JSON result.

Usage:

    Run the script from the skill directory:

    ```bash
    python ./scripts/calculate_cvss.py \
    --vector 'CVSS:4.0/AV:P/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N'
    ```

    Output:

    ```plaintext
    {"ok":true,"version":"4.0","vector":"CVSS:4.0/AV:P/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N","score":5.3,"severity":"Medium"}
    ```

    Request the complete score tuple and schema-compatible CVSS representation
    when required:

    ```bash
    python ./scripts/calculate_cvss.py \
    --details \
    --vector 'CVSS:4.0/AV:P/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N'
    ```
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Mapping, Union

from cvss import CVSS2, CVSS3, CVSS4, CVSSError

CVSSObject = Union[CVSS2, CVSS3, CVSS4]


def emit_json(payload: Mapping[str, object]) -> None:
    """Write one compact JSON object to stdout."""
    json.dump(
        payload,
        sys.stdout,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    sys.stdout.write("\n")


class JsonArgumentParser(argparse.ArgumentParser):
    """Argument parser that reports usage errors as JSON."""

    def error(self, message: str) -> None:
        """Emit a structured argument error and terminate with status 2."""
        emit_json(
            {
                "ok": False,
                "error": {
                    "type": "ArgumentError",
                    "message": message,
                },
            }
        )
        raise SystemExit(2)


def parse_vector(vector: str) -> tuple[str, CVSSObject]:
    """Parse a CVSS v2, v3, or v4 vector.

    CVSS v3 and v4 vectors must include their standard ``CVSS:x.y/``
    prefix. CVSS v2 vectors are accepted in their standard unprefixed
    form.

    Args:
        vector: Non-empty CVSS vector string.

    Returns:
        A tuple containing the normalized version and parsed CVSS object.

    Raises:
        ValueError: If the prefix declares an unsupported CVSS version.
        CVSSError: If the vector is malformed or incomplete.
    """
    if vector.startswith("CVSS:4.0/"):
        return "4.0", CVSS4(vector)

    if vector.startswith(("CVSS:3.0/", "CVSS:3.1/")):
        version = vector.split("/", 1)[0].removeprefix("CVSS:")
        return version, CVSS3(vector)

    if vector.startswith("CVSS:"):
        prefix = vector.split("/", 1)[0]
        raise ValueError(
            f'Unsupported CVSS prefix "{prefix}". '
            "Supported versions are 2.0, 3.0, 3.1, and 4.0; "
            "CVSS v2 vectors must omit the prefix."
        )

    return "2.0", CVSS2(vector)


def main() -> int:
    """Validate one CVSS vector and emit its normalized score data."""
    parser = JsonArgumentParser(
        description=("Validate a CVSS v2, v3, or v4 vector and return JSON."),
        epilog=(
            "CVSS v3 and v4 vectors require their CVSS:x.y prefix; "
            "CVSS v2 vectors are unprefixed."
        ),
    )
    parser.add_argument(
        "--vector",
        required=True,
        help="CVSS vector string",
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help=("include version-specific scores and " "schema-compatible CVSS data"),
    )
    args = parser.parse_args()

    vector = args.vector.strip()
    if not vector:
        emit_json(
            {
                "ok": False,
                "error": {
                    "type": "ArgumentError",
                    "message": "--vector must not be empty.",
                },
            }
        )
        return 2

    try:
        version, cvss = parse_vector(vector)
        scores = cvss.scores()
        severities = cvss.severities()

        result: dict[str, object] = {
            "ok": True,
            "version": version,
            "vector": cvss.clean_vector(),
            "score": scores[0],
            "severity": severities[0],
        }

        if args.details:
            result.update(
                {
                    "scores": list(scores),
                    "severities": list(severities),
                    "cvss": cvss.as_json(minimal=True),
                }
            )

        emit_json(result)
        return 0

    except (CVSSError, ValueError) as exc:
        emit_json(
            {
                "ok": False,
                "error": {
                    "type": type(exc).__name__,
                    "message": str(exc),
                },
            }
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
