# Hitchhiker Guide Local Source

Use this reference when an agentic-AI blog topic would benefit from the local guide:

`agent-101/The Hitchhiker’s Guide to Agentic AI/`

The guide is optional supporting context. Use it when it helps with structure, terminology, mechanisms, implementation patterns, or pointers to primary literature. Do not use it as a substitute for current web research on products, standards, releases, benchmarks, or ecosystem status.

## Files

- `book.toc`: use first as the map of chapters and sections.
- `book.tex`: use as the primary readable source.
- `book.pdf`: use only when page layout, figures, or visual confirmation matters.
- `book.bib`: use only when following the guide's citations to original papers.

Avoid loading the full `book.tex`; it is large. Search `book.toc` for the topic, then inspect focused ranges in `book.tex`.

Useful search patterns:

```bash
rg -n "RAG|memory|harness|orchestration|MCP|A2A|multi-agent|framework|evaluation|benchmark|UI" "agent-101/The Hitchhiker’s Guide to Agentic AI/book.toc"
rg -n "Agentic Memory|Agent Harness|Model Context Protocol|Agent-to-Agent|Agent Development Frameworks|Agentic UI" "agent-101/The Hitchhiker’s Guide to Agentic AI/book.tex"
```

Relevant areas include:

- Chapter 16: Retrieval-Augmented Generation and Agentic RAG
- Chapter 17: Agentic Memory Systems
- Chapter 18: Agent Harness, context management, and orchestration
- Chapter 19: Agent Design Patterns
- Chapter 20: Agentic Environments and Benchmarks
- Chapter 21: Model Context Protocol
- Chapter 22: Agent Skills
- Chapter 23: Agent-to-Agent Communication
- Chapter 24: Multi-Agent Systems
- Chapter 25: Agent Development Frameworks, testing, evaluation, tracing, and production research-agent examples
- Chapter 26: Agentic UI Frameworks

## Citation

Cite the guide only when it directly informs the post. Use this reference format:

```markdown
[n] "The Hitchhiker's Guide to Agentic AI: From Foundations to Systems." Haggai Roitman. Local source: agent-101/The Hitchhiker’s Guide to Agentic AI/book.tex. Published/updated: 2026. Accessed: 2026-07-05. Used for: short note.
```

If the guide points to an original paper, official spec, or product document that supports a key factual claim, prefer finding and citing that primary source directly.
