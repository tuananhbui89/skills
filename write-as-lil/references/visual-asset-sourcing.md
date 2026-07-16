# Visual Asset Sourcing

Use this decision gate before commissioning an original illustration. A downloadable paper source or website image is evidence to inspect, not automatic permission to republish or modify.

## Selection order

1. Reuse an existing article figure when it already teaches the unit.
2. Reuse an external source figure exactly when it teaches the precise claim, its labels and scale remain useful, and its explicit license or user-confirmed permission allows the intended publication.
3. Adapt a source figure only when the explicit license or documented permission allows adaptation and the added value justifies it.
4. Plan an original explanatory figure when the article needs a cross-source synthesis, reader-oriented simplification, blog-specific decision framework, accessible labels, or a visual whose reuse rights are unavailable or unclear.

## Source inspection

- For an arXiv URL or ID, use `$arxiv-tex-crawler` to retrieve the source package and inspect figure files, captions, labels, and the nearby TeX passage.
- Use `$lazy-reader`'s `prepare_paper_materials.py` when several paper assets or an asset manifest are needed to match figures to claims.
- For a website asset, inspect the page's stated license or permission terms. Do not hotlink it.
- Prefer the source asset that supports the exact article claim, not merely a visually attractive or familiar image.

## Rights gate

Record an explicit license or user-confirmed permission before reuse. Apply attribution and license conditions exactly; check whether commercial use, adaptation, or share-alike obligations affect the destination. Do not assume that an arXiv submission, a public URL, or extracted TeX source grants reuse rights. Do not make legal determinations; ask the user when the status is unclear.

## Source Asset Record

Use this in a recommendation when external reuse is the proposed single change:

```markdown
## Source Asset Record: <short title>

- **Asset strategy:** Existing article figure | Reuse source figure exactly | Adapt source figure
- **Source work:** <title, authors, year, DOI or stable URL>
- **Source asset:** Figure <n>; `<original filename or asset URL>`
- **Source claim:** <the exact claim it supports in this article>
- **Rights status:** <explicit license / documented permission / needs user confirmation>
- **Permitted treatment:** Exact reproduction only | Adaptation permitted
- **Insertion point:** <exact source anchor>
- **Credit line:** <complete attribution and license text>
- **Editorial caption:** <why the reader needs this here>
- **Alt text:** <standalone description for the destination article>
- **Local asset destination:** <approved project-relative path>
- **Why reuse beats redraw:** <evidentiary, precision, or canonical-value rationale>
- **Acceptance criteria:** <license/permission verified, asset inspected, credit and alt text ready, no hotlink>
```

Use the source figure unchanged when permission permits exact reuse but not adaptation. If the source asset is too dense, inaccessible, or unsuitable for the article's claim, prefer an original figure rather than silently modifying it.
