import type { DayRecord, LogEntry, SiteData, TagRecord } from "./content/types";
import type { RouteState } from "./lib/routeState";
import { HeatmapGrid } from "./components/HeatmapGrid";
import { DayDetailPanel } from "./components/DayDetailPanel";
import { TagResultsList } from "./components/TagResultsList";
import { EntryTimeline } from "./components/EntryTimeline";

interface LearningLogExperienceProps {
  siteData: SiteData;
  routeState: RouteState;
  onSelectDay: (day: DayRecord, trigger: HTMLElement) => void;
  onSelectTag: (tag: string) => void;
  onOpenDay: (day: string) => void;
  onClearRoute: () => void;
  returnFocusRef?: { current: HTMLElement | null };
}

export function LearningLogExperience(props: LearningLogExperienceProps) {
  const activeDayRecord = props.routeState.kind === "day" ? props.siteData.dayIndex[props.routeState.day] ?? emptyDay(props.routeState.day) : null;
  const activeDayEntries = activeDayRecord ? activeDayRecord.entryIds.map((entryId) => props.siteData.entries[entryId]).filter(Boolean) : [];

  const activeTagRecord =
    props.routeState.kind === "tag" ? props.siteData.tagIndex[props.routeState.tag.toLowerCase()] ?? null : null;
  const activeTagEntries =
    props.routeState.kind === "tag"
      ? (activeTagRecord?.entryIds ?? []).map((entryId) => props.siteData.entries[entryId]).filter(Boolean)
      : [];

  const timelineEntries = Object.values(props.siteData.entries).sort((left, right) => right.sortTimestamp.localeCompare(left.sortTimestamp));

  return (
    <div className="app-shell">
      <main className="page-layout">
        <HeatmapGrid
          days={props.siteData.heatmapDays}
          selectedDay={props.routeState.kind === "day" ? props.routeState.day : null}
          onSelectDay={props.onSelectDay}
        />

        <EntryTimeline
          entries={timelineEntries}
          selectedDay={props.routeState.kind === "day" ? props.routeState.day : null}
          onOpenDay={(day, trigger) => props.onSelectDay(props.siteData.dayIndex[day] ?? emptyDay(day), trigger)}
          onSelectTag={props.onSelectTag}
        />
      </main>

      <DayDetailPanel
        day={activeDayRecord ?? emptyDay(props.siteData.datasetRange.endDate)}
        entries={activeDayEntries}
        isOpen={props.routeState.kind === "day"}
        onClose={props.onClearRoute}
        onSelectTag={props.onSelectTag}
        returnFocusRef={props.returnFocusRef}
      />

      <TagResultsList
        tagRecord={activeTagRecord}
        entries={activeTagEntries}
        requestedTag={props.routeState.kind === "tag" ? props.routeState.tag : ""}
        isOpen={props.routeState.kind === "tag"}
        onClose={props.onClearRoute}
        onOpenDay={props.onOpenDay}
        onSelectTag={props.onSelectTag}
      />
    </div>
  );
}

function emptyDay(date: string): DayRecord {
  return {
    date,
    entryIds: [],
    activityScore: 0,
    activityLevel: 0,
    tags: [],
  };
}
