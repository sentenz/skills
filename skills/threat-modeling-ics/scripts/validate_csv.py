#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///

"""Validate an entire generated OT/ICS threat-model CSV and report all findings."""

from __future__ import annotations

import argparse
import json
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
MID_PATTERN = re.compile(r"\bMID-\d{3}\b", re.IGNORECASE)
TID_PATTERN = re.compile(r"\bTID-\d{3}\b", re.IGNORECASE)
ATTACK_ID_PATTERN = re.compile(r"T\d{4}(?:\.\d{3})?")
CWE_ID_PATTERN = re.compile(r"CWE-\d+")
CWE_RATIONALE_PATTERN = re.compile(r"\bCWE mapping rationale\s*:", re.IGNORECASE)
MITIGATION_CLAUSE_PATTERN = re.compile(
    r"\b(Basic|Foundational|Intermediate|Leading)(?:\s+mitigation)?\s*:",
    re.IGNORECASE,
)
EMB3D_LEVELS = frozenset({"foundational", "intermediate", "leading"})
CWE_MAPPING_USAGES = frozenset(
    {"Allowed", "Allowed-with-Review", "Discouraged", "Prohibited"}
)
DEFAULT_ATTACK_SOURCE = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "attack"
    / "ics-attack-19.2.json"
)
DEFAULT_CWE_SOURCE = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "cwe"
    / "cwe-4.20.json"
)
DEFAULT_EMB3D_MITIGATIONS = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "emb3d"
    / "mitigations_threat_mappings_2.0.1.json"
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


@dataclass(frozen=True)
class Emb3dMitigation:
    identifier: str
    name: str
    level: str
    threat_ids: frozenset[str]


@dataclass(frozen=True)
class AttackTechnique:
    identifier: str
    name: str
    active: bool


@dataclass(frozen=True)
class CweWeakness:
    identifier: str
    name: str
    abstraction: str
    status: str
    mapping_usage: str


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


def load_attack_techniques(path: Path) -> dict[str, AttackTechnique]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_objects = payload.get("objects") if isinstance(payload, dict) else None
    if not isinstance(raw_objects, list):
        raise ValueError("ATT&CK source must contain an objects list")

    technique_index: dict[str, AttackTechnique] = {}
    for position, item in enumerate(raw_objects, start=1):
        if not isinstance(item, dict) or item.get("type") != "attack-pattern":
            continue

        raw_references = item.get("external_references")
        if not isinstance(raw_references, list):
            continue
        identifiers = {
            str(reference.get("external_id", "")).strip().upper()
            for reference in raw_references
            if isinstance(reference, dict)
            and reference.get("source_name") == "mitre-attack"
            and ATTACK_ID_PATTERN.fullmatch(
                str(reference.get("external_id", "")).strip().upper()
            )
        }
        if not identifiers:
            continue
        if len(identifiers) != 1:
            raise ValueError(
                f"ATT&CK attack-pattern entry {position} has multiple technique ids"
            )

        identifier = next(iter(identifiers))
        name = str(item.get("name", "")).strip()
        if not name:
            raise ValueError(f"ATT&CK technique {identifier} has no name")
        if identifier in technique_index:
            raise ValueError(f"ATT&CK technique id is duplicated: {identifier}")

        technique_index[identifier] = AttackTechnique(
            identifier=identifier,
            name=name,
            active=not bool(
                item.get("revoked", False) or item.get("x_mitre_deprecated", False)
            ),
        )

    if not technique_index:
        raise ValueError("ATT&CK source contains no ICS technique ids")
    return technique_index


def load_cwe_weaknesses(path: Path) -> dict[str, CweWeakness]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    metadata = payload.get("metadata") if isinstance(payload, dict) else None
    raw_weaknesses = payload.get("weaknesses") if isinstance(payload, dict) else None
    if not isinstance(metadata, dict) or not metadata.get("content_version"):
        raise ValueError("CWE source must contain version metadata")
    if not isinstance(raw_weaknesses, list):
        raise ValueError("CWE source must contain a weaknesses list")
    if metadata.get("total_weaknesses") != len(raw_weaknesses):
        raise ValueError("CWE source weakness count differs from its metadata")

    weakness_index: dict[str, CweWeakness] = {}
    for position, item in enumerate(raw_weaknesses, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"CWE weakness entry {position} must be an object")

        identifier = str(item.get("id", "")).strip().upper()
        name = str(item.get("name", "")).strip()
        abstraction = str(item.get("abstraction", "")).strip()
        status = str(item.get("status", "")).strip()
        mapping_notes = item.get("mapping_notes")
        mapping_usage = (
            str(mapping_notes.get("usage", "")).strip()
            if isinstance(mapping_notes, dict)
            else ""
        )
        if not CWE_ID_PATTERN.fullmatch(identifier):
            raise ValueError(f"CWE weakness entry {position} has an invalid id")
        if not name or not abstraction or not status:
            raise ValueError(f"CWE weakness {identifier} has incomplete metadata")
        if mapping_usage not in CWE_MAPPING_USAGES:
            raise ValueError(f"CWE weakness {identifier} has invalid mapping usage")
        if identifier in weakness_index:
            raise ValueError(f"CWE weakness id is duplicated: {identifier}")

        weakness_index[identifier] = CweWeakness(
            identifier=identifier,
            name=name,
            abstraction=abstraction,
            status=status,
            mapping_usage=mapping_usage,
        )

    if not weakness_index:
        raise ValueError("CWE source contains no weakness ids")
    return weakness_index


def _comma_identifiers(value: str) -> list[str]:
    if not value or value.casefold() == "n/a":
        return []
    return [item.strip() for item in value.split(",")]


def validate_attack_mappings(
    value: str,
    *,
    row_number: int,
    threat_id: str,
    technique_index: dict[str, AttackTechnique],
) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[str] = set()
    for raw_identifier in _comma_identifiers(value):
        identifier = raw_identifier.upper()
        if not ATTACK_ID_PATTERN.fullmatch(identifier):
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="ATT&CK ID",
                    message="ATT&CK value is not a canonical ICS technique id",
                    actual=raw_identifier or "<empty item>",
                    expected="TNNNN or TNNNN.NNN",
                )
            )
            continue
        if raw_identifier != identifier:
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="ATT&CK ID",
                    message="ATT&CK technique id must use canonical case",
                    actual=raw_identifier,
                    expected=identifier,
                )
            )
        if identifier in seen:
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="ATT&CK ID",
                    message="ATT&CK technique id is duplicated in the row",
                    actual=identifier,
                    expected="<one occurrence per technique id>",
                )
            )
            continue
        seen.add(identifier)

        technique = technique_index.get(identifier)
        if technique is None:
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="ATT&CK ID",
                    message="ATT&CK technique is absent from the ICS snapshot",
                    actual=identifier,
                    expected="<technique id present in the bundled ICS snapshot>",
                )
            )
        elif not technique.active:
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="ATT&CK ID",
                    message="ATT&CK technique is revoked or deprecated",
                    actual=f"{identifier} ({technique.name})",
                    expected="<active ICS technique>",
                )
            )
    return findings


def validate_cwe_mappings(
    value: str,
    justification: str,
    *,
    row_number: int,
    threat_id: str,
    weakness_index: dict[str, CweWeakness],
) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[str] = set()
    for raw_identifier in _comma_identifiers(value):
        identifier = raw_identifier.upper()
        if not CWE_ID_PATTERN.fullmatch(identifier):
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="CWE ID",
                    message="CWE value is not a canonical weakness id",
                    actual=raw_identifier or "<empty item>",
                    expected="CWE-NNN",
                )
            )
            continue
        if raw_identifier != identifier:
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="CWE ID",
                    message="CWE weakness id must use canonical case",
                    actual=raw_identifier,
                    expected=identifier,
                )
            )
        if identifier in seen:
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="CWE ID",
                    message="CWE weakness id is duplicated in the row",
                    actual=identifier,
                    expected="<one occurrence per weakness id>",
                )
            )
            continue
        seen.add(identifier)

        weakness = weakness_index.get(identifier)
        if weakness is None:
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="CWE ID",
                    message="CWE weakness is absent from the versioned snapshot",
                    actual=identifier,
                    expected="<weakness id present in the bundled CWE snapshot>",
                )
            )
            continue
        if weakness.status == "Deprecated":
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="CWE ID",
                    message="CWE weakness is deprecated",
                    actual=f"{identifier} ({weakness.name})",
                    expected="<active CWE weakness>",
                )
            )
            continue
        if weakness.mapping_usage == "Prohibited":
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="CWE ID",
                    message="CWE mapping usage is Prohibited",
                    actual=f"{identifier} ({weakness.name})",
                    expected="<mappable CWE weakness>",
                )
            )
            continue
        if (
            weakness.mapping_usage in {"Allowed-with-Review", "Discouraged"}
            and not CWE_RATIONALE_PATTERN.search(justification)
        ):
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="Justification",
                    message=(
                        f"{weakness.mapping_usage} CWE mapping requires an explicit "
                        "review rationale"
                    ),
                    actual=f"{identifier} without CWE mapping rationale",
                    expected=(
                        "CWE mapping rationale: <evidence and why no more-specific "
                        "Allowed entry fits>"
                    ),
                )
            )
    return findings


def load_emb3d_mitigations(path: Path) -> dict[str, Emb3dMitigation]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_mitigations = payload.get("mitigations") if isinstance(payload, dict) else None
    if not isinstance(raw_mitigations, list):
        raise ValueError("EMB3D mitigation source must contain a mitigations list")

    mitigation_index: dict[str, Emb3dMitigation] = {}
    for position, item in enumerate(raw_mitigations, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"EMB3D mitigation entry {position} must be an object")

        identifier = str(item.get("id", "")).strip().upper()
        name = str(item.get("name", "")).strip()
        level = str(item.get("level", "")).strip().casefold()
        raw_threats = item.get("threats")
        if not re.fullmatch(r"MID-\d{3}", identifier):
            raise ValueError(f"EMB3D mitigation entry {position} has an invalid id")
        if not name:
            raise ValueError(f"EMB3D mitigation {identifier} has no name")
        if level not in EMB3D_LEVELS:
            raise ValueError(f"EMB3D mitigation {identifier} has an invalid level")
        if not isinstance(raw_threats, list):
            raise ValueError(f"EMB3D mitigation {identifier} has no threats list")

        threat_ids: set[str] = set()
        for threat in raw_threats:
            if not isinstance(threat, dict):
                raise ValueError(f"EMB3D mitigation {identifier} has an invalid threat")
            threat_id = str(threat.get("id", "")).strip().upper()
            if not re.fullmatch(r"TID-\d{3}", threat_id):
                raise ValueError(
                    f"EMB3D mitigation {identifier} has an invalid threat id"
                )
            threat_ids.add(threat_id)

        if identifier in mitigation_index:
            raise ValueError(f"EMB3D mitigation id is duplicated: {identifier}")
        mitigation_index[identifier] = Emb3dMitigation(
            identifier=identifier,
            name=name,
            level=level,
            threat_ids=frozenset(threat_ids),
        )

    return mitigation_index


def _mitigation_clauses(text: str) -> list[tuple[str, int, int, str]]:
    matches = list(MITIGATION_CLAUSE_PATTERN.finditer(text))
    clauses: list[tuple[str, int, int, str]] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        clauses.append((match.group(1).casefold(), start, end, text[start:end].strip()))
    return clauses


def validate_mitigation_citations(
    justification: str,
    tid_value: str,
    *,
    row_number: int,
    threat_id: str,
    mitigation_index: dict[str, Emb3dMitigation],
) -> list[Finding]:
    findings: list[Finding] = []
    clauses = _mitigation_clauses(justification)
    mid_matches = list(MID_PATTERN.finditer(justification))
    row_tids = {match.group().upper() for match in TID_PATTERN.finditer(tid_value)}

    for level, _, _, clause_text in clauses:
        if level != "basic" and not MID_PATTERN.search(clause_text):
            label = level.title()
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="Justification",
                    message="EMB3D mitigation clause has no MID",
                    actual=clause_text,
                    expected=f"{label} mitigation: <exact source name> (MID-NNN)",
                )
            )

    seen_mids: set[str] = set()
    for mid_match in mid_matches:
        identifier = mid_match.group().upper()
        if identifier in seen_mids:
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="Justification",
                    message="MID is cited more than once in the row",
                    actual=identifier,
                    expected="<one source-backed citation per MID>",
                )
            )
            continue
        seen_mids.add(identifier)

        mitigation = mitigation_index.get(identifier)
        if mitigation is None:
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="Justification",
                    message="MID is absent from the EMB3D mitigation source",
                    actual=identifier,
                    expected="<MID present in the bundled EMB3D mitigation source>",
                )
            )
            continue

        clause = next(
            (
                candidate
                for candidate in clauses
                if candidate[1] <= mid_match.start() < candidate[2]
            ),
            None,
        )
        if clause is None:
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="Justification",
                    message="MID is not grouped under an EMB3D mitigation level",
                    actual=identifier,
                    expected=(
                        f"{mitigation.level.title()} mitigation: "
                        f"{mitigation.name} ({identifier})"
                    ),
                )
            )
        else:
            declared_level, _, _, clause_text = clause
            if declared_level == "basic":
                findings.append(
                    Finding(
                        origin="output",
                        row_number=row_number,
                        threat_id=threat_id,
                        column="Justification",
                        message="Basic is product-specific and must not cite an MID",
                        actual=clause_text,
                        expected=(
                            f"{mitigation.level.title()} mitigation: "
                            f"{mitigation.name} ({identifier})"
                        ),
                    )
                )
            elif declared_level != mitigation.level:
                findings.append(
                    Finding(
                        origin="output",
                        row_number=row_number,
                        threat_id=threat_id,
                        column="Justification",
                        message="MID level differs from the EMB3D mitigation source",
                        actual=f"{declared_level.title()} mitigation: {identifier}",
                        expected=(
                            f"{mitigation.level.title()} mitigation: {identifier}"
                        ),
                    )
                )

            if mitigation.name not in clause_text:
                findings.append(
                    Finding(
                        origin="output",
                        row_number=row_number,
                        threat_id=threat_id,
                        column="Justification",
                        message="MID exact source name is missing from its clause",
                        actual=clause_text,
                        expected=(
                            f"{mitigation.level.title()} mitigation: "
                            f"{mitigation.name} ({identifier})"
                        ),
                    )
                )

        if not row_tids:
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="EMB3D TID",
                    message="MID requires a populated EMB3D TID",
                    actual=tid_value or "<blank>",
                    expected="<TID mapped to the cited MID>",
                )
            )
        elif row_tids.isdisjoint(mitigation.threat_ids):
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="EMB3D TID",
                    message="MID is not mapped to any EMB3D TID in the row",
                    actual=f"{identifier} with {', '.join(sorted(row_tids))}",
                    expected=(
                        f"{identifier} with one of "
                        f"{', '.join(sorted(mitigation.threat_ids))}"
                    ),
                )
            )

    return findings


def validate_rows(
    records: list[Record],
    technique_index: Optional[dict[str, AttackTechnique]] = None,
    weakness_index: Optional[dict[str, CweWeakness]] = None,
    mitigation_index: Optional[dict[str, Emb3dMitigation]] = None,
) -> list[Finding]:
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
        justification = (
            justification_cell.value.strip() if justification_cell is not None else ""
        )
        if justification_cell is not None:
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
            if mitigation_index is not None:
                tid_cell = _cell(record, "EMB3D TID")
                tid_value = tid_cell.value.strip() if tid_cell is not None else ""
                findings.extend(
                    validate_mitigation_citations(
                        justification,
                        tid_value,
                        row_number=row_number,
                        threat_id=threat_id,
                        mitigation_index=mitigation_index,
                    )
                )

        if technique_index is not None:
            attack_cell = _cell(record, "ATT&CK ID")
            attack_value = attack_cell.value.strip() if attack_cell is not None else ""
            findings.extend(
                validate_attack_mappings(
                    attack_value,
                    row_number=row_number,
                    threat_id=threat_id,
                    technique_index=technique_index,
                )
            )

        if weakness_index is not None:
            cwe_cell = _cell(record, "CWE ID")
            cwe_value = cwe_cell.value.strip() if cwe_cell is not None else ""
            findings.extend(
                validate_cwe_mappings(
                    cwe_value,
                    justification,
                    row_number=row_number,
                    threat_id=threat_id,
                    weakness_index=weakness_index,
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
    parser.add_argument("--artifact", required=True, help="Generated threat-model CSV")
    parser.add_argument(
        "--source",
        help="Optional raw TMT CSV used to verify the preserved row inventory",
    )
    parser.add_argument(
        "--attack",
        type=Path,
        default=DEFAULT_ATTACK_SOURCE,
        help=(
            "MITRE ATT&CK for ICS STIX JSON used to validate active technique ids "
            "(defaults to the bundled asset)"
        ),
    )
    parser.add_argument(
        "--cwe",
        type=Path,
        default=DEFAULT_CWE_SOURCE,
        help=(
            "Versioned MITRE CWE projection used to validate mappable weakness ids "
            "(defaults to the bundled asset)"
        ),
    )
    parser.add_argument(
        "--emb3d-mitigations",
        type=Path,
        default=DEFAULT_EMB3D_MITIGATIONS,
        help=(
            "EMB3D mitigation-to-threat JSON used to validate MID names, levels, "
            "and row TID associations (defaults to the bundled asset)"
        ),
    )
    args = parser.parse_args()

    output_path = Path(args.artifact).expanduser()
    source_path = Path(args.source).expanduser() if args.source else None
    attack_path = args.attack.expanduser()
    cwe_path = args.cwe.expanduser()
    mitigation_path = args.emb3d_mitigations.expanduser()
    if not output_path.is_file():
        print(f"ERROR: CSV file not found: {output_path}", file=sys.stderr)
        return 2
    if source_path is not None and not source_path.is_file():
        print(f"ERROR: source CSV file not found: {source_path}", file=sys.stderr)
        return 2
    if not attack_path.is_file():
        print(f"ERROR: ATT&CK source not found: {attack_path}", file=sys.stderr)
        return 2
    if not cwe_path.is_file():
        print(f"ERROR: CWE source not found: {cwe_path}", file=sys.stderr)
        return 2
    if not mitigation_path.is_file():
        print(
            f"ERROR: EMB3D mitigation source not found: {mitigation_path}",
            file=sys.stderr,
        )
        return 2

    findings: list[Finding] = []
    try:
        technique_index = load_attack_techniques(attack_path)
        weakness_index = load_cwe_weaknesses(cwe_path)
        mitigation_index = load_emb3d_mitigations(mitigation_path)
        output_records = read_records(
            output_path,
            origin="output",
            findings=findings,
        )
        findings.extend(validate_header(output_records))
        findings.extend(
            validate_rows(
                output_records,
                technique_index=technique_index,
                weakness_index=weakness_index,
                mitigation_index=mitigation_index,
            )
        )

        source_records: Optional[list[Record]] = None
        if source_path is not None:
            source_records = read_source_records(source_path, findings)
            findings.extend(validate_source(output_records, source_records))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print_report(findings, output_records, source_records)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
