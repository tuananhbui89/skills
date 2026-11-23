import type { LogEntry } from "../content/types";
import { formatLongDate, formatTimeRange } from "../lib/date";
import { TagChip } from "./TagChip";

interface EntryTimelineProps {
  entries: LogEntry[];
  selectedDay: string | null;
  onOpenDay: (day: string, trigger: HTMLElement) => void;
  onSelectTag: (tag: string) => void;
}

export function EntryTimeline(props: EntryTimelineProps) {
  return (
    <section className="timeline-card" aria-label="Lessons over time">
      <ol className="timeline-list">
        {props.entries.map((entry) => {
          const isActive = props.selectedDay === entry.date;

          return (
            <li key={entry.id} className="timeline-item">
              <article className="timeline-entry" data-active={isActive ? "true" : "false"}>
                <div className="timeline-entry-head">
                  <div>
                    <p className="timeline-date">{formatLongDate(entry.date)}</p>
                    <h3>{entry.title}</h3>
                  </div>
                  <p className="timeline-time">{formatTimeRange(entry.timeStart, entry.timeEnd)}</p>
                </div>

                <p className="timeline-meta">
                  <span>{entry.category ?? "Uncategorized"}</span>
                  <span aria-hidden="true">•</span>
                  <span>{entry.source ?? "Unknown source"}</span>
                </p>

                <p className="timeline-summary">{entry.summary}</p>

                <div className="tag-row" aria-label={`Tags for ${entry.title}`}>
                  {entry.tags.map((tag) => (
                    <TagChip key={`${entry.id}-${tag}`} tag={tag} onClick={props.onSelectTag} />
                  ))}
                </div>

                <div className="timeline-actions">
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={(event) => props.onOpenDay(entry.date, event.currentTarget)}
                  >
                    Open day
                  </button>
                </div>
              </article>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
