# Agent Skills for AI/ML Research Scientists

## Thread Learning Log

Motivation: I want a lightweight way to track what I actually learn while working with AI agents. Today, agents can support many parts of our work, such as reading papers, planning experiments, writing code, debugging, and running evaluations. As a result, we can accomplish much more in a single day than before.

But in my own experience, moving faster does not always feel the same as understanding more deeply. It can feel like the difference between walking somewhere and riding in a self-driving car. When I walk, progress is slower and I may stumble, but the obstacles I encounter force me to observe, reason, and solve problems myself. Knowledge is formed through that friction, and it tends to stay in my mind. In a self-driving car, I may travel much farther, but I can lose the embodied sense that I actually learned the route.

There is also a more personal reason: my memory is not especially reliable. If I do not revisit something, I often forget the details after a while. This is consistent with the idea of the "forgetting curve": without review or reinforcement, knowledge fades over time.

The idea behind this skill is simple: ask an AI agent to review the session or thread we just worked through together and extract durable, reusable lessons that may be useful in the future. For example, after using Codex to read and discuss a research paper, I can ask it to capture the paper's main ideas, assumptions, and takeaways. Or, after solving a difficult bug, I can ask the skill to summarize the debugging path, the root cause, and the fix.

The memory file will be a Markdown document. Each item or section represents one lesson, tagged with a timestamp and the related project or topic.

To make the skill more useful, visible, and easy to revisit, I also want Codex to build a small website from the main memory Markdown file. The UI should look like the image below, inspired by GitHub's commit history. Seeing a daily record of what I have learned and solved should make it easier to return to the log regularly and encourage me to save at least one interesting lesson each day.

![Thread learning log UI](/images/thread-learning-log/mainui.png)

## Grill Me

Matt Pocock's [`grilling`](https://github.com/mattpocock/skills/tree/main) skill is a small but powerful example of prompt design. I tried it and found it surprisingly useful, not because the prompt is long or complex, but because it gives the model a clear conversational role: slow the user down, pressure-test the plan, and expose hidden assumptions before implementation begins.

That experience changed how I think about skills. A good skill does not always need a large knowledge base, a complicated toolchain, or many pages of instructions. Sometimes a few carefully chosen sentences are enough to unlock much better behavior from an LLM.

**The skill**

Below is Matt's original `grilling` skill, which is the starting point for my local `grill-me` skill:

```text
---
name: grilling
description: Grill the user relentlessly about a plan or design. Use when the user wants to stress-test a plan before building, or uses any 'grill' trigger phrases.
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing. Asking multiple questions at once is bewildering.

If a question can be answered by exploring the codebase, explore the codebase instead.

Do not enact the plan until I confirm we have reached a shared understanding.
```

I modified the skill slightly with Codex, but the core principles remain the same:

- Interview relentlessly, but ask only one question at a time.
- Provide a recommended answer for each question so the user has something concrete to accept, reject, or revise.
- Walk down each branch of the design tree, resolving dependencies between decisions one by one.
- Explore the codebase directly when a question can be answered from local context.

The phrase "walk down each branch of the design tree" feels especially important. It tells the model not to ask random clarification questions, but to treat the plan as a structured set of dependent decisions. Each answer either opens or closes later branches. This is what makes the skill feel closer to a serious architecture review than a normal back-and-forth chat.

**Usage**

Use this skill to stress-test a plan, design, architecture, research direction, or implementation strategy before committing to it. It is especially useful when the problem has unclear requirements, hidden tradeoffs, or decisions that depend on one another.

Its behavior feels related to Plan mode in Codex: both ask clarifying questions and often provide recommended answers. The difference is intensity and depth. Plan mode usually asks only a small number of questions before moving toward execution. `grill-me` can keep going for much longer, which makes it better for uncovering unknown-yet-important details. I have often been surprised by the questions it raises, because they reveal assumptions I did not realize were part of the plan.

## Ask Me Paper

This skill was inspired by `grill-me`, but adapts the same interview-driven pattern to one of my most important workflows: reading academic papers and technical articles.

One reading principle I try to follow is active hypothesis testing:

- Before reading, and while reading, I form hypotheses and questions about the problem setting, assumptions, method, evidence, and limitations.
- Reading becomes the process of looking for answers to those hypotheses and questions.
- I should stop only when I can make a clear judgment: the paper addresses the question, the paper does not address it, or the answer remains uncertain.

This skill tries to recreate that discipline with Codex. Instead of letting me passively read a summary, Codex first reads the supplied paper or article, builds an internal understanding map, and then interviews me with rigorous four-choice multiple-choice questions. The goal is not to collect trivia from the paper. The goal is to check whether I understand the paper's central argument, how its claims depend on its evidence, what assumptions the method makes, and where the limitations are.

**The skill**

The core behavior of `ask-me-paper` is:

- Read the supplied paper or article before asking questions.
- Stay grounded in the source unless I explicitly ask for external context.
- Build an understanding map covering the thesis, claims, evidence, methods, definitions, assumptions, limitations, implications, and open questions.
- Ask exactly one multiple-choice question at a time, with four options labeled `A.` to `D.`.
- Make the distractors plausible and diagnostic, so wrong answers reveal specific misunderstandings rather than random mistakes.
- After each answer, classify it as correct, partial, unsupported, or wrong.
- Correct misunderstandings with concise evidence from the source before moving on.
- Continue until the main concepts have been tested or I ask to pause.

This is important because good paper reading is not just "Can I repeat the abstract?" It is closer to "Can I distinguish the paper's actual claim from a tempting stronger claim? Can I explain why the method is appropriate? Can I see what the evidence does and does not prove?" Multiple-choice questions are useful here because they force commitment. I cannot hide behind vague familiarity; I have to pick an interpretation.

**Usage**

Use this skill when I have a paper, article, PDF, excerpt, or pasted text and want to test whether I really understand it. A typical prompt is:

```text
Use $ask-me-paper on this paper and quiz me one question at a time.
```

It is useful in several moments:

- before a deep read, to surface what the paper is probably about and what I should pay attention to
- after a first read, to check whether I understood the main argument
- before a meeting or discussion, to make weak points visible
- when reading a difficult method section, to separate real understanding from recognition of familiar terms
- after using an AI agent to summarize a paper, to make sure I did not only outsource the understanding

The most valuable behavior is correction. If I choose the wrong answer, the skill should not simply reveal the correct option and move on. It should explain the misconception, point back to the paper's evidence or logic, and ask a targeted follow-up question when the misunderstanding affects later understanding. That turns paper reading into an active loop: commit, get corrected, refine the model, and continue.
