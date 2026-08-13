import type { ExplainResponse } from "@/types";
import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { ConfidenceBadge } from "./ConfidenceBadge";

/**
 * Lead result panel: a plain-language summary of the user's situation and the
 * model's confidence, plus an honest note about anything uncertain.
 */
export function SummaryCard({ explain }: { explain: ExplainResponse }) {
  return (
    <Card className="overflow-hidden">
      <div className="h-1 w-full bg-gradient-to-r from-teal via-teal/70 to-gold" aria-hidden="true" />
      <CardContent className="space-y-4 pt-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="font-display text-h3 text-teal">Here's what this means</h2>
          <ConfidenceBadge confidence={explain.confidence} />
        </div>

        {explain.what_we_understood && (
          <p className="text-small leading-relaxed text-muted">{explain.what_we_understood}</p>
        )}

        <p className="text-body-lg leading-relaxed text-ink">{explain.summary}</p>

        {explain.what_is_uncertain && (
          <div className="rounded-lg border border-warning/30 bg-warning/[0.06] px-4 py-3">
            <p className="text-tiny font-semibold uppercase tracking-wide text-[#8a6416]">
              What's still uncertain
            </p>
            <p className="mt-1 text-small leading-relaxed text-ink/80">{explain.what_is_uncertain}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
