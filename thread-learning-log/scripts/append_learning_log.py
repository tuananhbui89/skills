#!/usr/bin/env python3
"""Render or append one structured learning log entry."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_LOG_PATH = (
    Path.home() / ".codex" / "skills" / "thread-learning-log" / "learning-log.md"
)
METADATA_ORDER = [
    "entry_id",
    "date",
    "time_start",
    "time_end",
    "time_basis",
    "category",
    "primary_tag",
    "tags",
    "context_status",
    "source",
    "source_locations",
    "reference_locations",
    "title",
]
SECTION_ORDER = [
    "Summary",
    "What I Did",
    "What I Learned",
    "Decisions",
    "Open Questions",
    "Next Steps",
]
VALID_CATEGORIES = {
    "learning",
    "research",
    "implementation",
    "debugging",
    "planning",
    "review",
    "status",
    "ops",
    "mixed",
}
VALID_CONTEXT_STATUS = {"full", "partial"}
VALID_TIME_BASIS = {"logged_at", "explicit_range", "inferred", "unknown"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--render", action="store_true", help="Render entry to stdout only")
    mode.add_argument("--append", action="store_true", help="Append entry to the log file")
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to a JSON payload file. If omitted, read JSON from stdin.",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=DEFAULT_LOG_PATH,
        help=f"Destination log path. Defaults to {DEFAULT_LOG_PATH}.",
    )
    return parser.parse_args()


def slugify(value: str) -> str:
    lowered = value.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug or "entry"


def normalize_tag(value: str) -> str:
    tag = value.strip()
    if not tag:
        raise ValueError("primary_tag cannot be empty")
    if not tag.startswith("@"):
        tag = f"@{tag}"
    if not re.fullmatch(r"@[A-Za-z0-9]+", tag):
        raise ValueError(
            "tags must match @PascalCase or @AlphaNumeric style values without spaces"
        )
    return tag


def normalize_tags(tags: object, primary_tag: str) -> list[str]:
    if tags is None:
        tag_values = [primary_tag]
    elif isinstance(tags, str):
        tag_values = [part.strip() for part in tags.split(",") if part.strip()]
    elif isinstance(tags, list):
        tag_values = [str(item).strip() for item in tags if str(item).strip()]
    else:
        raise ValueError("tags must be a string or a list of strings")

    normalized: list[str] = []
    seen: set[str] = set()
    for tag in [primary_tag, *tag_values]:
        normalized_tag = normalize_tag(tag)
        if normalized_tag not in seen:
            normalized.append(normalized_tag)
            seen.add(normalized_tag)
    return normalized


def normalize_location_list(value: object, field_name: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list):
        values = [str(item) for item in value]
    else:
        raise ValueError(f"{field_name} must be a string or a list of strings")

    normalized: list[str] = []
    seen: set[str] = set()
    for item in values:
        location = str(item).strip()
        if not location or location in seen:
            continue
        normalized.append(location)
        seen.add(location)
    return normalized


def load_payload(input_path: Path | None) -> dict:
    raw = input_path.read_text(encoding="utf-8") if input_path else sys.stdin.read()
    if not raw.strip():
        raise ValueError("input payload is empty")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
    return payload


def build_entry_id(date: str, time_start: str, primary_tag: str, title: str) -> str:
    date_part = date.replace("-", "")
    time_part = time_start.replace(":", "") if time_start != "unknown" else "unknown"
    tag_part = slugify(primary_tag.lstrip("@"))
    title_part = slugify(title)[:40]
    return f"{date_part}-{time_part}-{tag_part}-{title_part}"


def normalize_section_body(value: object) -> str:
    if value is None:
        return "- None."
    body = str(value).strip()
    return body if body else "- None."


def normalize_payload(payload: dict) -> dict:
    now = datetime.now().astimezone()
    date = str(payload.get("date") or now.strftime("%Y-%m-%d"))
    time_basis = str(payload.get("time_basis") or "logged_at")
    if time_basis not in VALID_TIME_BASIS:
        raise ValueError(
            f"time_basis must be one of {sorted(VALID_TIME_BASIS)}, got {time_basis!r}"
        )

    time_start = str(payload.get("time_start") or "").strip()
    time_end = str(payload.get("time_end") or "").strip()
    if time_basis == "unknown":
        time_start = time_start or "unknown"
        time_end = time_end or "unknown"
    else:
        current_time = now.strftime("%H:%M")
        time_start = time_start or current_time
        time_end = time_end or time_start or current_time

    category = str(payload.get("category") or "mixed")
    if category not in VALID_CATEGORIES:
        raise ValueError(
            f"category must be one of {sorted(VALID_CATEGORIES)}, got {category!r}"
        )

    context_status = str(payload.get("context_status") or "full")
    if context_status not in VALID_CONTEXT_STATUS:
        raise ValueError(
            "context_status must be one of "
            f"{sorted(VALID_CONTEXT_STATUS)}, got {context_status!r}"
        )

    title = str(payload.get("title") or "").strip()
    if not title:
        raise ValueError("title is required")

    primary_tag_raw = payload.get("primary_tag")
    if primary_tag_raw is None:
        tags_value = payload.get("tags")
        if isinstance(tags_value, list) and tags_value:
            primary_tag_raw = tags_value[0]
        elif isinstance(tags_value, str) and tags_value.strip():
            primary_tag_raw = tags_value.split(",")[0]
        else:
            raise ValueError("primary_tag is required")
    primary_tag = normalize_tag(str(primary_tag_raw))
    tags = normalize_tags(payload.get("tags"), primary_tag)

    source = str(payload.get("source") or "codex-thread")
    source_locations = normalize_location_list(
        payload.get("source_locations", payload.get("source_paths")),
        "source_locations",
    )
    reference_locations = normalize_location_list(
        payload.get("reference_locations", payload.get("reference_paths")),
        "reference_locations",
    )
    entry_id = str(
        payload.get("entry_id") or build_entry_id(date, time_start, primary_tag, title)
    )

    sections = payload.get("sections")
    if not isinstance(sections, dict):
        raise ValueError("sections must be an object keyed by section name")
    normalized_sections = {
        section_name: normalize_section_body(sections.get(section_name))
        for section_name in SECTION_ORDER
    }

    return {
        "entry_id": entry_id,
        "date": date,
        "time_start": time_start,
        "time_end": time_end,
        "time_basis": time_basis,
        "category": category,
        "primary_tag": primary_tag,
        "tags": tags,
        "context_status": context_status,
        "source": source,
        "source_locations": source_locations,
        "reference_locations": reference_locations,
        "title": title,
        "sections": normalized_sections,
    }


def render_entry(entry: dict) -> str:
    heading = f"## {entry['date']}"
    if entry["time_start"] != "unknown":
        heading += f" {entry['time_start']}"
    heading += f" | {entry['primary_tag']} | {entry['title']}"

    lines = [heading, ""]
    for key in METADATA_ORDER:
        lines.append(f"{key}: {json.dumps(entry[key], ensure_ascii=True)}")
    for section_name in SECTION_ORDER:
        lines.extend(["", f"### {section_name}", entry["sections"][section_name]])
    return "\n".join(lines).rstrip() + "\n"


def ensure_root_heading(existing_text: str) -> str:
    if not existing_text.strip():
        return "# Learning Log\n"

    for line in existing_text.splitlines():
        stripped = line.strip()
        if stripped:
            if stripped == "# Learning Log":
                return existing_text
            break
    return "# Learning Log\n\n" + existing_text.lstrip()


def append_entry(log_path: Path, rendered_entry: str) -> None:
    existing_text = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    base_text = ensure_root_heading(existing_text).rstrip()
    final_text = f"{base_text}\n\n{rendered_entry.rstrip()}\n"
    log_path.write_text(final_text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        payload = load_payload(args.input)
        entry = normalize_payload(payload)
        rendered_entry = render_entry(entry)
        if args.render:
            sys.stdout.write(rendered_entry)
            return 0

        append_entry(args.log_path, rendered_entry)
        sys.stdout.write(
            f'Appended entry_id="{entry["entry_id"]}" log_path="{args.log_path}"\n'
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
