import { useRef } from "react";

import { LearningLogExperience } from "./LearningLogExperience";
import { WeeklyOverview } from "./components/WeeklyOverview";
import type { DayRecord } from "./content/types";
import { useRouteState } from "./hooks/useRouteState";
import { useSiteData } from "./hooks/useSiteData";

export default function App() {
  const siteData = useSiteData();
  const { routeState, selectDay, selectTag, clearSelection, selectWeek, showLessons } = useRouteState();
  const returnFocusRef = useRef<HTMLElement | null>(null);

  const handleSelectDay = (day: DayRecord, trigger: HTMLElement) => {
    returnFocusRef.current = trigger;
    selectDay(day.date);
  };

  const weekly = routeState.kind === "none" || routeState.kind === "weekly";
  return <>
    <nav className="view-navigation app-shell" aria-label="Main views">
      <button type="button" aria-current={weekly ? "page" : undefined} onClick={() => selectWeek()}>Weekly</button>
      <button type="button" aria-current={!weekly ? "page" : undefined} onClick={showLessons}>Lessons</button>
    </nav>
    {weekly ? <WeeklyOverview siteData={siteData} weekStart={routeState.kind === "weekly" ? routeState.week : null} onSelectWeek={selectWeek} /> : (
    <LearningLogExperience
      siteData={siteData}
      routeState={routeState}
      onSelectDay={handleSelectDay}
      onSelectTag={selectTag}
      onOpenDay={selectDay}
      onClearRoute={clearSelection}
      returnFocusRef={returnFocusRef}
    />
  )}</>;
}
