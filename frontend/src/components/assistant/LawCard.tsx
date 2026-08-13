import { ExternalLink } from "lucide-react";
import type { WhyThisLaw } from "@/types";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { LawStatusBadge } from "./LawStatusBadge";
import { VerifiedSeal } from "@/components/common/VerifiedSeal";

/**
 * A single statutory provision as returned by the backend corpus. All fields —
 * act, section, status, and the official source URL — come from verified data;
 * nothing is hardcoded or inferred client-side (Part 37).
 */
export function LawCard({ law, className }: { law: WhyThisLaw; className?: string }) {
  const heading = law.title?.trim() || [law.act, law.section].filter(Boolean).join(" · ");
  const subline = [law.act, law.section ? `Section ${law.section}` : null].filter(Boolean).join(" · ");

  return (
    <article
      className={cn(
        "rounded-lg border border-hairline bg-surface p-4 transition-colors hover:border-teal/25",
        className,
      )}
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="min-w-0 space-y-0.5">
          <h4 className="text-body font-semibold leading-snug text-ink">{heading}</h4>
          {subline && heading !== subline && <p className="text-tiny text-muted">{subline}</p>}
        </div>
        <div className="flex shrink-0 flex-wrap items-center gap-1.5">
          {law.status && <LawStatusBadge status={law.status} />}
          {law.source_badge && <VerifiedSeal label={law.source_badge} size="sm" />}
        </div>
      </div>

      {law.why_applies && (
        <p className="mt-3 text-small leading-relaxed text-muted">{law.why_applies}</p>
      )}

      {law.matching_factors && law.matching_factors.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {law.matching_factors.map((factor, i) => (
            <Badge key={i} variant="teal">
              {factor}
            </Badge>
          ))}
        </div>
      )}

      {(law.official_source_url || law.source_authority) && (
        <div className="mt-3 flex items-center gap-2 border-t border-hairline pt-3 text-tiny">
          {law.official_source_url ? (
            <a
              href={law.official_source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 font-medium text-teal underline-offset-2 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal focus-visible:ring-offset-1 focus-visible:ring-offset-surface rounded-sm"
            >
              {law.source_authority || "Official source"}
              <ExternalLink className="size-3" />
            </a>
          ) : (
            <span className="text-muted">Source: {law.source_authority}</span>
          )}
        </div>
      )}
    </article>
  );
}
