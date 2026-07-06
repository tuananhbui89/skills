---
name: ask-me-paper
description: Deeply read an input paper or article, then interview the user with rigorous four-choice multiple-choice questions until the agent and user share the same understanding. Use when the user provides or references a paper, article, PDF, URL, pasted text, excerpt, or reading material and asks to be questioned, grilled, tested, interviewed, corrected, quizzed, or walked through comprehension one multiple-choice question at a time.
---

# Ask Me Paper

## Purpose

Drive shared understanding of a supplied paper or article through a rigorous, source-grounded multiple-choice interview. Read first, ask one high-leverage question at a time, correct misunderstandings before moving on, and keep the exchange anchored in the input source unless the user explicitly asks for outside context.

## Source Grounding

1. Ingest the whole supplied source before questioning whenever possible. Accept pasted text, local files, PDFs, URLs, excerpts, or screenshots with readable text.
2. If no source is available or accessible, ask the user for the paper or article before starting the interview.
3. Build an internal understanding map before asking the first question:
   - central thesis or research question
   - key claims and contributions
   - evidence, examples, data, methods, or reasoning
   - important definitions and terms of art
   - assumptions and scope boundaries
   - limitations, caveats, counterarguments, and open questions
   - implications, applications, and connections across sections
4. Use only the supplied paper or article as the default evidence source. Do not browse, import outside facts, or correct from general knowledge unless the user explicitly requests external context.

## Interview Loop

1. Ask exactly one multiple-choice question per assistant turn.
2. Start with the paper's central thesis or problem, then progress through claims, evidence, methods or reasoning, definitions, limitations, implications, and synthesis.
3. Prefer questions that expose whether the user understands relationships, not just isolated facts.
4. Format every question with exactly four answer choices labeled `A.`, `B.`, `C.`, and `D.`.
5. Make exactly one option correct unless the user explicitly asks for a different quiz format.
6. Make the incorrect options plausible and diagnostic: each distractor should reflect a common misconception, overgeneralization, reversed causal claim, confused definition, unsupported extrapolation, or tempting-but-wrong reading of the source.
7. Avoid giveaways in the choices. Keep options similar in length, specificity, tone, and grammatical fit; do not make the correct answer the only nuanced, hedged, longest, or source-like option.
8. Do not include "all of the above", "none of the above", joke answers, obviously extreme claims, or choices that can be eliminated by test-taking tricks rather than source understanding.
9. If useful, silently decide what misconception each distractor is testing before asking, but do not reveal the answer or rationale until after the user responds.
10. Ask the user to answer with the letter, optionally with a brief reason.
11. After each answer, briefly classify it as correct, partial, unsupported, or wrong.
12. If the answer is correct, briefly affirm the specific understanding demonstrated and ask the next multiple-choice question.
13. If the answer is partial, name what is right, add the missing paper-grounded detail, and ask a follow-up multiple-choice question if the gap affects later understanding.
14. If the answer is unsupported or wrong, correct it with concise evidence from the source before moving on. Require a targeted follow-up multiple-choice question when the misconception is foundational.
15. Do not ask multi-part questions unless the parts are inseparable for one concept.

## Correction Style

- Be Socratic but firm: treat mistakes as useful signal, not failure.
- Correct claims by pointing to the paper's stated argument, evidence, section logic, definitions, or examples.
- Avoid long lectures. Give the minimum correction needed for the user to answer the next question better.
- Distinguish clearly between what the paper says, what the paper implies, and what remains uncertain.
- If the user's answer introduces outside knowledge, accept it only when the user asked for external context; otherwise redirect to the source.

## Stopping Criteria

Continue until the major concepts in the understanding map have been tested, the user asks to pause, or the remaining uncertainty depends on inaccessible source material. When stopping, summarize:

- what the user now understands well
- corrected misunderstandings
- remaining weak spots or ambiguities
- the paper's core argument in a concise shared-understanding statement
