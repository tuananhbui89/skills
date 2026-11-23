export type RouteState =
  | { kind: "none" }
  | { kind: "weekly"; week: string | null }
  | { kind: "lessons" }
  | { kind: "day"; day: string }
  | { kind: "tag"; tag: string };

const dayPattern = /^\d{4}-\d{2}-\d{2}$/;

export function parseRouteState(search: string): RouteState {
  const params = new URLSearchParams(search);
  const tag = params.get("tag");
  const day = params.get("day");
  const view = params.get("view");
  const week = params.get("week");
  if (view === "weekly") return { kind: "weekly", week: week && dayPattern.test(week) ? week : null };

  if (tag && tag.trim()) {
    return { kind: "tag", tag: tag.trim() };
  }

  if (day && dayPattern.test(day)) {
    return { kind: "day", day };
  }

  return view === "lessons" ? { kind: "lessons" } : { kind: "none" };
}

export function toCanonicalSearch(routeState: RouteState): string {
  const params = new URLSearchParams();
  if (routeState.kind === "weekly") {
    params.set("view", "weekly");
    if (routeState.week) params.set("week", routeState.week);
  }
  if (routeState.kind === "lessons") params.set("view", "lessons");

  if (routeState.kind === "day") {
    params.set("day", routeState.day);
  }

  if (routeState.kind === "tag") {
    params.set("tag", routeState.tag);
  }

  const serialized = params.toString();
  return serialized ? `?${serialized}` : "";
}

export function normalizeSearch(search: string): string {
  return toCanonicalSearch(parseRouteState(search));
}
