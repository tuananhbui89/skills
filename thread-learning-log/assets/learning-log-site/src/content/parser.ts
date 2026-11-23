import { visit } from "unist-util-visit";

import { extractSectionMarkdown, firstParagraphText, markdownToPlainText, parseMarkdownTree } from "../lib/markdown.ts";
import type { ParsedLogEntry } from "./types.ts";

const headingPattern = /^##\s+(\d{4}-\d{2}-\d{2})(?:\s+(\d{2}:\d{2}))?\s+\|\s+(@[A-Za-z][\w-]*)\s+\|\s+(.+?)\s*$/;
const metadataPattern = /^([a-z_]+):\s*(.+)\s*$/;
const knownMetadataKeys = new Set([
  "entry_id",
  "date",
  "time_start",
  "time_end",
  "time_basis",
  "category",
  "primary_tag",
  "tags",
  "source",
  "title",
  "source_locations",
  "reference_locations",
]);

export function parseLearningLogMarkdown(markdown: string): ParsedLogEntry[] {
  const lines = markdown.split(/\r?\n/);
  const entries: ParsedLogEntry[] = [];
  let currentStart = -1;

  for (let index = 0; index < lines.length; index += 1) {
    if (headingPattern.test(lines[index] ?? "")) {
      if (currentStart >= 0) {
        entries.push(parseEntry(lines, currentStart, index - 1));
      }
      currentStart = index;
    }
  }

  if (currentStart >= 0) {
    entries.push(parseEntry(lines, currentStart, lines.length - 1));
  }

  return entries;
}

export function extractInlineTags(markdown: string): string[] {
  const tree = parseMarkdownTree(markdown);
  const found = new Map<string, string>();

  visit(tree, "text", (node: any, _index: number | undefined, parent: any) => {
    if (parent?.type === "link" || parent?.type === "definition") {
      return;
    }

    const value = String(node.value ?? "");

    for (const match of value.matchAll(/(^|[^/\w])(@[A-Za-z][\w-]*)/g)) {
      addNormalizedTag(found, match[2]);
    }

    for (const match of value.matchAll(/(^|[^/\w])(#[A-Za-z][A-Za-z0-9_-]*)/g)) {
      addNormalizedTag(found, match[2]);
    }
  });

  return [...found.values()];
}

export function deriveSummary(markdown: string): string {
  const summarySection = extractSectionMarkdown(markdown, "Summary");
  if (summarySection) {
    return markdownToPlainText(summarySection);
  }

  return firstParagraphText(markdown);
}

export function partitionMetadata(metadata: Record<string, unknown>): {
  entryId: string | null;
  date: string | null;
  timeStart: string | null;
  timeEnd: string | null;
  timeBasis: string | null;
  category: string | null;
  primaryTag: string | null;
  tags: string[];
  source: string | null;
  title: string | null;
  metadata: Record<string, unknown>;
} {
  const known = {
    entryId: typeof metadata.entry_id === "string" ? metadata.entry_id : null,
    date: typeof metadata.date === "string" ? metadata.date : null,
    timeStart: typeof metadata.time_start === "string" && metadata.time_start !== "unknown" ? metadata.time_start : null,
    timeEnd: typeof metadata.time_end === "string" && metadata.time_end !== "unknown" ? metadata.time_end : null,
    timeBasis: typeof metadata.time_basis === "string" && metadata.time_basis !== "unknown" ? metadata.time_basis : null,
    category: typeof metadata.category === "string" ? metadata.category : null,
    primaryTag: typeof metadata.primary_tag === "string" ? metadata.primary_tag : null,
    tags: Array.isArray(metadata.tags) ? metadata.tags.filter((value): value is string => typeof value === "string") : [],
    source: typeof metadata.source === "string" ? metadata.source : null,
    title: typeof metadata.title === "string" ? metadata.title : null,
  };

  const extra: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(metadata)) {
    if (!knownMetadataKeys.has(key)) {
      extra[key] = value;
    }
  }

  if (Array.isArray(metadata.source_locations)) {
    extra.source_locations = metadata.source_locations;
  }

  if (Array.isArray(metadata.reference_locations)) {
    extra.reference_locations = metadata.reference_locations;
  }

  if (typeof metadata.context_status === "string") {
    extra.context_status = metadata.context_status;
  }

  return {
    ...known,
    metadata: extra,
  };
}

export function addNormalizedTag(store: Map<string, string>, tag: string) {
  const normalized = tag.trim();
  if (!normalized) {
    return;
  }

  const key = normalized.toLowerCase();
  if (!store.has(key)) {
    store.set(key, normalized);
  }
}

function parseEntry(lines: string[], startIndex: number, endIndex: number): ParsedLogEntry {
  const headingLine = lines[startIndex] ?? "";
  const headingMatch = headingLine.match(headingPattern);

  if (!headingMatch) {
    throw new Error(`Malformed entry heading at line ${startIndex + 1}: ${headingLine}`);
  }

  const rawMetadata: Record<string, unknown> = {};
  let cursor = startIndex + 1;

  while (cursor <= endIndex && !(lines[cursor] ?? "").trim()) {
    cursor += 1;
  }

  while (cursor <= endIndex) {
    const line = lines[cursor] ?? "";
    const metadataMatch = line.match(metadataPattern);

    if (!metadataMatch) {
      break;
    }

    rawMetadata[metadataMatch[1]] = parseMetadataValue(metadataMatch[2], cursor + 1);
    cursor += 1;
  }

  while (cursor <= endIndex && !(lines[cursor] ?? "").startsWith("### ")) {
    if ((lines[cursor] ?? "").trim()) {
      break;
    }
    cursor += 1;
  }

  const markdown = lines
    .slice(cursor, endIndex + 1)
    .join("\n")
    .trim();

  return {
    lineNumber: startIndex + 1,
    headingDate: headingMatch[1],
    headingTime: headingMatch[2] ?? null,
    headingTag: headingMatch[3] ?? null,
    headingTitle: headingMatch[4] ?? "",
    rawMetadata,
    markdown,
  };
}

function parseMetadataValue(rawValue: string, lineNumber: number): unknown {
  const trimmed = rawValue.trim();

  if (trimmed.startsWith("[") || trimmed.startsWith("{") || trimmed.startsWith("\"")) {
    try {
      return JSON.parse(trimmed);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      throw new Error(`Malformed metadata value at line ${lineNumber}: ${message}`);
    }
  }

  return trimmed;
}
