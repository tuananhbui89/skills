export interface LogEntry {
  id: string;
  entryId: string;
  date: string;
  timeStart: string | null;
  timeEnd: string | null;
  timeBasis: string | null;
  title: string;
  primaryTag: string | null;
  tags: string[];
  category: string | null;
  source: string | null;
  metadata: Record<string, unknown>;
  markdown: string;
  summary: string;
  sortTimestamp: string;
}

export interface DayRecord {
  date: string;
  entryIds: string[];
  activityScore: number;
  activityLevel: 0 | 1 | 2 | 3 | 4;
  tags: string[];
}

export interface TagRecord {
  tag: string;
  entryIds: string[];
  entryCount: number;
  latestDate: string | null;
}

export interface DatasetRange {
  startDate: string;
  endDate: string;
}

export interface SiteData {
  appId?: "personal-learning-log";
  weeks?: Record<string, WeeklyReview>;
  entries: Record<string, LogEntry>;
  dayIndex: Record<string, DayRecord>;
  tagIndex: Record<string, TagRecord>;
  heatmapDays: DayRecord[];
  datasetRange: DatasetRange;
  generatedAt: string;
}

export interface EvidenceReference { thread_id: string; title: string; at: string; line?: number; url: string }
export interface TaskSnapshot {
  id: string; title: string; project: string; status: "completed" | "in_progress";
  summary: string; blocker?: string; evidence: EvidenceReference[]; lesson_ids: string[];
}
export interface WeeklyReview {
  schema_version: 1; week_start: string; week_end: string; timezone: "Australia/Melbourne"; generated_at: string;
  coverage: { thread_count: number; archived_count: number; limitations: string[] };
  tasks: TaskSnapshot[]; lesson_ids: string[]; lesson_evidence?: Record<string, EvidenceReference[]>;
}

export interface ParsedLogEntry {
  lineNumber: number;
  headingDate: string;
  headingTime: string | null;
  headingTag: string | null;
  headingTitle: string;
  rawMetadata: Record<string, unknown>;
  markdown: string;
}
