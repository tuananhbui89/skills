---
name: research-blog-writer
description: Research and write grounded blog-style Markdown posts from a topic, outline, or source section. Use when the user asks to study a topic, develop a section into a blog post, create layered explanations from fundamentals to deep engineering detail, split an outline into researched posts, or produce writing that must use current web research with inline citations and a references section.
---

# Research Blog Writer

## Overview

Use this skill to turn a topic or outline section into a grounded, readable Markdown blog post. The default audience is technical beginners with programming literacy: start from first principles, then gradually deepen into concepts, mechanisms, engineering tradeoffs, implementation detail, and current practice.

Default to a technical deep dive, not a surface overview. A post should leave a technical reader with enough understanding to reason about how the system is built, where it fails, how to evaluate it, and what design choices matter.

Do not rely only on model knowledge. Browse or search the web for every topic before drafting, especially when the subject is modern, fast-moving, product-related, standards-related, or ecosystem-related.

## Workflow

### 1. Read the topic and define the post

Identify:

- the exact topic or outline section to develop
- the audience and expected depth
- the core question the post should answer
- the subtopics that must be covered
- the output path if the user asks for files

For `agent-101/01-big-picture.md`, treat each top-level `## N. Title` section as a separate post. Write posts to `agent-101/blog/<section-number>-<slug>.md`, such as `agent-101/blog/01-why-agents-why-now.md`.

### 2. Plan research questions

Before searching, write 3-6 research questions that cover:

- definitions and fundamental framing
- current ecosystem or product updates
- engineering patterns, architecture, and implementation tradeoffs
- APIs, protocols, interfaces, data flow, or runtime behavior when relevant
- observability, evaluation, testing, deployment, or operations when relevant
- risks, limits, and when not to use the approach
- examples or case studies that make the topic concrete

### 3. Research current sources

Search the web for every post. Prefer primary and current sources:

- official docs, product pages, release notes, standards, specifications, and project docs
- papers, technical reports, conference pages, and standards bodies
- authoritative engineering posts from the maintainers or organizations involved
- secondary explainers only when they add framing or practitioner vocabulary

For AI, agent, ML, software-engineering, or developer-platform topics, actively check preferred source families before general web sources when relevant:

- OpenAI official docs, research, product, and engineering posts
- Anthropic official docs, research, and engineering posts
- Google official sources, including Google AI, Google DeepMind, Google Research, Google Cloud, Google Developers, and official Google blogs
- Hugging Face docs, blog posts, papers, model cards, and project pages
- Towards Data Science for practitioner framing, examples, or vocabulary

For agentic-AI topics, also consider the local `agent-101/The Hitchhiker’s Guide to Agentic AI/` source when relevant, especially for RAG, memory, harness/orchestration, MCP, A2A, multi-agent systems, agent frameworks, evaluation, benchmarks, and agentic UI. Use `references/hitchhiker-guide.md` before searching that local source. Treat it as optional supporting context and cite it only when it directly informs the post; keep current web research mandatory for modern, time-sensitive, product, standards, or ecosystem claims.

Use `references/source-grounding.md` when choosing, citing, and auditing sources. Capture enough source metadata while researching to build a complete reference list later.

### 4. Build a layered explanation

Use the researched material to organize the post from broad to deep:

- `Intro`: why the topic matters now
- `Level 1: Fundamentals`: beginner-friendly definitions and mental models
- `Level 2: Concepts`: how the pieces relate
- `Level 3: Engineering Detail`: architecture, implementation patterns, interfaces, data/control flow, state, tradeoffs, failure modes, observability, evaluation, and operations
- `Current Landscape`: recent updates, standards, ecosystem movement, or open debates
- `Practical Takeaways`: concrete judgment rules
- `References`: complete source list

Use `references/blog-structure.md` when drafting or reshaping the post.

The engineering section is not optional polish. It should be substantial enough that a reader can move from concept to prototype or design review. Include concrete mechanisms such as schemas, request flows, runtime boundaries, tool/API contracts, failure-mode tables, eval plans, deployment constraints, or operational checklists when they fit the topic.

### 5. Draft with citations

Write in a blog style: clear, concrete, and explanatory without sounding like a textbook. Keep paragraphs short, use headings to show the depth progression, and define terms before using them heavily.

Citation rules:

- Add inline citation markers such as `[1]` for factual, specific, non-obvious, time-sensitive, or source-derived claims.
- Reuse a marker when citing the same source again.
- Do not cite every sentence; cite claim clusters where the source support is clear.
- Never invent source details, dates, titles, or URLs.

### 6. Audit before finalizing

Before returning or writing the final post:

- verify every inline marker appears in `References`
- verify every reference is cited at least once
- check that current claims came from current sources
- check that preferred source families were considered for relevant AI, agent, ML, software, or developer-platform topics
- if the Hitchhiker guide was used, check that it is cited only for directly used structure, terminology, mechanisms, or background synthesis
- remove unsupported claims or soften them
- check the post starts at a basic level before going deeper
- check the post does not stop at surface explanation; add technical mechanisms, implementation detail, failure modes, and evaluation guidance if the deep section feels thin
- check that the final file is valid Markdown

## Output Defaults

When writing a file, include:

- one H1 matching the post title
- a short opening thesis
- the layered sections from `references/blog-structure.md`
- a substantial technical deep-dive section with concrete implementation or architecture detail
- inline citations throughout the body
- a `## References` section at the end

If the user asks for a batch from an outline, process one section at a time unless they explicitly ask for all sections in one run. This keeps research quality high and citation auditing tractable.

## Reference Usage

- Load `references/source-grounding.md` before researching or auditing citations.
- Load `references/hitchhiker-guide.md` before using the local Hitchhiker guide as a source.
- Load `references/blog-structure.md` before drafting the final post.

## Reusable Prompt Pattern

`Use $research-blog-writer to research this topic from current preferred sources and draft a layered Markdown blog post that deep-dives into engineering detail with inline citations and references.`
