---
name: grill-me
description: Relentlessly interview the user about a plan, proposal, architecture, feature idea, implementation strategy, or design until the agent and user reach shared understanding. Use when the user asks to be grilled, pressure-tested, interrogated, walked through a design tree, or questioned one decision at a time before implementation. Explore the codebase instead of asking whenever a question can be answered from local files, tests, docs, or existing patterns.
---

# Grill Me

## Purpose

Drive a plan from vague intent to shared understanding by resolving the design tree one dependency at a time. Keep the exchange focused, rigorous, and useful: ask exactly one question per turn, and include the recommended answer with that question.

## Operating Loop

1. Restate the current understanding in one or two sentences when useful.
2. Identify the highest-leverage unresolved decision whose answer affects later choices.
3. If local context can answer it, inspect the codebase instead of asking the user. Use normal repo-reading tools such as `rg`, file reads, tests, docs, or existing implementation patterns.
4. Ask one question only.
5. Provide the recommended answer immediately after the question, with a brief reason.
6. After the user answers, update the shared understanding, note any resolved dependency, and continue to the next unresolved branch.
7. Stop only when the significant branches are resolved or the user asks to pause, then summarize the agreed plan, assumptions, and remaining risks.

## Question Discipline

- Ask one question per assistant turn. Do not bundle multiple independent questions.
- Prefer questions that unblock several downstream decisions.
- Sequence questions by dependency: goals before scope, scope before architecture, architecture before APIs, APIs before implementation details, implementation details before tests and rollout.
- Make each question concrete enough that the user can answer directly.
- Include a recommendation every time, phrased as the default answer the agent would choose.
- If the recommendation depends on an assumption, state that assumption briefly.
- If the user gives a partial answer, ask the narrowest follow-up needed to resolve the ambiguity.

## Codebase Exploration

Before asking a question, check whether the repo can answer it. Explore instead of asking when the answer is likely in:

- Existing architecture, module boundaries, naming conventions, or similar features
- Tests, fixtures, snapshots, or golden files
- Configuration, routing, schemas, migrations, or API contracts
- Documentation, comments, ADRs, issues, or examples in the repo

When exploration answers the question, report the discovered answer succinctly and move to the next unresolved question. If exploration only narrows the options, use that evidence in the recommendation.

## Tone

Be relentless without being theatrical. Stay collaborative, direct, and specific. The goal is not to win an argument; the goal is to remove ambiguity until both sides could independently describe the same plan.

## Output Pattern

Use this shape by default:

```markdown
Current understanding: <brief state of the plan, only if helpful>

Question: <one question>

Recommended answer: <the answer I recommend>, because <short reason>.
```

If codebase exploration resolved the next decision, use:

```markdown
I checked <files or patterns>. The repo already answers <decision>: <answer>.

Question: <next unresolved question>

Recommended answer: <the answer I recommend>, because <short reason>.
```
