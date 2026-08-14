import { AlertTriangle, ShieldCheck } from "lucide-react";
import type { DocumentData } from "@/types";
import { formatDate } from "@/lib/format";
import { useAppStore } from "@/store/appStore";

/**
 * Read-only, print-like preview of a generated document (Part 17).
 * Renders the structured sections as a calm, letter-style page.
 */
export function DocumentPreview({ document }: { document: DocumentData }) {
  const language = useAppStore((s) => s.language);
  const hi = language === "hi";
  return (
    <div className="space-y-4">
      {document.quality_warnings && document.quality_warnings.length > 0 && (
        <div className="rounded-lg border border-warning/35 bg-warning/[0.07] px-4 py-3">
          <p className="flex items-center gap-2 text-small font-medium text-[#7a5a12]">
            <AlertTriangle className="size-4" />
            {hi ? "भेजने से पहले कृपया समीक्षा करें" : "Please review before sending"}
          </p>
          <ul className="mt-2 space-y-1 pl-6 text-small leading-relaxed text-[#7a5a12]">
            {document.quality_warnings.map((w, i) => (
              <li key={i} className="list-disc">
                {w}
              </li>
            ))}
          </ul>
        </div>
      )}

      <article className="rounded-xl border border-hairline bg-surface px-6 py-8 sm:px-10 sm:py-10">
        <header className="mb-6 border-b border-hairline pb-5">
          <h1 className="font-display text-h2 leading-tight text-ink">{document.title}</h1>
          <p className="mt-2 text-tiny uppercase tracking-wide text-muted">
            {hi ? "ड्राफ्ट बनाया गया" : "Drafted"} {formatDate(document.created_at, language)}
          </p>
        </header>

        <div className="space-y-6">
          {document.sections.map((section) => (
            <section key={section.id}>
              {section.title && (
                <h2 className="mb-1.5 text-small font-semibold uppercase tracking-wide text-teal">
                  {section.title}
                </h2>
              )}
              <p className="whitespace-pre-wrap text-body leading-relaxed text-ink">
                {section.content}
              </p>
            </section>
          ))}
        </div>

        {document.disclaimer && (
          <footer className="mt-8 flex items-start gap-2 border-t border-hairline pt-5 text-tiny leading-relaxed text-muted">
            <ShieldCheck className="mt-0.5 size-3.5 shrink-0 text-success" />
            <span>{document.disclaimer}</span>
          </footer>
        )}
      </article>
    </div>
  );
}
