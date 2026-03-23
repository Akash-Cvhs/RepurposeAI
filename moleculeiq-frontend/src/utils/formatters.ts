export function formatDate(value?: string): string {
  if (!value) {
    return "-";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  }).format(date);
}

export function formatPercent(value?: number): string {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return "-";
  }

  return `${Math.round(value * 100)}%`;
}

export function toTitleCase(value: string): string {
  return value
    .split(/[\s_]+/)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}
