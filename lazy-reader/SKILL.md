---
name: lazy-reader
description: Create exhaustive Markdown and standalone HTML reading notes for arXiv papers. Use when the user provides an arXiv URL or ID and asks to read, summarize, explain, make notes for, or create a lazy-reader report from a paper, especially when the output should preserve the paper's section flow, extract specific claims and details, reuse figures/tables in context, and include motivation, insights, method, experiments, limitations, and open questions.
---

# Lazy Reader

## Quick Start

Prepare paper materials:

```bash
python3 /Users/tuananhbui/.codex/skills/lazy-reader/scripts/prepare_paper_materials.py "https://arxiv.org/html/2605.07514" --output-root docs/lazy-reader
```

This creates `docs/lazy-reader/<arxiv-id>/` with extracted source, optional `paper.html`, optional `paper.pdf`, `paper_source_expanded.tex`, `asset_manifest.json`, `asset_snippets.md`, and copied figures.

For offline testing or a previously downloaded source package, pass `--archive <path>` to route extraction through `$arxiv-tex-crawler` without fetching from arXiv.

After writing the reading note Markdown, convert it:

```bash
python3 /Users/tuananhbui/.codex/skills/markdown-to-html/scripts/convert_markdown_to_html.py docs/lazy-reader/<arxiv-id>/<arxiv-id>-lazy-reader.md --output docs/lazy-reader/<arxiv-id>/<arxiv-id>-lazy-reader.html
python3 /Users/tuananhbui/.codex/skills/lazy-reader/scripts/inline_html_images.py docs/lazy-reader/<arxiv-id>/<arxiv-id>-lazy-reader.html
```

## Workflow

1. Run `prepare_paper_materials.py` first. It normalizes the arXiv URL or ID, invokes `$arxiv-tex-crawler`, saves arXiv HTML when available, expands TeX inputs, extracts figure/table snippets, and prepares local figure assets.
2. Read the paper in this priority order:
   - `paper.html` if available and useful
   - `paper_source_expanded.tex`
   - `paper.pdf` only when HTML and TeX are unavailable or insufficient
3. Use `asset_snippets.md` and `asset_manifest.json` to place figures and tables at the point where they naturally belong in the reading flow. Match each figure/table to the nearest source section, paragraph, method component, experiment, result, or limitation it supports. Do not collect all figures and tables at the end unless the source itself does so.
4. Write `<arxiv-id>-lazy-reader.md` in the output directory as the canonical source.
5. Convert with `$markdown-to-html`, then run `inline_html_images.py` so the final HTML remains standalone even when the Markdown used local figure links.
6. Verify the HTML has `<!doctype html>`, a correct title, a table of contents, rendered Markdown tables, and no remaining local `figures/...` image references.

## Core Reading Principles

1. **Exhaustiveness over brevity.** Do not skip key points to save space. If a paper has 30 distinct insights, list all 30.
2. **Specificity is mandatory.** Every point must include concrete details such as numbers, effect sizes, sample sizes, method names, comparisons, datasets, metrics, dates, ablations, and experimental settings when the paper provides them. Vague paraphrases are failures.
3. **Quotes support, not duplicate.** Embed short direct quotes only when they convey the point more precisely than paraphrase alone. Do not quote a sentence and then restate the same idea next to it.
4. **No meta-discourse.** Do not write phrases like "In this section, the authors argue...", "Below is a summary...", or "End of summary." Attribution to the paper is assumed.
5. **Section structure mirrors the source.** If the paper has sections, organize the reading note by those sections using the original section titles. Skip References, Author Information, Acknowledgments, and similar boilerplate unless the user asks for them.

## Required Two-Step Reading Method

Use this method internally, but only write the final Step 2 result to the Markdown file.

### Step 1: Exhaustive extraction

Read the paper carefully. For each section, extract every key point or insight as a numbered list item.

Each extracted item must use this structure:

```markdown
N. **Heading in sentence case**
Body paragraph with specific details and naturally embedded direct quotes in *"italicized double quotation marks"*.
```

Rules for extraction:

- Start each item with an Arabic numeral, a period, a space, and a bold sentence-case heading.
- Put the body paragraph on the next line with no indentation.
- Use **bold** within the body to emphasize important concepts, method names, datasets, metrics, or comparisons.
- Enclose direct quotes in double quotation marks and italicize the quoted text: *"like this"*.
- Keep direct quotes short and purposeful. Follow copyright limits and do not quote long passages.
- Combine redundant near-duplicates instead of listing the same point twice.
- Proceed section by section. Each section gets its own `## <Original Section Title>` header before its numbered items.
- Numbering may restart at 1 for each section or continue sequentially across the paper, but it must be consistent within a note.

Correct style:

```markdown
1. **Copilot is the most favorable workflow in the comparison**
Table 1 compares six methods: **no software**, **point-and-click**, **modify code chunks**, **Excel**, **teach coding**, and **Copilot**. The Copilot column is the only one marked favorable across all evaluated characteristics, described as *"the only approach that is favorable across all [the] characteristics"*.
```

Incorrect style:

```markdown
1. **Copilot is the most favorable workflow in the comparison**
In Table 1 the authors compare six methods and emphasize that the Copilot method is the only one favorable across all five characteristics. They note that *"Copilot... is the only approach that is favorable across all [the] characteristics"*.
```

The incorrect style duplicates the quote's content and adds unnecessary attribution.

### Step 2: Clean and organize

Transform the extraction before writing the final Markdown:

1. Remove citation markers and reference links. Strip superscript numbers, bracketed references such as `[1]`, inline citations such as `(Smith et al., 2023)`, URLs, and DOI links unless a URL is the paper source line.
2. Add an overview/takeaway at the top. This must be one concise paragraph of 3-6 sentences capturing the main contribution, key findings, and significance. Do not use bullet points in the overview.
3. Preserve the source's section structure when it works well. If the paper has unclear sections, reorganize thematically using headings that reflect the content, but do not remove extracted items during reorganization.
4. Only output the Step 2 result. Do not include preambles, process notes, "Step 1", "Step 2", or closing meta-commentary in the reading note.

## Required Markdown Structure

Use this structure unless the user asks otherwise:

```markdown
# <Paper Title>

Source: <arXiv URL>

## Overview / Takeaway

<One paragraph, 3-6 sentences.>

## <Original Section Title>

1. **Heading in sentence case**
Body paragraph with concrete details, short quotes when useful, and no citation markers.

<Relevant figure or table, placed here if it supports this item or nearby items.>

2. **Heading in sentence case**
Body paragraph...

## <Next Original Section Title>

1. **Heading in sentence case**
Body paragraph...
```

Do not add a generic `Figure And Table Guide` at the end. Figures and tables must appear where the reader needs them.

## Figures And Tables In The Reading Flow

- Place each relevant figure or table immediately after the numbered item it supports, or after the small group of items it supports.
- Prefer the paper's original figure/table order when multiple assets support the same section.
- Before embedding an asset, write one concrete sentence explaining what it shows and why it matters.
- Preserve the paper's label and caption when available, but remove citation markers from captions.
- For image assets copied into `figures/`, use relative Markdown links such as `![Figure 2: caption](figures/example.png)`.
- For tables extracted as TeX or text, convert them into readable Markdown tables when practical. If conversion would be lossy, include a compact prose rendering that preserves exact rows, columns, metrics, and values.
- Include all figures and tables that materially support the explanation. Do not dump irrelevant assets, appendix-only clutter, or duplicate visualizations.
- If an asset file cannot be embedded, still place its label, caption, and extracted table/figure description at the correct point in the note.

## Required Content Coverage

The source-section extraction should naturally cover these questions, but verify that the final note explicitly answers all of them:

- What problem motivates the paper?
- What insights or observations drive the approach?
- What method is proposed, including the concrete architecture, objective, algorithm, training recipe, or mathematical mechanism?
- Why should the method work?
- Which experiments, datasets, metrics, baselines, ablations, and numerical results support the claims?
- What limitations, caveats, failure cases, and open questions remain?

If a required question is not addressed directly by the paper, say so in the relevant section with the most specific evidence available.

## Handling Edge Cases

- **Documents without clear sections:** Organize thematically and create section headings that reflect the content's structure.
- **Very short documents under 2 pages:** Still apply the full method, but do not pad.
- **Foreign-language documents:** Summarize in the language the user is writing in, defaulting to English. Translate quotes as needed and include the original-language quote in parentheses when useful.
- **Multiple documents:** Summarize each document separately under its own top-level heading unless the user explicitly asks for a combined synthesis.
- **Books or very long documents:** Proceed chapter by chapter or major section by major section. Maintain the same rigor throughout; do not become less detailed later in the document.

## Output Defaults

- Default output root: `docs/lazy-reader`
- Default paper directory: `docs/lazy-reader/<arxiv-id>/`
- Markdown output: `<arxiv-id>-lazy-reader.md`
- HTML output: `<arxiv-id>-lazy-reader.html`

Use `--force` with `prepare_paper_materials.py` only when replacing a previous generated directory is intended.
