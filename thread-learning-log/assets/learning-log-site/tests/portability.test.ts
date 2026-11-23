import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { afterEach, expect, it, vi } from 'vitest';

afterEach(() => { vi.unstubAllEnvs(); vi.resetModules(); });
it('builds a private empty dataset before the first review', async () => {
  const { buildSiteDataOutputs } = await import('../src/content/buildSiteDataOutputs.ts');
  const root = await fs.mkdtemp(path.join(os.tmpdir(),'cold-learning-site-'));
  const data = await buildSiteDataOutputs(path.join(root,'learning-log.md'),{generatedOutputPath:path.join(root,'generated/site-data.json'),publicOutputPath:path.join(root,'public/site-data.json'),weeksDirectory:path.join(root,'reports/weeks')});
  expect(data.entries).toEqual({});expect(data.weeks).toEqual({});
});
it('uses configured data paths outside the code checkout', async () => {
  vi.stubEnv('LEARNING_LOG_ROOT','/example/private-notes');vi.stubEnv('LEARNING_LOG_REPORT_DIR','/example/private-reports');vi.resetModules();
  const config = await import('../src/content/buildSiteDataOutputs.ts');
  expect((config as any).defaultLogPath).toBe('/example/private-notes/learning-log.md');
  expect(config.defaultWeeksDirectory).toBe('/example/private-reports/weeks');
});
it('accepts a weekly snapshot in another IANA timezone', async () => {
  const { buildSiteDataOutputs } = await import('../src/content/buildSiteDataOutputs.ts');
  const root = await fs.mkdtemp(path.join(os.tmpdir(),'utc-learning-site-'));await fs.mkdir(path.join(root,'weeks'));await fs.writeFile(path.join(root,'learning-log.md'),'# Learning Log\n');
  await fs.writeFile(path.join(root,'weeks/2026-11-16.json'),JSON.stringify({schema_version:1,week_start:'2026-11-16',week_end:'2026-11-22',timezone:'UTC',tasks:[],lesson_ids:[],coverage:{thread_count:0,archived_count:0,limitations:[]}}));
  const data=await buildSiteDataOutputs(path.join(root,'learning-log.md'),{generatedOutputPath:path.join(root,'generated.json'),publicOutputPath:path.join(root,'public/site-data.json'),weeksDirectory:path.join(root,'weeks')});
  expect(data.weeks?.['2026-11-16'].timezone).toBe('UTC');
});
