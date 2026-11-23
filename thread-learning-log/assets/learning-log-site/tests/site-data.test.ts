import { describe, expect, it } from "vitest";

import { buildSiteDataFromText } from "../src/content/buildSiteData.ts";

const sampleLog = `
## 2026-03-01 10:30 | @Alpha | Morning review

entry_id: "alpha-1"
date: "2026-03-01"
time_start: "10:30"
time_end: "11:00"
time_basis: "logged_at"
category: "learning"
primary_tag: "@Alpha"
tags: ["@Alpha"]
source: "manual"
title: "Morning review"

### Summary
Reviewed the morning notes.

## 2026-03-01 08:15 | @Beta | Early sketch

entry_id: "beta-1"
date: "2026-03-01"
time_start: "08:15"
time_end: "08:45"
time_basis: "logged_at"
category: "planning"
primary_tag: "@Beta"
tags: ["@Beta", "@Alpha"]
source: "manual"
title: "Early sketch"

### Summary
Sketched the first approach.

## 2026-03-04 14:00 | @Alpha | Later note

entry_id: "alpha-2"
date: "2026-03-04"
time_start: "14:00"
time_end: "14:30"
time_basis: "logged_at"
category: "research"
primary_tag: "@Alpha"
tags: ["@Alpha"]
source: "manual"
title: "Later note"

### Summary
Captured the later update.
`.trim();

describe("site data builder", () => {
  it("indexes days, tags, ordering, and activity levels", () => {
    const data = buildSiteDataFromText(sampleLog);

    expect(data.dayIndex["2026-03-01"]?.entryIds).toEqual(["beta-1", "alpha-1"]);
    expect(data.dayIndex["2026-03-01"]?.activityScore).toBe(2);
    expect(data.dayIndex["2026-03-01"]?.activityLevel).toBe(2);

    expect(data.tagIndex["@alpha"]?.entryIds).toEqual(["alpha-2", "alpha-1", "beta-1"]);
    expect(data.tagIndex["@alpha"]?.entryCount).toBe(3);
    expect(data.tagIndex["@alpha"]?.latestDate).toBe("2026-03-04");
  });

  it("builds a heatmap range that starts in March 2026 and tracks forward from there", () => {
    const data = buildSiteDataFromText(sampleLog);

    expect(data.datasetRange.endDate).toBe("2026-03-04");
    expect(data.datasetRange.startDate).toBe("2026-03-01");
    expect(data.heatmapDays[0]?.date).toBe("2026-03-01");
    expect(data.heatmapDays[data.heatmapDays.length - 1]?.date).toBe("2026-03-04");
  });

  it("derives summaries from the Summary section", () => {
    const data = buildSiteDataFromText(sampleLog);
    expect(data.entries["alpha-2"]?.summary).toBe("Captured the later update.");
  });
});
