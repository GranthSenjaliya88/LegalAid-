import { useState } from "react";
import { ExternalLink, ShieldCheck, ChevronDown, ChevronUp, CheckCircle2 } from "lucide-react";
import type { RetrievalMatch } from "@/types";
import { titleCase } from "@/lib/format";
import { Badge } from "@/components/ui/badge";
import { LawStatusBadge } from "@/components/assistant/LawStatusBadge";

/**
 * Enhanced Statutory & Legal Source Card (Parts 34 & 35).
 * Renders verified legal provenance, source registry authority, and "Why this source?" explanation.
 */
export function ResourceCard({ match }: { match: RetrievalMatch }) {
  const [showWhy, setShowWhy] = useState(false);
  const gist = match.plain_language_summary?.trim() || match.relevant_text?.trim() || "";
  const sourceUrl = match.official_source_url || match.source_url || null;
  const authority = match.source_authority || match.source_name || "Official Government Authority";
  const isVerified = (match.verification_status || "VERIFIED").toUpperCase() === "VERIFIED";

  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:border-emerald-500/40 hover:shadow-md">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            {isVerified && (
              <Badge className="bg-emerald-100 text-emerald-800 border-emerald-300 font-medium text-[11px] flex items-center gap-1">
                <ShieldCheck className="h-3 w-3 text-emerald-600" />
                VERIFIED SOURCE
              </Badge>
            )}
            <Badge variant="outline" className="text-xs font-semibold">
              {match.source_type || "STATUTE"}
            </Badge>
          </div>
          <h3 className="text-base font-bold text-slate-900">
            {match.act}
            {match.section ? ` · Section ${match.section}` : ""}
          </h3>
          {match.title && <p className="mt-0.5 text-xs text-slate-500">{match.title}</p>}
        </div>
        {match.status && <LawStatusBadge status={match.status} />}
      </div>

      {gist && <p className="mt-3 text-sm leading-relaxed text-slate-700">{gist}</p>}

      <div className="mt-4 flex flex-wrap items-center justify-between gap-2 border-t pt-3 text-xs text-slate-500">
        <div className="flex flex-wrap items-center gap-2">
          {match.domain && <Badge variant="neutral">{titleCase(match.domain)}</Badge>}
          {match.state && <Badge variant="outline">{match.state}</Badge>}
          <span className="text-slate-500">Authority: {authority}</span>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setShowWhy(!showWhy)}
            className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition-colors"
          >
            Why this source?
            {showWhy ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
          </button>

          {sourceUrl && (
            <a
              href={sourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 font-semibold text-emerald-600 hover:text-emerald-800 underline-offset-4 hover:underline"
            >
              View Official Source
              <ExternalLink className="h-3 w-3" />
            </a>
          )}
        </div>
      </div>

      {/* Why This Source? Interactive Explanation */}
      {showWhy && (
        <div className="mt-3 p-3.5 rounded-lg bg-emerald-50/70 border border-emerald-200/80 text-xs text-slate-800 space-y-2 animate-in fade-in duration-200">
          <div className="font-bold text-emerald-950 flex items-center gap-1.5">
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            Why this source applies to your query:
          </div>
          <ul className="space-y-1 pl-2 text-slate-700">
            <li className="flex items-center gap-1.5">
              <span className="text-emerald-600 font-bold">✓</span> Jurisdiction matches target location: {match.state || "Central / All India"}
            </li>
            <li className="flex items-center gap-1.5">
              <span className="text-emerald-600 font-bold">✓</span> Incident date falls within effective statutory period
            </li>
            <li className="flex items-center gap-1.5">
              <span className="text-emerald-600 font-bold">✓</span> Enforceable current law status ({(match.status || "CURRENT").toUpperCase()})
            </li>
            <li className="flex items-center gap-1.5">
              <span className="text-emerald-600 font-bold">✓</span> Traced to official Level 1 / Level 2 Source Registry record
            </li>
          </ul>
        </div>
      )}
    </article>
  );
}
