#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///

"""Validate the generated OT/ICS threat-model CSV output contract."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

EXPECTED_COLUMNS = (
    "Id",
    "Title",
    "Category",
    "Diagram",
    "Interaction",
    "Priority",
    "State",
    "Changed By",
    "Description",
    "Justification",
    "Last Modified",
    "ATT&CK ID",
    "EMB3D TID",
    "CWE ID",
    "CVSS v4.0 Vector",
    "CVSS-B v4.0 Score",
    "CVSS v4.0 Severity",
    "Likelihood of Exploit",
    "Risk Prioritization",
    "Threat Actor",
    "Risk Treatment",
    "Risk Approval",
)

PRESERVED_NATIVE_COLUMNS = (
    "Id",
    "Title",
    "Category",
    "Diagram",
    "Interaction",
    "Changed By",
    "Description",
    "Last Modified",
)

IDENTIFIER_COLUMNS = ("ATT&CK ID", "EMB3D TID", "CWE ID")
QUOTED_COLUMNS = ("Description", "Justification")
SCORE_PATTERN = re.compile(r"^(?:[0-9],[0-9]|10,0)$")
IDENTIFIER_ONLY_PATTERN = re.compile(
    r"^\s*(?:N/?A|(?:ATT&CK|TID|CWE|MID)[- :0-9.,]+|\([^)]*\))\s*$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Cell:
    value: str
    quoted: bool


@dataclass(frozen=True)
class Record:
    cells: tuple[Cell, ...]


class CSVContractError(ValueError):
    """Raised when the semicolon-delimited CSV cannot be parsed canonically."""


def parse_records(text: str, delimiter: str = ";") -> list[Record]:
    """Parse delimited CSV while retaining whether fields were quoted."""

    if len(delimiter) != 1:
        raise ValueError("delimiter must be one character")

    if text.startswith("\ufeff"):
        text = text[1:]

    records: list[Record] = []
    row: list[Cell] = []
    value: list[str] = []
    state = "start"
    quoted = False
    record_touched = False
    index = 0

    def push_cell() -> None:
        nonlocal value, quoted, state
        row.append(Cell("".join(value), quoted))
        value = []
        quoted = False
        state = "start"

    def push_record() -> None:
        nonlocal row, record_touched
        push_cell()
        records.append(Record(tuple(row)))
        row = []
        record_touched = False

    while index < len(text):
        char = text[index]
        newline_width = 0
        if char == "\n":
            newline_width = 1
        elif char == "\r" and index + 1 < len(text) and text[index + 1] == "\n":
            newline_width = 2
        elif char == "\r":
            newline_width = 1

        if state == "quoted":
            if char == '"':
                if index + 1 < len(text) and text[index + 1] == '"':
                    value.append('"')
                    index += 2
                    continue
                state = "after_quote"
            else:
                value.append(char)
            index += 1
            continue

        if newline_width:
            push_record()
            index += newline_width
            continue

        if state == "after_quote":
            if char != delimiter:
                raise CSVContractError(
                    f"unexpected character after closing quote at offset {index}"
                )
            push_cell()
            record_touched = True
            index += 1
            continue

        if char == delimiter:
            push_cell()
            record_touched = True
        elif char == '"':
            if state != "start" or value:
                raise CSVContractError(f"unexpected quote at offset {index}")
            state = "quoted"
            quoted = True
            record_touched = True
        else:
            state = "unquoted"
            value.append(char)
            record_touched = True
        index += 1

    if state == "quoted":
        raise CSVContractError("unterminated quoted field")
    if row or value or quoted or record_touched:
        push_record()
    return records


def read_records(path: Path) -> list[Record]:
    return parse_records(path.read_text(encoding="utf-8-sig"))


def read_source_records(path: Path) -> list[Record]:
    text = path.read_text(encoding="utf-8-sig")
    for delimiter in (";", ",", "\t"):
        try:
            records = parse_records(text, delimiter)
        except CSVContractError:
            continue
        if records and all(
            column in values(records[0]) for column in PRESERVED_NATIVE_COLUMNS
        ):
            return records
    raise CSVContractError(
        f"{path}: could not detect a semicolon-, comma-, or tab-delimited "
        "native TMT header"
    )


def values(record: Record) -> tuple[str, ...]:
    return tuple(cell.value for cell in record.cells)


def validate_header(records: list[Record], path: Path) -> list[str]:
    if not records:
        return [f"{path}: CSV is empty"]
    actual = values(records[0])
    if actual == EXPECTED_COLUMNS:
        return []
    return [
        f"{path}: header must exactly match the {len(EXPECTED_COLUMNS)}-column "
        "Output Contract"
    ]


def validate_rows(records: list[Record], path: Path) -> list[str]:
    errors: list[str] = []
    if not records or values(records[0]) != EXPECTED_COLUMNS:
        return errors

    indexes = {name: index for index, name in enumerate(EXPECTED_COLUMNS)}
    seen_ids: set[str] = set()

    for row_number, record in enumerate(records[1:], start=2):
        if len(record.cells) != len(EXPECTED_COLUMNS):
            errors.append(
                f"{path}:{row_number}: expected {len(EXPECTED_COLUMNS)} fields, "
                f"found {len(record.cells)}"
            )
            continue

        row = {name: record.cells[index] for name, index in indexes.items()}
        threat_id = row["Id"].value.strip()
        prefix = f"{path}:{row_number} (Id {threat_id or '<blank>'})"

        if not threat_id:
            errors.append(f"{prefix}: Id must not be blank")
        elif threat_id in seen_ids:
            errors.append(f"{prefix}: duplicate Id")
        seen_ids.add(threat_id)

        for column in QUOTED_COLUMNS:
            if not row[column].quoted:
                errors.append(f"{prefix}: {column} must be enclosed in double quotes")

        justification = row["Justification"].value.strip()
        if ";" in justification:
            errors.append(f"{prefix}: Justification must not contain semicolons")
        if justification and IDENTIFIER_ONLY_PATTERN.fullmatch(justification):
            errors.append(f"{prefix}: Justification must not be identifier-only")

        score = row["CVSS-B v4.0 Score"].value.strip()
        if score and score.casefold() not in {"n/a", "none"}:
            if not SCORE_PATTERN.fullmatch(score):
                errors.append(
                    f"{prefix}: CVSS-B v4.0 Score must use one comma-decimal "
                    "place, for example 0,0 or 5,2"
                )

        state = row["State"].value.strip()
        treatment = row["Risk Treatment"].value.strip()
        approval = row["Risk Approval"].value.strip()
        if state in {"Not Started", "Needs Investigation"}:
            if treatment or approval:
                errors.append(
                    f"{prefix}: {state} requires blank Risk Treatment and Risk Approval"
                )
        elif state == "Not Applicable":
            if treatment != "Avoidance":
                errors.append(
                    f"{prefix}: Not Applicable requires Avoidance treatment"
                )
            for column in IDENTIFIER_COLUMNS:
                if row[column].value.strip() != "N/A":
                    errors.append(f"{prefix}: {column} must be N/A when Not Applicable")
        elif state == "Mitigated" and treatment not in {
            "Mitigation",
            "Acceptance",
            "Transfer",
        }:
            errors.append(
                f"{prefix}: Mitigated requires Mitigation, Acceptance, or Transfer"
            )

    return errors


def validate_source(
    output_records: list[Record], source_records: list[Record], source_path: Path
) -> list[str]:
    errors: list[str] = []
    if not output_records or values(output_records[0]) != EXPECTED_COLUMNS:
        return errors
    if not source_records:
        return [f"{source_path}: source CSV is empty"]

    source_header = values(source_records[0])
    missing = [
        column for column in PRESERVED_NATIVE_COLUMNS if column not in source_header
    ]
    if missing:
        return [f"{source_path}: missing native columns: {', '.join(missing)}"]

    output_index = {name: index for index, name in enumerate(EXPECTED_COLUMNS)}
    source_index = {name: index for index, name in enumerate(source_header)}
    source_by_id: dict[str, Record] = {}
    source_ids: list[str] = []

    for row_number, record in enumerate(source_records[1:], start=2):
        if len(record.cells) != len(source_header):
            errors.append(
                f"{source_path}:{row_number}: expected {len(source_header)} fields, "
                f"found {len(record.cells)}"
            )
            continue
        threat_id = record.cells[source_index["Id"]].value
        if threat_id in source_by_id:
            errors.append(f"{source_path}:{row_number}: duplicate Id {threat_id!r}")
        source_by_id[threat_id] = record
        source_ids.append(threat_id)

    output_ids = [
        record.cells[output_index["Id"]].value
        for record in output_records[1:]
        if len(record.cells) == len(EXPECTED_COLUMNS)
    ]
    if output_ids != source_ids:
        errors.append("output Id sequence must exactly match the source-row inventory")

    for row_number, record in enumerate(output_records[1:], start=2):
        if len(record.cells) != len(EXPECTED_COLUMNS):
            continue
        threat_id = record.cells[output_index["Id"]].value
        source = source_by_id.get(threat_id)
        if source is None:
            continue
        for column in PRESERVED_NATIVE_COLUMNS:
            output_value = record.cells[output_index[column]].value
            source_value = source.cells[source_index[column]].value
            if output_value != source_value:
                errors.append(
                    f"output:{row_number} (Id {threat_id}): preserved field "
                    f"{column!r} differs from source"
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a generated OT/ICS threat-model CSV."
    )
    parser.add_argument("--csv", required=True, help="Generated threat-model CSV")
    parser.add_argument(
        "--source",
        help="Optional raw TMT CSV used to verify the preserved row inventory",
    )
    args = parser.parse_args()

    output_path = Path(args.csv).expanduser()
    source_path = Path(args.source).expanduser() if args.source else None
    if not output_path.is_file():
        print(f"ERROR: CSV file not found: {output_path}", file=sys.stderr)
        return 2
    if source_path is not None and not source_path.is_file():
        print(f"ERROR: source CSV file not found: {source_path}", file=sys.stderr)
        return 2

    try:
        output_records = read_records(output_path)
        errors = validate_header(output_records, output_path)
        errors.extend(validate_rows(output_records, output_path))
        if source_path is not None:
            errors.extend(
                validate_source(
                    output_records, read_source_records(source_path), source_path
                )
            )
    except (OSError, CSVContractError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if errors:
        print("Output Contract validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"PASS: {output_path} satisfies the Output Contract "
        f"({max(len(output_records) - 1, 0)} threat rows)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
