import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { randomUUID } from "node:crypto";
import type { SiteData, WeeklyReview } from "./types.ts";
import { buildSiteDataFromText, rewriteLocalImages } from "./buildSiteData.ts";
import { addDays } from "../lib/date.ts";

interface BuildSiteDataOutputsOptions {
  generatedOutputPath: string;
  publicOutputPath: string;
  weeksDirectory?: string;
}
const dataRoot = path.resolve(process.env.LEARNING_LOG_ROOT ?? path.join(process.env.CODEX_HOME ?? path.join(os.homedir(), ".codex"), "skills/thread-learning-log"));
export const defaultLogPath = path.join(dataRoot, "learning-log.md");
export const defaultWeeksDirectory = process.env.LEARNING_LOG_WEEKLY_DIR ?? path.join(process.env.LEARNING_LOG_REPORT_DIR ?? path.join(dataRoot, "reports"), "weeks");
function validTimezone(value: string): boolean {
  try { new Intl.DateTimeFormat("en", { timeZone: value }).format(); return typeof value === "string" && Boolean(value); }
  catch { return false; }
}

async function readWeeks(directory: string | undefined, data: SiteData): Promise<Record<string, WeeklyReview>> {
  if (!directory) return {};
  const files = await fs.readdir(directory).catch((error: NodeJS.ErrnoException) => {
    if (error.code === "ENOENT") return [];
    throw error;
  });
  const weeks: Record<string, WeeklyReview> = {};
  for (const file of files.filter((file) => file.endsWith(".json")).sort()) {
    const week = JSON.parse(await fs.readFile(path.join(directory, file), "utf8")) as WeeklyReview;
    if (week.schema_version !== 1 || !/^\d{4}-\d{2}-\d{2}$/.test(week.week_start) || file !== `${week.week_start}.json` || week.week_end !== addDays(week.week_start, 6) || new Date(`${week.week_start}T00:00:00Z`).getUTCDay() !== 1 || !validTimezone(week.timezone) || !Array.isArray(week.tasks) || !Array.isArray(week.lesson_ids) || !Array.isArray(week.coverage?.limitations)) {
      throw new Error(`Invalid weekly snapshot: ${file}`);
    }
    const ids = new Set<string>();
    for (const task of week.tasks) {
      if (!task.id || ids.has(task.id) || !task.title || !task.project || !task.summary || !["completed", "in_progress"].includes(task.status) || !Array.isArray(task.evidence) || !task.evidence.length || !Array.isArray(task.lesson_ids)) throw new Error(`Invalid task in ${file}`);
      ids.add(task.id);
      for (const reference of task.evidence) {
        if (!reference.title || !reference.thread_id || reference.url !== `codex://threads/${reference.thread_id}`) throw new Error(`Invalid source link in ${file}`);
      }
      for (const id of task.lesson_ids) if (!week.lesson_ids.includes(id)) throw new Error(`Task references a lesson outside its week: ${id}`);
    }
    for (const id of week.lesson_ids) if (!data.entries[id]) throw new Error(`Missing canonical lesson ${id} in ${file}`);
    weeks[week.week_start] = week;
  }
  return weeks;
}

async function writeAtomic(destination: string, content: string) {
  await fs.mkdir(path.dirname(destination), { recursive: true });
  const temporary = `${destination}.${randomUUID()}.tmp`;
  try {
    await fs.writeFile(temporary, content, { encoding: "utf8", mode: 0o600 });
    await fs.rename(temporary, destination);
  } finally {
    await fs.rm(temporary, { force: true });
  }
}

export async function buildSiteDataOutputs(sourcePath: string, options: BuildSiteDataOutputsOptions): Promise<SiteData> {
  const source = await fs.readFile(sourcePath, "utf8").catch((error: NodeJS.ErrnoException) => {
    if (error.code === "ENOENT") return "# Learning Log\n";
    throw error;
  });
  const siteData = buildSiteDataFromText(source);
  siteData.weeks = await readWeeks(options.weeksDirectory, siteData);
  await rewriteLocalImages(siteData, sourcePath, path.join(path.dirname(options.publicOutputPath), "log-assets"));
  const serialized = `${JSON.stringify(siteData, null, 2)}\n`;
  await writeAtomic(options.generatedOutputPath, serialized);
  await writeAtomic(options.publicOutputPath, serialized);
  return siteData;
}
