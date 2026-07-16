#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

try:
    import mistune
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("mistune is required: python3 -m pip install mistune") from exc

try:
    from latex2mathml.converter import convert as latex_to_mathml
except ImportError:  # pragma: no cover - optional offline renderer
    latex_to_mathml = None

try:
    from mistune.plugins.math import math as mistune_math
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("Mistune's math plugin is required; upgrade mistune") from exc


ARTICLE_CSS = """
:root {
  color-scheme: light;
  --bg: #f7f7f4;
  --paper: #ffffff;
  --ink: #1f2933;
  --muted: #5f6f7a;
  --line: #d8ddd7;
  --accent: #276c77;
  --accent-soft: #e4f1f2;
  --code-bg: #111827;
  --code-ink: #e5edf2;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.65;
}

main {
  width: min(100% - 32px, 1220px);
  margin: 0 auto;
  padding: 48px 0;
  display: grid;
  grid-template-columns: minmax(0, 240px) minmax(0, 920px);
  gap: 24px;
  align-items: start;
}

article {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: clamp(24px, 5vw, 56px);
  box-shadow: 0 18px 45px rgba(31, 41, 51, 0.08);
  min-width: 0;
}

.toc {
  position: sticky;
  top: 24px;
  max-height: calc(100vh - 48px);
  overflow: auto;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 12px 30px rgba(31, 41, 51, 0.06);
}

.toc-title {
  color: #162129;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0;
  margin: 0 0 10px;
  text-transform: uppercase;
}

.toc ol {
  list-style: none;
  margin: 0;
  padding: 0;
}

.toc li {
  font-size: 0.92rem;
  line-height: 1.35;
  margin: 0;
}

.toc a {
  border-radius: 6px;
  color: var(--muted);
  display: block;
  padding: 6px 8px;
  text-decoration: none;
}

.toc a:hover,
.toc a:focus {
  background: var(--accent-soft);
  color: var(--accent);
}

.toc-level-3 {
  padding-left: 12px;
}

.toc-level-4,
.toc-level-5,
.toc-level-6 {
  padding-left: 24px;
}

h1,
h2,
h3 {
  line-height: 1.18;
  color: #162129;
  letter-spacing: 0;
}

h1 {
  font-size: clamp(2rem, 5vw, 3.8rem);
  margin: 0 0 24px;
}

h2 {
  font-size: 1.45rem;
  margin-top: 40px;
  padding-top: 10px;
}

h3 {
  font-size: 1.15rem;
  margin-top: 28px;
}

article [id] {
  scroll-margin-top: 24px;
}

p,
li {
  font-size: 1.02rem;
}

a {
  color: var(--accent);
  text-underline-offset: 3px;
}

blockquote {
  border-left: 4px solid var(--accent);
  color: var(--muted);
  margin: 24px 0;
  padding: 4px 0 4px 18px;
}

pre {
  background: var(--code-bg);
  color: var(--code-ink);
  border-radius: 8px;
  overflow-x: auto;
  padding: 16px;
  margin: 18px 0;
  font-size: 0.95rem;
}

code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
}

:not(pre) > code {
  background: var(--accent-soft);
  border-radius: 4px;
  padding: 0.12rem 0.28rem;
}

.math-display {
  margin: 24px 0;
  overflow-x: auto;
  padding: 4px 0;
}

.math-display math {
  display: block;
  margin: 0 auto;
  width: max-content;
  max-width: 100%;
}

.math-inline math {
  vertical-align: -0.2em;
}

.math-display mjx-container[display="true"] {
  margin: 0 auto !important;
}

.math-inline mjx-container {
  margin: 0 !important;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  font-size: 0.96rem;
}

th,
td {
  border: 1px solid var(--line);
  padding: 10px 12px;
  text-align: left;
  vertical-align: top;
}

th {
  background: var(--accent-soft);
}

ol,
ul {
  padding-left: 1.4rem;
}

li {
  margin: 10px 0;
}

hr {
  border: 0;
  border-top: 1px solid var(--line);
  margin: 36px 0;
}

@media (max-width: 1020px) {
  main {
    width: min(100% - 20px, 920px);
    padding: 20px 0;
    display: block;
  }

  .toc {
    margin-bottom: 16px;
    max-height: none;
    position: static;
  }

  article {
    padding: 22px;
  }
}
""".strip()


def strip_inline_markdown(value: str) -> str:
    value = re.sub(r"`([^`]*)`", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[*_~#]+", "", value)
    return value.strip()


def infer_title(markdown_text: str, input_path: Path) -> str:
    for line in markdown_text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*#*\s*$", line)
        if match:
            return strip_inline_markdown(match.group(1))
    return input_path.stem.replace("-", " ").replace("_", " ").title()


def render_markdown(markdown_text: str, math_renderer: str) -> str:
    plugin_sets = (
        ("table", "strikethrough", "task_lists"),
        ("table", "strikethrough"),
        ("table",),
        (),
    )
    last_error: Exception | None = None
    for plugins in plugin_sets:
        try:
            markdown = mistune.create_markdown(
                escape=True, plugins=[*plugins, mistune_math]
            )
            body_html = markdown(normalize_latex_delimiters(markdown_text))
            if math_renderer == "mathjax":
                return render_mathjax(body_html)
            return render_mathml(body_html)
        except Exception as exc:  # pragma: no cover - fallback for mistune variants
            last_error = exc
    raise RuntimeError(f"Unable to render Markdown: {last_error}")


FENCED_CODE_RE = re.compile(r"(^```.*?^```)", re.MULTILINE | re.DOTALL)
BRACKET_DISPLAY_MATH_RE = re.compile(r"\\\[(.*?)\\\]", re.DOTALL)
PAREN_INLINE_MATH_RE = re.compile(r"\\\((.*?)\\\)", re.DOTALL)
BLOCK_MATH_HTML_RE = re.compile(
    r'<div class="math">\$\$\s*(.*?)\s*\$\$</div>', re.DOTALL
)
INLINE_MATH_HTML_RE = re.compile(
    r'<span class="math">\\\((.*?)\\\)</span>', re.DOTALL
)


def normalize_latex_delimiters(markdown_text: str) -> str:
    """Normalize common LaTeX delimiters without changing fenced code samples."""

    def normalize_prose(segment: str) -> str:
        segment = BRACKET_DISPLAY_MATH_RE.sub(
            lambda match: f"$$\n{match.group(1).strip()}\n$$", segment
        )
        return PAREN_INLINE_MATH_RE.sub(
            lambda match: f"${match.group(1).strip()}$", segment
        )

    return "".join(
        segment if FENCED_CODE_RE.fullmatch(segment) else normalize_prose(segment)
        for segment in FENCED_CODE_RE.split(markdown_text)
    )


def mathml(latex: str, display: bool) -> str:
    """Convert a LaTeX expression into self-contained, browser-native MathML."""

    if latex_to_mathml is None:
        raise RuntimeError(
            "latex2mathml is required for --math-renderer mathml: "
            "python3 -m pip install latex2mathml"
        )
    rendered = latex_to_mathml(latex.strip())
    if display:
        rendered = rendered.replace('display="inline"', 'display="block"', 1)
    return rendered


def render_mathml(body_html: str) -> str:
    def render_block(match: re.Match[str]) -> str:
        return f'<div class="math-display">{mathml(match.group(1), display=True)}</div>'

    def render_inline(match: re.Match[str]) -> str:
        return f'<span class="math-inline">{mathml(match.group(1), display=False)}</span>'

    body_html = BLOCK_MATH_HTML_RE.sub(render_block, body_html)
    return INLINE_MATH_HTML_RE.sub(render_inline, body_html)


def render_mathjax(body_html: str) -> str:
    """Keep TeX delimiters for MathJax's more complete TeX parser."""

    def render_block(match: re.Match[str]) -> str:
        return f'<div class="math-display">\\[\n{match.group(1).strip()}\n\\]</div>'

    return BLOCK_MATH_HTML_RE.sub(render_block, body_html)


MATHJAX_HEAD = """  <script>
    window.MathJax = {
      tex: {
        inlineMath: [['\\\\(', '\\\\)'], ['$', '$']],
        displayMath: [['\\\\[', '\\\\]'], ['$$', '$$']]
      },
      svg: { fontCache: 'global' }
    };
  </script>
  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
"""


HEADING_RE = re.compile(r"<h([1-6])>(.*?)</h\1>", re.DOTALL)
HTML_TAG_RE = re.compile(r"(<[^>]+>)")
URL_RE = re.compile(r"https?://[^\s<]+")
ANCHOR_RE = re.compile(r"<a\b(?P<attrs>[^>]*)>", re.IGNORECASE)
HREF_RE = re.compile(r'\bhref=(["\'])(?P<href>.*?)\1', re.IGNORECASE)
TAG_NAME_RE = re.compile(r"</?\s*([a-zA-Z][\w:-]*)")
DISABLED_LINKIFY_TAGS = {"a", "code", "pre", "script", "style"}
TRAILING_URL_PUNCTUATION = ".,;:"


def heading_text(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", "", fragment)
    return html.unescape(text).strip()


def slugify_heading(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "section"


def add_heading_anchors(body_html: str) -> tuple[str, list[tuple[int, str, str]]]:
    toc_entries: list[tuple[int, str, str]] = []
    slug_counts: dict[str, int] = {}

    def replace(match: re.Match[str]) -> str:
        level = int(match.group(1))
        inner_html = match.group(2)
        text = heading_text(inner_html)
        if not text:
            return match.group(0)

        base_slug = slugify_heading(text)
        count = slug_counts.get(base_slug, 0)
        slug_counts[base_slug] = count + 1
        heading_id = base_slug if count == 0 else f"{base_slug}-{count + 1}"

        if level >= 2:
            toc_entries.append((level, heading_id, text))

        return f'<h{level} id="{html.escape(heading_id, quote=True)}">{inner_html}</h{level}>'

    return HEADING_RE.sub(replace, body_html), toc_entries


def split_trailing_url_punctuation(value: str) -> tuple[str, str]:
    trailing = ""
    while value and value[-1] in TRAILING_URL_PUNCTUATION:
        trailing = value[-1] + trailing
        value = value[:-1]

    while value.endswith(")") and value.count("(") < value.count(")"):
        trailing = ")" + trailing
        value = value[:-1]

    return value, trailing


def linkify_text_segment(value: str) -> str:
    def replace(match: re.Match[str]) -> str:
        url, trailing = split_trailing_url_punctuation(match.group(0))
        if not url:
            return match.group(0)

        href = html.escape(html.unescape(url), quote=True)
        return (
            f'<a href="{href}">{url}</a>'
            f"{trailing}"
        )

    return URL_RE.sub(replace, value)


def linkify_plain_urls(body_html: str) -> str:
    parts = HTML_TAG_RE.split(body_html)
    disabled_stack: list[str] = []
    output: list[str] = []

    for part in parts:
        if not part:
            continue

        if HTML_TAG_RE.fullmatch(part):
            output.append(part)
            tag_match = TAG_NAME_RE.match(part)
            if not tag_match:
                continue

            tag_name = tag_match.group(1).lower()
            if tag_name not in DISABLED_LINKIFY_TAGS:
                continue

            if part.startswith("</"):
                if tag_name in disabled_stack:
                    disabled_stack.remove(tag_name)
            elif not part.rstrip().endswith("/>"):
                disabled_stack.append(tag_name)
            continue

        output.append(part if disabled_stack else linkify_text_segment(part))

    return "".join(output)


def make_external_links_open_in_new_tabs(body_html: str) -> str:
    def replace(match: re.Match[str]) -> str:
        attrs = match.group("attrs")
        href_match = HREF_RE.search(attrs)
        if not href_match:
            return match.group(0)

        href = html.unescape(href_match.group("href"))
        if not href.startswith(("http://", "https://")):
            return match.group(0)

        if not re.search(r"\btarget\s*=", attrs, re.IGNORECASE):
            attrs += ' target="_blank"'
        if not re.search(r"\brel\s*=", attrs, re.IGNORECASE):
            attrs += ' rel="noopener noreferrer"'

        return f"<a{attrs}>"

    return ANCHOR_RE.sub(replace, body_html)


def prepare_article_html(body_html: str) -> tuple[str, list[tuple[int, str, str]]]:
    body_html, toc_entries = add_heading_anchors(body_html)
    body_html = linkify_plain_urls(body_html)
    body_html = make_external_links_open_in_new_tabs(body_html)
    return body_html, toc_entries


def build_toc_html(toc_entries: list[tuple[int, str, str]]) -> str:
    if not toc_entries:
        return ""

    links = "\n".join(
        "        "
        f'<li class="toc-level-{level}"><a href="#{html.escape(heading_id, quote=True)}">'
        f"{html.escape(text)}</a></li>"
        for level, heading_id, text in toc_entries
    )
    return f"""    <aside class="toc" aria-label="Table of contents">
      <p class="toc-title">Contents</p>
      <nav>
        <ol>
{links}
        </ol>
      </nav>
    </aside>
"""


def build_html_document(title: str, body_html: str, math_renderer: str) -> str:
    escaped_title = html.escape(title, quote=True)
    body_html, toc_entries = prepare_article_html(body_html)
    toc_html = build_toc_html(toc_entries)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title}</title>
{MATHJAX_HEAD if math_renderer == "mathjax" else ""}  <style>
{ARTICLE_CSS}
  </style>
</head>
<body>
  <main>
{toc_html.rstrip()}
    <article>
{body_html.rstrip()}
    </article>
  </main>
</body>
</html>
"""


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a Markdown file into an HTML article."
    )
    parser.add_argument("input", type=Path, help="Markdown input file")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="HTML output file. Defaults to the input path with .html suffix.",
    )
    parser.add_argument("--title", help="Override the HTML <title> value")
    parser.add_argument(
        "--math-renderer",
        choices=("mathjax", "mathml"),
        default="mathjax",
        help=(
            "LaTeX renderer: mathjax (default, accurate TeX-to-SVG via CDN) or "
            "mathml (offline native MathML fallback)"
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    input_path: Path = args.input
    output_path: Path = args.output or input_path.with_suffix(".html")

    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 2
    if not input_path.is_file():
        print(f"Input path is not a file: {input_path}", file=sys.stderr)
        return 2

    markdown_text = input_path.read_text(encoding="utf-8")
    title = args.title or infer_title(markdown_text, input_path)
    body_html = render_markdown(markdown_text, args.math_renderer)
    document = build_html_document(title, body_html, args.math_renderer)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
