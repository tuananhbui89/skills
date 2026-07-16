---
name: markdown-to-html
description: Convert local Markdown files into standalone self-contained HTML articles. Use when the user asks to render, publish, preview, or convert a `.md` Markdown document as an `.html` file with embedded CSS, native MathML-rendered LaTeX equations, semantic article structure, tables, links, lists, fenced code blocks, and no external assets.
---

# Markdown to HTML

## Overview

Use this skill to convert a Markdown document into a standalone HTML article. The converter preserves the Markdown file as the source of truth and writes a derived `.html` file that can be opened directly from disk. Generated articles include a side-panel table of contents built from section headings for quick in-page navigation. LaTeX is rendered as browser-native MathML, so the output remains standalone and does not depend on a CDN or JavaScript.

## Quick Start

Use the bundled script:

```bash
python3 markdown-to-html/scripts/convert_markdown_to_html.py input.md --output output.html
```

Optional title override:

```bash
python3 markdown-to-html/scripts/convert_markdown_to_html.py input.md --output output.html --title "Custom Title"
```

If `--title` is omitted, infer the title from the first Markdown H1. If no H1 exists, infer a readable title from the input filename.

## Workflow

1. Confirm the input file is Markdown and should remain the canonical source.
2. Choose the output path:
   - use the user-provided path when given
   - otherwise use the same directory and filename with `.html`
3. Run `scripts/convert_markdown_to_html.py`.
4. Inspect the generated HTML enough to confirm:
   - `<!doctype html>` is present
   - the `<title>` is correct
   - viewport metadata exists
   - CSS is embedded in `<style>`
   - content appears inside `<main><article>`
   - a side-panel table of contents appears when the document has section headings
   - heading anchors are present and table-of-contents links target those anchors
   - reference URLs and other external HTTP(S) links are clickable
   - external links include `target="_blank"` and `rel="noopener noreferrer"`
   - tables, lists, links, citations, references, and fenced code blocks render as HTML
   - inline `$...$` and `\(...\)` equations render as inline MathML
   - display `$$...$$` and `\[...\]` equations render as display MathML, not as literal LaTeX or code blocks

## Output Rules

The generated HTML must be self-contained:

- include `<!doctype html>`, `<html lang="en">`, `<head>`, `<body>`, `<main>`, and `<article>`
- include `meta charset="utf-8"` and responsive viewport metadata
- include all CSS inline in a `<style>` block
- require no external CSS, JavaScript, fonts, images, or build tooling
- convert supported LaTeX to native MathML: use `$...$` or `\(...\)` for inline math, and `$$...$$` or `\[...\]` for display math
- keep visual styling quiet, readable, and article-focused
- include a responsive table of contents beside the article when section headings exist; on narrow screens it may stack above the article
- add stable `id` anchors to rendered headings so table-of-contents links work from local files
- turn bare HTTP(S) URLs into clickable links, including URLs in reference sections
- make external HTTP(S) links open in a new browser tab with `target="_blank"` and `rel="noopener noreferrer"`; keep local in-page links such as table-of-contents anchors in the same tab

Do not edit the Markdown input unless the user explicitly asks. Treat HTML as a derived artifact.

## Script

- `scripts/convert_markdown_to_html.py`
  Converts Markdown to standalone HTML using local `mistune` and `latex2mathml`. Supports headings, heading anchors, a side-panel table of contents, LaTeX-to-MathML conversion, clickable external links, paragraphs, links, lists, blockquotes, tables, fenced code blocks, and inline citation text.

## Reusable Prompt Pattern

`Use $markdown-to-html to convert this Markdown file into a standalone HTML article.`
