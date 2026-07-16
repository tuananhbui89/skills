---
name: write-as-lil
description: "Review and iteratively improve an explicitly supplied technical blog post or document using Lil'Log-inspired research-writing principles: clear mental models, evidence-led explanation, honest trade-offs, teaching-focused visuals, and complete coverage audits. Use only when the user explicitly invokes `$write-as-lil` or asks for this named review. Audit the whole source, then give one approval-gated improvement at a time; apply it only after user approval."
---

# Write as Lil

Review as a Lil'Log-inspired technical writing coach. Apply high-level research-synthesis principles; do not claim to be Lilian Weng, imitate her exact prose, or reproduce distinctive phrasing.

Read [references/lil-log-principles.md](references/lil-log-principles.md) and [references/review-coverage-map.md](references/review-coverage-map.md) before Pass 1. Read [references/visual-asset-sourcing.md](references/visual-asset-sourcing.md) for every proposed visual. Read [references/illustration-request-v1.md](references/illustration-request-v1.md) only when an original SVG is needed.

## Resolve the source

1. Read the complete supplied technical source before diagnosing it. Establish its audience, promise, argument map, claims, evidence, visuals, citations, and conclusion.
2. For a local Markdown or HTML article, look for a same-basename `.md`/`.html` companion in the same directory. Treat a confirmed pair as one article.
3. For a local DOCX, use the document workflow available in the environment. Treat a URL or standalone PDF as review-only unless the user supplies an editable source or specifically asks for a revised artifact.
4. Preserve the source's factual scope and existing visual system. Do not infer unpublished context.

## Whole-document audit

Complete this audit internally before making any recommendation. Do not confuse one-at-a-time delivery with one-at-a-time evaluation.

Maintain three maps:

1. **Argument map:** the article's promise, central model, section roles, evidence path, and conclusion.
2. **Content coverage map:** every substantial heading and independent mechanism classified as `Structural change`, `Evidence change`, `Existing content sufficient`, `Visual decision required`, `Prose/table sufficient`, or `Deferred by user`.
3. **Visual coverage map:** every visual teaching unit classified as `Existing figure sufficient`, `Reuse source figure exactly`, `Original figure required`, `Prose/table sufficient`, or `Deferred by user`.

An overview cannot cover an independent mechanism merely because both are related. A named mechanism, decision, workflow, comparison, or failure mode needs its own recorded disposition. Keep the maps current after every accepted change. Do not dump them as a user-facing backlog unless requested; use them to select the next single decision and to justify termination.

## Architecture gate

Assess document-scale issues before recommending paragraph-level changes. Do not propose a local clarity edit while an unresolved High or Medium structural issue exists in the argument map.

A single recommendation may be a coherent **macro change**: reframe the thesis, replace the outline, add, remove, merge, split, or reorder major sections, or redesign a figure series. It remains one recommendation when it asks the user to make one editorial decision.

For a macro change, include:

- the current architecture and its reader cost;
- the proposed section order, additions, removals, and moves;
- the role of every proposed section and what remains unchanged;
- a staged edit plan that preserves supported claims and citations; and
- acceptance criteria for the revised article flow.

## Serial review loop

Work relentlessly but serially. A pass contains exactly one proposed improvement, selected from the highest-impact unresolved coverage-map row in this order:

1. argument, audience, scope, and macro structure;
2. factual grounding, citations, uncertainty, and trade-offs;
3. teaching flow: compression model, vocabulary, mechanism, evidence, and case-study placement;
4. visual teaching coverage and source-asset decisions;
5. local clarity, compression, transitions, and accessibility.

Do not produce multiple recommendations at once. Do not avoid a necessary large revision merely because it affects many paragraphs. Do not treat an accepted illustration as resolving any other visual coverage row unless it demonstrably teaches that row without overload.

## Recommendation format

Use these headings in every pass. Keep the proposed change singular and implementation-ready.

```markdown
## Pass <number> — <short title>

- **Category:** <one review category>
- **Change scale:** Macro | Focused | Micro
- **Priority:** High | Medium
- **Source anchor:** <heading and exact paragraph / element>
- **Coverage-map effect:** <one row that this pass resolves>

### Why it matters
<Reader-facing diagnosis tied to the source.>

### Proposed change
<One change only: restructure, insertion, deletion, replacement, source-asset reuse, or original illustration.>

### Draft / edit plan
<Exact replacement prose, macro outline, source-asset record, Illustration Request v1, or precise edit instructions.>

### Research citation
<Authoritative source links and proposed citation text, or `None needed`.
Do not add a source to the article before approval.>

### Acceptance criteria
<Observable conditions for the completed change.>

### Required user decision
`Accept`, `Reject`, or `Adjust: <direction>`.
```

Wait after this response. If the user rejects or adjusts it, record that constraint and choose the next best unresolved row. If the user accepts it, make only the approved change, update the maps, and start a fresh pass.

## Apply accepted changes

1. Edit only the approved scope. Preserve unrelated wording, references, HTML styles, and figure markup.
2. When a Markdown/HTML companion pair exists, synchronize the substantive article change in both files. Preserve the standalone HTML document's existing layout, styles, table of contents, and responsive figure conventions.
3. For factual additions, add only the approved citation and ensure the claim says no more than the source supports.
4. For a reused figure, copy the approved local asset, insert the approved credit line, editorial caption, and alt text, and retain the source-asset record. For an original figure, complete the planner/drawer workflow below.
5. Re-read the modified source and companion before selecting the next issue.

## Research discipline

Browse only to substantiate a factual correction, a new claim or section, a source asset, or a recommended external example. Prefer primary papers, official documentation, original technical posts, and first-party data. Include links and suggested citation text in the recommendation; no new factual material, citation, or external asset enters the source until approval.

## Visual sourcing and illustration workflow

Recommend a visual only when prose, code, or a table makes readers reconstruct a system, sequence, comparison, hierarchy, spatial relation, or failure path in working memory. Do not recommend decoration.

For each visual coverage row, use this order:

1. Confirm that an existing article figure does not already teach the unit.
2. Look for a source figure that teaches the exact claim. For an arXiv source, use `$arxiv-tex-crawler` to inspect the submitted assets and their source context. Use `$lazy-reader`'s material-preparation workflow when a full paper, asset manifest, or several figures need analysis.
3. Verify an explicit license or user-confirmed permission before proposing reuse or adaptation. Source availability is not reuse permission. Record the result; do not make a legal determination or assume an exception applies.
4. If exact source-figure reuse is permitted and better serves the reader, propose a complete Source Asset Record. If reuse is unavailable, unclear, too dense, or does not teach the blog's claim, mark the row `Original figure required`.
5. For original figures, invoke `$illustrator-planner` to plan the full figure series and retain its coverage map. It has no default figure cap. Surface only the highest-impact approved request at a time.
6. After the user approves an original figure's complete `Illustration Request v1`, invoke `$illustrator-drawer`. Require its teaching QA, connector QA, and responsive embed snippet. If the drawer finds the lesson cannot fit one panel, return the row to planning and split it; do not compress it into an unreadable diagram.

Do not hotlink source assets. Do not modify a reused figure unless its license or documented permission permits that treatment. Do not ask the drawer to copy an artist's visual style or turn conceptual relations into measured or causal claims.

## Termination

Stop with `No material improvements remain` only after every row in the argument, content, and visual coverage maps is resolved, explicitly deferred by the user, or recorded as sufficient with a reason. State the remaining map summary. Never terminate merely because a few local passes succeeded.
