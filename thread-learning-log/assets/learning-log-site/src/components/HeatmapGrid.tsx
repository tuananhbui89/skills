import type { CSSProperties } from "react";

import type { DayRecord } from "../content/types";
import { addMonths, dayOfWeek, daysBetween, formatHeatmapMonthLabel, startOfMonth } from "../lib/date";
import { HeatmapCell } from "./HeatmapCell";

interface HeatmapGridProps {
  days: DayRecord[];
  selectedDay: string | null;
  onSelectDay: (day: DayRecord, trigger: HTMLElement) => void;
}

export function HeatmapGrid(props: HeatmapGridProps) {
  const weeks = buildWeeks(props.days);
  const weekdayLabels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const visibleWeekCount = getVisibleWeekCount(props.days, 3);
  const heatmapStyle = {
    "--heatmap-week-count": weeks.length,
    "--heatmap-visible-week-count": visibleWeekCount,
  } as CSSProperties;

  return (
    <section className="heatmap-card" aria-labelledby="heatmap-title">
      <div className="heatmap-header">
        <div>
          <p className="eyebrow">Activity Atlas</p>
          <h2 id="heatmap-title">Learning heatmap</h2>
        </div>
        <p className="heatmap-legend" aria-hidden="true">
          Less <span data-level="0" /> <span data-level="1" /> <span data-level="2" /> <span data-level="3" /> <span data-level="4" /> More
        </p>
      </div>

      <div className="heatmap-scroll" style={heatmapStyle}>
        <div className="heatmap-months">
          <div className="heatmap-month-label heatmap-month-gutter" />
          {weeks.map((week, index) => (
            <div key={`month-${index}`} className="heatmap-month-label">
              {week.monthLabel}
            </div>
          ))}
        </div>

        <div className="heatmap-grid-wrap">
          <div className="heatmap-weekdays" aria-hidden="true">
            {weekdayLabels.map((label) => (
              <span key={label}>{label}</span>
            ))}
          </div>

          <div className="heatmap-grid" role="grid" aria-label="Daily activity heatmap">
            {weeks.map((week, weekIndex) => (
              <div key={`week-${weekIndex}`} className="heatmap-week" role="rowgroup">
                {week.days.map((day, dayIndex) =>
                  day ? (
                    <HeatmapCell
                      key={day.date}
                      day={day}
                      isSelected={props.selectedDay === day.date}
                      onSelect={props.onSelectDay}
                    />
                  ) : (
                    <span key={`placeholder-${weekIndex}-${dayIndex}`} className="heatmap-cell heatmap-cell--placeholder" aria-hidden="true" />
                  ),
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function buildWeeks(days: DayRecord[]) {
  const weeks: Array<{ monthLabel: string; days: Array<DayRecord | null> }> = [];
  let previousMonthKey: string | null = null;

  for (let index = 0; index < days.length; index += 7) {
    const slice = days.slice(index, index + 7);
    const padded: Array<DayRecord | null> = [...slice];

    while (padded.length < 7) {
      padded.push(null);
    }

    const firstDay = slice[0];
    const monthKey = firstDay ? firstDay.date.slice(0, 7) : "";
    const includeYear = Boolean(firstDay && (previousMonthKey === null || previousMonthKey.slice(0, 4) !== monthKey.slice(0, 4)));
    const monthLabel = firstDay && monthKey !== previousMonthKey ? formatHeatmapMonthLabel(firstDay.date, includeYear) : "";

    weeks.push({
      monthLabel,
      days: padded,
    });

    previousMonthKey = monthKey;
  }

  return weeks;
}

function getVisibleWeekCount(days: DayRecord[], visibleMonths: number): number {
  const firstDate = days[0]?.date;
  if (!firstDate) {
    return 1;
  }

  const startDate = startOfMonth(firstDate);
  const endDate = addMonths(startDate, visibleMonths);
  return Math.max(1, Math.ceil(daysBetween(startDate, endDate) / 7));
}

export function isSundayAligned(days: DayRecord[]): boolean {
  if (!days.length) {
    return true;
  }

  return dayOfWeek(days[0].date) === 0;
}
