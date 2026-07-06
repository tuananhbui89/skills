---
name: thread-learning-log
description: "Use when asked to summarize the current Codex thread into a durable learning-log entry and append it to the personal learning log after confirmation."
---

# Thread Learning Log

This skill has one mode: `log-thread`.

The learning log lives in the installed global skill folder:

```text
~/.codex/skills/thread-learning-log/learning-log.md
```

Use this skill only to capture durable learning from the visible Codex thread. Do not use it for historical backfills, external source ingestion, or knowledge-base retrieval.

## Rules

- Summarize only the visible Codex thread. Do not claim to have seen messages that are not in context.
- Optimize for reusable knowledge, not chat chronology.
- Render a draft first and wait for explicit confirmation before appending.
- Append through `scripts/append_learning_log.py`; do not edit `learning-log.md` directly.
- If append fails because the log path is not writable, return the rendered draft and clearly say that no file was modified.

## Goal

Create a learning-log entry that preserves durable knowledge from the current thread.

Prioritize:

- key concepts, definitions, and mental models
- practical rules of thumb
- useful comparisons and distinctions
- important examples, starter code, and implementation patterns
- conclusions worth remembering later

De-emphasize:

- turn-by-turn narration of what the user asked
- activity summaries that do not add learning value
- process details unless they materially explain the knowledge
- low-signal housekeeping sections

## Workflow

1. Read the visible thread and identify:
   - the core knowledge worth remembering
   - any examples, code snippets, comparisons, or implementation patterns worth preserving
   - decisions, open questions, or next steps only if they add lasting value
   - exact source or reference locations worth preserving
2. Decide whether the context is `full` or `partial`.
3. Reuse an existing tag when possible:

```bash
rg -o '@[A-Za-z0-9]+' ~/.codex/skills/thread-learning-log/learning-log.md | sort -u
```

If the log file does not exist yet, choose a concise new tag.

4. Choose one category:
   - `learning`
   - `research`
   - `implementation`
   - `debugging`
   - `planning`
   - `review`
   - `status`
   - `ops`
   - `mixed`
5. Build one JSON payload for `scripts/append_learning_log.py` with:
   - `entry_id`
   - `date`
   - `time_start`
   - `time_end`
   - `time_basis`
   - `category`
   - `primary_tag`
   - `tags`
   - `context_status`
   - `source`
   - `source_locations`
   - `reference_locations`
   - `title`
   - `sections`
6. Draft first:

```bash
python3 ~/.codex/skills/thread-learning-log/scripts/append_learning_log.py --render --input <payload.json>
```

7. Show the rendered entry and wait for explicit confirmation.
8. Append only after confirmation:

```bash
python3 ~/.codex/skills/thread-learning-log/scripts/append_learning_log.py --append --input <payload.json>
```

9. If the installed global skill path is unavailable while developing locally, run the local script path but keep the default log destination unchanged:

```bash
python3 thread-learning-log/scripts/append_learning_log.py --render --input <payload.json>
```

## Section Guidance

- `Summary`: one compact paragraph with the main takeaway
- `What I Did`: include only if the process itself is worth remembering
- `What I Learned`: this is the primary section
- `Decisions`: include only if they materially affect future use
- `Open Questions`: include only if they are worth preserving
- `Next Steps`: include only if they are meaningful follow-up actions

Empty or low-value sections should render as `- None.`

## Install Note

- This repository folder is only the local source copy of the skill.
- The installed skill can be copied to `~/.codex/skills/thread-learning-log`.
- The append helper defaults to `~/.codex/skills/thread-learning-log/learning-log.md`, so the log is stored beside the installed global skill.
