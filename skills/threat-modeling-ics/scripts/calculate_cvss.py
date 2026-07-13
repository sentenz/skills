#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "cvss==3.6",
# ]
# ///
"""Calculate and normalize CVSS vectors for agentic workflows.

The command is intentionally non-interactive. Structured results are written to
stdout; diagnostics and argument errors are written to stderr.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable, Sequence

from cvss import CVSS2, CVSS3, CVSS4

SUPPORTED_VERSIONS = ("auto", "2.0", "3.0", "3.1", "4.0")


@dataclass(frozen=True)
class VectorInput:
    vector: str
    source: str
    line: int | None = None


class VectorVersionError(ValueError):
    """Raised when a vector version cannot be determined safely."""


def _json_value(value: Any) -> Any:
    """Convert library values into JSON-safe primitives."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


def _strip_cvss2_prefix(vector: str) -> str:
    prefix = "CVSS:2.0/"
    return vector[len(prefix) :] if vector.upper().startswith(prefix) else vector


def _detect_version(vector: str, requested: str) -> tuple[str, str]:
    """Return (version, vector accepted by the selected library class)."""
    value = vector.strip()
    upper = value.upper()

    explicit: str | None = None
    if upper.startswith("CVSS:4.0/"):
        explicit = "4.0"
    elif upper.startswith("CVSS:3.1/"):
        explicit = "3.1"
    elif upper.startswith("CVSS:3.0/"):
        explicit = "3.0"
    elif upper.startswith("CVSS:2.0/"):
        explicit = "2.0"

    if requested != "auto":
        if explicit is not None and explicit != requested:
            raise VectorVersionError(
                f"Vector prefix declares CVSS {explicit}, but --version {requested} was requested."
            )
        version = requested
    elif explicit is not None:
        version = explicit
    elif "AU:" in upper:
        # Authentication (Au) is a mandatory CVSS v2 metric and is not used by v3/v4.
        version = "2.0"
    else:
        raise VectorVersionError(
            "Cannot safely detect a prefixless vector version. CVSS 3.x and 4.0 "
            "share metric abbreviations. Add the CVSS prefix or pass --version."
        )

    if version == "2.0":
        return version, _strip_cvss2_prefix(value)

    required_prefix = f"CVSS:{version}/"
    if not upper.startswith(required_prefix):
        value = required_prefix + value.lstrip("/")
    return version, value


def _score_names(version: str) -> tuple[str, ...]:
    if version == "2.0":
        return ("base", "temporal", "environmental")
    if version in ("3.0", "3.1"):
        return ("base", "temporal", "environmental")
    return ("overall",)


def _calculate(
    item: VectorInput,
    requested_version: str,
    include_metrics: bool,
) -> dict[str, Any]:
    raw = item.vector.strip()
    if not raw:
        raise ValueError("Vector is empty.")

    version, normalized_input = _detect_version(raw, requested_version)
    calculator_class = {
        "2.0": CVSS2,
        "3.0": CVSS3,
        "3.1": CVSS3,
        "4.0": CVSS4,
    }[version]

    calculator = calculator_class(normalized_input)
    score_values = tuple(_json_value(value) for value in calculator.scores())
    severity_values = tuple(str(value) for value in calculator.severities())
    names = _score_names(version)

    scores = {name: score_values[index] for index, name in enumerate(names)}
    severities = {name: severity_values[index] for index, name in enumerate(names)}

    # CVSS 2 may omit Temporal or Environmental groups. Report the most specific
    # available score as the final score; later CVSS versions return their final
    # score directly through the last group or sole value.
    valid_indices = [
        index for index, value in enumerate(score_values) if value is not None
    ]
    if not valid_indices:
        raise ValueError("The CVSS library did not return a score for this vector.")
    final_index = valid_indices[-1]

    result: dict[str, Any] = {
        "ok": True,
        "input_vector": raw,
        "version": version,
        "canonical_vector": calculator.clean_vector(),
        "score": score_values[final_index],
        "severity": severity_values[final_index],
        "scores": scores,
        "severities": severities,
        "source": item.source,
    }
    if item.line is not None:
        result["line"] = item.line

    if include_metrics:
        original_metrics = getattr(calculator, "original_metrics", None)
        metrics = (
            original_metrics if original_metrics is not None else calculator.metrics
        )
        result["metrics"] = _json_value(metrics)

    return result


def _hint_for_error(exc: Exception) -> str:
    text = str(exc).lower()
    if isinstance(exc, VectorVersionError):
        return "Use a complete CVSS prefix or pass --version with the intended standard."
    if "mandatory" in text or "missing" in text:
        return "Supply every mandatory Base metric required by the selected CVSS version."
    if "unknown metric" in text:
        return "Check metric names and ensure the vector belongs to the selected CVSS version."
    if "invalid metric value" in text or "invalid value" in text:
        return "Check each metric value against the selected CVSS specification."
    if "duplicate" in text:
        return "Remove duplicate metric entries from the vector."
    return (
        "Run with --help, verify the vector syntax, and preserve the "
        "standard metric separators."
    )


def _error_record(item: VectorInput, exc: Exception) -> dict[str, Any]:
    record: dict[str, Any] = {
        "ok": False,
        "input_vector": item.vector.strip(),
        "source": item.source,
        "error": {
            "type": type(exc).__name__,
            "message": str(exc),
            "hint": _hint_for_error(exc),
        },
    }
    if item.line is not None:
        record["line"] = item.line
    return record


def _iter_lines(stream: Iterable[str], source: str) -> Iterable[VectorInput]:
    for number, line in enumerate(stream, start=1):
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        yield VectorInput(vector=value, source=source, line=number)


def _read_inputs(args: argparse.Namespace) -> list[VectorInput]:
    items = [VectorInput(vector=value, source="argument") for value in args.vectors]

    for filename in args.input:
        path = Path(filename)
        try:
            with path.open("r", encoding="utf-8") as handle:
                items.extend(_iter_lines(handle, str(path)))
        except OSError as exc:
            raise OSError(
                f'Cannot read input file "{path}": {exc.strerror or exc}'
            ) from exc

    should_read_stdin = args.stdin or (not items and not sys.stdin.isatty())
    if should_read_stdin:
        items.extend(_iter_lines(sys.stdin, "stdin"))

    if not items:
        raise ValueError(
            "No CVSS vectors were provided. Pass vectors as arguments, use --input, "
            "or pipe one vector per line on stdin."
        )
    return items


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="calculate_cvss.py",
        description=(
            "Validate, normalize, and calculate CVSS 2.0, 3.0, 3.1, or 4.0 vectors. "
            "Results are emitted as structured JSON."
        ),
        epilog=(
            "Examples:\n"
            "  uv run scripts/calculate_cvss.py "
            "'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'\n"
            "  uv run scripts/calculate_cvss.py --version 3.1 "
            "'AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'\n"
            "  uv run scripts/calculate_cvss.py "
            "--input vectors.txt --format jsonl\n"
            "  cat vectors.txt | uv run scripts/calculate_cvss.py --format jsonl"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "vectors",
        nargs="*",
        help="CVSS vector string(s) to calculate.",
    )
    parser.add_argument(
        "--input",
        "-i",
        action="append",
        default=[],
        metavar="FILE",
        help="Read one vector per line from FILE. May be supplied multiple times.",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Also read one vector per line from stdin.",
    )
    parser.add_argument(
        "--version",
        choices=SUPPORTED_VERSIONS,
        default="auto",
        help="Force a CVSS version for prefixless input (default: auto).",
    )
    parser.add_argument(
        "--format",
        choices=("json", "jsonl"),
        default="json",
        help="Output format (default: json).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Indent JSON output. Ignored for JSON Lines.",
    )
    parser.add_argument(
        "--include-metrics",
        action="store_true",
        help="Include parsed metric abbreviations and values in successful records.",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help=(
            "Stop after the first invalid vector instead of processing "
            "the remaining inputs."
        ),
    )
    return parser


def _emit(
    records: Sequence[dict[str, Any]],
    output_format: str,
    pretty: bool,
) -> None:
    if output_format == "jsonl":
        for record in records:
            print(json.dumps(record, sort_keys=True, separators=(",", ":")))
        return

    payload: Any = records[0] if len(records) == 1 else list(records)
    print(json.dumps(payload, indent=2 if pretty else None, sort_keys=True))


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        items = _read_inputs(args)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    records: list[dict[str, Any]] = []
    failures = 0
    for item in items:
        try:
            records.append(
                _calculate(item, args.version, args.include_metrics)
            )
        except Exception as exc:
            # The library exposes several version-specific errors.
            failures += 1
            records.append(_error_record(item, exc))
            if args.fail_fast:
                break

    _emit(records, args.format, args.pretty)
    if failures:
        print(
            f"CVSS validation failed for {failures} vector(s).",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
