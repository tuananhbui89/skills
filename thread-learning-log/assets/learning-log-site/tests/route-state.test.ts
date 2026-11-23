import { describe, expect, it } from "vitest";

import { normalizeSearch, parseRouteState, toCanonicalSearch } from "../src/lib/routeState.ts";

describe("route state helpers", () => {
  it("parses a day route", () => {
    expect(parseRouteState("?day=2026-04-02")).toEqual({ kind: "day", day: "2026-04-02" });
  });

  it("prefers tags over days when both are present", () => {
    expect(parseRouteState("?day=2026-04-02&tag=%40AgentMemory")).toEqual({
      kind: "tag",
      tag: "@AgentMemory",
    });
    expect(normalizeSearch("?day=2026-04-02&tag=%40AgentMemory")).toBe("?tag=%40AgentMemory");
  });

  it("serializes shareable URLs for refresh", () => {
    expect(toCanonicalSearch({ kind: "tag", tag: "@PSOM" })).toBe("?tag=%40PSOM");
    expect(toCanonicalSearch({ kind: "day", day: "2026-03-25" })).toBe("?day=2026-03-25");
  });
});
