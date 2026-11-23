const ONE_DAY_IN_MS = 24 * 60 * 60 * 1000;

export function parseIsoDate(dateIso: string): Date {
  return new Date(`${dateIso}T00:00:00Z`);
}

export function formatIsoDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

export function addDays(dateIso: string, amount: number): string {
  const date = parseIsoDate(dateIso);
  date.setUTCDate(date.getUTCDate() + amount);
  return formatIsoDate(date);
}

export function startOfMonth(dateIso: string): string {
  const date = parseIsoDate(dateIso);
  date.setUTCDate(1);
  return formatIsoDate(date);
}

export function addMonths(dateIso: string, amount: number): string {
  const date = parseIsoDate(dateIso);
  date.setUTCDate(1);
  date.setUTCMonth(date.getUTCMonth() + amount);
  return formatIsoDate(date);
}

export function dayOfWeek(dateIso: string): number {
  return parseIsoDate(dateIso).getUTCDay();
}

export function startOfWeek(dateIso: string): string {
  return addDays(dateIso, -dayOfWeek(dateIso));
}

export function compareIsoDates(left: string, right: string): number {
  if (left < right) return -1;
  if (left > right) return 1;
  return 0;
}

export function formatLongDate(dateIso: string): string {
  return new Intl.DateTimeFormat("en-AU", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  }).format(parseIsoDate(dateIso));
}

export function formatShortMonth(dateIso: string): string {
  return new Intl.DateTimeFormat("en-AU", {
    month: "short",
    timeZone: "UTC",
  }).format(parseIsoDate(dateIso));
}

export function formatHeatmapMonthLabel(dateIso: string, includeYear = false): string {
  return new Intl.DateTimeFormat("en-AU", {
    month: "short",
    ...(includeYear ? { year: "numeric" as const } : {}),
    timeZone: "UTC",
  }).format(parseIsoDate(dateIso));
}

export function buildSortTimestamp(dateIso: string, time: string | null, fallbackIndex: number): string {
  const normalizedTime = time && /^\d{2}:\d{2}$/.test(time) ? `${time}:00` : "00:00:00";
  return `${dateIso}T${normalizedTime}.${String(fallbackIndex).padStart(3, "0")}Z`;
}

export function formatTimeRange(start: string | null, end: string | null): string {
  if (start && end && start !== end) {
    return `${start} to ${end}`;
  }

  if (start) {
    return start;
  }

  if (end) {
    return end;
  }

  return "Time not specified";
}

export function daysBetween(startDate: string, endDate: string): number {
  const diff = parseIsoDate(endDate).getTime() - parseIsoDate(startDate).getTime();
  return Math.floor(diff / ONE_DAY_IN_MS);
}
