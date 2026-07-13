#!/usr/bin/env python3
"""Inline local HTML image references as data URIs."""

from __future__ import annotations

import argparse
import base64
import html
import mimetypes
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlparse


IMG_SRC_RE = re.compile(
    r"(<img\b[^>]*?\bsrc=)(?P<quote>[\"'])(?P<src>.*?)(?P=quote)([^>]*>)",
    re.IGNORECASE | re.DOTALL,
)


def should_skip(src: str) -> bool:
    parsed = urlparse(src)
    if parsed.scheme in {"http", "https", "data", "mailto"}:
        return True
    return src.startswith("#")


def guess_mime(path: Path) -> str:
    if path.suffix.lower() == ".svg":
        return "image/svg+xml"
    mime, _ = mimetypes.guess_type(path.name)
    return mime or "application/octet-stream"


def inline_images(html_text: str, base_dir: Path) -> tuple[str, int, list[str]]:
    warnings: list[str] = []
    count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        src = html.unescape(match.group("src"))
        if should_skip(src):
            return match.group(0)
        parsed = urlparse(src)
        if parsed.scheme and parsed.scheme != "file":
            return match.group(0)
        relative = unquote(parsed.path if parsed.scheme == "file" else src)
        image_path = (base_dir / relative).resolve()
        try:
            image_path.relative_to(base_dir.resolve())
        except ValueError:
            warnings.append(f"skipped image outside base dir: {src}")
            return match.group(0)
        if not image_path.exists() or not image_path.is_file():
            warnings.append(f"missing image: {src}")
            return match.group(0)
        data = base64.b64encode(image_path.read_bytes()).decode("ascii")
        data_uri = f"data:{guess_mime(image_path)};base64,{data}"
        count += 1
        return f"{match.group(1)}{match.group('quote')}{data_uri}{match.group('quote')}{match.group(4)}"

    return IMG_SRC_RE.sub(replace, html_text), count, warnings


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inline local <img> sources in an HTML file.")
    parser.add_argument("html_file", type=Path, help="HTML file to update")
    parser.add_argument(
        "--base-dir",
        type=Path,
        help="Directory for resolving relative image paths (default: HTML file directory)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output HTML path (default: overwrite the input file)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    html_file = args.html_file.expanduser().resolve()
    if not html_file.exists():
        print(f"error: HTML file not found: {html_file}", file=sys.stderr)
        return 2
    base_dir = (args.base_dir.expanduser().resolve() if args.base_dir else html_file.parent)
    output = args.output.expanduser().resolve() if args.output else html_file
    html_text = html_file.read_text(encoding="utf-8")
    updated, count, warnings = inline_images(html_text, base_dir)
    output.write_text(updated, encoding="utf-8")
    print(f"inlined={count}")
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
