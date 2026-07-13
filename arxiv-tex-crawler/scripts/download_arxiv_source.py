#!/usr/bin/env python3
"""Download and extract an arXiv source package."""

from __future__ import annotations

import argparse
import gzip
import os
from pathlib import Path
import re
import shutil
import sys
import tarfile
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen
import zipfile


NEW_ID_RE = re.compile(r"^\d{4}\.\d{4,5}(?:v\d+)?$")
OLD_ID_RE = re.compile(r"^[a-z-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?$")


def normalize_arxiv_id(value: str) -> str:
    text = value.strip().strip("<>")
    if text.lower().startswith("arxiv:"):
        text = text.split(":", 1)[1]

    parsed = urlparse(text)
    if parsed.scheme and parsed.netloc:
        path = unquote(parsed.path).strip("/")
        parts = path.split("/")
        if parsed.netloc.lower().endswith("arxiv.org") and parts:
            if parts[0] in {"abs", "html", "pdf", "e-print", "src"}:
                paper_id = "/".join(parts[1:])
            else:
                paper_id = "/".join(parts)
        else:
            raise ValueError(f"not an arXiv URL: {value}")
    else:
        paper_id = text.split("?", 1)[0].split("#", 1)[0].strip("/")

    if paper_id.endswith(".pdf"):
        paper_id = paper_id[:-4]
    paper_id = paper_id.strip("/")

    if NEW_ID_RE.match(paper_id) or OLD_ID_RE.match(paper_id):
        return paper_id
    raise ValueError(f"could not parse a valid arXiv ID from: {value}")


def safe_dir_name(arxiv_id: str) -> str:
    return arxiv_id.replace("/", "_")


def ensure_clean_destination(path: Path, force: bool) -> None:
    if path.exists() and not path.is_dir():
        if not force:
            raise FileExistsError(f"destination exists and is not a directory: {path}")
        path.unlink()
    if path.exists() and any(path.iterdir()):
        if not force:
            raise FileExistsError(f"destination already exists and is not empty: {path}")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def ensure_within_directory(base: Path, target: Path) -> None:
    base_resolved = base.resolve()
    target_resolved = target.resolve()
    if os.path.commonpath([base_resolved, target_resolved]) != str(base_resolved):
        raise ValueError(f"archive member escapes destination: {target}")


def safe_extract_tar(archive: Path, dest: Path) -> None:
    with tarfile.open(archive, "r:*") as tar:
        for member in tar.getmembers():
            ensure_within_directory(dest, dest / member.name)
            if not (member.isfile() or member.isdir()):
                raise ValueError(f"unsupported archive member type: {member.name}")
        try:
            tar.extractall(dest, filter="data")
        except TypeError:
            tar.extractall(dest)


def safe_extract_zip(archive: Path, dest: Path) -> None:
    with zipfile.ZipFile(archive) as zf:
        for member in zf.infolist():
            ensure_within_directory(dest, dest / member.filename)
        zf.extractall(dest)


def looks_like_html(path: Path) -> bool:
    head = path.read_bytes()[:512].lstrip().lower()
    return head.startswith(b"<!doctype html") or head.startswith(b"<html")


def copy_stream_from_url(url: str, target: Path) -> None:
    request = Request(
        url,
        headers={
            "User-Agent": "Codex arxiv-tex-crawler/1.0 (+https://arxiv.org)",
        },
    )
    try:
        with urlopen(request, timeout=60) as response, target.open("wb") as out:
            shutil.copyfileobj(response, out)
    except HTTPError as exc:
        raise RuntimeError(f"download failed with HTTP {exc.code}: {url}") from exc
    except URLError as exc:
        raise RuntimeError(f"download failed: {exc.reason}") from exc


def extract_package(archive: Path, dest: Path, arxiv_id: str) -> str:
    if looks_like_html(archive):
        raise RuntimeError("downloaded file looks like HTML, not an arXiv source package")

    if tarfile.is_tarfile(archive):
        safe_extract_tar(archive, dest)
        return "tar"

    if zipfile.is_zipfile(archive):
        safe_extract_zip(archive, dest)
        return "zip"

    data = archive.read_bytes()[:8]
    if data.startswith(b"\x1f\x8b"):
        tex_name = f"{safe_dir_name(arxiv_id)}.tex"
        with gzip.open(archive, "rb") as src, (dest / tex_name).open("wb") as out:
            shutil.copyfileobj(src, out)
        return "gzip-single-file"

    if data.startswith(b"%PDF"):
        shutil.copy2(archive, dest / f"{safe_dir_name(arxiv_id)}.pdf")
        return "pdf"

    if archive.stat().st_size > 0:
        shutil.copy2(archive, dest / f"{safe_dir_name(arxiv_id)}.tex")
        return "raw-file"

    raise RuntimeError("downloaded source package is empty")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download an arXiv source package and extract it."
    )
    parser.add_argument("url_or_id", help="arXiv html/abs/pdf/e-print URL or raw arXiv ID")
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Parent directory for the extracted <id>-source folder (default: current directory)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing non-empty extraction directory",
    )
    parser.add_argument(
        "--keep-archive",
        action="store_true",
        help="Keep the downloaded source package after extraction",
    )
    parser.add_argument(
        "--archive",
        help="Extract this local archive instead of downloading; useful for testing or retries",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the normalized arXiv ID and e-print URL without downloading",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        arxiv_id = normalize_arxiv_id(args.url_or_id)
        eprint_url = f"https://arxiv.org/e-print/{arxiv_id}"
        dest = Path(args.output_dir).expanduser().resolve() / f"{safe_dir_name(arxiv_id)}-source"

        if args.dry_run:
            print(f"arxiv_id={arxiv_id}")
            print(f"eprint_url={eprint_url}")
            print(f"destination={dest}")
            return 0

        ensure_clean_destination(dest, args.force)
        archive = Path(args.archive).expanduser().resolve() if args.archive else dest / f"{safe_dir_name(arxiv_id)}.tar.gz"

        if args.archive:
            if not archive.exists():
                raise FileNotFoundError(f"local archive not found: {archive}")
        else:
            copy_stream_from_url(eprint_url, archive)

        package_type = extract_package(archive, dest, arxiv_id)

        if not args.keep_archive and not args.archive and archive.exists():
            archive.unlink()

        print(f"arxiv_id={arxiv_id}")
        print(f"eprint_url={eprint_url}")
        print(f"destination={dest}")
        print(f"package_type={package_type}")
        if args.keep_archive or args.archive:
            print(f"archive={archive}")
        else:
            print("archive_removed=true")
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
