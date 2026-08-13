import { ExternalLink, Landmark, Phone } from "lucide-react";
import type { CorpusAuthority } from "@/types";
import { titleCase } from "@/lib/format";
import { Badge } from "@/components/ui/badge";

/**
 * Directory entry for an official authority / helpline (Part 12). Rows come
 * straight from the corpus DB and may be sparse, so every field is optional and
 * rendered defensively. Only official, public contact details are shown.
 */
export function AuthorityCard({ authority }: { authority: CorpusAuthority }) {
  const name = authority.name || "Authority";
  const website = authority.official_url || authority.website || null;
  const helpline = authority.helpline || null;

  return (
    <article className="flex h-full flex-col rounded-xl border border-hairline bg-surface p-5">
      <div className="flex items-start gap-3">
        <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-teal/[0.07] text-teal">
          <Landmark className="size-[1.1rem]" />
        </span>
        <div className="min-w-0">
          <h3 className="text-body font-semibold leading-snug text-ink">{name}</h3>
          {authority.jurisdiction && (
            <p className="mt-0.5 text-tiny text-muted">{authority.jurisdiction}</p>
          )}
        </div>
      </div>

      {authority.description && (
        <p className="mt-3 text-small leading-relaxed text-muted">{authority.description}</p>
      )}

      <div className="mt-4 flex flex-wrap items-center gap-2 pt-1">
        {authority.domain && <Badge variant="neutral">{titleCase(String(authority.domain))}</Badge>}
      </div>

      <div className="mt-3 flex flex-col gap-1.5">
        {helpline && (
          <a
            href={`tel:${String(helpline).replace(/\s+/g, "")}`}
            className="inline-flex items-center gap-1.5 text-small font-medium text-teal underline-offset-4 hover:underline"
          >
            <Phone className="size-3.5" />
            {helpline}
          </a>
        )}
        {website && (
          <a
            href={website}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-small font-medium text-teal underline-offset-4 hover:underline"
          >
            <ExternalLink className="size-3.5" />
            Official website
          </a>
        )}
      </div>
    </article>
  );
}
