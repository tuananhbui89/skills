import { useRef } from "react";

import type { DayRecord, LogEntry } from "../content/types";
import { formatLongDate, formatTimeRange } from "../lib/date";
import { usePanelFocusTrap } from "../hooks/usePanelFocusTrap";
import { MarkdownRenderer } from "./MarkdownRenderer";
import { MetadataList } from "./MetadataList";
import { TagChip } from "./TagChip";

interface DayDetailPanelProps {
  day: DayRecord;
  entries: LogEntry[];
  isOpen: boolean;
  onClose: () => void;
  onSelectTag: (tag: string) => void;
  returnFocusRef?: { current: HTMLElement | null };
}

export function DayDetailPanel(props: DayDetailPanelProps) {
  const panelRef = useRef<HTMLElement | null>(null);

  usePanelFocusTrap({
    active: props.isOpen,
    containerRef: panelRef,
    returnFocusRef: props.returnFocusRef,
    onClose: props.onClose,
  });

  if (!props.isOpen) {
    return null;
  }

  return (
    <div className="panel-shell" role="presentation">
      <div className="panel-backdrop" onClick={props.onClose} />
      <aside ref={panelRef} className="panel panel--day" role="dialog" aria-modal="true" aria-labelledby="day-panel-title" tabIndex={-1}>
        <header className="panel-header">
          <div>
            <p className="eyebrow">Day detail</p>
            <h2 id="day-panel-title">{formatLongDate(props.day.date)}</h2>
            <p className="panel-subtitle">
              {props.day.activityScore} {props.day.activityScore === 1 ? "entry" : "entries"}
            </p>
          </div>
          <button type="button" className="panel-close" onClick={props.onClose} aria-label="Close day details" data-autofocus>
            Close
          </button>
        </header>

        <div className="panel-body">
          {!props.entries.length ? (
            <section className="empty-state">
              <h3>No activity logged</h3>
              <p>This date is in the visible range, but there are no entries recorded for it yet.</p>
            </section>
          ) : (
            props.entries.map((entry) => (
              <article key={entry.id} className="entry-card">
                <header className="entry-card-header">
                  <div>
                    <p className="entry-meta-line">{entry.category ?? "Uncategorized"}</p>
                    <h3>{entry.title}</h3>
                  </div>
                  <p className="entry-time">{formatTimeRange(entry.timeStart, entry.timeEnd)}</p>
                </header>

                <dl className="entry-summary-grid">
                  <div>
                    <dt>Source</dt>
                    <dd>{entry.source ?? "Unknown source"}</dd>
                  </div>
                  <div>
                    <dt>Time basis</dt>
                    <dd>{entry.timeBasis ?? "Not specified"}</dd>
                  </div>
                </dl>

                <div className="tag-row" aria-label={`Tags for ${entry.title}`}>
                  {entry.tags.map((tag) => (
                    <TagChip key={`${entry.id}-${tag}`} tag={tag} onClick={props.onSelectTag} />
                  ))}
                </div>

                <MetadataList metadata={entry.metadata} />
                <MarkdownRenderer markdown={entry.markdown} />
              </article>
            ))
          )}
        </div>
      </aside>
    </div>
  );
}
