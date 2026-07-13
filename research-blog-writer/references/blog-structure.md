# Blog Structure

Use this structure unless the user requests a different format.

## Title

Use one H1 that names the topic directly.

## Intro

Open with the practical reason the topic matters now. State the main thesis in plain language and preview the depth progression.

## Level 1: Fundamentals

Explain the topic from first principles:

- define the core term
- contrast it with nearby ideas
- give a simple mental model
- name the beginner mistake to avoid

## Level 2: Concepts

Show how the main pieces fit together:

- components and relationships
- common patterns
- what changes as systems get more complex
- vocabulary the reader needs before deeper detail

## Level 3: Engineering Detail

Explain implementation-level mechanisms and tradeoffs. This section should be a real technical deep dive, not a high-level recap.

- architecture and runtime shape
- interfaces, APIs, schemas, or protocols when relevant
- state, data flow, control flow, observability, and evaluation
- dependency boundaries, permissions, and deployment constraints
- failure modes and recovery paths
- performance, cost, latency, reliability, or scaling considerations when relevant
- security, privacy, and governance concerns

Use concrete artifacts where they help: tables, pseudocode, request/response examples, data-flow descriptions, failure-mode matrices, eval checklists, or operational runbooks. A reader should be able to use this section to begin a prototype, review an architecture, or ask sharper implementation questions.

## Current Landscape

Ground the topic in current sources:

- recent product or standards updates
- active ecosystem debates
- emerging best practices
- limits or open problems

## Practical Takeaways

End with judgment rules the reader can apply:

- when to use the idea
- when not to use it
- what to prototype first
- what to measure before trusting it

## References

List every cited source using the format from `source-grounding.md`.
