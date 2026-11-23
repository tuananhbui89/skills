import type { DayRecord } from "../content/types";
import { formatLongDate } from "../lib/date";

interface HeatmapCellProps {
  day: DayRecord;
  isSelected: boolean;
  onSelect: (day: DayRecord, trigger: HTMLElement) => void;
}

export function HeatmapCell(props: HeatmapCellProps) {
  const { day, isSelected, onSelect } = props;
  const label = `${formatLongDate(day.date)}. ${day.activityScore} ${day.activityScore === 1 ? "entry" : "entries"}.`;

  return (
    <button
      type="button"
      className="heatmap-cell"
      data-level={day.activityLevel}
      data-selected={isSelected ? "true" : "false"}
      aria-label={label}
      aria-pressed={isSelected}
      onClick={(event) => onSelect(day, event.currentTarget)}
    >
      <span className="sr-only">{label}</span>
    </button>
  );
}
