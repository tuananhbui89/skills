import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { describe, expect, it } from 'vitest';
import { buildSiteDataOutputs } from '../src/content/buildSiteDataOutputs.ts';
import { parseRouteState, toCanonicalSearch } from '../src/lib/routeState.ts';

const log = `# Learning Log
## 2026-11-18 | @Testing | Durable lesson
entry_id: "lesson-1"
date: "2026-11-18"
title: "Durable lesson"
tags: ["@Testing"]
### Summary
Keep timezone boundaries explicit.
### What I Learned
Use local calendar arithmetic.
`;
const evidence = [{ thread_id: 'source', title: 'Source chat', at: '2026-11-18T00:00:00Z', url: 'codex://threads/source' }];
const week = { schema_version: 1, week_start: '2026-11-16', week_end: '2026-11-22', timezone: 'Australia/Melbourne', generated_at: '2026-11-23T00:00:00Z', coverage: { thread_count: 1, archived_count: 0, limitations: [] }, tasks: [
  { id: 'done', title: 'Shipped parser', project: 'Demo', status: 'completed', summary: 'Parser passes.', evidence, lesson_ids: ['lesson-1'] },
  { id: 'pending', title: 'Submit PR', project: 'Demo', status: 'in_progress', summary: 'Branch pushed.', blocker: 'Sign-in needed', evidence, lesson_ids: [] },
], lesson_ids: ['lesson-1'] };

async function fixture() {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'weekly-site-test-'));
  const source = path.join(root, 'learning-log.md');
  const options = { generatedOutputPath: path.join(root, 'src/generated/site-data.json'), publicOutputPath: path.join(root, 'public/site-data.json'), weeksDirectory: path.join(root, 'weeks') };
  await fs.writeFile(source, log);
  await fs.mkdir(options.weeksDirectory);
  await fs.writeFile(path.join(options.weeksDirectory, '2026-11-16.json'), JSON.stringify(week));
  return { root, source, options };
}

describe('weekly snapshots', () => {
  it('loads weekly records linked to canonical lessons', async () => {
    const { source, options } = await fixture();
    const data = await buildSiteDataOutputs(source, options);
    expect((data as any).weeks?.['2026-11-16']?.tasks).toHaveLength(2);
    expect(data.entries['lesson-1'].title).toBe('Durable lesson');
  });

  it('preserves the last published website snapshot when input is invalid', async () => {
    const { source, options } = await fixture();
    await buildSiteDataOutputs(source, options);
    const before = await fs.readFile(options.publicOutputPath, 'utf8');
    await fs.writeFile(path.join(options.weeksDirectory, '2026-11-16.json'), JSON.stringify({ ...week, lesson_ids: ['missing'] }));
    await expect(buildSiteDataOutputs(source, options)).rejects.toThrow(/lesson/i);
    expect(await fs.readFile(options.publicOutputPath, 'utf8')).toBe(before);
    expect(await fs.readFile(options.generatedOutputPath, 'utf8')).toBe(before);
  });

  it('keeps old links and adds weekly and lessons routes', () => {
    expect(parseRouteState('?view=weekly&week=2026-11-16')).toEqual({ kind: 'weekly', week: '2026-11-16' });
    expect(parseRouteState('?view=lessons')).toEqual({ kind: 'lessons' });
    expect(parseRouteState('?day=2026-11-18')).toEqual({ kind: 'day', day: '2026-11-18' });
    expect(toCanonicalSearch({ kind: 'weekly', week: '2026-11-16' } as any)).toBe('?view=weekly&week=2026-11-16');
  });

  it('renders completed, in-progress, source links and expandable lessons', async () => {
    const file = path.resolve('src/components/WeeklyOverview.tsx');
    expect(await fs.stat(file).then(() => true).catch(() => false)).toBe(true);
    const { WeeklyOverview } = await import('../src/components/WeeklyOverview.tsx');
    const { source, options } = await fixture();
    const data = await buildSiteDataOutputs(source, options);
    const html = renderToStaticMarkup(<WeeklyOverview siteData={data} weekStart="2026-11-16" onSelectWeek={() => {}} />);
    expect(html).toContain('Completed');
    expect(html).toContain('In progress');
    expect(html).toContain('Sign-in needed');
    expect(html).toContain('codex://threads/source');
    expect(html).toContain('<details');
    expect(html).toContain('Use local calendar arithmetic.');
  });
});
