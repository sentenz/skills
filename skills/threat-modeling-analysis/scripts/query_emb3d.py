#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///

"""Return bounded, joined EMB3D records without printing the source assets."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

ASSET_ROOT = Path(__file__).resolve().parent.parent / "assets" / "emb3d"
DEFAULT_THREATS_SOURCE = ASSET_ROOT / "threats_2.0.1.json"
DEFAULT_COMBINED_SOURCE = (
    ASSET_ROOT / "threats_properties_mitigations_mappings_2.0.1.json"
)
DEFAULT_PROPERTIES_SOURCE = ASSET_ROOT / "properties_threat_mappings_2.0.1.json"
DEFAULT_MITIGATIONS_SOURCE = ASSET_ROOT / "mitigations_threat_mappings_2.0.1.json"
TID_PATTERN = re.compile(r"TID-\d{3}")
PID_PATTERN = re.compile(r"PID-\d+")
MID_PATTERN = re.compile(r"MID-\d{3}")
VERSION_PATTERN = re.compile(r"_(\d+\.\d+\.\d+)\.json")
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
ALLOWED_LEVELS = frozenset({"foundational", "intermediate", "leading"})
ALLOWED_KINDS = frozenset({"all", "threat", "property", "mitigation"})
ALLOWED_INCLUDES = frozenset(
    {"properties", "mitigations", "threats", "hierarchy"}
)
KIND_INCLUDES = {
    "threat": frozenset({"properties", "mitigations"}),
    "property": frozenset({"threats", "hierarchy"}),
    "mitigation": frozenset({"threats"}),
}
KIND_RANK = {
    "threat": 0,
    "property": 1,
    "mitigation": 2,
    "unresolved-property": 3,
}
MAX_IDS = 20
MAX_TOP = 10
MAX_MAPPINGS = 20
MAX_UNRESOLVED_REFS = 20
MAX_OUTPUT_CHARS = 30000


def _normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _bounded_list(items: list[Any], limit: int) -> dict[str, Any]:
    return {
        "total": len(items),
        "items": items[:limit],
        "truncated": len(items) > limit,
    }


def _read_list(path: Path, key: str) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    values = payload.get(key) if isinstance(payload, dict) else None
    if not isinstance(values, list):
        raise ValueError(f"EMB3D source {path.name} must contain a {key} list")
    if any(not isinstance(item, dict) for item in values):
        raise ValueError(f"EMB3D source {path.name} contains a non-object entry")
    return values


def _version(path: Path) -> str:
    match = VERSION_PATTERN.search(path.name)
    if not match:
        raise ValueError(f"EMB3D source filename has no version: {path.name}")
    return match.group(1)


def _index_records(
    records: list[dict[str, Any]],
    *,
    pattern: re.Pattern[str],
    label: str,
) -> dict[str, dict[str, Any]]:
    index = {}
    for position, record in enumerate(records, start=1):
        identifier = str(record.get("id", "")).strip().upper()
        if not pattern.fullmatch(identifier):
            raise ValueError(
                f"EMB3D {label} entry {position} has an invalid id"
            )
        if identifier in index:
            raise ValueError(f"EMB3D {label} id is duplicated: {identifier}")
        index[identifier] = record
    return index


def _reference_ids(
    record: dict[str, Any],
    field: str,
    pattern: re.Pattern[str],
) -> list[str]:
    references = record.get(field)
    if not isinstance(references, list):
        raise ValueError(f"EMB3D {record.get('id')} has no {field} list")
    identifiers = []
    for reference in references:
        if not isinstance(reference, dict):
            raise ValueError(
                f"EMB3D {record.get('id')} has an invalid {field} reference"
            )
        identifier = str(reference.get("id", "")).strip().upper()
        if not pattern.fullmatch(identifier):
            raise ValueError(
                f"EMB3D {record.get('id')} has an invalid {field} id"
            )
        identifiers.append(identifier)
    if len(identifiers) != len(set(identifiers)):
        raise ValueError(
            f"EMB3D {record.get('id')} has duplicate {field} references"
        )
    return identifiers


def load_emb3d_sources(
    threats_path: Path,
    combined_path: Path,
    properties_path: Path,
    mitigations_path: Path,
) -> dict[str, Any]:
    versions = {
        _version(path)
        for path in (
            threats_path,
            combined_path,
            properties_path,
            mitigations_path,
        )
    }
    if len(versions) != 1:
        raise ValueError("EMB3D source versions differ")
    version = next(iter(versions))

    raw_threats = _read_list(threats_path, "threats")
    combined_threats = _read_list(combined_path, "threats")
    properties = _read_list(properties_path, "properties")
    mitigations = _read_list(mitigations_path, "mitigations")
    raw_threat_index = _index_records(
        raw_threats, pattern=TID_PATTERN, label="threat"
    )
    threat_index = _index_records(
        combined_threats, pattern=TID_PATTERN, label="combined threat"
    )
    property_index = _index_records(
        properties, pattern=PID_PATTERN, label="property"
    )
    mitigation_index = _index_records(
        mitigations, pattern=MID_PATTERN, label="mitigation"
    )
    if set(raw_threat_index) != set(threat_index):
        raise ValueError("EMB3D base and combined threat id sets differ")

    for identifier, raw_threat in raw_threat_index.items():
        combined = threat_index[identifier]
        for field in ("text", "category"):
            if raw_threat.get(field) != combined.get(field):
                raise ValueError(
                    f"EMB3D base and combined {identifier} {field} values differ"
                )
        for field, pattern in (
            ("properties", PID_PATTERN),
            ("mitigations", MID_PATTERN),
        ):
            if set(_reference_ids(raw_threat, field, pattern)) != set(
                _reference_ids(combined, field, pattern)
            ):
                raise ValueError(
                    f"EMB3D base and combined {identifier} {field} differ"
                )

    for identifier, mitigation in mitigation_index.items():
        if not _normalize_text(mitigation.get("name")):
            raise ValueError(f"EMB3D mitigation {identifier} has no name")
        level = str(mitigation.get("level", "")).strip().casefold()
        if level not in ALLOWED_LEVELS:
            raise ValueError(f"EMB3D mitigation {identifier} has an invalid level")
        for threat_id in _reference_ids(mitigation, "threats", TID_PATTERN):
            if threat_id not in threat_index:
                raise ValueError(
                    f"EMB3D mitigation {identifier} references unknown {threat_id}"
                )
            if identifier not in _reference_ids(
                threat_index[threat_id], "mitigations", MID_PATTERN
            ):
                raise ValueError(
                    f"EMB3D mitigation mapping is asymmetric: "
                    f"{identifier} and {threat_id}"
                )

    for identifier, prop in property_index.items():
        if not _normalize_text(prop.get("text")):
            raise ValueError(f"EMB3D property {identifier} has no name")
        parent = str(prop.get("parentProp", "")).strip().upper()
        if parent and parent not in property_index:
            raise ValueError(
                f"EMB3D property {identifier} references unknown parent {parent}"
            )
        subproperties = prop.get("subProps")
        if not isinstance(subproperties, list):
            raise ValueError(f"EMB3D property {identifier} has no subProps list")
        for child in subproperties:
            child_id = str(child).strip().upper()
            if not PID_PATTERN.fullmatch(child_id) or child_id not in property_index:
                raise ValueError(
                    f"EMB3D property {identifier} references unknown child {child_id}"
                )
        for threat_id in _reference_ids(prop, "threats", TID_PATTERN):
            if threat_id not in threat_index:
                raise ValueError(
                    f"EMB3D property {identifier} references unknown {threat_id}"
                )
            if identifier not in _reference_ids(
                threat_index[threat_id], "properties", PID_PATTERN
            ):
                raise ValueError(
                    f"EMB3D property mapping is asymmetric: "
                    f"{identifier} and {threat_id}"
                )

    unresolved_property_refs: dict[str, dict[str, Any]] = {}
    for threat_id, threat in threat_index.items():
        for reference in threat.get("properties", []):
            property_id = str(reference.get("id", "")).strip().upper()
            if property_id not in property_index:
                unresolved_property_refs.setdefault(
                    property_id,
                    {"id": property_id, "name": reference.get("text"), "threats": []},
                )["threats"].append(threat_id)
                continue
            prop = property_index[property_id]
            if threat_id not in _reference_ids(prop, "threats", TID_PATTERN):
                raise ValueError(
                    f"EMB3D threat mapping is asymmetric: "
                    f"{threat_id} and {property_id}"
                )
        for reference in threat.get("mitigations", []):
            mitigation_id = str(reference.get("id", "")).strip().upper()
            mitigation = mitigation_index.get(mitigation_id)
            if mitigation is None:
                raise ValueError(
                    f"EMB3D threat {threat_id} references unknown {mitigation_id}"
                )
            expected_name = _normalize_text(mitigation.get("name"))
            reference_name = _normalize_text(reference.get("text"))
            if reference_name and reference_name != expected_name:
                raise ValueError(
                    f"EMB3D mitigation name differs for {mitigation_id}"
                )
            expected_level = str(mitigation.get("level", "")).strip().casefold()
            reference_level = str(reference.get("level", "")).strip().casefold()
            if reference_level and reference_level != expected_level:
                raise ValueError(
                    f"EMB3D mitigation level differs for {mitigation_id}"
                )

    return {
        "version": version,
        "files": {
            "base_threats": threats_path.name,
            "combined_threats": combined_path.name,
            "properties": properties_path.name,
            "mitigations": mitigations_path.name,
        },
        "threats": threat_index,
        "properties": property_index,
        "mitigations": mitigation_index,
        "unresolved_property_refs": unresolved_property_refs,
    }


def _parse_identifiers(
    raw_values: list[str],
    *,
    pattern: re.Pattern[str],
    option: str,
) -> list[str]:
    identifiers: list[str] = []
    for value in raw_values:
        identifiers.extend(item.strip().upper() for item in value.split(","))
    if any(not pattern.fullmatch(item) for item in identifiers):
        raise ValueError(f"each {option} value must use its canonical format")
    if len(identifiers) > MAX_IDS:
        raise ValueError(f"no more than {MAX_IDS} EMB3D ids may be requested")
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("duplicate EMB3D ids are not allowed")
    return identifiers


def _parse_includes(value: str) -> set[str]:
    includes = {item.strip().casefold() for item in value.split(",") if item.strip()}
    unsupported = includes - ALLOWED_INCLUDES
    if unsupported:
        raise ValueError(
            "unsupported --include value: " + ", ".join(sorted(unsupported))
        )
    return includes


def _threat_summary(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "threat",
        "id": record.get("id"),
        "name": record.get("text"),
        "category": record.get("category"),
        "property_count": len(record.get("properties", [])),
        "mitigation_count": len(record.get("mitigations", [])),
    }


def _property_summary(
    record: dict[str, Any],
    *,
    resolved: bool = True,
) -> dict[str, Any]:
    if not resolved:
        return {
            "kind": "property",
            "id": record.get("id"),
            "name": record.get("name"),
            "resolved": False,
            "threat_count": len(record.get("threats", [])),
        }
    return {
        "kind": "property",
        "id": record.get("id"),
        "name": record.get("text"),
        "category": record.get("category"),
        "resolved": True,
        "is_parent": bool(record.get("isparentProp")),
        "parent_id": record.get("parentProp") or None,
        "subproperty_count": len(record.get("subProps", [])),
        "threat_count": len(record.get("threats", [])),
    }


def _mitigation_summary(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "mitigation",
        "id": record.get("id"),
        "name": record.get("name"),
        "level": record.get("level"),
        "threat_count": len(record.get("threats", [])),
    }


def _record_summary(kind: str, record: dict[str, Any]) -> dict[str, Any]:
    if kind == "threat":
        return _threat_summary(record)
    if kind == "property":
        return _property_summary(record)
    return _mitigation_summary(record)


def _add_details(
    result: dict[str, Any],
    kind: str,
    record: dict[str, Any],
    dataset: dict[str, Any],
    includes: set[str],
) -> None:
    if kind == "threat":
        if "properties" in includes:
            properties = []
            for property_id in _reference_ids(record, "properties", PID_PATTERN):
                prop = dataset["properties"].get(property_id)
                if prop is not None:
                    properties.append(_property_summary(prop))
                else:
                    properties.append(
                        _property_summary(
                            dataset["unresolved_property_refs"][property_id],
                            resolved=False,
                        )
                    )
            result["properties"] = _bounded_list(properties, MAX_MAPPINGS)
        if "mitigations" in includes:
            mitigations = [
                _mitigation_summary(dataset["mitigations"][mitigation_id])
                for mitigation_id in _reference_ids(
                    record, "mitigations", MID_PATTERN
                )
            ]
            result["mitigations"] = _bounded_list(
                mitigations, MAX_MAPPINGS
            )

    if kind == "property":
        if "threats" in includes:
            threats = [
                _threat_summary(dataset["threats"][threat_id])
                for threat_id in _reference_ids(record, "threats", TID_PATTERN)
            ]
            result["threats"] = _bounded_list(threats, MAX_MAPPINGS)
        if "hierarchy" in includes:
            parent_id = str(record.get("parentProp", "")).strip().upper()
            subproperty_ids = [
                str(item).strip().upper() for item in record.get("subProps", [])
            ]
            result["hierarchy"] = {
                "parent": (
                    _property_summary(dataset["properties"][parent_id])
                    if parent_id
                    else None
                ),
                "subproperties": _bounded_list(
                    [
                        _property_summary(dataset["properties"][identifier])
                        for identifier in subproperty_ids
                    ],
                    MAX_MAPPINGS,
                ),
            }

    if kind == "mitigation" and "threats" in includes:
        threats = [
            _threat_summary(dataset["threats"][threat_id])
            for threat_id in _reference_ids(record, "threats", TID_PATTERN)
        ]
        result["threats"] = _bounded_list(threats, MAX_MAPPINGS)


def _search_score(kind: str, record: dict[str, Any], query: str) -> int:
    terms = TOKEN_PATTERN.findall(query.casefold())
    if not terms:
        return 0
    identifier = str(record.get("id", "")).casefold()
    name = _normalize_text(record.get("name") or record.get("text")).casefold()
    metadata = _normalize_text(
        f"{record.get('category', '')} {record.get('level', '')}"
    ).casefold()
    combined = " ".join((identifier, name, metadata))
    if not all(term in combined for term in terms):
        return 0
    normalized_query = _normalize_text(query).casefold()
    name_tokens = set(TOKEN_PATTERN.findall(name))
    score = 20
    if normalized_query == identifier or normalized_query == name:
        score += 1000
    elif normalized_query in name:
        score += 300
    for term in set(terms):
        if term in name_tokens:
            score += 40
        elif term in name:
            score += 24
        if term in metadata:
            score += 10
    return score


def search_records(
    dataset: dict[str, Any],
    query: str,
    *,
    kind: str,
    top: int,
) -> list[tuple[int, str, dict[str, Any]]]:
    collections = {
        "threat": dataset["threats"],
        "property": dataset["properties"],
        "mitigation": dataset["mitigations"],
    }
    matches = []
    for record_kind, index in collections.items():
        if kind != "all" and kind != record_kind:
            continue
        for record in index.values():
            score = _search_score(record_kind, record, query)
            if score:
                matches.append((score, record_kind, record))
    if kind in {"all", "property"}:
        for record in dataset["unresolved_property_refs"].values():
            score = _search_score("property", record, query)
            if score:
                matches.append((score, "unresolved-property", record))
    return sorted(
        matches,
        key=lambda item: (
            -item[0],
            KIND_RANK[item[1]],
            str(item[2].get("id")),
        ),
    )[:top]


def _dataset_summary(dataset: dict[str, Any]) -> dict[str, Any]:
    unresolved = sorted(dataset["unresolved_property_refs"])
    return {
        "name": "MITRE EMB3D",
        "version": dataset["version"],
        "source": "https://github.com/mitre/emb3d/tree/main/_data",
        "files": dataset["files"],
        "threats": len(dataset["threats"]),
        "properties": len(dataset["properties"]),
        "mitigations": len(dataset["mitigations"]),
        "unresolved_property_references": _bounded_list(
            unresolved, MAX_UNRESOLVED_REFS
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Query bounded, joined records from the versioned EMB3D assets "
            "without printing the complete sources."
        )
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--tid",
        action="append",
        help="TID-NNN threat id; repeat or use commas for bounded batches",
    )
    mode.add_argument(
        "--pid",
        action="append",
        help="PID-NN property id; repeat or use commas for bounded batches",
    )
    mode.add_argument(
        "--mid",
        action="append",
        help="MID-NNN mitigation id; repeat or use commas for bounded batches",
    )
    mode.add_argument("--search", help="Lexical search over EMB3D records")
    parser.add_argument(
        "--kind",
        choices=sorted(ALLOWED_KINDS),
        default="all",
        help="Search threats, properties, mitigations, or all records",
    )
    parser.add_argument(
        "--include",
        default="",
        help=(
            "Comma-separated detail fields for one id: properties, mitigations, "
            "threats, hierarchy"
        ),
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help=f"Maximum search matches from 1 through {MAX_TOP} (default: 5)",
    )
    parser.add_argument(
        "--threats",
        type=Path,
        default=DEFAULT_THREATS_SOURCE,
        help="Versioned base threat source",
    )
    parser.add_argument(
        "--combined",
        type=Path,
        default=DEFAULT_COMBINED_SOURCE,
        help="Versioned threat-centric mapping source",
    )
    parser.add_argument(
        "--properties",
        type=Path,
        default=DEFAULT_PROPERTIES_SOURCE,
        help="Versioned property-centric mapping source",
    )
    parser.add_argument(
        "--mitigations",
        type=Path,
        default=DEFAULT_MITIGATIONS_SOURCE,
        help="Versioned mitigation-centric mapping source",
    )
    args = parser.parse_args()

    try:
        if not 1 <= args.top <= MAX_TOP:
            raise ValueError(f"--top must be from 1 through {MAX_TOP}")
        includes = _parse_includes(args.include)
        if includes and args.search is not None:
            raise ValueError(
                "--include cannot be used with --search; inspect one selected "
                "EMB3D id instead"
            )
        if args.search is not None and len(args.search) > 200:
            raise ValueError("--search must not exceed 200 characters")
        if args.search is None and args.kind != "all":
            raise ValueError("--kind may be used only with --search")

        if args.tid:
            query_kind = "threat"
            identifiers = _parse_identifiers(
                args.tid, pattern=TID_PATTERN, option="--tid"
            )
        elif args.pid:
            query_kind = "property"
            identifiers = _parse_identifiers(
                args.pid, pattern=PID_PATTERN, option="--pid"
            )
        elif args.mid:
            query_kind = "mitigation"
            identifiers = _parse_identifiers(
                args.mid, pattern=MID_PATTERN, option="--mid"
            )
        else:
            query_kind = "search"
            identifiers = []
        if includes and len(identifiers) != 1:
            raise ValueError("--include requires exactly one EMB3D id")
        if includes and query_kind != "search":
            incompatible = includes - KIND_INCLUDES[query_kind]
            if incompatible:
                raise ValueError(
                    f"unsupported --include for {query_kind}: "
                    + ", ".join(sorted(incompatible))
                )

        paths = (
            args.threats.expanduser(),
            args.combined.expanduser(),
            args.properties.expanduser(),
            args.mitigations.expanduser(),
        )
        missing_paths = [str(path) for path in paths if not path.is_file()]
        if missing_paths:
            raise ValueError("EMB3D source not found: " + ", ".join(missing_paths))
        dataset = load_emb3d_sources(*paths)
        response: dict[str, Any] = {
            "dataset": _dataset_summary(dataset),
            "query": {},
            "match_count": 0,
            "matches": [],
        }
        exit_code = 0

        if identifiers:
            response["query"] = {
                "mode": "id",
                "kind": query_kind,
                "ids": identifiers,
                "include": sorted(includes),
            }
            index = {
                "threat": dataset["threats"],
                "property": dataset["properties"],
                "mitigation": dataset["mitigations"],
            }[query_kind]
            missing = []
            for identifier in identifiers:
                record = index.get(identifier)
                if record is None and query_kind == "property":
                    unresolved = dataset["unresolved_property_refs"].get(identifier)
                    if unresolved is not None:
                        result = _property_summary(unresolved, resolved=False)
                        if includes:
                            result["details_unavailable"] = (
                                "property is referenced by the threat-centric source "
                                "but absent from the property-centric source"
                            )
                        response["matches"].append(result)
                        continue
                if record is None:
                    missing.append(identifier)
                    continue
                result = _record_summary(query_kind, record)
                _add_details(
                    result,
                    query_kind,
                    record,
                    dataset,
                    includes,
                )
                response["matches"].append(result)
            if missing:
                response["not_found"] = missing
                exit_code = 1
        else:
            search_query = str(args.search or "").strip()
            if not TOKEN_PATTERN.search(search_query.casefold()):
                raise ValueError("--search must contain at least one letter or digit")
            matches = search_records(
                dataset, search_query, kind=args.kind, top=args.top
            )
            response["query"] = {
                "mode": "search",
                "text": search_query,
                "kind": args.kind,
                "top": args.top,
            }
            for score, record_kind, record in matches:
                if record_kind == "unresolved-property":
                    result = _property_summary(record, resolved=False)
                else:
                    result = _record_summary(record_kind, record)
                result["match_score"] = score
                response["matches"].append(result)

        response["match_count"] = len(response["matches"])
        serialized = json.dumps(response, indent=2, ensure_ascii=False)
        if len(serialized) > MAX_OUTPUT_CHARS:
            raise ValueError(
                f"bounded response exceeds {MAX_OUTPUT_CHARS} characters; "
                "request fewer ids or fewer detail fields"
            )
        print(serialized)
        return exit_code
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
