---
name: illustrator-drawer
description: Transform an approved Illustration Request v1 into an original, accessible, static SVG figure and a responsive embed snippet. Use when Codex needs to draw explanatory diagrams or editorial illustrations for a website, blog, document, or report from a clear visual brief.
---

# Illustrator Drawer

Create a polished visual explanation from one approved `Illustration Request v1`. Deliver a static SVG, not an interactive artifact, unless the user explicitly changes the format.

## Workflow

1. Validate the request: locate its learning objective, source claim, required entities, insertion context, constraints, caption-first takeaway, focus cue, detail strategy, connector semantics, caption, and alt text. Read the referenced source passage and target styles when available. For a legacy request missing any of these fields, derive them before drawing and resolve a material ambiguity before proceeding.
2. Establish the visual system before drawing paths: start from the caption-first takeaway; choose a clear hierarchy, aspect ratio, grid, palette, focus treatment, label strategy, and the minimum visual vocabulary needed to teach the idea.
3. Draw an original standalone SVG at the requested output path. Place all nodes before connectors. Use a `viewBox`, semantic grouping, `<title>`, `<desc>`, legible system-font text, and only inline SVG features. Do not rely on remote fonts, scripts, images, or CSS.
4. Apply the useful core of algorithmic art selectively: begin from the concept, tune relationships and spacing carefully, and use deterministic geometric texture only when it helps reveal structure. Do not add noise merely to make a diagram look generative.
5. Render the SVG at its intended article width and inspect it. Correct clipping, overlap, low contrast, unreadable labels, ambiguous arrows, connector endpoints, or decoration that competes with the lesson.
6. Return the file path, caption, alt text, and a responsive `<figure>`/`<img>` snippet. Do not modify the source document unless the user asks.

## Drawing rules

- Make the learning objective visible within a few seconds; let supporting detail reward a longer look.
- Make the planned focus cue unmistakable. Use position, contrast, enclosure, or a callout to direct the first glance; do not make readers search for the lesson.
- Use colour, shape, labels, and connector style redundantly. Never make colour the only distinction.
- Keep text concise, high contrast, and readable at article width. Use arrows only when direction matters.
- Respect the detail strategy. If the request cannot be taught in one panel without visual overload, create the approved overview and subsystem figures rather than shrinking, squeezing, or omitting essential meaning.
- Draw connectors from a source outline to a target outline. Never start or end a connector inside a card, circle, label, or other node unless the visual convention explicitly calls for it.
- Express unknowns honestly. Do not convert a conceptual relationship into a measured quantity or causal claim.
- Prefer clean vectors over photo-like effects. Keep any generative geometry subordinate to the explanatory structure.
- Create new work; do not copy a distinctive artist's style, existing infographic, logo, or illustration.

## Connector geometry

Treat each arrow as a relationship between two specific node boundaries.

- Establish the source and target geometry before writing the path. For rectangles, choose a point on the relevant side away from rounded corners; for circles, use the circle-edge intersection in the connector direction.
- End the path at the target outline, not at the target centre. Set the marker reference point to the arrow-tip coordinate so the visible tip lands exactly on that endpoint. Prefer `markerUnits="userSpaceOnUse"`, a tip at `x=11`, and `refX="11"` for a stable, inspectable marker.
- Start the path at the source outline. Do not hide an incorrect tail beneath a card, and do not let a line run through a card before it emerges.
- Route curves around nodes and labels. Keep a visible gap between unrelated connectors; use orthogonal paths for process diagrams and smooth curves only when they clarify grouping or flow.
- Use `stroke-linecap="round"` and one arrowhead style per relationship class. Make a branch's colour, dash pattern, and head direction agree with its meaning.
- If a relationship is bidirectional, draw two deliberate arrows or use an explicitly documented bidirectional marker; never rely on an ambiguous line.
- Apply the request's connector semantics literally. Different flows must have distinguishable direction, line treatment, and labels when a reader could otherwise confuse their meaning.

## Teaching QA

Before final rendering, verify that the caption-first takeaway is visible without reading supporting prose. Then verify that the focus cue directs attention to that takeaway and that the figure can be explained in one paragraph or five bullets. Simplify, split, or add concise callouts when it fails any of these tests.

## Connector QA

Before delivery, inspect every connector at normal article width and again at a narrow responsive width. For each one, verify:

1. its tail visibly touches the intended source boundary;
2. its head visibly touches and points into the intended target boundary;
3. no part of the connector passes beneath a node, label, or unrelated arrowhead; and
4. its direction agrees with the caption and source claim.

Fix the SVG and re-render whenever any answer is no. XML validity alone is not sufficient.

## SVG completion checklist

- Use a meaningful `<title>` and `<desc>` connected through `aria-labelledby`.
- Include no external dependencies and no interactive controls.
- Leave adequate padding inside the `viewBox`; preserve labels at narrow article widths.
- Use a neutral background or transparent canvas appropriate for the host page.
- Verify contrast and distinguish lines, branches, and states with more than colour.
- Verify that the caption-first takeaway, focus cue, detail strategy, and connector semantics from the request are all visibly satisfied.
- Complete the connector QA for every arrow, including loopbacks and approval or error branches.
- Include the request's caption and alt text unchanged unless a factual correction is necessary.

## Required response

Report:

1. the created SVG path;
2. a one-sentence visual rationale;
3. the final caption and alt text; and
4. this integration pattern, adjusted to the actual relative path:

```html
<figure class="illustration">
  <img src="assets/illustrations/example.svg" alt="..." loading="lazy">
  <figcaption>...</figcaption>
</figure>
```
