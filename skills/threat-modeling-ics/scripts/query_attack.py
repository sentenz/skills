#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///

"""Return bounded ATT&CK for ICS records without printing the STIX bundle."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

DEFAULT_ATTACK_SOURCE = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "attack"
    / "ics-attack-19.2.json"
)
ATTACK_ID_PATTERN = re.compile(r"T\d{4}(?:\.\d{3})?")
VERSIONED_FILENAME_PATTERN = re.compile(r"ics-attack-(.+)\.json")
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
ATTACK_SOURCE_NAMES = frozenset({"mitre-attack", "mitre-ics-attack"})
ALLOWED_INCLUDES = frozenset(
    {
        "description",
        "tactics",
        "platforms",
        "mitigations",
        "detections",
        "relationships",
    }
)
MAX_IDS = 20
MAX_TOP = 10
MAX_MITIGATIONS = 15
MAX_DETECTIONS = 15
MAX_RELATIONSHIPS = 20
MIN_TEXT_CHARS = 200
MAX_TEXT_CHARS = 2000
DEFAULT_TEXT_CHARS = 600
MAX_NESTED_TEXT_CHARS = 320
MAX_OUTPUT_CHARS = 30000


def _normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _bounded_text(value: Any, limit: int) -> tuple[str, bool]:
    text = _normalize_text(value)
    if len(text) <= limit:
        return text, False
    return text[: max(0, limit - 1)].rstrip() + "…", True


def _bounded_list(items: list[Any], limit: int) -> dict[str, Any]:
    return {
        "total": len(items),
        "items": items[:limit],
        "truncated": len(items) > limit,
    }


def _is_active(item: dict[str, Any]) -> bool:
    return not bool(item.get("revoked") or item.get("x_mitre_deprecated"))


def _external_id(
    item: dict[str, Any],
    pattern: Optional[re.Pattern[str]] = None,
) -> Optional[str]:
    references = item.get("external_references")
    if not isinstance(references, list):
        return None
    identifiers = {
        str(reference.get("external_id", "")).strip().upper()
        for reference in references
        if isinstance(reference, dict)
        and reference.get("source_name") in ATTACK_SOURCE_NAMES
        and reference.get("external_id")
    }
    if pattern is not None:
        identifiers = {
            identifier
            for identifier in identifiers
            if pattern.fullmatch(identifier)
        }
    if len(identifiers) > 1:
        raise ValueError(
            f"ATT&CK object {item.get('id', '<unknown>')} has multiple external ids"
        )
    return next(iter(identifiers), None)


def load_attack_source(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("type") != "bundle":
        raise ValueError("ATT&CK source must be a STIX bundle")
    objects = payload.get("objects")
    if not isinstance(objects, list):
        raise ValueError("ATT&CK source must contain an objects list")

    object_index: dict[str, dict[str, Any]] = {}
    for position, item in enumerate(objects, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"ATT&CK object {position} must be an object")
        stix_id = str(item.get("id", "")).strip()
        if not stix_id:
            raise ValueError(f"ATT&CK object {position} has no STIX id")
        if stix_id in object_index:
            raise ValueError(f"ATT&CK STIX id is duplicated: {stix_id}")
        object_index[stix_id] = item

    collections = [
        item for item in objects if item.get("type") == "x-mitre-collection"
    ]
    if len(collections) != 1:
        raise ValueError("ATT&CK source must contain one collection record")
    collection = collections[0]
    version = str(collection.get("x_mitre_version", "")).strip()
    if not version:
        raise ValueError("ATT&CK collection has no version")
    filename_match = VERSIONED_FILENAME_PATTERN.fullmatch(path.name)
    if filename_match and filename_match.group(1) != version:
        raise ValueError("ATT&CK filename and collection version differ")

    techniques: dict[str, dict[str, Any]] = {}
    for position, item in enumerate(objects, start=1):
        if item.get("type") != "attack-pattern":
            continue
        identifier = _external_id(item, ATTACK_ID_PATTERN)
        if identifier is None:
            continue
        if not _normalize_text(item.get("name")):
            raise ValueError(f"ATT&CK technique {identifier} has no name")
        if identifier in techniques:
            raise ValueError(f"ATT&CK technique id is duplicated: {identifier}")
        techniques[identifier] = item
    if not techniques:
        raise ValueError("ATT&CK source contains no ICS technique ids")

    relationships = [
        item for item in objects if item.get("type") == "relationship"
    ]
    for relationship in relationships:
        source_ref = str(relationship.get("source_ref", ""))
        target_ref = str(relationship.get("target_ref", ""))
        if source_ref not in object_index or target_ref not in object_index:
            raise ValueError(
                f"ATT&CK relationship {relationship.get('id')} has an unknown endpoint"
            )

    tactics_by_shortname = {
        str(item.get("x_mitre_shortname")): item
        for item in objects
        if item.get("type") == "x-mitre-tactic"
        and item.get("x_mitre_shortname")
        and _is_active(item)
    }
    return {
        "source_file": path.name,
        "bundle_id": payload.get("id"),
        "collection": collection,
        "objects": objects,
        "object_index": object_index,
        "techniques": techniques,
        "relationships": relationships,
        "tactics_by_shortname": tactics_by_shortname,
    }


def _parse_identifiers(raw_values: list[str]) -> list[str]:
    identifiers: list[str] = []
    for value in raw_values:
        identifiers.extend(item.strip().upper() for item in value.split(","))
    if any(not ATTACK_ID_PATTERN.fullmatch(item) for item in identifiers):
        raise ValueError(
            "each --id value must use canonical TNNNN or TNNNN.NNN format"
        )
    if len(identifiers) > MAX_IDS:
        raise ValueError(f"no more than {MAX_IDS} ATT&CK ids may be requested")
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("duplicate ATT&CK ids are not allowed")
    return identifiers


def _parse_includes(value: str) -> set[str]:
    includes = {item.strip().casefold() for item in value.split(",") if item.strip()}
    unsupported = includes - ALLOWED_INCLUDES
    if unsupported:
        raise ValueError(
            "unsupported --include value: " + ", ".join(sorted(unsupported))
        )
    return includes


def _tactic_records(
    technique: dict[str, Any],
    tactics_by_shortname: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    result = []
    for phase in technique.get("kill_chain_phases", []):
        if not isinstance(phase, dict):
            continue
        shortname = str(phase.get("phase_name", "")).strip()
        tactic = tactics_by_shortname.get(shortname)
        result.append(
            {
                "id": _external_id(tactic) if tactic else None,
                "name": tactic.get("name") if tactic else shortname,
                "shortname": shortname,
            }
        )
    return result


def _summary(
    technique: dict[str, Any],
    *,
    tactics_by_shortname: dict[str, dict[str, Any]],
    text_limit: int,
    match_score: Optional[int] = None,
) -> dict[str, Any]:
    description, truncated = _bounded_text(technique.get("description"), text_limit)
    result: dict[str, Any] = {
        "id": _external_id(technique, ATTACK_ID_PATTERN),
        "name": technique.get("name"),
        "active": _is_active(technique),
        "revoked": bool(technique.get("revoked")),
        "deprecated": bool(technique.get("x_mitre_deprecated")),
        "subtechnique": bool(technique.get("x_mitre_is_subtechnique")),
        "version": technique.get("x_mitre_version"),
        "tactic_shortnames": [
            item["shortname"]
            for item in _tactic_records(technique, tactics_by_shortname)
        ],
        "description_excerpt": description,
        "description_truncated": truncated,
    }
    if match_score is not None:
        result["match_score"] = match_score
    return result


def _object_record(item: dict[str, Any], text_limit: int) -> dict[str, Any]:
    description, truncated = _bounded_text(item.get("description"), text_limit)
    return {
        "type": item.get("type"),
        "stix_id": item.get("id"),
        "id": _external_id(item),
        "name": item.get("name"),
        "description_excerpt": description,
        "description_truncated": truncated,
    }


def _related_object_record(
    relationship: dict[str, Any],
    item: dict[str, Any],
    text_limit: int,
) -> dict[str, Any]:
    result = _object_record(item, text_limit)
    description, truncated = _bounded_text(
        relationship.get("description"), text_limit
    )
    result.update(
        {
            "relationship": relationship.get("relationship_type"),
            "relationship_stix_id": relationship.get("id"),
            "relationship_description_excerpt": description,
            "relationship_description_truncated": truncated,
        }
    )
    return result


def _related_objects(
    dataset: dict[str, Any],
    technique: dict[str, Any],
    relationship_type: str,
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    pairs = []
    technique_ref = technique.get("id")
    for relationship in dataset["relationships"]:
        if not _is_active(relationship):
            continue
        if relationship.get("relationship_type") != relationship_type:
            continue
        if relationship.get("target_ref") != technique_ref:
            continue
        source = dataset["object_index"][relationship["source_ref"]]
        if _is_active(source):
            pairs.append((relationship, source))
    return sorted(
        pairs,
        key=lambda pair: (
            _normalize_text(pair[1].get("name")).casefold(),
            str(pair[1].get("id")),
        ),
    )


def _add_details(
    result: dict[str, Any],
    technique: dict[str, Any],
    dataset: dict[str, Any],
    *,
    includes: set[str],
    text_limit: int,
) -> None:
    nested_text_limit = min(text_limit, MAX_NESTED_TEXT_CHARS)
    if "description" in includes:
        description, truncated = _bounded_text(
            technique.get("description"), text_limit
        )
        result["description"] = description
        result["description_truncated"] = truncated

    if "tactics" in includes:
        result["tactics"] = _tactic_records(
            technique, dataset["tactics_by_shortname"]
        )

    if "platforms" in includes:
        platforms = technique.get("x_mitre_platforms", [])
        result["platforms"] = sorted(
            str(item) for item in platforms if str(item).strip()
        )

    if "mitigations" in includes:
        mitigations = [
            _related_object_record(relationship, source, nested_text_limit)
            for relationship, source in _related_objects(
                dataset, technique, "mitigates"
            )
        ]
        result["mitigations"] = _bounded_list(
            mitigations, MAX_MITIGATIONS
        )

    if "detections" in includes:
        detections = [
            _related_object_record(relationship, source, nested_text_limit)
            for relationship, source in _related_objects(
                dataset, technique, "detects"
            )
        ]
        result["detections"] = _bounded_list(detections, MAX_DETECTIONS)

    if "relationships" in includes:
        relationships = []
        technique_ref = technique.get("id")
        for relationship in dataset["relationships"]:
            if not _is_active(relationship):
                continue
            source_ref = relationship.get("source_ref")
            target_ref = relationship.get("target_ref")
            if technique_ref not in {source_ref, target_ref}:
                continue
            direction = "outgoing" if source_ref == technique_ref else "incoming"
            counterpart_ref = target_ref if direction == "outgoing" else source_ref
            counterpart = dataset["object_index"][counterpart_ref]
            if not _is_active(counterpart):
                continue
            description, truncated = _bounded_text(
                relationship.get("description"), nested_text_limit
            )
            relationships.append(
                {
                    "relationship": relationship.get("relationship_type"),
                    "direction": direction,
                    "counterpart": _object_record(
                        counterpart, nested_text_limit
                    ),
                    "description_excerpt": description,
                    "description_truncated": truncated,
                }
            )
        relationships.sort(
            key=lambda item: (
                str(item["relationship"]),
                str(item["direction"]),
                _normalize_text(item["counterpart"].get("name")).casefold(),
                str(item["counterpart"].get("stix_id")),
            )
        )
        result["relationships"] = _bounded_list(
            relationships, MAX_RELATIONSHIPS
        )


def _search_score(
    technique: dict[str, Any],
    query: str,
    tactics_by_shortname: dict[str, dict[str, Any]],
) -> int:
    terms = TOKEN_PATTERN.findall(query.casefold())
    if not terms:
        return 0
    identifier = str(_external_id(technique, ATTACK_ID_PATTERN) or "").casefold()
    name = _normalize_text(technique.get("name")).casefold()
    description = _normalize_text(technique.get("description")).casefold()
    tactics = " ".join(
        f"{item.get('id') or ''} {item.get('name') or ''} {item['shortname']}"
        for item in _tactic_records(technique, tactics_by_shortname)
    ).casefold()
    platforms = " ".join(
        str(item) for item in technique.get("x_mitre_platforms", [])
    ).casefold()
    combined = " ".join((identifier, name, description, tactics, platforms))
    if not all(term in combined for term in terms):
        return 0

    normalized_query = _normalize_text(query).casefold()
    name_tokens = set(TOKEN_PATTERN.findall(name))
    score = 20
    if normalized_query == identifier or normalized_query == name:
        score += 1000
    elif normalized_query in name:
        score += 300
    elif normalized_query in description:
        score += 80
    for term in set(terms):
        if term in name_tokens:
            score += 40
        elif term in name:
            score += 24
        if term in tactics or term in platforms:
            score += 10
        if term in description:
            score += 6
    return score


def search_techniques(
    dataset: dict[str, Any],
    query: str,
    *,
    top: int,
) -> list[tuple[int, dict[str, Any]]]:
    matches = []
    for technique in dataset["techniques"].values():
        if not _is_active(technique):
            continue
        score = _search_score(
            technique, query, dataset["tactics_by_shortname"]
        )
        if score:
            matches.append((score, technique))
    return sorted(
        matches,
        key=lambda item: (
            -item[0],
            bool(item[1].get("x_mitre_is_subtechnique")),
            str(_external_id(item[1], ATTACK_ID_PATTERN)),
        ),
    )[:top]


def _dataset_summary(dataset: dict[str, Any]) -> dict[str, Any]:
    collection = dataset["collection"]
    techniques = list(dataset["techniques"].values())
    return {
        "name": collection.get("name"),
        "version": collection.get("x_mitre_version"),
        "modified": collection.get("modified"),
        "file": dataset.get("source_file"),
        "bundle_id": dataset.get("bundle_id"),
        "source": "https://github.com/mitre-attack/attack-stix-data",
        "total_techniques": len(techniques),
        "active_techniques": sum(_is_active(item) for item in techniques),
        "revoked_techniques": sum(bool(item.get("revoked")) for item in techniques),
        "deprecated_techniques": sum(
            bool(item.get("x_mitre_deprecated")) for item in techniques
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Query bounded records from the ATT&CK for ICS STIX snapshot "
            "without printing the complete bundle."
        )
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--id",
        action="append",
        help=(
            "Canonical technique id; repeat the option or provide comma-separated "
            f"ids (maximum {MAX_IDS})"
        ),
    )
    mode.add_argument(
        "--search",
        help="Lexical search over active ICS techniques",
    )
    parser.add_argument(
        "--include",
        default="",
        help=(
            "Comma-separated detail fields for one --id: description, tactics, "
            "platforms, mitigations, detections, relationships. Mitigation and "
            "detection records include their technique-specific relationship text."
        ),
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help=f"Maximum search matches from 1 through {MAX_TOP} (default: 5)",
    )
    parser.add_argument(
        "--max-text-chars",
        type=int,
        default=DEFAULT_TEXT_CHARS,
        help=(
            f"Per-primary-text limit from {MIN_TEXT_CHARS} through "
            f"{MAX_TEXT_CHARS} (default: {DEFAULT_TEXT_CHARS})"
        ),
    )
    parser.add_argument(
        "--attack",
        type=Path,
        default=DEFAULT_ATTACK_SOURCE,
        help="Versioned ATT&CK STIX snapshot (defaults to the bundled asset)",
    )
    args = parser.parse_args()

    try:
        if not 1 <= args.top <= MAX_TOP:
            raise ValueError(f"--top must be from 1 through {MAX_TOP}")
        if not MIN_TEXT_CHARS <= args.max_text_chars <= MAX_TEXT_CHARS:
            raise ValueError(
                f"--max-text-chars must be from {MIN_TEXT_CHARS} through "
                f"{MAX_TEXT_CHARS}"
            )
        includes = _parse_includes(args.include)
        identifiers = _parse_identifiers(args.id) if args.id else []
        if includes and args.search is not None:
            raise ValueError(
                "--include cannot be used with --search; inspect one selected "
                "technique instead"
            )
        if includes and len(identifiers) != 1:
            raise ValueError("--include requires exactly one --id")
        if args.search is not None and len(args.search) > 200:
            raise ValueError("--search must not exceed 200 characters")

        source_path = args.attack.expanduser()
        if not source_path.is_file():
            raise ValueError(f"ATT&CK source not found: {source_path}")
        dataset = load_attack_source(source_path)
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
                "ids": identifiers,
                "include": sorted(includes),
            }
            missing = []
            for identifier in identifiers:
                technique = dataset["techniques"].get(identifier)
                if technique is None:
                    missing.append(identifier)
                    continue
                result = _summary(
                    technique,
                    tactics_by_shortname=dataset["tactics_by_shortname"],
                    text_limit=args.max_text_chars,
                )
                _add_details(
                    result,
                    technique,
                    dataset,
                    includes=includes,
                    text_limit=args.max_text_chars,
                )
                response["matches"].append(result)
            if missing:
                response["not_found"] = missing
                exit_code = 1
        else:
            search_query = str(args.search or "").strip()
            if not TOKEN_PATTERN.search(search_query.casefold()):
                raise ValueError("--search must contain at least one letter or digit")
            matches = search_techniques(dataset, search_query, top=args.top)
            response["query"] = {
                "mode": "search",
                "text": search_query,
                "top": args.top,
                "filters": {"active": True, "domain": "ics-attack"},
            }
            response["matches"] = [
                _summary(
                    technique,
                    tactics_by_shortname=dataset["tactics_by_shortname"],
                    text_limit=args.max_text_chars,
                    match_score=score,
                )
                for score, technique in matches
            ]

        response["match_count"] = len(response["matches"])
        serialized = json.dumps(response, indent=2, ensure_ascii=False)
        if len(serialized) > MAX_OUTPUT_CHARS:
            raise ValueError(
                f"bounded response exceeds {MAX_OUTPUT_CHARS} characters; "
                "request fewer ids, fewer detail fields, or reduce "
                "--max-text-chars"
            )
        print(serialized)
        return exit_code
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
