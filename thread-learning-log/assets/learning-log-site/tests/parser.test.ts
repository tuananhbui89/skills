import { describe, expect, it } from "vitest";

import { buildSiteDataFromText } from "../src/content/buildSiteData.ts";
import { extractInlineTags, parseLearningLogMarkdown } from "../src/content/parser.ts";

describe("learning log parser", () => {
  it("parses headings with and without times and preserves markdown body", () => {
    const entries = parseLearningLogMarkdown(`
## 2026-03-19 | @AgentMemory | First note

entry_id: "entry-one"
date: "2026-03-19"
title: "First note"
tags: ["@AgentMemory"]
category: "learning"
custom_key: "custom"

### Summary
Hello world.

## 2026-03-20 09:15 | @PSOM | Second note

entry_id: "entry-two"
date: "2026-03-20"
title: "Second note"
tags: ["@PSOM"]
time_start: "09:15"

### Summary
Another entry.
`.trim());

    expect(entries).toHaveLength(2);
    expect(entries[0]?.headingDate).toBe("2026-03-19");
    expect(entries[0]?.headingTime).toBeNull();
    expect(entries[0]?.rawMetadata.entry_id).toBe("entry-one");
    expect(entries[0]?.markdown.startsWith("### Summary")).toBe(true);
    expect(entries[0]?.markdown.includes("entry_id")).toBe(false);

    expect(entries[1]?.headingTime).toBe("09:15");
    expect(entries[1]?.rawMetadata.time_start).toBe("09:15");
  });

  it("fails on malformed metadata arrays with line numbers", () => {
    expect(() =>
      parseLearningLogMarkdown(`
## 2026-03-19 | @AgentMemory | Broken note

entry_id: "broken"
tags: ["@AgentMemory"

### Summary
Broken.
`.trim()),
    ).toThrow(/line 4/i);
  });

  it("fails on duplicate entry ids", () => {
    expect(() =>
      buildSiteDataFromText(`
## 2026-03-19 | @AgentMemory | First

entry_id: "duplicate"
date: "2026-03-19"
title: "First"

### Summary
First.

## 2026-03-20 | @AgentMemory | Second

entry_id: "duplicate"
date: "2026-03-20"
title: "Second"

### Summary
Second.
`.trim()),
    ).toThrow(/Duplicate entry_id "duplicate"/);
  });

  it("extracts inline prose tags and ignores tags inside code or bare urls", () => {
    const tags = extractInlineTags(`
Working on @AgentMemory and #DeepWork today.

\`Ignore @inlineCode and #skip\`

https://example.com/@ignore-me

\`\`\`ts
const value = "@function_tool #notATag";
\`\`\`
`.trim());

    expect(tags).toEqual(["@AgentMemory", "#DeepWork"]);
  });
});
