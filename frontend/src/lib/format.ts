/** Display formatting helpers (no legal content — presentation only). */

/** Format an amount as Indian Rupees. Returns null if not a usable number. */
export function formatINR(amount?: string | number | null): string | null {
  if (amount === null || amount === undefined || amount === "") return null;
  const raw = typeof amount === "number" ? amount : Number(String(amount).replace(/[^0-9.]/g, ""));
  if (!Number.isFinite(raw) || raw === 0) {
    return typeof amount === "string" && amount.trim() ? amount : null;
  }
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(raw);
}

/** Human friendly absolute date, e.g. "12 Aug 2026". */
export function formatDate(iso?: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

/** "Today" / "Yesterday" / absolute date. */
export function relativeDay(iso?: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  const now = new Date();
  const startOf = (x: Date) => new Date(x.getFullYear(), x.getMonth(), x.getDate()).getTime();
  const diffDays = Math.round((startOf(now) - startOf(d)) / 86_400_000);
  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays > 1 && diffDays < 7) return `${diffDays} days ago`;
  return formatDate(iso);
}

/** Turn "consumer_court" / "NOT_APPLICABLE" into "Consumer Court" / "Not Applicable". */
export function titleCase(value?: string | null): string {
  if (!value) return "";
  return value
    .replace(/[_-]+/g, " ")
    .toLowerCase()
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Compact percentage from a 0..1 confidence float (used only for internal labels, never fake claims). */
export function pct(value?: number | null): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return "—";
  return `${Math.round(value * 100)}%`;
}
