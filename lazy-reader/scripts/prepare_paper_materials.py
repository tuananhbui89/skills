#!/usr/bin/env python3
"""Prepare source, HTML/PDF fallbacks, and reusable assets for arXiv notes."""

from __future__ import annotations

import argparse
import json
import mimetypes
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ARXIV_CRAWLER = Path(
    "/Users/tuananhbui/.codex/skills/arxiv-tex-crawler/scripts/download_arxiv_source.py"
)
IMAGE_EXTENSIONS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".pdf",
    ".eps",
    ".ps",
)
RASTER_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
ENV_RE = re.compile(
    r"\\begin\{(?P<env>figure\*?|table\*?)\}(?P<body>.*?)\\end\{(?P=env)\}",
    re.DOTALL,
)
GRAPHICS_RE = re.compile(r"\\includegraphics(?:\s*\[[^\]]*\])?\s*\{([^}]+)\}")


def run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def parse_key_values(output: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in output.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key.strip()] = value.strip()
    return result


def normalize_arxiv(url_or_id: str) -> dict[str, str]:
    cmd = [sys.executable, str(ARXIV_CRAWLER), url_or_id, "--dry-run"]
    proc = run_command(cmd)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "could not normalize arXiv input")
    values = parse_key_values(proc.stdout)
    if "arxiv_id" not in values or "eprint_url" not in values:
        raise RuntimeError(f"unexpected crawler dry-run output: {proc.stdout}")
    return values


def safe_id(arxiv_id: str) -> str:
    return arxiv_id.replace("/", "_")


def strip_tex_comments(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        escaped = False
        kept: list[str] = []
        for char in line:
            if char == "%" and not escaped:
                break
            kept.append(char)
            escaped = char == "\\" and not escaped
            if char != "\\":
                escaped = False
        lines.append("".join(kept))
    return "\n".join(lines)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="replace")


def tex_has_document_markers(path: Path) -> bool:
    text = read_text(path)
    return "\\documentclass" in text or "\\begin{document}" in text


def rank_tex_file(path: Path) -> int:
    text = read_text(path)
    score = 0
    if "\\documentclass" in text:
        score += 100
    if "\\begin{document}" in text:
        score += 100
    if "\\title" in text:
        score += 15
    if "\\begin{abstract}" in text:
        score += 15
    if path.name.lower() in {"main.tex", "paper.tex", "article.tex", "ms.tex"}:
        score += 10
    return score


def find_root_tex_files(source_dir: Path) -> list[Path]:
    tex_files = sorted(source_dir.rglob("*.tex"))
    roots = [path for path in tex_files if tex_has_document_markers(path)]
    return sorted(roots or tex_files, key=lambda path: (-rank_tex_file(path), len(path.parts), path.name))


def resolve_tex_include(name: str, current_dir: Path, source_dir: Path) -> Path | None:
    clean = name.strip().strip("{}").strip()
    if not clean:
        return None
    candidates = [Path(clean)]
    if not candidates[0].suffix:
        candidates.append(Path(f"{clean}.tex"))
    for candidate in candidates:
        for base in (current_dir, source_dir):
            path = (base / candidate).resolve()
            try:
                path.relative_to(source_dir.resolve())
            except ValueError:
                continue
            if path.exists() and path.is_file():
                return path
    return None


INPUT_RE = re.compile(r"\\(?:input|include)(?![a-zA-Z])\s*(?:\{([^}]+)\}|([^\s%{}]+))")


def expand_tex(path: Path, source_dir: Path, seen: set[Path] | None = None) -> str:
    seen = seen or set()
    path = path.resolve()
    if path in seen:
        return f"\n% Skipped recursive include: {path.name}\n"
    seen.add(path)
    text = strip_tex_comments(read_text(path))

    def replace(match: re.Match[str]) -> str:
        include_name = match.group(1) or match.group(2) or ""
        include_path = resolve_tex_include(include_name, path.parent, source_dir)
        if include_path is None:
            return f"\n% Unresolved include: {include_name}\n"
        return "\n" + expand_tex(include_path, source_dir, seen) + "\n"

    return INPUT_RE.sub(replace, text)


def find_balanced_argument(text: str, command: str) -> str:
    start = text.find(f"\\{command}")
    if start < 0:
        return ""
    brace_start = text.find("{", start)
    if brace_start < 0:
        return ""
    depth = 0
    for index in range(brace_start, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[brace_start + 1 : index]
    return ""


def tex_to_plain_text(value: str) -> str:
    text = strip_tex_comments(value)
    text = re.sub(r"\\label\{[^}]*\}", "", text)
    text = re.sub(r"\\includegraphics(?:\s*\[[^\]]*\])?\s*\{[^}]*\}", "", text)
    for _ in range(8):
        new_text = re.sub(r"\\[a-zA-Z]+\*?(?:\s*\[[^\]]*\])?\s*\{([^{}]*)\}", r"\1", text)
        if new_text == text:
            break
        text = new_text
    replacements = {
        r"\%": "%",
        r"\_": "_",
        r"\&": "&",
        r"\#": "#",
        r"\$": "$",
        "~": " ",
        "$": "",
        "{": "",
        "}": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"\\[a-zA-Z]+\*?", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_label(tex: str) -> str:
    match = re.search(r"\\label\{([^}]+)\}", tex)
    return match.group(1).strip() if match else ""


def split_latex_row(row: str) -> list[str]:
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    depth = 0
    for char in row:
        if char == "\\" and not escaped:
            escaped = True
            current.append(char)
            continue
        if char == "{" and not escaped:
            depth += 1
        elif char == "}" and not escaped and depth > 0:
            depth -= 1
        if char == "&" and not escaped and depth == 0:
            cells.append("".join(current))
            current = []
        else:
            current.append(char)
        escaped = False
    cells.append("".join(current))
    return [tex_to_plain_text(cell) for cell in cells]


def latex_table_to_markdown(tex: str) -> str:
    match = re.search(r"\\begin\{tabular\}\{[^}]*\}(.*?)\\end\{tabular\}", tex, re.DOTALL)
    if not match:
        return ""
    body = match.group(1)
    body = re.sub(r"\\(?:toprule|midrule|bottomrule|hline|cline\{[^}]*\})", "", body)
    rows = []
    for raw_row in re.split(r"\\\\", body):
        row = raw_row.strip()
        if not row:
            continue
        cells = [cell for cell in split_latex_row(row) if cell]
        if cells:
            rows.append(cells)
    if len(rows) < 2:
        return ""
    width = max(len(row) for row in rows)
    normalized = [row + [""] * (width - len(row)) for row in rows]
    header = normalized[0]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * width) + " |",
    ]
    for row in normalized[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def resolve_graphic_path(name: str, tex_file: Path, source_dir: Path) -> Path | None:
    raw = name.strip()
    candidate = Path(raw)
    names = [candidate]
    if not candidate.suffix:
        names.extend(Path(f"{raw}{ext}") for ext in IMAGE_EXTENSIONS)
    bases = [tex_file.parent, source_dir]
    for base in bases:
        for name_candidate in names:
            path = (base / name_candidate).resolve()
            try:
                path.relative_to(source_dir.resolve())
            except ValueError:
                continue
            if path.exists() and path.is_file():
                return path
    target_names = {path.name for path in names}
    for path in source_dir.rglob("*"):
        if path.is_file() and path.name in target_names:
            return path
    return None


def unique_destination(figures_dir: Path, desired_name: str) -> Path:
    dest = figures_dir / desired_name
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    index = 2
    while True:
        candidate = figures_dir / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def copy_or_convert_graphic(source: Path, figures_dir: Path) -> Path | None:
    suffix = source.suffix.lower()
    figures_dir.mkdir(parents=True, exist_ok=True)
    if suffix in RASTER_EXTENSIONS:
        dest = unique_destination(figures_dir, source.name)
        shutil.copy2(source, dest)
        return dest
    if suffix in {".pdf", ".eps", ".ps"} and shutil.which("sips"):
        dest = unique_destination(figures_dir, f"{source.stem}.png")
        proc = run_command(["sips", "-s", "format", "png", str(source), "--out", str(dest)])
        if proc.returncode == 0 and dest.exists():
            return dest
        if dest.exists():
            dest.unlink()
    return None


def extract_assets(expanded_tex: str, root_tex: Path, source_dir: Path, output_dir: Path) -> list[dict[str, object]]:
    figures_dir = output_dir / "figures"
    assets: list[dict[str, object]] = []
    counters = {"figure": 0, "table": 0}

    for match in ENV_RE.finditer(expanded_tex):
        env = match.group("env")
        body = match.group("body")
        kind = "figure" if env.startswith("figure") else "table"
        counters[kind] += 1
        caption = tex_to_plain_text(find_balanced_argument(body, "caption"))
        label = extract_label(body)
        entry: dict[str, object] = {
            "kind": kind,
            "index": counters[kind],
            "environment": env,
            "label": label,
            "caption": caption,
            "source_tex": str(root_tex),
            "markdown": "",
            "graphics": [],
            "copied_graphics": [],
        }

        if kind == "figure":
            copied: list[str] = []
            graphics: list[str] = []
            for graphic in GRAPHICS_RE.findall(body):
                resolved = resolve_graphic_path(graphic, root_tex, source_dir)
                graphics.append(str(resolved or graphic))
                if resolved is not None:
                    copied_path = copy_or_convert_graphic(resolved, figures_dir)
                    if copied_path is not None:
                        copied.append(str(copied_path.relative_to(output_dir)))
            entry["graphics"] = graphics
            entry["copied_graphics"] = copied
            if copied:
                alt = caption or label or f"Figure {counters[kind]}"
                entry["markdown"] = f"![{alt}]({copied[0]})"
        else:
            table_markdown = latex_table_to_markdown(body)
            entry["markdown"] = table_markdown
            entry["latex"] = body.strip()

        assets.append(entry)
    return assets


def write_asset_snippets(path: Path, assets: list[dict[str, object]]) -> None:
    lines = ["# Paper Assets", ""]
    if not assets:
        lines.extend(["No figure or table environments were extracted.", ""])
    for asset in assets:
        kind = str(asset["kind"]).title()
        index = asset["index"]
        label = asset.get("label") or "unlabeled"
        caption = asset.get("caption") or "No caption extracted."
        lines.extend([f"## {kind} {index}: {label}", "", f"Caption: {caption}", ""])
        markdown = str(asset.get("markdown") or "")
        if markdown:
            lines.extend([markdown, ""])
        elif asset.get("kind") == "figure":
            graphics = asset.get("graphics") or []
            lines.extend(["No embeddable figure file was copied.", ""])
            if graphics:
                lines.extend(["Referenced graphics:", ""])
                for graphic in graphics:
                    lines.append(f"- `{graphic}`")
                lines.append("")
        latex = str(asset.get("latex") or "")
        if latex and not markdown:
            lines.extend(["```tex", latex, "```", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def fetch_url(url: str, target: Path, expected: str, warnings: list[str]) -> bool:
    request = Request(url, headers={"User-Agent": "Codex lazy-reader/1.0"})
    try:
        with urlopen(request, timeout=60) as response:
            data = response.read()
    except HTTPError as exc:
        warnings.append(f"{url} returned HTTP {exc.code}")
        return False
    except URLError as exc:
        warnings.append(f"{url} failed: {exc.reason}")
        return False
    except TimeoutError:
        warnings.append(f"{url} timed out")
        return False

    head = data[:2048].lstrip().lower()
    if expected == "html" and not (head.startswith(b"<!doctype html") or head.startswith(b"<html")):
        warnings.append(f"{url} did not look like HTML")
        return False
    if expected == "pdf" and not head.startswith(b"%pdf"):
        warnings.append(f"{url} did not look like a PDF")
        return False
    target.write_bytes(data)
    return True


def copy_source_dir(source_dir: Path, dest: Path, force: bool) -> None:
    if dest.exists():
        if not force:
            raise FileExistsError(f"source destination already exists: {dest}")
        shutil.rmtree(dest)
    shutil.copytree(source_dir, dest)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare materials for a lazy-reader arXiv report.")
    parser.add_argument("url_or_id", help="arXiv html/abs/pdf/e-print URL or raw arXiv ID")
    parser.add_argument(
        "--output-root",
        default="docs/lazy-reader",
        help="Root directory for generated paper folders (default: docs/lazy-reader)",
    )
    parser.add_argument("--force", action="store_true", help="Replace existing generated files")
    parser.add_argument(
        "--source-dir",
        type=Path,
        help="Use an existing extracted TeX source directory instead of invoking arxiv-tex-crawler",
    )
    parser.add_argument(
        "--archive",
        type=Path,
        help="Pass a local source archive to arxiv-tex-crawler; useful for offline tests and retries",
    )
    parser.add_argument("--skip-html", action="store_true", help="Do not download arXiv HTML")
    parser.add_argument("--skip-pdf", action="store_true", help="Do not download PDF fallback")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    warnings: list[str] = []

    try:
        normalized = normalize_arxiv(args.url_or_id)
        arxiv_id = normalized["arxiv_id"]
        paper_key = safe_id(arxiv_id)
        output_root = Path(args.output_root).expanduser().resolve()
        output_dir = output_root / paper_key

        if output_dir.exists() and args.force:
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        source_dir = output_dir / f"{paper_key}-source"
        if args.source_dir:
            copy_source_dir(args.source_dir.expanduser().resolve(), source_dir, args.force)
        else:
            crawler_cmd = [
                sys.executable,
                str(ARXIV_CRAWLER),
                args.url_or_id,
                "--output-dir",
                str(output_dir),
            ]
            if args.force:
                crawler_cmd.append("--force")
            if args.archive:
                crawler_cmd.extend(["--archive", str(args.archive.expanduser().resolve())])
            crawler_proc = run_command(crawler_cmd)
            if crawler_proc.returncode != 0:
                warnings.append(crawler_proc.stderr.strip() or "arxiv-tex-crawler failed")

        html_path = output_dir / "paper.html"
        html_saved = False
        if not args.skip_html:
            html_saved = fetch_url(f"https://arxiv.org/html/{arxiv_id}", html_path, "html", warnings)

        expanded_path = output_dir / "paper_source_expanded.tex"
        root_tex_path = ""
        tex_available = False
        assets: list[dict[str, object]] = []
        if source_dir.exists():
            roots = find_root_tex_files(source_dir)
            if roots:
                root = roots[0]
                root_tex_path = str(root)
                expanded = expand_tex(root, source_dir)
                expanded_path.write_text(expanded, encoding="utf-8")
                tex_available = True
                assets = extract_assets(expanded, root, source_dir, output_dir)
            else:
                warnings.append(f"no .tex files found in {source_dir}")
        else:
            warnings.append(f"source directory not available: {source_dir}")

        manifest_path = output_dir / "asset_manifest.json"
        snippets_path = output_dir / "asset_snippets.md"
        manifest_path.write_text(json.dumps(assets, indent=2), encoding="utf-8")
        write_asset_snippets(snippets_path, assets)

        pdf_path = output_dir / "paper.pdf"
        pdf_saved = False
        if not args.skip_pdf and not html_saved and not tex_available:
            pdf_saved = fetch_url(f"https://arxiv.org/pdf/{arxiv_id}", pdf_path, "pdf", warnings)

        markdown_path = output_dir / f"{paper_key}-lazy-reader.md"
        html_output_path = output_dir / f"{paper_key}-lazy-reader.html"
        summary = {
            "arxiv_id": arxiv_id,
            "eprint_url": normalized["eprint_url"],
            "output_dir": str(output_dir),
            "source_dir": str(source_dir) if source_dir.exists() else "",
            "paper_html": str(html_path) if html_saved else "",
            "paper_pdf": str(pdf_path) if pdf_saved else "",
            "expanded_tex": str(expanded_path) if tex_available else "",
            "root_tex": root_tex_path,
            "asset_manifest": str(manifest_path),
            "asset_snippets": str(snippets_path),
            "markdown_output": str(markdown_path),
            "html_output": str(html_output_path),
            "asset_count": len(assets),
            "warnings": warnings,
        }
        (output_dir / "materials_summary.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
        print(json.dumps(summary, indent=2))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
