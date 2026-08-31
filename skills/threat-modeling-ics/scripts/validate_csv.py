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
AMBIGUOUS_BASIC_CONTROL_PATTERN = re.compile(
    r"\bBasic\s+(?:mitigation|controls?)\b|\bBasic\s*:", re.IGNORECASE
)
CONTROL_CLAUSE_PATTERN = re.compile(
    r"\b(?:(?P<boundary>Implemented|Compensating)\s+controls?"
    r"|EMB3D\s+(?P<level>Foundational|Intermediate|Leading)\s+mitigation)\s*:",
    re.IGNORECASE,
)
MID_IMPLEMENTATION_CLAIM_PATTERN = re.compile(
    r"\b(?:is|are|was|were|has been|have been)\s+"
    r"(?:implemented|enforced|enabled)\b"
    r"|\bimplementation status\s*:\s*implemented\b",
    re.IGNORECASE,
)
DEVICE_SPECIFIC_EVIDENCE_PATTERN = re.compile(
    r"\bDevice-specific evidence\s*:", re.IGNORECASE
)
BOUNDARY_CONTROL_EVIDENCE_PATTERN = re.compile(
    r"\b(?:Implemented|Compensating)\s+controls?\s*:\s*\S", re.IGNORECASE
)
RESIDUAL_RISK_EVIDENCE_PATTERN = re.compile(
    r"\bResidual\s+risk\s+(?:is|remains?)\s+"
    r"(?:None|Info|Low|Medium|High|Critical)\b",
    re.IGNORECASE,
)
RISK_OWNER_EVIDENCE_PATTERN = re.compile(
    r"\b(?:owns?\s+the\s+residual\s+risk|residual[- ]risk\s+owner|"
    r"risk\s+owner|approving\s+stakeholder|responsible\s+stakeholder)\b",
    re.IGNORECASE,
)
APPROVAL_MECHANISM_EVIDENCE_PATTERN = re.compile(
    r"\b(?:records?|documents?|grants?|provides?)\s+(?:explicit\s+)?approval\b"
    r"[^.]{0,160}\b(?:through|in|via|under|by)\b|\bapproval\s+mechanism\b",
    re.IGNORECASE,
)
ACCEPTANCE_RATIONALE_EVIDENCE_PATTERN = re.compile(
    r"\bTreatment\s+is\s+Acceptance\s+because\b", re.IGNORECASE
)
ACCEPTANCE_THRESHOLD_EVIDENCE_PATTERN = re.compile(
    r"\b(?:(?:acceptance|risk|retention)\s+threshold|risk\s+appetite|"
    r"risk\s+tolerance|"
    r"documented\s+(?:None|Info|Low|Medium|High|Critical)\s+threshold)\b",
    re.IGNORECASE,
)
TRANSFER_PARTY_EVIDENCE_PATTERN = re.compile(
    r"\b(?:third\s+party|vendor|supplier|provider|insurer|contractor|"
    r"managed\s+service)\b|\bTreatment\s+is\s+Transfer\s+(?:to|with)\s+"
    r"[A-Z][\w&.-]+(?:\s+[A-Z][\w&.-]+){0,3}\b",
    re.IGNORECASE,
)
TRANSFER_INSTRUMENT_EVIDENCE_PATTERN = re.compile(
    r"\b(?:contract|SLA|warranty|insurance(?:\s+policy)?|managed\s+service)\b",
    re.IGNORECASE,
)
TRANSFER_SCOPE_EVIDENCE_PATTERN = re.compile(
    r"\b(?:transfer(?:red|s)?|shift(?:ed|s)?|share(?:d|s)?|delegat(?:ed|es)?)\b"
    r"[^.]{0,160}\b(?:risk|exposure|impact|consequence|scope)\b|"
    r"\b(?:risk|exposure|impact|consequence|scope)\b[^.]{0,160}"
    r"\b(?:transfer(?:red|s)?|shift(?:ed|s)?|share(?:d|s)?|delegat(?:ed|es)?)\b",
    re.IGNORECASE,
)
AVOIDANCE_CONTEXT_EVIDENCE_PATTERN = re.compile(
    r"\b(?:architectur(?:al|e)|design|record|decision|interface|element|"
    r"component|capability|function|data\s+flow|attack\s+path|risk\s+source|"
    r"mechanism)\b",
    re.IGNORECASE,
)
AVOIDANCE_OUTCOME_EVIDENCE_PATTERN = re.compile(
    r"\b(?:eliminat(?:e|ed|es)|remov(?:e|ed)|impossible|absent|"
    r"unavailable|no\s+longer\s+present|outside(?:\s+the)?\s+scope|"
    r"does\s+not\s+apply|no\s+(?:mechanism|network\s+stack|attack\s+path))\b",
    re.IGNORECASE,
)
EMB3D_LEVELS = frozenset({"foundational", "intermediate", "leading"})
CWE_MAPPING_USAGES = frozenset(
    {"Allowed", "Allowed-with-Review", "Discouraged", "Prohibited"}
)
RISK_LEVELS = ("Info", "Low", "Medium", "High", "Critical")
CVSS_SEVERITIES = ("None", "Low", "Medium", "High", "Critical")
RISK_MATRIX = {
    "Info": {
        "None": "Info",
        "Low": "Info",
        "Medium": "Low",
        "High": "Low",
        "Critical": "Medium",
    },
    "Low": {
        "None": "Info",
        "Low": "Low",
        "Medium": "Low",
        "High": "Medium",
        "Critical": "High",
    },
    "Medium": {
        "None": "Low",
        "Low": "Low",
        "Medium": "Medium",
        "High": "High",
        "Critical": "High",
    },
    "High": {
        "None": "Low",
        "Low": "Medium",
        "Medium": "High",
        "High": "High",
        "Critical": "Critical",
    },
    "Critical": {
        "None": "Medium",
        "Low": "High",
        "Medium": "High",
        "High": "Critical",
        "Critical": "Critical",
    },
}
RISK_TREATMENTS = ("Avoidance", "Mitigation", "Acceptance", "Transfer")
RISK_TREATMENT_GUIDANCE = {
    "Info": ("Avoidance", "Acceptance"),
    "Low": ("Acceptance", "Avoidance", "Mitigation"),
    "Medium": ("Mitigation", "Acceptance", "Transfer"),
    "High": ("Mitigation", "Avoidance", "Transfer", "Acceptance"),
    "Critical": ("Avoidance", "Mitigation", "Transfer", "Acceptance"),
}
DEFAULT_RISK_TREATMENTS = {
    "Info": "Avoidance",
    "Low": "Acceptance",
    "Medium": "Mitigation",
    "High": "Mitigation",
    "Critical": "Avoidance",
}
STATE_RISK_TREATMENTS = {
    "Not Applicable": ("Avoidance",),
    "Mitigated": ("Mitigation", "Acceptance", "Transfer"),
}
RISK_APPROVAL_ROLES = (
    "Not Required",
    "Product Security",
    "Lead Security",
    "CPSO",
    "Executive",
)
RISK_APPROVAL_MATRIX = {
    "Info": {
        "Avoidance": "Not Required",
        "Mitigation": "Product Security",
        "Acceptance": "Product Security",
        "Transfer": "Product Security",
    },
    "Low": {
        "Avoidance": "Not Required",
        "Mitigation": "Product Security",
        "Acceptance": "Product Security",
        "Transfer": "Product Security",
    },
    "Medium": {
        "Avoidance": "Not Required",
        "Mitigation": "Lead Security",
        "Acceptance": "Lead Security",
        "Transfer": "Lead Security",
    },
    "High": {
        "Avoidance": "Not Required",
        "Mitigation": "CPSO",
        "Acceptance": "CPSO",
        "Transfer": "CPSO",
    },
    "Critical": {
        "Avoidance": "Not Required",
        "Mitigation": "Executive",
        "Acceptance": "Executive",
        "Transfer": "Executive",
    },
}
UNFINISHED_STATES = frozenset({"Not Started", "Needs Investigation"})
FINALIZED_STATES = frozenset(STATE_RISK_TREATMENTS)
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
    matches = list(CONTROL_CLAUSE_PATTERN.finditer(text))
    clauses: list[tuple[str, int, int, str]] = []
    for index, match in enumerate(matches):
        level = match.group("level")
        if level is None:
            continue
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        clauses.append((level.casefold(), start, end, text[start:end].strip()))
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
        if not MID_PATTERN.search(clause_text):
            label = level.title()
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="Justification",
                    message="EMB3D mitigation clause has no MID",
                    actual=clause_text,
                    expected=(
                        f"EMB3D {label} mitigation: <exact source name> (MID-NNN)"
                    ),
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
                        f"EMB3D {mitigation.level.title()} mitigation: "
                        f"{mitigation.name} ({identifier})"
                    ),
                )
            )
        else:
            declared_level, _, _, clause_text = clause
            if declared_level != mitigation.level:
                findings.append(
                    Finding(
                        origin="output",
                        row_number=row_number,
                        threat_id=threat_id,
                        column="Justification",
                        message="MID level differs from the EMB3D mitigation source",
                        actual=(
                            f"EMB3D {declared_level.title()} mitigation: {identifier}"
                        ),
                        expected=(
                            f"EMB3D {mitigation.level.title()} mitigation: {identifier}"
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
                        f"EMB3D {mitigation.level.title()} mitigation: "
                        f"{mitigation.name} ({identifier})"
                    ),
                )
            )

            if (
                MID_IMPLEMENTATION_CLAIM_PATTERN.search(clause_text)
                and not DEVICE_SPECIFIC_EVIDENCE_PATTERN.search(clause_text)
            ):
                findings.append(
                    Finding(
                        origin="output",
                        row_number=row_number,
                        threat_id=threat_id,
                        column="Justification",
                        message=(
                            "MID implementation claim lacks device-specific evidence"
                        ),
                        actual=clause_text,
                        expected=(
                            "Device-specific evidence: <design, configuration, test, "
                            "or verified behavior evidence>"
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


def _option_list(options: tuple[str, ...]) -> str:
    if len(options) == 1:
        return options[0]
    return f"{', '.join(options[:-1])}, or {options[-1]}"


def validate_treatment_evidence(
    justification: str,
    *,
    state: str,
    treatment: str,
    prioritization: Optional[str],
    row_number: int,
    threat_id: str,
) -> list[Finding]:
    """Validate explicit treatment-evidence markers in Justification."""

    findings: list[Finding] = []

    def require(pattern: re.Pattern[str], message: str, expected: str) -> None:
        if pattern.search(justification) is None:
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="Justification",
                    message=message,
                    actual=justification,
                    expected=expected,
                )
            )

    if treatment == "Avoidance":
        if not (
            AVOIDANCE_CONTEXT_EVIDENCE_PATTERN.search(justification)
            and AVOIDANCE_OUTCOME_EVIDENCE_PATTERN.search(justification)
        ):
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="Justification",
                    message="Avoidance lacks an architectural elimination decision",
                    actual=justification,
                    expected=(
                        "<architectural record or design decision identifying the "
                        "eliminated risk source or attack path>"
                    ),
                )
            )
        return findings

    if state != "Mitigated":
        return findings

    require(
        BOUNDARY_CONTROL_EVIDENCE_PATTERN,
        "Mitigated treatment lacks enforcement-boundary control evidence",
        (
            "Implemented controls: <within-boundary controls> or "
            "Compensating controls: <outside-boundary controls>"
        ),
    )
    require(
        RESIDUAL_RISK_EVIDENCE_PATTERN,
        "Mitigated treatment lacks a standardized residual-risk level",
        "Residual risk is <None, Info, Low, Medium, High, or Critical>",
    )

    default_treatment = (
        DEFAULT_RISK_TREATMENTS.get(prioritization)
        if prioritization is not None
        else None
    )
    decision_kind = "alternative " if treatment != default_treatment else ""
    if treatment != "Acceptance":
        decision_pattern = re.compile(
            rf"\bTreatment\s+is\s+{re.escape(treatment)}\s+"
            rf"(?:because|through|via|under|to)\b",
            re.IGNORECASE,
        )
        require(
            decision_pattern,
            f"{decision_kind}Risk Treatment lacks a documented decision rationale",
            f"Treatment is {treatment} <because or through supporting evidence>",
        )

    if treatment == "Mitigation":
        require(
            RISK_OWNER_EVIDENCE_PATTERN,
            "Mitigation lacks a residual-risk owner",
            "<stakeholder> owns the residual risk",
        )
        require(
            APPROVAL_MECHANISM_EVIDENCE_PATTERN,
            "Mitigation lacks an approval mechanism",
            "<stakeholder> records approval through <mechanism>",
        )
    elif treatment == "Acceptance":
        require(
            ACCEPTANCE_RATIONALE_EVIDENCE_PATTERN,
            f"{decision_kind}Acceptance lacks a business rationale",
            "Treatment is Acceptance because <business rationale>",
        )
        require(
            ACCEPTANCE_THRESHOLD_EVIDENCE_PATTERN,
            "Acceptance lacks an acceptance threshold",
            "<documented risk threshold, appetite, or tolerance>",
        )
        require(
            RISK_OWNER_EVIDENCE_PATTERN,
            "Acceptance lacks an approving stakeholder",
            "<approving stakeholder> owns the residual risk",
        )
        require(
            APPROVAL_MECHANISM_EVIDENCE_PATTERN,
            "Acceptance lacks an explicit approval mechanism",
            "<stakeholder> records approval through <mechanism>",
        )
    elif treatment == "Transfer":
        require(
            TRANSFER_PARTY_EVIDENCE_PATTERN,
            "Transfer lacks a named third party",
            "<named third party responsible for the transferred risk scope>",
        )
        require(
            TRANSFER_INSTRUMENT_EVIDENCE_PATTERN,
            "Transfer lacks a specific transfer instrument",
            "<contract, SLA, warranty, insurance policy, or managed service>",
        )
        require(
            TRANSFER_SCOPE_EVIDENCE_PATTERN,
            "Transfer lacks an explicit risk scope",
            "<risk, exposure, impact, or consequence shifted to the third party>",
        )

    return findings


def validate_risk_governance(
    record: Record,
    *,
    row_number: int,
    threat_id: str,
) -> list[Finding]:
    """Validate risk priority, treatment, and approval mapping rules for a row."""

    findings: list[Finding] = []
    row_values = {
        column: (cell.value.strip() if (cell := _cell(record, column)) else "")
        for column in (
            "State",
            "CVSS v4.0 Severity",
            "Likelihood of Exploit",
            "Risk Prioritization",
            "Risk Treatment",
            "Risk Approval",
            "Justification",
        )
    }
    state = row_values["State"]
    severity = row_values["CVSS v4.0 Severity"]
    likelihood = row_values["Likelihood of Exploit"]
    prioritization = row_values["Risk Prioritization"]
    treatment = row_values["Risk Treatment"]
    approval = row_values["Risk Approval"]
    justification = row_values["Justification"]

    if state in UNFINISHED_STATES:
        for column, value in (
            ("Risk Prioritization", prioritization),
            ("Risk Treatment", treatment),
            ("Risk Approval", approval),
        ):
            if value:
                findings.append(
                    Finding(
                        origin="output",
                        row_number=row_number,
                        threat_id=threat_id,
                        column=column,
                        message=f"{state} requires blank {column}",
                        actual=value,
                        expected="<blank>",
                    )
                )
        return findings

    requires_completed_risk = state in FINALIZED_STATES
    severity_valid = severity in CVSS_SEVERITIES
    likelihood_valid = likelihood in RISK_LEVELS

    if requires_completed_risk and not severity_valid:
        findings.append(
            Finding(
                origin="output",
                row_number=row_number,
                threat_id=threat_id,
                column="CVSS v4.0 Severity",
                message="finalized row has no valid risk-matrix impact",
                actual=severity,
                expected=_option_list(CVSS_SEVERITIES),
            )
        )
    if requires_completed_risk and not likelihood_valid:
        findings.append(
            Finding(
                origin="output",
                row_number=row_number,
                threat_id=threat_id,
                column="Likelihood of Exploit",
                message="finalized row has no valid risk-matrix probability",
                actual=likelihood,
                expected=_option_list(RISK_LEVELS),
            )
        )

    expected_priority: Optional[str] = None
    if severity_valid and likelihood_valid:
        expected_priority = RISK_MATRIX[likelihood][severity]
        if prioritization != expected_priority:
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="Risk Prioritization",
                    message="Risk Prioritization differs from the risk matrix",
                    actual=prioritization,
                    expected=expected_priority,
                )
            )
    elif prioritization not in RISK_LEVELS and (
        prioritization or requires_completed_risk
    ):
        findings.append(
            Finding(
                origin="output",
                row_number=row_number,
                threat_id=threat_id,
                column="Risk Prioritization",
                message="Risk Prioritization is not a standardized risk level",
                actual=prioritization,
                expected=_option_list(RISK_LEVELS),
            )
        )

    if expected_priority is not None:
        effective_priority = expected_priority
    elif prioritization in RISK_LEVELS:
        effective_priority = prioritization
    else:
        effective_priority = None
    treatment_valid = treatment in RISK_TREATMENTS
    state_compatible = True
    priority_compatible = True
    if not treatment_valid:
        if treatment or requires_completed_risk:
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="Risk Treatment",
                    message="Risk Treatment is not a standardized treatment",
                    actual=treatment,
                    expected=_option_list(RISK_TREATMENTS),
                )
            )
    else:
        compatible_treatments = STATE_RISK_TREATMENTS.get(state)
        if compatible_treatments is not None and treatment not in compatible_treatments:
            state_compatible = False
            if state == "Not Applicable":
                message = "Not Applicable requires Avoidance treatment"
            else:
                message = "Mitigated uses an incompatible treatment"
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="Risk Treatment",
                    message=message,
                    actual=treatment,
                    expected=_option_list(compatible_treatments),
                )
            )

        # Not Applicable has an explicit Avoidance requirement that takes precedence
        # over the general prioritization guidance.
        if state != "Not Applicable" and effective_priority is not None:
            guided_treatments = RISK_TREATMENT_GUIDANCE[effective_priority]
            if treatment not in guided_treatments:
                priority_compatible = False
                findings.append(
                    Finding(
                        origin="output",
                        row_number=row_number,
                        threat_id=threat_id,
                        column="Risk Treatment",
                        message=(
                            "Risk Treatment is incompatible with Risk Prioritization"
                        ),
                        actual=treatment,
                        expected=_option_list(guided_treatments),
                    )
                )

    approval_valid = approval in RISK_APPROVAL_ROLES
    if not approval_valid:
        if approval or requires_completed_risk:
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="Risk Approval",
                    message="Risk Approval is not a standardized role label",
                    actual=approval,
                    expected=_option_list(RISK_APPROVAL_ROLES),
                )
            )
    elif effective_priority is not None and treatment_valid:
        minimum_approval = RISK_APPROVAL_MATRIX[effective_priority][treatment]
        actual_rank = RISK_APPROVAL_ROLES.index(approval)
        minimum_rank = RISK_APPROVAL_ROLES.index(minimum_approval)
        if actual_rank < minimum_rank:
            acceptable_roles = RISK_APPROVAL_ROLES[minimum_rank:]
            findings.append(
                Finding(
                    origin="output",
                    row_number=row_number,
                    threat_id=threat_id,
                    column="Risk Approval",
                    message="Risk Approval is below the minimum required role",
                    actual=approval,
                    expected=_option_list(acceptable_roles),
                )
            )

    if (
        requires_completed_risk
        and treatment_valid
        and state_compatible
        and priority_compatible
    ):
        findings.extend(
            validate_treatment_evidence(
                justification,
                state=state,
                treatment=treatment,
                prioritization=effective_priority,
                row_number=row_number,
                threat_id=threat_id,
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
            basic_control_match = AMBIGUOUS_BASIC_CONTROL_PATTERN.search(justification)
            if basic_control_match is not None:
                findings.append(
                    Finding(
                        origin="output",
                        row_number=row_number,
                        threat_id=threat_id,
                        column="Justification",
                        message=(
                            "ambiguous Basic control category does not identify the "
                            "enforcement boundary"
                        ),
                        actual=basic_control_match.group(),
                        expected=(
                            "Implemented controls: <within-boundary controls> or "
                            "Compensating controls: <outside-boundary controls>"
                        ),
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

        findings.extend(
            validate_risk_governance(
                record,
                row_number=row_number,
                threat_id=threat_id,
            )
        )

        state_cell = _cell(record, "State")
        state = state_cell.value.strip() if state_cell is not None else ""
        if state == "Not Applicable":
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
