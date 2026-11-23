import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { LearningLogExperience } from "../src/LearningLogExperience.tsx";
import { HeatmapCell } from "../src/components/HeatmapCell.tsx";
import { MarkdownRenderer } from "../src/components/MarkdownRenderer.tsx";
import { buildSiteDataFromText } from "../src/content/buildSiteData.ts";

const fixtureData = buildSiteDataFromText(`
## 2026-03-25 19:01 | @SmartCalendar | First

entry_id: "first"
date: "2026-03-25"
time_start: "19:01"
time_end: "19:01"
time_basis: "logged_at"
category: "mixed"
primary_tag: "@SmartCalendar"
tags: ["@SmartCalendar"]
source: "codex-thread"
title: "First"

### Summary
First summary.

### What I Learned
- One

## 2026-03-25 19:04 | @AgentMemory | Second

entry_id: "second"
date: "2026-03-25"
time_start: "19:04"
time_end: "19:04"
time_basis: "logged_at"
category: "research"
primary_tag: "@AgentMemory"
tags: ["@AgentMemory", "#Atlas"]
source: "codex-thread"
title: "Second"

### Summary
Second summary.

### What I Learned
| Name | Value |
| --- | --- |
| A | B |
`.trim());

describe("component rendering", () => {
  it("renders heatmap cells with accessible labels and selected state", () => {
    const markup = renderToStaticMarkup(
      <HeatmapCell
        day={fixtureData.dayIndex["2026-03-25"]!}
        isSelected
        onSelect={() => undefined}
      />,
    );

    expect(markup).toContain('aria-label="Wednesday 25 March 2026. 2 entries."');
    expect(markup).toContain('data-selected="true"');
  });

  it("renders all entries for a selected day", () => {
    const markup = renderToStaticMarkup(
      <LearningLogExperience
        siteData={fixtureData}
        routeState={{ kind: "day", day: "2026-03-25" }}
        onSelectDay={() => undefined}
        onSelectTag={() => undefined}
        onOpenDay={() => undefined}
        onClearRoute={() => undefined}
      />,
    );

    expect(markup).toContain("First");
    expect(markup).toContain("Second");
  });

  it("renders a heatmap timeline that starts at March 2026 and limits the viewport to about three months", () => {
    const markup = renderToStaticMarkup(
      <LearningLogExperience
        siteData={fixtureData}
        routeState={{ kind: "none" }}
        onSelectDay={() => undefined}
        onSelectTag={() => undefined}
        onOpenDay={() => undefined}
        onClearRoute={() => undefined}
      />,
    );

    expect(markup).toContain("Mar 2026");
    expect(markup).toContain("--heatmap-visible-week-count:14");
  });

  it("renders the vertical roll newest first", () => {
    const markup = renderToStaticMarkup(
      <LearningLogExperience
        siteData={fixtureData}
        routeState={{ kind: "none" }}
        onSelectDay={() => undefined}
        onSelectTag={() => undefined}
        onOpenDay={() => undefined}
        onClearRoute={() => undefined}
      />,
    );

    expect(markup.indexOf("Second summary.")).toBeLessThan(markup.indexOf("First summary."));
    expect(markup).not.toContain("Vertical Roll");
    expect(markup).not.toContain("Lessons Over Time");
    expect(markup).not.toContain("Newest notes sit at the top");
    expect(markup).not.toContain("Learning Log Atlas");
    expect(markup).not.toContain("Total entries");
  });

  it("renders an empty day state", () => {
    const markup = renderToStaticMarkup(
      <LearningLogExperience
        siteData={fixtureData}
        routeState={{ kind: "day", day: "2026-03-24" }}
        onSelectDay={() => undefined}
        onSelectTag={() => undefined}
        onOpenDay={() => undefined}
        onClearRoute={() => undefined}
      />,
    );

    expect(markup).toContain("No activity logged");
  });

  it("renders tag results and empty tag states", () => {
    const tagMarkup = renderToStaticMarkup(
      <LearningLogExperience
        siteData={fixtureData}
        routeState={{ kind: "tag", tag: "@AgentMemory" }}
        onSelectDay={() => undefined}
        onSelectTag={() => undefined}
        onOpenDay={() => undefined}
        onClearRoute={() => undefined}
      />,
    );

    expect(tagMarkup).toContain("Second summary.");
    expect(tagMarkup).toContain("Open day");

    const emptyMarkup = renderToStaticMarkup(
      <LearningLogExperience
        siteData={fixtureData}
        routeState={{ kind: "tag", tag: "@Missing" }}
        onSelectDay={() => undefined}
        onSelectTag={() => undefined}
        onOpenDay={() => undefined}
        onClearRoute={() => undefined}
      />,
    );

    expect(emptyMarkup).toContain("No posts found");
  });

  it("renders markdown lists, tables, and images", () => {
    const markup = renderToStaticMarkup(
      <MarkdownRenderer
        markdown={`
### Summary
Hello

- One

| Name | Value |
| --- | --- |
| A | B |

![alt](/log-assets/example.png)
`.trim()}
      />,
    );

    expect(markup).toContain("<ul>");
    expect(markup).toContain("<table>");
    expect(markup).toContain('src="/log-assets/example.png"');
  });
});
