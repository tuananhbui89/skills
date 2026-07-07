#!/usr/bin/env python3
"""Fetch a YouTube transcript and save it to disk."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def extract_video_id(value: str) -> str:
    """Return a YouTube video ID from common URL formats or a bare ID."""
    candidate = value.strip()
    if VIDEO_ID_RE.fullmatch(candidate):
        return candidate

    parsed = urlparse(candidate)
    host = parsed.netloc.lower()
    path_parts = [part for part in parsed.path.split("/") if part]

    query_id = parse_qs(parsed.query).get("v", [None])[0]
    if query_id and VIDEO_ID_RE.fullmatch(query_id):
        return query_id

    if host.endswith("youtu.be") and path_parts:
        video_id = path_parts[0]
        if VIDEO_ID_RE.fullmatch(video_id):
            return video_id

    for marker in ("shorts", "embed", "live", "v"):
        if marker in path_parts:
            index = path_parts.index(marker)
            if len(path_parts) > index + 1:
                video_id = path_parts[index + 1]
                if VIDEO_ID_RE.fullmatch(video_id):
                    return video_id

    # Some copied URLs omit a scheme, which urlparse treats as a path.
    if not parsed.scheme and not parsed.netloc and "/" in candidate:
        return extract_video_id("https://" + candidate)

    raise ValueError(f"Could not extract an 11-character YouTube video ID from: {value}")


def snippet_to_dict(snippet: Any) -> dict[str, Any]:
    if isinstance(snippet, dict):
        return snippet
    return {
        "text": getattr(snippet, "text"),
        "start": getattr(snippet, "start"),
        "duration": getattr(snippet, "duration"),
    }


def sanitize_filename(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-")
    return safe or "youtube-transcript"


def fetch_transcript(args: argparse.Namespace) -> tuple[Any, list[dict[str, Any]], str | None]:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency: install with `python3 -m pip install youtube-transcript-api`."
        ) from exc

    api = YouTubeTranscriptApi()
    fallback_note = None
    try:
        fetched = api.fetch(
            args.video_id,
            languages=args.languages,
            preserve_formatting=args.preserve_formatting,
        )
    except Exception as primary_error:
        if not args.fallback_any:
            raise
        try:
            transcript = next(iter(api.list(args.video_id)))
            fetched = transcript.fetch(preserve_formatting=args.preserve_formatting)
            fallback_note = (
                "Requested language transcript was unavailable; fetched the first "
                "available transcript instead."
            )
        except Exception:
            raise primary_error

    if hasattr(fetched, "to_raw_data"):
        raw = fetched.to_raw_data()
    else:
        raw = [snippet_to_dict(snippet) for snippet in fetched]
    return fetched, raw, fallback_note


def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def write_transcript(
    output_path: Path,
    video_id: str,
    source: str,
    fetched: Any,
    snippets: list[dict[str, Any]],
    output_format: str,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_format == "json":
        payload = {
            "video_id": video_id,
            "source": source,
            "language": getattr(fetched, "language", None),
            "language_code": getattr(fetched, "language_code", None),
            "is_generated": getattr(fetched, "is_generated", None),
            "snippets": snippets,
        }
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return

    lines = [
        f"# YouTube Transcript",
        f"Source: {source}",
        f"Video ID: {video_id}",
        f"Language: {getattr(fetched, 'language', 'unknown')} ({getattr(fetched, 'language_code', 'unknown')})",
        f"Generated: {getattr(fetched, 'is_generated', 'unknown')}",
        "",
    ]
    for snippet in snippets:
        start = float(snippet.get("start", 0.0))
        text = str(snippet.get("text", "")).replace("\n", " ").strip()
        if text:
            lines.append(f"[{format_timestamp(start)}] {text}")
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch and save a YouTube transcript.")
    parser.add_argument("url_or_id", help="YouTube URL or 11-character video ID")
    parser.add_argument(
        "--languages",
        nargs="+",
        default=["en"],
        help="Language codes in priority order. Default: en",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory for the saved transcript. Default: current directory",
    )
    parser.add_argument("--filename", help="Optional output filename without directory")
    parser.add_argument(
        "--format",
        choices=["txt", "json"],
        default="txt",
        help="Output format. Default: txt",
    )
    parser.add_argument(
        "--preserve-formatting",
        action="store_true",
        help="Preserve YouTube transcript HTML formatting tags where available.",
    )
    parser.add_argument(
        "--no-fallback-any",
        dest="fallback_any",
        action="store_false",
        help="Do not fall back to another available transcript when requested languages fail.",
    )
    args = parser.parse_args(argv)
    args.video_id = extract_video_id(args.url_or_id)
    return args


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        fetched, snippets, fallback_note = fetch_transcript(args)
        filename = args.filename or f"youtube-transcript-{sanitize_filename(args.video_id)}.{args.format}"
        output_path = Path(args.output_dir).expanduser().resolve() / filename
        write_transcript(output_path, args.video_id, args.url_or_id, fetched, snippets, args.format)
        metadata = {
            "output_path": str(output_path),
            "video_id": args.video_id,
            "language": getattr(fetched, "language", None),
            "language_code": getattr(fetched, "language_code", None),
            "is_generated": getattr(fetched, "is_generated", None),
            "snippet_count": len(snippets),
            "format": args.format,
            "fallback_note": fallback_note,
        }
        print(json.dumps(metadata, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI should surface concise errors.
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
