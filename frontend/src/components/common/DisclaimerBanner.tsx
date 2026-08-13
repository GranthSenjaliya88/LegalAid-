import { Scale } from "lucide-react";
import { GLOBAL_DISCLAIMER } from "@/lib/constants";
import { cn } from "@/lib/utils";

/**
 * Global "information, not advice" disclaimer (Part 26/37). Rendered in the
 * app footer and at the end of result flows. Calm, never a scary red banner.
 */
export function DisclaimerBanner({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "flex items-start gap-3 rounded-lg border border-hairline bg-teal/[0.03] px-4 py-3 text-small text-muted",
        className,
      )}
      role="note"
    >
      <Scale className="mt-0.5 size-4 shrink-0 text-teal/70" strokeWidth={1.7} />
      <p className="leading-relaxed">{GLOBAL_DISCLAIMER}</p>
    </div>
  );
}
