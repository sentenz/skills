#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "cvss==3.6",
# ]
# ///

"""Validate stored CVSS v4.0 values in a threat-model CSV."""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

COL_ID = "Id"
COL_TITLE = "Title"
COL_VECTOR = "CVSS v4.0 Vector"
COL_STORED_SCORE = "CVSS-B v4.0 Score"
COL_STORED_SEV = "CVSS v4.0 Severity"

REQUIRED_COLUMNS = (
    COL_ID,
    COL_TITLE,
    COL_VECTOR,
    COL_STORED_SCORE,
    COL_STORED_SEV,
)

SCORE_EPSILON = 0.0001
DEFAULT_TIMEOUT_SECONDS = 30.0
MAX_DIAGNOSTIC_LENGTH = 500
DEFAULT_VALIDATOR_PATH = Path(__file__).resolve().with_name("calculate_cvss.py")

ValidationStatus = Literal["PASS", "FAIL", "ERROR", "SKIP"]


@dataclass(frozen=True)
class ValidationResult:
    row_number: int
    threat_id: str
    title: str
    vector: str
    stored_score: float | None
    computed_score: float | None
    stored_severity: str
    computed_severity: str
    status: ValidationStatus
    error: str | None


def _cell(row: Mapping[str, str | None], column: str) -> str:
    value = row.get(column)
    return value.strip() if value is not None else ""


def _normalise_score(raw: str | None) -> float | None:
    if raw is None:
        return None

    value = raw.strip()
    if not value or value.casefold() in {"n/a", "none"}:
        return None

    try:
        score = float(value.replace(",", "."))
    except ValueError as exc:
        raise ValueError(f"invalid score {raw!r}") from exc

    if not math.isfinite(score):
        raise ValueError(f"score must be finite, got {raw!r}")
    if not 0.0 <= score <= 10.0:
        raise ValueError(f"score must be between 0.0 and 10.0, got {score}")

    return score


def _coerce_computed_score(raw: object) -> float:
    if isinstance(raw, bool):
        raise ValueError("validator returned a Boolean score")

    score = _normalise_score(None if raw is None else str(raw))
    if score is None:
        raise ValueError("validator returned no score")
    return score


def _truncate(text: str, limit: int = MAX_DIAGNOSTIC_LENGTH) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3]}..."


def _process_diagnostic(result: subprocess.CompletedProcess[str]) -> str:
    parts: list[str] = []
    if result.returncode != 0:
        parts.append(f"exit code {result.returncode}")
    if result.stderr.strip():
        parts.append(f"stderr: {_truncate(result.stderr)}")
    return "; ".join(parts)


def _payload_error(payload: dict[str, object]) -> str:
    raw_error = payload.get("error")

    if isinstance(raw_error, dict):
        error_type = str(raw_error.get("type") or "").strip()
        message = str(raw_error.get("message") or "").strip()
        detail = ": ".join(part for part in (error_type, message) if part)
        return detail or "validator rejected the vector"

    if raw_error is not None:
        detail = str(raw_error).strip()
        if detail:
            return detail

    return "validator rejected the vector"


def _validate_one_vector(
    vector: str,
    validator_path: Path,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> tuple[float | None, str | None, str | None]:
    try:
        result = subprocess.run(
            [sys.executable, str(validator_path), "--vector", vector],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None, None, f"validator timed out after {timeout_seconds:g} seconds"
    except OSError as exc:
        return None, None, f"could not start validator: {exc}"

    if not result.stdout.strip():
        diagnostic = _process_diagnostic(result)
        message = "validator produced no JSON output"
        return None, None, f"{message}; {diagnostic}" if diagnostic else message

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        diagnostic = _process_diagnostic(result)
        message = f"invalid validator JSON: {exc}"
        return None, None, f"{message}; {diagnostic}" if diagnostic else message

    if not isinstance(payload, dict):
        return None, None, "validator JSON root must be an object"

    if payload.get("ok") is not True:
        message = _payload_error(payload)
        diagnostic = _process_diagnostic(result)
        return None, None, f"{message}; {diagnostic}" if diagnostic else message

    if result.returncode != 0:
        diagnostic = _process_diagnostic(result)
        return None, None, f"validator reported success but returned {diagnostic}"

    try:
        score = _coerce_computed_score(payload.get("score"))
    except ValueError as exc:
        return None, None, str(exc)

    raw_severity = payload.get("severity")
    severity = str(raw_severity).strip() if raw_severity is not None else ""
    if not severity:
        return None, None, "validator returned no severity"

    return score, severity, None


def validate_csv(
    csv_path: Path,
    validator_path: Path,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> list[ValidationResult]:
    results: list[ValidationResult] = []

    with csv_path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh, delimiter=";")

        if reader.fieldnames is None:
            raise ValueError("CSV has no header row")

        duplicate_columns = sorted(
            column
            for column in set(reader.fieldnames)
            if reader.fieldnames.count(column) > 1
        )
        if duplicate_columns:
            raise ValueError(
                "CSV contains duplicate columns: " + ", ".join(duplicate_columns)
            )

        missing_columns = [
            column for column in REQUIRED_COLUMNS if column not in reader.fieldnames
        ]
        if missing_columns:
            raise ValueError(
                "CSV is missing required columns: " + ", ".join(missing_columns)
            )

        for row_number, row in enumerate(reader, start=2):
            threat_id = _cell(row, COL_ID)
            title = _cell(row, COL_TITLE)
            vector = _cell(row, COL_VECTOR)
            raw_score = _cell(row, COL_STORED_SCORE)
            stored_severity = _cell(row, COL_STORED_SEV)

            if not any((threat_id, title, vector, raw_score, stored_severity)):
                continue

            if not vector or vector.casefold() == "n/a":
                results.append(
                    ValidationResult(
                        row_number=row_number,
                        threat_id=threat_id,
                        title=title,
                        vector=vector,
                        stored_score=None,
                        computed_score=None,
                        stored_severity=stored_severity,
                        computed_severity="N/A",
                        status="SKIP",
                        error=None,
                    )
                )
                continue

            input_errors: list[str] = []
            try:
                stored_score = _normalise_score(raw_score)
            except ValueError as exc:
                stored_score = None
                input_errors.append(str(exc))

            computed_score, computed_severity, validator_error = _validate_one_vector(
                vector,
                validator_path,
                timeout_seconds,
            )
            if validator_error:
                input_errors.append(validator_error)

            if input_errors:
                results.append(
                    ValidationResult(
                        row_number=row_number,
                        threat_id=threat_id,
                        title=title,
                        vector=vector,
                        stored_score=stored_score,
                        computed_score=computed_score,
                        stored_severity=stored_severity,
                        computed_severity=computed_severity or "",
                        status="ERROR",
                        error="; ".join(input_errors),
                    )
                )
                continue

            issues: list[str] = []
            if stored_score is None:
                issues.append("stored score is missing")
            elif computed_score is None:
                issues.append("computed score is missing")
            elif not math.isclose(
                stored_score,
                computed_score,
                rel_tol=0.0,
                abs_tol=SCORE_EPSILON,
            ):
                issues.append(
                    f"score mismatch ({stored_score:g} vs {computed_score:g})"
                )

            if not stored_severity:
                issues.append("stored severity is missing")
            elif computed_severity is None:
                issues.append("computed severity is missing")
            elif stored_severity.casefold() != computed_severity.casefold():
                issues.append(
                    f"severity mismatch ({stored_severity} vs {computed_severity})"
                )

            results.append(
                ValidationResult(
                    row_number=row_number,
                    threat_id=threat_id,
                    title=title,
                    vector=vector,
                    stored_score=stored_score,
                    computed_score=computed_score,
                    stored_severity=stored_severity,
                    computed_severity=computed_severity or "",
                    status="FAIL" if issues else "PASS",
                    error="; ".join(issues) if issues else None,
                )
            )

    return results


def _format_score(score: float | None) -> str:
    return f"{score:.1f}" if score is not None else "N/A"


def print_report(results: list[ValidationResult]) -> None:
    counts = {
        status: sum(result.status == status for result in results)
        for status in ("SKIP", "PASS", "FAIL", "ERROR")
    }

    separator = "=" * 24
    print(separator)
    print("CVSS Validation Report")
    print(separator)
    print(f"Total threats : {len(results)}")
    print(f"Skipped (N/A) : {counts['SKIP']}")
    print(f"Passed         : {counts['PASS']}")
    print(f"Failed         : {counts['FAIL']}")
    print(f"Errors         : {counts['ERROR']}")
    print(separator)
    print()

    if not results:
        print("No data rows found.")
        return

    headers = (
        "Row",
        "Id",
        "Stored",
        "Computed",
        "Stored Sev",
        "Computed Sev",
        "Status",
        "Issue",
    )
    table_rows = [
        (
            str(result.row_number),
            result.threat_id,
            _format_score(result.stored_score),
            _format_score(result.computed_score),
            result.stored_severity,
            result.computed_severity,
            result.status,
            result.error or "",
        )
        for result in results
    ]

    widths = [
        max(len(headers[index]), *(len(row[index]) for row in table_rows))
        for index in range(len(headers) - 1)
    ]
    right_aligned = {0, 2, 3}

    def format_row(row: tuple[str, ...]) -> str:
        cells = []
        for index, width in enumerate(widths):
            alignment = ">" if index in right_aligned else "<"
            cells.append(f"{row[index]:{alignment}{width}}")
        cells.append(row[-1])
        return "  ".join(cells)

    print(format_row(headers))
    print("-" * len(format_row(headers)))
    for row in table_rows:
        print(format_row(row))

    problems = [result for result in results if result.status in {"FAIL", "ERROR"}]
    if not problems:
        return

    print("\n--- Details for FAIL/ERROR entries ---\n")
    for result in problems:
        print(
            f"  Row {result.row_number}, Id {result.threat_id or '<missing>'}: {result.title}"
        )
        print(f"    Vector  : {result.vector}")
        print(
            "    Stored  : "
            f"score={_format_score(result.stored_score)}, "
            f"severity={result.stored_severity or '<missing>'}"
        )
        print(
            "    Computed: "
            f"score={_format_score(result.computed_score)}, "
            f"severity={result.computed_severity or '<missing>'}"
        )
        if result.error:
            print(f"    Issue   : {result.error}")
        print()


def _positive_float(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate CVSS vectors in a threat-model CSV."
    )
    parser.add_argument("--csv", required=True, help="Path to the threat-model CSV")
    parser.add_argument(
        "--validator",
        default=DEFAULT_VALIDATOR_PATH,
        help="Path to calculate_cvss.py (default: sibling script)",
    )
    parser.add_argument(
        "--timeout",
        type=_positive_float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Validator timeout in seconds (default: {DEFAULT_TIMEOUT_SECONDS:g})",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv).expanduser()
    validator_path = Path(args.validator).expanduser()

    if not csv_path.is_file():
        print(f"ERROR: CSV file not found: {csv_path}", file=sys.stderr)
        return 2
    if not validator_path.is_file():
        print(f"ERROR: Validator script not found: {validator_path}", file=sys.stderr)
        return 2

    try:
        results = validate_csv(csv_path, validator_path, args.timeout)
    except (OSError, csv.Error, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print_report(results)

    has_failures = any(result.status in {"FAIL", "ERROR"} for result in results)
    return 1 if has_failures else 0


if __name__ == "__main__":
    sys.exit(main())
