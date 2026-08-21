#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///

"""Validate an entire generated OT/ICS threat-model CSV and report all findings."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

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
MAX_DIFF_LENGTH = 500


@dataclass(frozen=True)
class Cell:
    value: str
    quoted: bool


@dataclass(frozen=True)
class Record:
    cells: tuple[Cell, ...]


@dataclass(frozen=True)
class Finding:
    origin: str
    row_number: Optional[int]
    threat_id: str
    column: str
    message: str
    actual: str
    expected: str


def values(record: Record) -> tuple[str, ...]:
    return tuple(cell.value for cell in record.cells)


def _record_row(records: list[Record]) -> int:
    return len(records) + 1


def parse_records(
    text: str,
    delimiter: str = ";",
    *,
    origin: str = "output",
    findings: Optional[list[Finding]] = None,
) -> list[Record]:
    """Parse all CSV content and recover from local syntax defects."""

    if len(delimiter) != 1:
        raise ValueError("delimiter must be one character")
    if findings is None:
        findings = []
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
        if not record_touched and not row and not value and not quoted:
            return
        push_cell()
        records.append(Record(tuple(row)))
        row = []
        record_touched = False

    def add_syntax_finding(message: str, actual: str, expected: str) -> None:
        findings.append(
            Finding(
                origin=origin,
                row_number=_record_row(records),
                threat_id="",
                column=f"Field {len(row) + 1}",
                message=message,
                actual=actual,
                expected=expected,
            )
        )

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
            if char == delimiter:
                push_cell()
                record_touched = True
                index += 1
                continue
            add_syntax_finding(
                "unexpected character after closing quote",
                char,
                f"{delimiter!r} or a record terminator",
            )
            state = "unquoted"
            value.append(char)
            record_touched = True
            index += 1
            continue

        if char == delimiter:
            push_cell()
            record_touched = True
        elif char == '"':
            if state == "start" and not value:
                state = "quoted"
                quoted = True
            else:
                add_syntax_finding(
                    "unexpected quote in an unquoted field",
                    char,
                    'a doubled quote inside a field enclosed by double quotes',
                )
                state = "unquoted"
                value.append(char)
            record_touched = True
        else:
            state = "unquoted"
            value.append(char)
            record_touched = True
        index += 1

    if state == "quoted":
        add_syntax_finding(
            "unterminated quoted field",
            "<end of file>",
            'closing double quote (")',
        )
    if row or value or quoted or record_touched:
        push_record()
    return records


def read_records(
    path: Path,
    *,
    origin: str,
    findings: list[Finding],
    delimiter: str = ";",
) -> list[Record]:
    return parse_records(
        path.read_text(encoding="utf-8-sig"),
        delimiter,
        origin=origin,
        findings=findings,
    )


def read_source_records(path: Path, findings: list[Finding]) -> list[Record]:
    text = path.read_text(encoding="utf-8-sig")
    best_records: list[Record] = []
    best_findings: list[Finding] = []
    best_score = -1

    for delimiter in (";", ",", "\t"):
        candidate_findings: list[Finding] = []
        candidate_records = parse_records(
            text,
            delimiter,
            origin="source",
            findings=candidate_findings,
        )
        header = values(candidate_records[0]) if candidate_records else ()
        score = sum(column in header for column in PRESERVED_NATIVE_COLUMNS)
        if score > best_score:
            best_records = candidate_records
            best_findings = candidate_findings
            best_score = score

    findings.extend(best_findings)
    if best_score < len(PRESERVED_NATIVE_COLUMNS):
        actual_header = (
            ";".join(values(best_records[0])) if best_records else "<missing>"
        )
        findings.append(
            Finding(
                origin="source",
                row_number=1,
                threat_id="",
                column="Header",
                message="native TMT delimiter or header could not be identified",
                actual=actual_header,
                expected=(
                    "semicolon-, comma-, or tab-delimited header containing "
                    + ", ".join(PRESERVED_NATIVE_COLUMNS)
                ),
            )
        )
    return best_records


def validate_header(records: list[Record]) -> list[Finding]:
    findings: list[Finding] = []
    if not records:
        return [
            Finding(
                origin="output",
                row_number=1,
                threat_id="",
                column="Header",
                message="CSV is empty",
                actual="<missing>",
                expected=";".join(EXPECTED_COLUMNS),
            )
        ]

    actual = values(records[0])
    if len(actual) != len(EXPECTED_COLUMNS):
        findings.append(
            Finding(
                origin="output",
                row_number=1,
                threat_id="",
                column="Header column count",
                message="header column count differs from the Output Contract",
                actual=str(len(actual)),
                expected=str(len(EXPECTED_COLUMNS)),
            )
        )

    for index in range(max(len(actual), len(EXPECTED_COLUMNS))):
        actual_name = actual[index] if index < len(actual) else "<missing>"
        expected_name = (
            EXPECTED_COLUMNS[index] if index < len(EXPECTED_COLUMNS) else "<no column>"
        )
        if actual_name != expected_name:
            findings.append(
                Finding(
                    origin="output",
                    row_number=1,
                    threat_id="",
                    column=f"Header[{index + 1}]",
                    message="header name or position differs from the Output Contract",
                    actual=actual_name,
                    expected=expected_name,
                )
            )
    return findings


def _cell(record: Record, column: str) -> Optional[Cell]:
    index = EXPECTED_COLUMNS.index(column)
    return record.cells[index] if index < len(record.cells) else None


def _quoted_value(value: str) -> str:
    return f'"{value.replace(chr(34), chr(34) * 2)}"'


def _expected_score(value: str) -> str:
    try:
        score = float(value.replace(",", "."))
    except ValueError:
        return "<score from 0,0 through 10,0 using one comma-decimal place>"
    if not 0.0 <= score <= 10.0:
        return "<score from 0,0 through 10,0 using one comma-decimal place>"
    return f"{score:.1f}".replace(".", ",")


def validate_rows(records: list[Record]) -> list[Finding]:
    findings: list[Finding] = []
    if not records:
        return findings

    seen_ids: set[str] = set()
    for row_number, record in enumerate(records[1:], start=2):
        id_cell = _cell(record, "Id")
        threat_id = id_cell.value.strip() if id_cell is not None else ""

        if len(record.cells) != len(EXPECTED_COLUMNS):
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="Field count",
                    message="row width differs from the Output Contract",
                    actual=str(len(record.cells)),
                    expected=str(len(EXPECTED_COLUMNS)),
                )
            )

        if id_cell is not None:
            if not threat_id:
                findings.append(
                    Finding(
                        origin="output",
                        row_number=row_number,
                        threat_id="",
                        column="Id",
                        message="Id must not be blank",
                        actual=id_cell.value,
                        expected="<unique source-row Id>",
                    )
                )
            elif threat_id in seen_ids:
                findings.append(
                    Finding(
                        origin="output",
                        row_number=row_number,
                        threat_id=threat_id,
                        column="Id",
                        message="Id is duplicated",
                        actual=threat_id,
                        expected="<unique source-row Id not used by another row>",
                    )
                )
            if threat_id:
                seen_ids.add(threat_id)

        for column in QUOTED_COLUMNS:
            cell = _cell(record, column)
            if cell is not None and not cell.quoted:
                findings.append(
                    Finding(
                        origin="output",
                        row_number=row_number,
                        threat_id=threat_id,
                        column=column,
                        message=f"{column} must be enclosed in double quotes",
                        actual=cell.value,
                        expected=_quoted_value(cell.value),
                    )
                )

        justification_cell = _cell(record, "Justification")
        if justification_cell is not None:
            justification = justification_cell.value.strip()
            if ";" in justification:
                findings.append(
                    Finding(
                        origin="output",
                        row_number=row_number,
                        threat_id=threat_id,
                        column="Justification",
                        message="Justification must not contain semicolons",
                        actual=justification,
                        expected=justification.replace(";", ","),
                    )
                )
            if justification and IDENTIFIER_ONLY_PATTERN.fullmatch(justification):
                findings.append(
                    Finding(
                        origin="output",
                        row_number=row_number,
                        threat_id=threat_id,
                        column="Justification",
                        message="Justification must not be identifier-only",
                        actual=justification,
                        expected="<structured narrative rationale>",
                    )
                )

        score_cell = _cell(record, "CVSS-B v4.0 Score")
        if score_cell is not None:
            score = score_cell.value.strip()
            if (
                score
                and score.casefold() not in {"n/a", "none"}
                and not SCORE_PATTERN.fullmatch(score)
            ):
                findings.append(
                    Finding(
                        origin="output",
                        row_number=row_number,
                        threat_id=threat_id,
                        column="CVSS-B v4.0 Score",
                        message="score must use one comma-decimal place",
                        actual=score,
                        expected=_expected_score(score),
                    )
                )

        state_cell = _cell(record, "State")
        treatment_cell = _cell(record, "Risk Treatment")
        approval_cell = _cell(record, "Risk Approval")
        state = state_cell.value.strip() if state_cell is not None else ""
        treatment = treatment_cell.value.strip() if treatment_cell is not None else ""
        approval = approval_cell.value.strip() if approval_cell is not None else ""

        if state in {"Not Started", "Needs Investigation"}:
            if treatment_cell is not None and treatment:
                findings.append(
                    Finding(
                        origin="output",
                        row_number=row_number,
                        threat_id=threat_id,
                        column="Risk Treatment",
                        message=f"{state} requires blank Risk Treatment",
                        actual=treatment,
                        expected="<blank>",
                    )
                )
            if approval_cell is not None and approval:
                findings.append(
                    Finding(
                        origin="output",
                        row_number=row_number,
                        threat_id=threat_id,
                        column="Risk Approval",
                        message=f"{state} requires blank Risk Approval",
                        actual=approval,
                        expected="<blank>",
                    )
                )
        elif state == "Not Applicable":
            if treatment_cell is not None and treatment != "Avoidance":
                findings.append(
                    Finding(
                        origin="output",
                        row_number=row_number,
                        threat_id=threat_id,
                        column="Risk Treatment",
                        message="Not Applicable requires Avoidance treatment",
                        actual=treatment,
                        expected="Avoidance",
                    )
                )
            for column in IDENTIFIER_COLUMNS:
                cell = _cell(record, column)
                if cell is not None and cell.value.strip() != "N/A":
                    findings.append(
                        Finding(
                            origin="output",
                            row_number=row_number,
                            threat_id=threat_id,
                            column=column,
                            message=f"{column} must be N/A when Not Applicable",
                            actual=cell.value.strip(),
                            expected="N/A",
                        )
                    )
        elif (
            state == "Mitigated"
            and treatment_cell is not None
            and treatment not in {"Mitigation", "Acceptance", "Transfer"}
        ):
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="Risk Treatment",
                    message="Mitigated uses an incompatible treatment",
                    actual=treatment,
                    expected="Mitigation, Acceptance, or Transfer",
                )
            )

    return findings


def validate_source(
    output_records: list[Record],
    source_records: list[Record],
) -> list[Finding]:
    findings: list[Finding] = []
    if not source_records:
        return [
            Finding(
                origin="source",
                row_number=1,
                threat_id="",
                column="CSV",
                message="source CSV is empty",
                actual="<missing>",
                expected="<native TMT header and source rows>",
            )
        ]

    source_header = values(source_records[0])
    source_index = {name: index for index, name in enumerate(source_header)}
    missing = [
        column for column in PRESERVED_NATIVE_COLUMNS if column not in source_index
    ]
    for column in missing:
        findings.append(
            Finding(
                origin="source",
                row_number=1,
                threat_id="",
                column=column,
                message="required native source column is missing",
                actual="<missing>",
                expected=column,
            )
        )

    id_index = source_index.get("Id")
    source_by_id: dict[str, Record] = {}
    source_ids: list[str] = []
    for row_number, record in enumerate(source_records[1:], start=2):
        threat_id = (
            record.cells[id_index].value
            if id_index is not None and id_index < len(record.cells)
            else ""
        )
        if len(record.cells) != len(source_header):
            findings.append(
                Finding(
                    origin="source",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="Field count",
                    message="source row width differs from its header",
                    actual=str(len(record.cells)),
                    expected=str(len(source_header)),
                )
            )
        if id_index is None or id_index >= len(record.cells):
            continue
        if threat_id in source_by_id:
            findings.append(
                Finding(
                    origin="source",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="Id",
                    message="source Id is duplicated",
                    actual=threat_id,
                    expected="<unique source-row Id>",
                )
            )
        else:
            source_by_id[threat_id] = record
        source_ids.append(threat_id)

    output_ids = [
        record.cells[0].value
        for record in output_records[1:]
        if record.cells
    ]
    if output_ids != source_ids:
        findings.append(
            Finding(
                origin="output",
                row_number=None,
                threat_id="",
                column="Id sequence",
                message="output Id sequence differs from the source-row inventory",
                actual=", ".join(output_ids),
                expected=", ".join(source_ids),
            )
        )

    output_index = {name: index for index, name in enumerate(EXPECTED_COLUMNS)}
    comparable_columns = [
        column for column in PRESERVED_NATIVE_COLUMNS if column in source_index
    ]
    for row_number, record in enumerate(output_records[1:], start=2):
        if not record.cells:
            continue
        threat_id = record.cells[0].value
        source = source_by_id.get(threat_id)
        if source is None:
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="Id",
                    message="output Id has no corresponding source row",
                    actual=threat_id,
                    expected="<Id present in the source CSV>",
                )
            )
            continue
        for column in comparable_columns:
            output_column = output_index[column]
            source_column = source_index[column]
            if output_column >= len(record.cells) or source_column >= len(source.cells):
                continue
            output_value = record.cells[output_column].value
            source_value = source.cells[source_column].value
            if output_value != source_value:
                findings.append(
                    Finding(
                        origin="output",
                        row_number=row_number,
                        threat_id=threat_id,
                        column=column,
                        message="preserved native field differs from the source",
                        actual=output_value,
                        expected=source_value,
                    )
                )
    return findings


def _display(value: str, limit: int = MAX_DIFF_LENGTH) -> str:
    rendered = value.replace("\r", "\\r").replace("\n", "\\n")
    if not rendered:
        return "<blank>"
    if len(rendered) <= limit:
        return rendered
    return f"{rendered[: limit - 3]}..."


def print_report(
    findings: list[Finding],
    output_records: list[Record],
    source_records: Optional[list[Record]],
) -> None:
    affected = {
        (finding.origin, finding.row_number)
        for finding in findings
        if finding.row_number is not None
    }
    separator = "=" * 34
    print(separator)
    print("Output Contract Validation Report")
    print(separator)
    print(f"Output rows     : {max(len(output_records) - 1, 0)}")
    if source_records is not None:
        print(f"Source rows     : {max(len(source_records) - 1, 0)}")
    print(f"Findings       : {len(findings)}")
    print(f"Affected rows  : {len(affected)}")
    print(separator)

    if not findings:
        print("\nNo findings.")
        return

    print()
    print("No.  Scope   Row    Id            Column                    Finding")
    print("-" * 96)
    for number, finding in enumerate(findings, start=1):
        row = str(finding.row_number) if finding.row_number is not None else "-"
        threat_id = finding.threat_id or "-"
        print(
            f"{number:>3}  {finding.origin:<6}  {row:>4}  "
            f"{threat_id[:12]:<12}  {finding.column[:24]:<24}  "
            f"{finding.message}"
        )

    print("\n--- Findings diff ---")
    for number, finding in enumerate(findings, start=1):
        row = str(finding.row_number) if finding.row_number is not None else "file"
        threat_id = finding.threat_id or "<unknown>"
        print(
            f"\n@@ finding {number}: {finding.origin}:{row} "
            f"Id {threat_id} [{finding.column}] @@"
        )
        print(f"  {finding.message}")
        print(f"- {_display(finding.actual)}")
        print(f"+ {_display(finding.expected)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate an entire generated OT/ICS threat-model CSV and report "
            "all findings with actual/expected diffs."
        )
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

    findings: list[Finding] = []
    try:
        output_records = read_records(
            output_path,
            origin="output",
            findings=findings,
        )
        findings.extend(validate_header(output_records))
        findings.extend(validate_rows(output_records))

        source_records: Optional[list[Record]] = None
        if source_path is not None:
            source_records = read_source_records(source_path, findings)
            findings.extend(validate_source(output_records, source_records))
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print_report(findings, output_records, source_records)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
