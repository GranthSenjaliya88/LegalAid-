import type { Domain } from "@/types";
import { DOMAINS } from "@/lib/constants";
import { cn } from "@/lib/utils";

interface ResourceFiltersProps {
  value?: Domain;
  onChange: (domain?: Domain) => void;
  className?: string;
}

const ORDER: Domain[] = ["consumer", "labor", "tenant", "cyber", "criminal", "general"];

/**
 * Domain filter chips for Legal Resources (Part 11). "All" clears the filter.
 */
export function ResourceFilters({ value, onChange, className }: ResourceFiltersProps) {
  const chip = (active: boolean) =>
    cn(
      "rounded-full border px-3.5 py-1.5 text-small font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal focus-visible:ring-offset-2 focus-visible:ring-offset-ivory",
      active
        ? "border-teal bg-teal text-ivory-soft"
        : "border-hairline bg-surface text-muted hover:border-teal/40 hover:text-ink",
    );

  return (
    <div className={cn("flex flex-wrap gap-2", className)} role="group" aria-label="Filter by category">
      <button type="button" className={chip(!value)} onClick={() => onChange(undefined)} aria-pressed={!value}>
        All
      </button>
      {ORDER.map((d) => (
        <button
          key={d}
          type="button"
          className={chip(value === d)}
          onClick={() => onChange(d)}
          aria-pressed={value === d}
        >
          {DOMAINS[d].label}
        </button>
      ))}
    </div>
  );
}
