---
name: illustrator-planner
description: Analyze a document and plan a complete, evidence-based set of high-value illustrations that improve comprehension. Use when Codex needs to plan figures, diagrams, explanatory artwork, or visual teaching aids for long articles, blog posts, reports, documentation, or drafts before anything is drawn.
---

# Illustrator Planner

Turn prose into a complete set of precise, evidence-based illustration requests. Optimize for teaching coverage and understanding, never decoration or an arbitrary figure count.

## Workflow

1. Read the whole document before recommending anything. For a long document, read it in sections, retain its argument map, then revisit the passages that need a visual.
2. Inspect existing figures and the target medium when available. Avoid duplicating a table, restating a heading, or disrupting the document's visual language.
3. Map the document's teaching units before selecting figures. For each substantial heading or independently explained mechanism, classify it as: needs a focused figure, covered by a proposed overview, already explained visually, or adequately taught by prose/table.
4. Identify comprehension bottlenecks: a system with interacting parts, a hidden mechanism, a sequence with branches, a comparison, a hierarchy, a spatial relationship, or a pattern that prose makes hard to hold in working memory.
5. Draft the caption before planning the composition. Use it to state the one takeaway a reader should retain; reject or re-scope any candidate whose visual cannot make that caption obvious.
6. Give each candidate one learning job. Do not merge independent teaching units merely to reduce the figure count. Prefer an overview plus focused figures when the source teaches several mechanisms that readers must understand separately.
7. Select for coverage, then remove only redundant or decorative candidates. There is no default cap: a substantial technical article commonly needs an overview and one focused figure for each major, independently useful topic. It is valid to recommend none only when the document contains no visual teaching opportunity.
8. Produce an `Illustration Request v1` for every selected figure. Do not draw the figure. Hand each request unchanged to `$illustrator-drawer` unless the user asks for a different production method.

## Quality rules

- Cover independent learning units deliberately. When a named topic introduces its own mechanism, decision, workflow, comparison, or failure mode, plan a focused figure unless an existing or planned figure already teaches that exact unit without overload.
- Use overview figures to orient readers, not to excuse omission of focused explanations. A broad system map may coexist with separate tool, harness, loop, evaluation, or safety figures when those topics carry distinct claims.
- Anchor each request to an exact heading and insertion point, and retain the source claim it must explain.
- Make the visual teach one primary idea at a glance. Use labels only where labels remove ambiguity.
- Keep one illustration to about one paragraph's worth of explanation or five explanatory items. When the source needs more, plan an overview plus one or more focused subsystem figures instead of a visual run-on.
- Treat a figure series as a teaching sequence: each figure must stand on its own, add a non-overlapping takeaway, and reuse a compatible visual vocabulary without repeating the overview.
- Name the first thing a reader should notice and the cue that directs attention to it: position, contrast, enclosure, callout, or a concise label.
- Prefer a diagram type that matches the idea: system map, process flow, comparison, hierarchy, timeline, spatial model, or data view.
- Define the meaning of every connector class. When arrows express different relationships, states, directions, or return values, require distinct styles and concise labels; never leave a two-way flow ambiguous.
- Preserve factual fidelity. Mark a relationship as illustrative when the source does not establish direction, magnitude, or causation.
- Treat titles, captions, alt text, and diagram labels as part of the explanation, not afterthoughts. Keep captions brief, takeaway-led, and placed after the figure.
- Use original concepts. Do not request imitation of a living artist or a copyrighted work.

## Required output

Start with a short `Illustration assessment` that states the document's audience, visual opportunities, coverage approach, selected count, and rejected opportunities. Then include a `Coverage map` that accounts for every substantial teaching unit as `Focused figure`, `Covered by <figure ID>`, `Existing figure`, or `Prose/table is sufficient`, with a brief reason. Do not mark an independent mechanism as covered by an overview unless the overview can teach it without shrinking, crowding, or weakening its own primary idea. Then provide one request per figure in this exact structure:

```markdown
## Illustration Request v1: <short title>

- **ID / filename:** `<kebab-case>.svg`
- **Source anchor:** `<heading>`; insert `<after the paragraph, table, or code block>`.
- **Learning objective:** What the reader should understand after viewing it.
- **Claim to clarify:** A faithful, concise statement from the source.
- **Caption-first takeaway:** Draft the final brief caption before composition; state what the reader should remember.
- **Visual type:** System map | process flow | comparison | hierarchy | timeline | spatial model | data view.
- **Composition:** Exact entities, relationships, directionality, grouping, and label text to show.
- **Visual hierarchy:** What is primary, secondary, and deliberately omitted.
- **Detail strategy:** One-panel | overview + subsystem detail; state why the planned scope fits one figure.
- **Focus cue:** The one element readers should notice first and the visual treatment that directs attention to it.
- **Connector semantics:** For every arrow or line class, specify its meaning, direction, label, and distinguishing style; write `None` when connectors are unnecessary.
- **Complexity check:** Count the explanatory items; split or simplify if the figure needs more than one paragraph or five bullets to explain.
- **Art direction:** Aspect ratio, palette direction, typography, and any restrained generative treatment.
- **Caption:** The caption-first takeaway, finalized for placement after the figure.
- **Alt text:** Complete text alternative that conveys the diagram's teaching point.
- **Accuracy constraints:** Facts that must not be implied, invented, or overstated.
- **Output path:** Requested destination.
- **Acceptance criteria:** Observable conditions that make the figure ready to embed.
```

End with `Drawer handoff` containing a one-sentence invocation for `$illustrator-drawer` and the complete request text. Keep the requests implementation-ready: the drawer should not need to rediscover the document's intent, decide what to emphasize, or infer connector meaning.
