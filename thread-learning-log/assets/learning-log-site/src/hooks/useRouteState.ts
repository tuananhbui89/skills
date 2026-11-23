import { useEffect, useState } from "react";

import { normalizeSearch, parseRouteState, toCanonicalSearch, type RouteState } from "../lib/routeState";

export function useRouteState() {
  const [routeState, setRouteState] = useState<RouteState>(() => {
    if (typeof window === "undefined") {
      return { kind: "none" };
    }

    return parseRouteState(window.location.search);
  });

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const canonicalSearch = normalizeSearch(window.location.search);
    if (canonicalSearch !== window.location.search) {
      window.history.replaceState({}, "", `${window.location.pathname}${canonicalSearch}`);
    }

    setRouteState(parseRouteState(canonicalSearch));

    const handlePopState = () => {
      setRouteState(parseRouteState(window.location.search));
    };

    window.addEventListener("popstate", handlePopState);
    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, []);

  const navigate = (nextState: RouteState) => {
    if (typeof window === "undefined") {
      setRouteState(nextState);
      return;
    }

    const nextSearch = toCanonicalSearch(nextState);
    const nextUrl = `${window.location.pathname}${nextSearch}`;
    const currentUrl = `${window.location.pathname}${window.location.search}`;

    if (nextUrl !== currentUrl) {
      window.history.pushState({}, "", nextUrl);
    }

    setRouteState(nextState);
  };

  return {
    routeState,
    selectWeek(week: string | null = null) { navigate({ kind: "weekly", week }); },
    showLessons() { navigate({ kind: "lessons" }); },
    selectDay(day: string) {
      navigate({ kind: "day", day });
    },
    selectTag(tag: string) {
      navigate({ kind: "tag", tag });
    },
    clearSelection() {
      navigate({ kind: "lessons" });
    },
  };
}
