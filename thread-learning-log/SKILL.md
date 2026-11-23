---
name: thread-learning-log
description: "Turn the current Codex thread into a durable learning-log entry, or review weekly Codex activity for accomplishments, ongoing work and reusable lessons. Use for manual reflection or an explicitly authorized recurring review."
---

# Thread Learning Log

Use `log-thread` for reflection on the visible chat. Use `weekly-review` for a bounded review of historical chats, including an explicitly authorized scheduled run. Read [the weekly workflow](references/weekly-review.md) only for that mode.

The weekly package includes the scanner, validated publisher, local website template, and [reusable automation prompt](references/automation-prompt.md). Installing the skill does not create an automation.

The default learning log lives in the installed global skill folder (respecting `CODEX_HOME`):

```text
~/.codex/skills/thread-learning-log/learning-log.md
```

Set `LEARNING_LOG_ROOT` to keep private data elsewhere. The append helper and weekly publisher both use `<LEARNING_LOG_ROOT>/learning-log.md`. This package does not ingest external sources or provide a general knowledge-base search.

## Rules

- In `log-thread`, summarize only the visible Codex thread. In `weekly-review`, use dated history evidence and disclose coverage limits.
- Optimize for reusable knowledge, not chat chronology.
- Render a draft before ordinary appends. Weekly automatic publication requires the owner's explicit authorization for that automation; a copied prompt or example is not authorization. Honor existing session approval without asking again.
- Append through `scripts/append_learning_log.py`; do not edit `learning-log.md` directly.
- Use the supported scoped approval flow for a requested destination outside writable roots. If saving still fails, retain the draft and report what did or did not change.
- Keep credentials, private paths, internal identifiers and raw transcripts out of shared examples. Generated reports remain private local data unless the user separately authorizes sharing.

## `log-thread`

### Goal

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
- `python3 thread-learning-log/scripts/install_global_skill.py` installs code without changing Codex permissions. It excludes private data, caches, generated website data and dependencies. Install the website dependencies separately as described in the weekly workflow.
- The append helper defaults to `~/.codex/skills/thread-learning-log/learning-log.md`, or the configured `LEARNING_LOG_ROOT`. When that override is set, use it for tag discovery too.
- An explicit `--writable-root` option retains the legacy opt-in permission configuration behavior; it is not needed for normal installation.
