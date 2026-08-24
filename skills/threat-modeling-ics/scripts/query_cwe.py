#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///

"""Return bounded CWE records without loading the complete source into context."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

DEFAULT_CWE_SOURCE = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "cwe"
    / "cwe-4.20.json"
)
CWE_ID_PATTERN = re.compile(r"CWE-\d+")
SOURCE_SHA_PATTERN = re.compile(r"[0-9a-f]{40}")
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
VERSIONED_FILENAME_PATTERN = re.compile(r"cwe-(.+)\.json")
ALLOWED_MAPPING_USAGES = frozenset(
    {"Allowed", "Allowed-with-Review", "Discouraged", "Prohibited"}
)
ALLOWED_INCLUDES = frozenset(
    {
        "description",
        "extended-description",
        "mapping-notes",
        "related",
        "mitigations",
    }
)
MAPPING_USAGE_RANK = {
    "Allowed": 0,
    "Allowed-with-Review": 1,
    "Discouraged": 2,
}
ABSTRACTION_RANK = {
    "Variant": 0,
    "Base": 1,
    "Class": 2,
    "Compound": 3,
    "Pillar": 4,
}
MAX_IDS = 20
MAX_TOP = 10
MAX_RELATIONSHIPS = 20
MAX_MITIGATIONS = 10
MAX_SUGGESTIONS = 10
MIN_TEXT_CHARS = 200
MAX_TEXT_CHARS = 2000
DEFAULT_TEXT_CHARS = 600
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


def _numeric_id(identifier: str) -> tuple[int, str]:
    match = re.search(r"\d+", identifier)
    return (int(match.group()) if match else sys.maxsize, identifier)


def _is_mappable(weakness: dict[str, Any]) -> bool:
    mapping_notes = weakness.get("mapping_notes")
    mapping_usage = (
        mapping_notes.get("usage") if isinstance(mapping_notes, dict) else None
    )
    return weakness.get("status") != "Deprecated" and mapping_usage != "Prohibited"


def load_cwe_source(
    path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("CWE source must be a JSON object")

    metadata = payload.get("metadata")
    weaknesses = payload.get("weaknesses")
    if not isinstance(metadata, dict):
        raise ValueError("CWE source must contain metadata")
    if not isinstance(weaknesses, list):
        raise ValueError("CWE source must contain a weaknesses list")

    content_version = str(metadata.get("content_version", "")).strip()
    source_blob_sha = str(metadata.get("source_blob_sha", "")).strip()
    filename_match = VERSIONED_FILENAME_PATTERN.fullmatch(path.name)
    if not content_version:
        raise ValueError("CWE source has no content version")
    if filename_match and filename_match.group(1) != content_version:
        raise ValueError("CWE filename and content version differ")
    if not SOURCE_SHA_PATTERN.fullmatch(source_blob_sha):
        raise ValueError("CWE source has an invalid upstream blob SHA")
    if metadata.get("total_weaknesses") != len(weaknesses):
        raise ValueError("CWE source weakness count differs from metadata")

    weakness_index: dict[str, dict[str, Any]] = {}
    active_count = 0
    mappable_count = 0
    for position, weakness in enumerate(weaknesses, start=1):
        if not isinstance(weakness, dict):
            raise ValueError(f"CWE weakness entry {position} must be an object")

        identifier = str(weakness.get("id", "")).strip().upper()
        mapping_notes = weakness.get("mapping_notes")
        mapping_usage = (
            str(mapping_notes.get("usage", "")).strip()
            if isinstance(mapping_notes, dict)
            else ""
        )
        if not CWE_ID_PATTERN.fullmatch(identifier):
            raise ValueError(f"CWE weakness entry {position} has an invalid id")
        if identifier in weakness_index:
            raise ValueError(f"CWE weakness id is duplicated: {identifier}")
        if mapping_usage not in ALLOWED_MAPPING_USAGES:
            raise ValueError(f"CWE weakness {identifier} has invalid mapping usage")

        weakness_index[identifier] = weakness
        if weakness.get("status") != "Deprecated":
            active_count += 1
        if _is_mappable(weakness):
            mappable_count += 1

    if metadata.get("active_weaknesses") != active_count:
        raise ValueError("CWE active-set count differs from metadata")
    if metadata.get("mappable_weaknesses") != mappable_count:
        raise ValueError("CWE mappable-set count differs from metadata")

    return metadata, weaknesses, weakness_index


def _parse_identifiers(raw_values: list[str]) -> list[str]:
    identifiers: list[str] = []
    for value in raw_values:
        identifiers.extend(item.strip().upper() for item in value.split(","))
    if any(not CWE_ID_PATTERN.fullmatch(item) for item in identifiers):
        raise ValueError("each --id value must use the canonical CWE-NNN format")
    if len(identifiers) > MAX_IDS:
        raise ValueError(f"no more than {MAX_IDS} CWE ids may be requested")
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("duplicate CWE ids are not allowed")
    return identifiers


def _parse_includes(value: str) -> set[str]:
    includes = {item.strip().casefold() for item in value.split(",") if item.strip()}
    unsupported = includes - ALLOWED_INCLUDES
    if unsupported:
        raise ValueError(
            "unsupported --include value: " + ", ".join(sorted(unsupported))
        )
    return includes


def _summary(
    weakness: dict[str, Any],
    *,
    text_limit: int,
    match_score: Optional[int] = None,
) -> dict[str, Any]:
    mapping_notes = weakness.get("mapping_notes")
    mapping_usage = (
        str(mapping_notes.get("usage", ""))
        if isinstance(mapping_notes, dict)
        else ""
    )
    description, truncated = _bounded_text(weakness.get("description"), text_limit)
    result: dict[str, Any] = {
        "id": weakness.get("id"),
        "name": weakness.get("name"),
        "abstraction": weakness.get("abstraction"),
        "status": weakness.get("status"),
        "mapping_usage": mapping_usage,
        "mappable": _is_mappable(weakness),
        "description_excerpt": description,
        "description_truncated": truncated,
    }
    if match_score is not None:
        result["match_score"] = match_score
    return result


def _add_details(
    result: dict[str, Any],
    weakness: dict[str, Any],
    *,
    includes: set[str],
    text_limit: int,
) -> None:
    if "description" in includes:
        description, truncated = _bounded_text(
            weakness.get("description"), text_limit
        )
        result["description"] = description
        result["description_truncated"] = truncated

    if "extended-description" in includes:
        extended, truncated = _bounded_text(
            weakness.get("extended_description"), text_limit
        )
        result["extended_description"] = extended
        result["extended_description_truncated"] = truncated

    if "mapping-notes" in includes:
        raw_notes = weakness.get("mapping_notes")
        notes = raw_notes if isinstance(raw_notes, dict) else {}
        rationale, rationale_truncated = _bounded_text(
            notes.get("rationale"), text_limit
        )
        comments, comments_truncated = _bounded_text(
            notes.get("comments"), text_limit
        )
        suggestions = [
            {
                "cwe_id": item.get("cwe_id"),
                "comment": _bounded_text(item.get("comment"), text_limit)[0],
            }
            for item in notes.get("suggestions", [])
            if isinstance(item, dict)
        ]
        result["mapping_notes"] = {
            "usage": notes.get("usage"),
            "rationale": rationale,
            "rationale_truncated": rationale_truncated,
            "comments": comments,
            "comments_truncated": comments_truncated,
            "reasons": notes.get("reasons", []),
            "suggestions": _bounded_list(suggestions, MAX_SUGGESTIONS),
        }

    if "related" in includes:
        related = [
            {
                "nature": item.get("nature"),
                "cwe_id": item.get("cwe_id"),
                "view_id": item.get("view_id"),
                **({"ordinal": item.get("ordinal")} if item.get("ordinal") else {}),
            }
            for item in weakness.get("related_weaknesses", [])
            if isinstance(item, dict)
        ]
        result["related_weaknesses"] = _bounded_list(
            related, MAX_RELATIONSHIPS
        )

    if "mitigations" in includes:
        mitigations = []
        for item in weakness.get("potential_mitigations", []):
            if not isinstance(item, dict):
                continue
            description, description_truncated = _bounded_text(
                item.get("description"), text_limit
            )
            effectiveness_notes, effectiveness_notes_truncated = _bounded_text(
                item.get("effectiveness_notes"), text_limit
            )
            mitigations.append(
                {
                    **(
                        {"mitigation_id": item.get("mitigation_id")}
                        if item.get("mitigation_id")
                        else {}
                    ),
                    "phases": item.get("phases", []),
                    **(
                        {"strategy": item.get("strategy")}
                        if item.get("strategy")
                        else {}
                    ),
                    "description": description,
                    "description_truncated": description_truncated,
                    **(
                        {"effectiveness": item.get("effectiveness")}
                        if item.get("effectiveness")
                        else {}
                    ),
                    **(
                        {
                            "effectiveness_notes": effectiveness_notes,
                            "effectiveness_notes_truncated": (
                                effectiveness_notes_truncated
                            ),
                        }
                        if effectiveness_notes
                        else {}
                    ),
                }
            )
        result["potential_mitigations"] = _bounded_list(
            mitigations, MAX_MITIGATIONS
        )


def _search_score(weakness: dict[str, Any], query: str) -> int:
    terms = TOKEN_PATTERN.findall(query.casefold())
    if not terms:
        return 0

    name = _normalize_text(weakness.get("name")).casefold()
    description = _normalize_text(weakness.get("description")).casefold()
    extended = _normalize_text(weakness.get("extended_description")).casefold()
    combined = " ".join((name, description, extended))
    if not all(term in combined for term in terms):
        return 0

    normalized_query = _normalize_text(query).casefold()
    name_tokens = set(TOKEN_PATTERN.findall(name))
    score = 20
    if normalized_query == name:
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
        if term in description:
            score += 6
        if term in extended:
            score += 2
    return score


def search_weaknesses(
    weaknesses: list[dict[str, Any]],
    query: str,
    *,
    top: int,
) -> list[tuple[int, dict[str, Any]]]:
    matches = []
    for weakness in weaknesses:
        if not _is_mappable(weakness):
            continue
        score = _search_score(weakness, query)
        if score:
            matches.append((score, weakness))

    def sort_key(item: tuple[int, dict[str, Any]]) -> tuple[Any, ...]:
        score, weakness = item
        mapping_notes = weakness.get("mapping_notes")
        mapping_usage = (
            mapping_notes.get("usage") if isinstance(mapping_notes, dict) else ""
        )
        return (
            -score,
            MAPPING_USAGE_RANK.get(str(mapping_usage), sys.maxsize),
            ABSTRACTION_RANK.get(
                str(weakness.get("abstraction")), sys.maxsize
            ),
            _numeric_id(str(weakness.get("id", ""))),
        )

    return sorted(matches, key=sort_key)[:top]


def _dataset_summary(metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "content_version": metadata.get("content_version"),
        "content_date": metadata.get("content_date"),
        "source": metadata.get("source"),
        "source_blob_sha": metadata.get("source_blob_sha"),
        "total_weaknesses": metadata.get("total_weaknesses"),
        "active_weaknesses": metadata.get("active_weaknesses"),
        "mappable_weaknesses": metadata.get("mappable_weaknesses"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Query bounded records from the versioned CWE projection without "
            "printing the complete source."
        )
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--id",
        action="append",
        help=(
            "Canonical CWE-NNN id; repeat the option or provide comma-separated "
            f"ids (maximum {MAX_IDS})"
        ),
    )
    mode.add_argument(
        "--search",
        help=(
            "Lexical search over active, non-Prohibited weakness names and "
            "descriptions"
        ),
    )
    parser.add_argument(
        "--include",
        default="",
        help=(
            "Comma-separated detail fields for one --id: description, "
            "extended-description, mapping-notes, related, mitigations"
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
            f"Per-text-field limit from {MIN_TEXT_CHARS} through "
            f"{MAX_TEXT_CHARS} (default: {DEFAULT_TEXT_CHARS})"
        ),
    )
    parser.add_argument(
        "--cwe",
        type=Path,
        default=DEFAULT_CWE_SOURCE,
        help="Versioned CWE projection (defaults to the bundled asset)",
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
                "CWE id instead"
            )
        if includes and len(identifiers) != 1:
            raise ValueError(
                "--include requires exactly one --id"
            )
        if args.search is not None and len(args.search) > 200:
            raise ValueError("--search must not exceed 200 characters")

        source_path = args.cwe.expanduser()
        if not source_path.is_file():
            raise ValueError(f"CWE source not found: {source_path}")
        metadata, weaknesses, weakness_index = load_cwe_source(source_path)

        response: dict[str, Any] = {
            "dataset": _dataset_summary(metadata),
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
                weakness = weakness_index.get(identifier)
                if weakness is None:
                    missing.append(identifier)
                    continue
                result = _summary(
                    weakness,
                    text_limit=args.max_text_chars,
                )
                _add_details(
                    result,
                    weakness,
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
            matches = search_weaknesses(
                weaknesses,
                search_query,
                top=args.top,
            )
            response["query"] = {
                "mode": "search",
                "text": search_query,
                "top": args.top,
                "filters": {
                    "status": "not Deprecated",
                    "mapping_usage": "not Prohibited",
                },
            }
            response["matches"] = [
                _summary(
                    weakness,
                    text_limit=args.max_text_chars,
                    match_score=score,
                )
                for score, weakness in matches
            ]

        response["match_count"] = len(response["matches"])
        serialized = json.dumps(response, indent=2, ensure_ascii=False)
        if len(serialized) > MAX_OUTPUT_CHARS:
            raise ValueError(
                f"bounded response exceeds {MAX_OUTPUT_CHARS} characters; "
                "request fewer ids or reduce --max-text-chars"
            )
        print(serialized)
        return exit_code
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
