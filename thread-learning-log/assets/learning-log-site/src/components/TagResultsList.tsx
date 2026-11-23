import { useRef } from "react";

import type { LogEntry, TagRecord } from "../content/types";
import { formatLongDate, formatTimeRange } from "../lib/date";
import { usePanelFocusTrap } from "../hooks/usePanelFocusTrap";
import { TagChip } from "./TagChip";

interface TagResultsListProps {
  tagRecord: TagRecord | null;
  entries: LogEntry[];
  requestedTag: string;
  isOpen: boolean;
  onClose: () => void;
  onOpenDay: (day: string) => void;
  onSelectTag: (tag: string) => void;
}

export function TagResultsList(props: TagResultsListProps) {
  const panelRef = useRef<HTMLElement | null>(null);

  usePanelFocusTrap({
    active: props.isOpen,
    containerRef: panelRef,
    onClose: props.onClose,
  });

  if (!props.isOpen) {
    return null;
  }

  const activeTagLabel = props.tagRecord?.tag ?? props.requestedTag;

  return (
    <div className="panel-shell" role="presentation">
      <div className="panel-backdrop" onClick={props.onClose} />
      <aside ref={panelRef} className="panel panel--tag" role="dialog" aria-modal="true" aria-labelledby="tag-panel-title" tabIndex={-1}>
        <header className="panel-header">
          <div>
            <p className="eyebrow">Tag view</p>
            <h2 id="tag-panel-title">{activeTagLabel}</h2>
            <p className="panel-subtitle">
              {props.tagRecord ? `${props.tagRecord.entryCount} matching posts` : "No matching posts"}
            </p>
          </div>
          <button type="button" className="panel-close" onClick={props.onClose} aria-label="Close tag results" data-autofocus>
            Close
          </button>
        </header>

        <div className="panel-body">
          {!props.entries.length ? (
            <section className="empty-state">
              <h3>No posts found</h3>
              <p>No entries in the current dataset include this tag.</p>
            </section>
          ) : (
            <div className="tag-results">
              {props.entries.map((entry) => (
                <article key={entry.id} className="tag-result-card">
                  <div className="tag-result-topline">
                    <p>{formatLongDate(entry.date)}</p>
                    <p>{formatTimeRange(entry.timeStart, entry.timeEnd)}</p>
                  </div>
                  <h3>{entry.title}</h3>
                  <p className="tag-result-snippet">{entry.summary}</p>
                  <div className="tag-row">
                    {entry.tags.map((tag) => (
                      <TagChip
                        key={`${entry.id}-${tag}`}
                        tag={tag}
                        onClick={props.onSelectTag}
                        isActive={tag.toLowerCase() === activeTagLabel.toLowerCase()}
                      />
                    ))}
                  </div>
                  <button type="button" className="secondary-button" onClick={() => props.onOpenDay(entry.date)}>
                    Open day
                  </button>
                </article>
              ))}
            </div>
          )}
        </div>
      </aside>
    </div>
  );
}
