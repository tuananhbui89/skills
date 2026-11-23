import type { SiteData, TaskSnapshot } from '../content/types';
import { formatLongDate } from '../lib/date';
import { MarkdownRenderer } from './MarkdownRenderer';

interface Props { siteData: SiteData; weekStart: string | null; onSelectWeek: (week: string) => void }
export function WeeklyOverview({ siteData, weekStart, onSelectWeek }: Props) {
  const weeks = siteData.weeks ?? {};
  const dates = Object.keys(weeks).sort().reverse();
  const selected = weekStart ?? dates[0];
  const week = weeks[selected];
  const formatWeek = (date: string) => `${formatLongDate(date)} – ${formatLongDate(weeks[date].week_end)}`;
  if (!dates.length) return <main className="app-shell"><section className="weekly-empty"><h1>Your weeks, in one place</h1><p>Completed work, progress and reusable lessons will appear after the next weekly review.</p></section></main>;
  return <main className="app-shell weekly-view">
    <header className="weekly-header">
      <div><p className="eyebrow">Progress &amp; learning</p><h1>Weekly review</h1><p className="weekly-intro">What moved forward, and what is worth remembering.</p></div>
      <label className="week-picker">Week<select value={selected} onChange={(event) => onSelectWeek(event.target.value)}>
        {!week && <option value={selected}>Week not available</option>}
        {dates.map((date) => <option key={date} value={date}>{formatWeek(date)}</option>)}
      </select></label>
    </header>
    {!week ? <section className="weekly-empty"><h2>No snapshot for this week</h2><p>Choose an available week above.</p></section> : <>
      <div className="weekly-stats" aria-label="Week totals">
        <span><strong>{week.tasks.filter(t => t.status === 'completed').length}</strong> completed</span>
        <span><strong>{week.tasks.filter(t => t.status === 'in_progress').length}</strong> in progress</span>
        <span><strong>{week.lesson_ids.length}</strong> reusable lessons</span>
        <span className="week-asof">Status at {formatLongDate(week.week_end)}</span>
      </div>
      <div className="task-columns">
        {(['completed', 'in_progress'] as const).map(status => <section key={status} aria-labelledby={`heading-${status}`}>
          <h2 id={`heading-${status}`} className="section-title"><span className={`status-dot ${status}`} />{status === 'completed' ? 'Completed' : 'In progress'}</h2>
          <div className="task-list">{week.tasks.filter(t => t.status === status).map(task => <TaskCard key={task.id} task={task} siteData={siteData} />)}
          {!week.tasks.some(t => t.status === status) && <p className="weekly-empty-small">No {status === 'completed' ? 'completed tasks' : 'work in progress'} recorded this week.</p>}</div>
        </section>)}
      </div>
      <section className="weekly-lessons" aria-labelledby="weekly-lessons-heading">
        <p className="eyebrow">Keep for next time</p><h2 id="weekly-lessons-heading" className="section-title">Lessons</h2>
        <div className="lesson-grid">{week.lesson_ids.map(id => {
          const entry = siteData.entries[id];
          return entry ? <article key={id} id={`lesson-${id}`} className="weekly-lesson">
            <div className="weekly-tags">{entry.tags.join(' · ')}</div><h3>{entry.title}</h3><p>{entry.summary}</p>
            <details><summary>Read lesson</summary><MarkdownRenderer markdown={entry.markdown} />
              <div className="task-sources">{(week.lesson_evidence?.[id] ?? []).filter((source, index, all) => all.findIndex(item => item.thread_id === source.thread_id) === index).map(source => <a key={source.thread_id} href={source.url}>{source.title}</a>)}</div>
            </details>
          </article> : null;
        })}</div>
        {!week.lesson_ids.length && <p>No reusable lessons met the inclusion criteria this week.</p>}
      </section>
      <footer className="weekly-coverage">Reviewed {week.coverage.thread_count} chats, including {week.coverage.archived_count} archived. Times use {week.timezone}.
        {week.coverage.limitations.map((limitation, index) => <p key={index}>Coverage limitation: {limitation}</p>)}
      </footer>
    </>}
  </main>;
}
function TaskCard({ task, siteData }: { task: TaskSnapshot; siteData: SiteData }) {
  const sources = task.evidence.filter((source, index, all) => all.findIndex(item => item.thread_id === source.thread_id) === index);
  return <article className="task-card"><p className="task-project">{task.project}</p><h3>{task.title}</h3><p>{task.summary}</p>
    {task.blocker && <p className="task-blocker"><strong>Blocker:</strong> {task.blocker}</p>}
    <div className="task-sources">{sources.map(source => <a key={source.thread_id} href={source.url}>{source.title}</a>)}</div>
    {task.lesson_ids.length > 0 && <div className="related-lessons">{task.lesson_ids.map(id => <a key={id} href={`#lesson-${id}`}>Lesson: {siteData.entries[id]?.title}</a>)}</div>}
  </article>;
}
