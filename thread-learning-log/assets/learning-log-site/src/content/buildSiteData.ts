import fs from "node:fs/promises";
import path from "node:path";

import { addDays, buildSortTimestamp, compareIsoDates } from "../lib/date.ts";
import type { DayRecord, LogEntry, SiteData, TagRecord } from "./types.ts";
import {
  addNormalizedTag,
  deriveSummary,
  extractInlineTags,
  parseLearningLogMarkdown,
  partitionMetadata,
} from "./parser.ts";

const HEATMAP_START_DATE = "2026-03-01";

export function buildSiteDataFromText(markdown: string): SiteData {
  const parsedEntries = parseLearningLogMarkdown(markdown);
  const seenEntryIds = new Map<string, number>();
  const entries: Record<string, LogEntry> = {};

  parsedEntries.forEach((parsedEntry, index) => {
    const partitioned = partitionMetadata(parsedEntry.rawMetadata);
    const entryId = partitioned.entryId ?? `entry-${index + 1}`;

    if (seenEntryIds.has(entryId)) {
      throw new Error(
        `Duplicate entry_id "${entryId}" at line ${parsedEntry.lineNumber}. First seen at line ${seenEntryIds.get(entryId)}.`,
      );
    }

    seenEntryIds.set(entryId, parsedEntry.lineNumber);

    const tagStore = new Map<string, string>();
    parsedEntry.rawMetadata.tags;
    for (const tag of partitioned.tags) {
      addNormalizedTag(tagStore, tag);
    }

    if (partitioned.primaryTag) {
      addNormalizedTag(tagStore, partitioned.primaryTag);
    }

    if (parsedEntry.headingTag) {
      addNormalizedTag(tagStore, parsedEntry.headingTag);
    }

    for (const tag of extractInlineTags(parsedEntry.markdown)) {
      addNormalizedTag(tagStore, tag);
    }

    const date = partitioned.date ?? parsedEntry.headingDate;
    const title = partitioned.title ?? parsedEntry.headingTitle;
    const timeStart = partitioned.timeStart ?? parsedEntry.headingTime;

    entries[entryId] = {
      id: entryId,
      entryId,
      date,
      timeStart,
      timeEnd: partitioned.timeEnd,
      timeBasis: partitioned.timeBasis,
      title,
      primaryTag: partitioned.primaryTag ?? parsedEntry.headingTag,
      tags: [...tagStore.values()],
      category: partitioned.category,
      source: partitioned.source,
      metadata: partitioned.metadata,
      markdown: parsedEntry.markdown,
      summary: deriveSummary(parsedEntry.markdown),
      sortTimestamp: buildSortTimestamp(date, timeStart, index),
    };
  });

  const sortedEntries = Object.values(entries).sort((left, right) => {
    if (left.date !== right.date) {
      return compareIsoDates(left.date, right.date);
    }

    const leftTime = left.timeStart ?? "99:99";
    const rightTime = right.timeStart ?? "99:99";

    if (leftTime !== rightTime) {
      return leftTime.localeCompare(rightTime);
    }

    return left.sortTimestamp.localeCompare(right.sortTimestamp);
  });

  const latestDate = sortedEntries[sortedEntries.length - 1]?.date;
  const earliestVisibleDate = HEATMAP_START_DATE;
  const lastVisibleDate =
    latestDate && compareIsoDates(latestDate, HEATMAP_START_DATE) >= 0 ? latestDate : HEATMAP_START_DATE;
  const dayIndex: Record<string, DayRecord> = {};

  let cursor = earliestVisibleDate;
  while (cursor <= lastVisibleDate) {
    dayIndex[cursor] = {
      date: cursor,
      entryIds: [],
      activityScore: 0,
      activityLevel: 0,
      tags: [],
    };
    cursor = addDays(cursor, 1);
  }

  const tagBuckets = new Map<string, { tag: string; entryIds: string[]; latestDate: string | null }>();

  for (const entry of sortedEntries) {
    const dayRecord = dayIndex[entry.date] ?? {
      date: entry.date,
      entryIds: [],
      activityScore: 0,
      activityLevel: 0,
      tags: [],
    };

    dayRecord.entryIds.push(entry.id);

    const dayTagStore = new Map<string, string>();
    for (const existingTag of dayRecord.tags) {
      dayTagStore.set(existingTag.toLowerCase(), existingTag);
    }
    for (const tag of entry.tags) {
      dayTagStore.set(tag.toLowerCase(), tag);
    }
    dayRecord.tags = [...dayTagStore.values()].sort((left, right) => left.localeCompare(right));
    dayRecord.activityScore = dayRecord.entryIds.length;
    dayRecord.activityLevel = toActivityLevel(dayRecord.activityScore);
    dayIndex[entry.date] = dayRecord;

    for (const tag of entry.tags) {
      const key = tag.toLowerCase();
      const bucket = tagBuckets.get(key) ?? { tag, entryIds: [], latestDate: null };
      bucket.entryIds.push(entry.id);
      if (!bucket.latestDate || compareIsoDates(bucket.latestDate, entry.date) < 0) {
        bucket.latestDate = entry.date;
      }
      tagBuckets.set(key, bucket);
    }
  }

  for (const record of Object.values(dayIndex)) {
    record.entryIds.sort((leftId, rightId) => {
      const leftEntry = entries[leftId];
      const rightEntry = entries[rightId];
      const leftTime = leftEntry?.timeStart ?? "99:99";
      const rightTime = rightEntry?.timeStart ?? "99:99";

      if (leftTime !== rightTime) {
        return leftTime.localeCompare(rightTime);
      }

      return (leftEntry?.sortTimestamp ?? "").localeCompare(rightEntry?.sortTimestamp ?? "");
    });
  }

  const tagIndex: Record<string, TagRecord> = {};
  for (const [key, bucket] of tagBuckets) {
    bucket.entryIds.sort((leftId, rightId) => {
      const leftEntry = entries[leftId];
      const rightEntry = entries[rightId];
      return (rightEntry?.sortTimestamp ?? "").localeCompare(leftEntry?.sortTimestamp ?? "");
    });

    tagIndex[key] = {
      tag: bucket.tag,
      entryIds: bucket.entryIds,
      entryCount: bucket.entryIds.length,
      latestDate: bucket.latestDate,
    };
  }

  const heatmapDays: DayRecord[] = [];
  let heatmapCursor = earliestVisibleDate;
  while (heatmapCursor <= lastVisibleDate) {
    heatmapDays.push(
      dayIndex[heatmapCursor] ?? {
        date: heatmapCursor,
        entryIds: [],
        activityScore: 0,
        activityLevel: 0,
        tags: [],
      },
    );
    heatmapCursor = addDays(heatmapCursor, 1);
  }

  return {
    appId: "personal-learning-log",
    weeks: {},
    entries,
    dayIndex,
    tagIndex,
    heatmapDays,
    datasetRange: {
      startDate: earliestVisibleDate,
      endDate: lastVisibleDate,
    },
    generatedAt: new Date().toISOString(),
  };
}

export async function buildSiteDataFile(sourcePath: string, outputPath: string): Promise<SiteData> {
  const markdown = await fs.readFile(sourcePath, "utf8");
  const siteData = buildSiteDataFromText(markdown);
  await rewriteLocalImages(siteData, sourcePath, path.resolve(path.dirname(outputPath), "../../public/log-assets"));

  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  await fs.writeFile(outputPath, `${JSON.stringify(siteData, null, 2)}\n`, "utf8");

  return siteData;
}

function toActivityLevel(activityScore: number): 0 | 1 | 2 | 3 | 4 {
  if (activityScore <= 0) return 0;
  if (activityScore === 1) return 1;
  if (activityScore === 2) return 2;
  if (activityScore === 3) return 3;
  return 4;
}

export async function rewriteLocalImages(siteData: SiteData, sourcePath: string, assetsDirectory: string) {
  const sourceDirectory = path.dirname(sourcePath);
  await fs.mkdir(assetsDirectory, { recursive: true });
  const copiedAssets = new Map<string, string>();

  for (const entry of Object.values(siteData.entries)) {
    entry.markdown = await replaceMarkdownImages(entry.markdown, async (assetPath) => {
      if (isRemoteAsset(assetPath)) {
        return assetPath;
      }

      const resolvedSource = path.resolve(sourceDirectory, assetPath);
      const relativeSource = path.relative(sourceDirectory, resolvedSource);
      const safeName = toSafeAssetName(relativeSource);
      const targetPath = path.join(assetsDirectory, safeName);

      if (!copiedAssets.has(resolvedSource)) {
        try {
          await fs.copyFile(resolvedSource, targetPath);
          copiedAssets.set(resolvedSource, `/log-assets/${safeName}`);
        } catch {
          copiedAssets.set(resolvedSource, assetPath);
        }
      }

      return copiedAssets.get(resolvedSource) ?? assetPath;
    });
  }
}

async function replaceMarkdownImages(
  markdown: string,
  resolveAssetPath: (assetPath: string) => Promise<string>,
): Promise<string> {
  const imagePattern = /(!\[[^\]]*\]\()([^)]+)(\))/g;
  let result = "";
  let lastIndex = 0;

  for (const match of markdown.matchAll(imagePattern)) {
    const [fullMatch, prefix, assetPath, suffix] = match;
    const matchIndex = match.index ?? 0;
    result += markdown.slice(lastIndex, matchIndex);
    const nextPath = await resolveAssetPath(assetPath.trim());
    result += `${prefix}${nextPath}${suffix}`;
    lastIndex = matchIndex + fullMatch.length;
  }

  result += markdown.slice(lastIndex);
  return result;
}

function isRemoteAsset(assetPath: string): boolean {
  return /^(?:https?:|data:|#)/i.test(assetPath);
}

function toSafeAssetName(relativePath: string): string {
  return relativePath
    .replace(/^[./]+/, "")
    .replace(/[\\/]+/g, "--")
    .replace(/[^A-Za-z0-9._-]+/g, "-");
}
