import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";

import { describe, expect, it } from "vitest";

import { buildSiteDataOutputs } from "../src/content/buildSiteDataOutputs.ts";

const sampleLog = `
## 2026-03-02 09:00 | @Alpha | Refresh check

entry_id: "alpha-refresh"
date: "2026-03-02"
time_start: "09:00"
time_end: "09:00"
time_basis: "logged_at"
category: "implementation"
primary_tag: "@Alpha"
tags: ["@Alpha"]
source: "manual"
title: "Refresh check"

### Summary
The public JSON should refresh with the generated artifact.
`.trim();

describe("site data output builder", () => {
  it("writes matching generated and public JSON artifacts", async () => {
    const tempRoot = await fs.mkdtemp(path.join(os.tmpdir(), "learning-log-site-"));
    const sourcePath = path.join(tempRoot, "learning-log.md");
    const generatedOutputPath = path.join(tempRoot, "src", "generated", "site-data.json");
    const publicOutputPath = path.join(tempRoot, "public", "site-data.json");

    await fs.writeFile(sourcePath, sampleLog, "utf8");

    const siteData = await buildSiteDataOutputs(sourcePath, {
      generatedOutputPath,
      publicOutputPath,
    });

    const generatedJson = JSON.parse(await fs.readFile(generatedOutputPath, "utf8"));
    const publicJson = JSON.parse(await fs.readFile(publicOutputPath, "utf8"));

    expect(generatedJson.generatedAt).toBe(siteData.generatedAt);
    expect(publicJson.generatedAt).toBe(siteData.generatedAt);
    expect(generatedJson.entries["alpha-refresh"]?.title).toBe("Refresh check");
    expect(publicJson.entries["alpha-refresh"]?.title).toBe("Refresh check");
  });
});
