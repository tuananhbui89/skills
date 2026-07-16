# Illustration Request v1

Use this complete request only when the visual coverage map marks a unit `Original figure required`. Complete the source-asset gate first. Ground every field in the supplied source and hand the request unchanged to `$illustrator-drawer` after user approval.

```markdown
## Illustration Request v1: <short title>

- **Asset strategy:** Original SVG; no external figure is sufficient or reusable for this teaching job.
- **ID / filename:** `<kebab-case>.svg`
- **Source anchor:** `<heading>`; insert `<after exact paragraph, table, or code block>`.
- **Learning objective:** <what the reader should understand after viewing it>
- **Claim to clarify:** <faithful concise source claim>
- **Caption-first takeaway:** <the one point readers should retain>
- **Visual type:** System map | process flow | comparison | hierarchy | timeline | spatial model | data view.
- **Composition:** <entities, exact relationships, directions, groupings, and label text>
- **Visual hierarchy:** <primary, secondary, and deliberately omitted elements>
- **Detail strategy:** One-panel | overview + subsystem detail; <why this scope fits>
- **Focus cue:** <first thing to notice and the treatment that directs attention>
- **Connector semantics:** <for every connector: meaning, direction, label, and distinct style>; write `None` if unused.
- **Complexity check:** <number of explanatory items; split or simplify if more than one paragraph or five bullets are needed>
- **Art direction:** <aspect ratio, compatible palette, type treatment, restrained texture if helpful>
- **Caption:** <final brief takeaway-led caption>
- **Alt text:** <complete text alternative conveying the teaching point>
- **Accuracy constraints:** <facts or relationships the figure must not imply, invent, quantify, or overstate>
- **Output path:** `<requested asset path>`
- **Acceptance criteria:** <observable requirements for embedding and readability>
```

Before handoff, verify that the request names the source passage, has one learning job, and makes every arrow's meaning and direction explicit. Do not use a figure to restate a heading or decorate a page.
