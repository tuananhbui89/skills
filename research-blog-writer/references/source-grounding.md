# Source Grounding

Use this reference when researching, citing, and auditing a post.

## Source Priority

Prefer sources in this order:

1. Primary sources: official documentation, specifications, standards, release notes, product pages, project docs, RFCs, and source repositories.
2. Scholarly sources: papers, technical reports, conference proceedings, arXiv, OpenReview, ACM, IEEE, USENIX, or comparable venues.
3. Maintainer or practitioner sources: engineering blogs from the organization or project team directly involved.
4. Local survey/reference sources: project-local books, notes, course material, or long-form guides that help with structure, terminology, mechanisms, or pointers to primary sources.
5. Secondary explainers: reputable summaries, analysis, journalism, or community posts, used only for context or vocabulary.

Avoid building core claims from unsourced commentary, SEO summaries, generic listicles, or anonymous posts.

## Local Survey Sources

For agentic-AI topics, `agent-101/The Hitchhiker’s Guide to Agentic AI/` may be used as a local survey/reference source when relevant. Load `references/hitchhiker-guide.md` before using it.

Use local survey sources for:

- topic structure and vocabulary
- background synthesis and mental models
- implementation mechanisms, tradeoff lists, and failure-mode framing
- pointers to original papers, specs, tools, or frameworks to verify separately

Do not let a local survey source override official docs, standards, current product documentation, release notes, or original papers. For time-sensitive claims, cite current primary or scholarly sources whenever possible. Cite the local source only when its own synthesis, framing, or extracted mechanism directly informs the post.

## Preferred Source Families

For AI, agent, ML, software-engineering, or developer-platform topics, check these source families early when relevant:

- OpenAI: official docs, research, product posts, engineering posts, API docs, SDK docs, and release notes.
- Anthropic: official docs, research, engineering posts, safety notes, and product documentation.
- Google: official sources from Google AI, Google DeepMind, Google Research, Google Cloud, Google Developers, Android, Chrome, official blogs, and product docs.
- Hugging Face: documentation, blog posts, papers, model cards, datasets, Spaces, libraries, and project pages.
- Towards Data Science: practitioner explanations, examples, and framing. Use for implementation perspective or vocabulary; do not let it override primary docs, papers, or maintainer sources.

Do not force these publishers when the topic is unrelated. When they are relevant, search them before relying on general web results.

## Freshness Rules

- For modern products, libraries, regulations, standards, benchmarks, or ecosystem claims, search current web sources during the task.
- Prefer pages with visible published, updated, or version dates.
- If a source may have changed, record the accessed date in the reference entry.
- When sources conflict, prefer the more primary and more recent source, and mention uncertainty if the conflict matters.

## Inline Citations

Use bracket markers such as `[1]`, `[2]`, and `[3]`.

- Assign numbers in order of first use.
- Reuse the same number for the same source.
- Put citations near the claim they support.
- Cite factual, specific, time-sensitive, or source-derived claims.
- Do not cite generic transitions, opinions, or original synthesis unless a source directly supports them.

Good citation targets:

- definitions from official docs or standards
- release dates, product capabilities, deprecations, or versioned behavior
- benchmark results, survey numbers, or security guidance
- claims about protocols, architecture, APIs, or tool behavior
- claims about what a named organization recommends
- claims about implementation mechanics, runtime behavior, failure modes, eval methods, or operational constraints

## References Format

End every post with `## References`.

Use this format:

```markdown
## References

[1] "Source title." Publisher or author. URL. Published/updated: YYYY-MM-DD or "not listed". Accessed: YYYY-MM-DD. Used for: short note.
```

If the publication date is unavailable, write `Published/updated: not listed`.

## Citation Audit

Before finalizing:

- every inline marker must have exactly one matching reference entry
- every reference entry must be cited in the body
- no reference entry may contain an invented title, publisher, URL, or date
- every time-sensitive claim must cite a current source
- every unsupported claim must be removed, softened, or clearly marked as interpretation
