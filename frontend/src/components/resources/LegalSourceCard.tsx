import React from "react";

export type LegalSource = {
  id: number | string;
  actName: string;
  sectionNumber: string;
  title: string;
  summary: string;
  status: string;
  jurisdiction: string;
  authority?: string;
  effectiveDate?: string;
  lastVerifiedDate?: string;
  whyApplies?: string;
  whyRejected?: string;
  sourceUrl: string;
};

export function LegalSourceCard({
  source,
}: {
  source: LegalSource;
}) {
  const isHistorical = source.status.toUpperCase() === "HISTORICAL";
  const isStateSpecific = source.jurisdiction && source.jurisdiction !== "All" && source.jurisdiction !== "INDIA";

  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
          ✓ VERIFIED SOURCE
        </span>

        {isHistorical && (
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
            ◷ HISTORICAL LAW
          </span>
        )}

        {isStateSpecific && (
          <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
            ! STATE-SPECIFIC ({source.jurisdiction})
          </span>
        )}
      </div>

      <div>
        <h3 className="text-xl font-semibold text-slate-900">
          {source.actName}
        </h3>
        <p className="mt-1 font-medium text-slate-600">
          Section {source.sectionNumber} — {source.title}
        </p>
      </div>

      <p className="leading-7 text-slate-600 text-sm">
        {source.summary}
      </p>

      {source.whyApplies && (
        <div className="p-3 bg-teal-50 border border-teal-100 rounded-xl text-xs text-teal-900">
          <span className="font-semibold block mb-0.5">Why this law may apply:</span>
          {source.whyApplies}
        </div>
      )}

      {source.whyRejected && (
        <div className="p-3 bg-red-50 border border-red-100 rounded-xl text-xs text-red-900">
          <span className="font-semibold block mb-0.5">Candidate rejection reason:</span>
          {source.whyRejected}
        </div>
      )}

      <div className="flex flex-wrap items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100">
        <div>
          <span>Authority: {source.authority || "Official Government Authority"}</span>
          {source.effectiveDate && <span> · Effective: {source.effectiveDate}</span>}
        </div>

        <a
          href={source.sourceUrl}
          target="_blank"
          rel="noreferrer"
          className="inline-flex rounded-xl bg-teal-900 px-4 py-2 text-xs font-semibold text-white transition hover:bg-teal-800"
        >
          View Official Source ↗
        </a>
      </div>
    </article>
  );
}
