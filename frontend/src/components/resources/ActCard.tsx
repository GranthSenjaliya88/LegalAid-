import { ExternalLink, Scale } from "lucide-react";
import type { CorpusAct } from "@/types";
import { titleCase } from "@/lib/format";
import { Badge } from "@/components/ui/badge";

/**
 * Browse-view card for a single Act in the corpus (Part 11).
 */
export function ActCard({ act }: { act: CorpusAct }) {
  return (
    <article className="flex h-full flex-col rounded-xl border border-hairline bg-surface p-5">
      <div className="flex items-start gap-3">
        <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-teal/[0.07] text-teal">
          <Scale className="size-[1.1rem]" />
        </span>
        <div className="min-w-0">
          <h3 className="text-body font-semibold leading-snug text-ink">{act.name}</h3>
          <p className="mt-0.5 text-tiny text-muted">
            {act.short_name}
            {act.year ? ` · ${act.year}` : ""}
          </p>
        </div>
      </div>

      {act.description && (
        <p className="mt-3 line-clamp-3 text-small leading-relaxed text-muted">{act.description}</p>
      )}

      <div className="mt-4 flex flex-wrap items-center gap-2 pt-1">
        {act.domain && <Badge variant="neutral">{titleCase(act.domain)}</Badge>}
        {act.jurisdiction && <Badge variant="outline">{act.jurisdiction}</Badge>}
        {typeof act.section_count === "number" && act.section_count > 0 && (
          <span className="text-tiny text-muted">{act.section_count} sections</span>
        )}
      </div>

      {act.source_url && (
        <a
          href={act.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-3 inline-flex items-center gap-1 text-tiny font-medium text-teal underline-offset-4 hover:underline"
        >
          Official source
          <ExternalLink className="size-3" />
        </a>
      )}
    </article>
  );
}
