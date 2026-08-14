import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { LegalSourceCard, LegalSource } from "./LegalSourceCard";
import { apiClient } from "@/services/apiClient";

async function searchLegal(q: string) {
  return apiClient.get<Record<string, any>>("/api/legal/search", { q });
}

export function ResourceSearch() {
  const [query, setQuery] = useState("");

  const { data, isLoading, error } = useQuery({
    queryKey: ["legal-search", query],
    queryFn: () => searchLegal(query),
    enabled: query.trim().length >= 2,
  });

  const resultsList = data?.results || data?.data?.results || [];

  return (
    <section>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search laws, sections, or legal topics..."
        className="w-full rounded-2xl border border-slate-300 px-5 py-4 outline-none focus:ring-2 focus:ring-amber-400"
      />

      {isLoading && (
        <p className="mt-4 text-slate-500">
          Finding verified legal sources...
        </p>
      )}

      {error && (
        <p className="mt-4 text-red-600">
          We couldn't load legal sources. Please try again.
        </p>
      )}

      {!isLoading && !error && query.trim().length >= 2 && resultsList.length === 0 && (
        <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-8 text-center">
          <h3 className="font-semibold text-slate-900">
            No verified sources found
          </h3>

          <p className="mt-2 text-slate-500">
            Try simpler terms such as "unpaid wages",
            "security deposit", or "defective product".
          </p>
        </div>
      )}

      <div className="mt-6 grid gap-5">
        {resultsList.map((item: any, idx: number) => {
          const source: LegalSource = {
            id: item.id || item.section_id || idx,
            actName: item.act || item.act_name || "Statute Act",
            sectionNumber: item.section || item.section_number || "Provision",
            title: item.title || "Legal Provision",
            summary: item.plain_language_summary || item.relevant_text || item.text || "",
            status: item.status || "CURRENT",
            jurisdiction: item.state || item.jurisdiction || "INDIA",
            sourceUrl: item.official_source_url || item.source_url || "https://www.indiacode.nic.in",
          };

          return (
            <LegalSourceCard
              key={source.id}
              source={source}
            />
          );
        })}
      </div>
    </section>
  );
}
