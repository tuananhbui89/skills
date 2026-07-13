---
name: arxiv-tex-crawler
description: Download and unpack arXiv TeX/source packages from arXiv URLs. Use when the user provides an arXiv html, abs, pdf, e-print, or raw arXiv ID and asks to fetch, crawl, download, extract, unpack, inspect, or work with the paper's LaTeX/source files.
---

# ArXiv TeX Crawler

## Quick Start

Use the bundled script for source retrieval:

```bash
python3 /Users/tuananhbui/.codex/skills/arxiv-tex-crawler/scripts/download_arxiv_source.py "https://arxiv.org/html/2605.07514" --output-dir .
```

The script accepts:

- `https://arxiv.org/html/2605.07514`
- `https://arxiv.org/abs/2605.07514`
- `https://arxiv.org/pdf/2605.07514`
- `https://arxiv.org/e-print/2605.07514`
- `2605.07514`

It normalizes the input to `https://arxiv.org/e-print/<id>`, downloads the source package, extracts it into `<output-dir>/<id>-source/`, and removes the downloaded archive after successful extraction.

## Workflow

1. Prefer the script over hand-written `wget`/`tar` commands.
2. Pass the user's original arXiv URL or ID directly to the script.
3. Use `--output-dir <dir>` to choose where the extracted source folder should be created.
4. Use `--force` only when overwriting an existing non-empty extraction directory is intended.
5. Use `--keep-archive` only when the user explicitly asks to retain the downloaded package.

## Notes

- Do not download the `/html`, `/abs`, or `/pdf` page as the source archive. Those URLs are accepted only so the script can extract the arXiv ID.
- The source package may be a tar archive, gzipped tar archive, zip archive, gzipped single file, raw TeX file, or occasionally a PDF-only source. The script detects the format and handles the common cases.
- If arXiv returns an HTML error page or the download fails, report the failure and the normalized e-print URL.
