import { Link } from "react-router-dom";
import { ArrowUpRight, FileText } from "lucide-react";
import type { DocSummary } from "@/store/libraryStore";
import { titleCase, relativeDay } from "@/lib/format";
import { Badge } from "@/components/ui/badge";

/**
 * Compact document row shown in the "My Documents" library (Part 18).
 * Content lives on the backend; this card only references it by id.
 */
export function DocumentCard({ doc }: { doc: DocSummary }) {
  return (
    <Link
      to={`/documents/${doc.documentId}`}
      className="group flex items-start gap-4 rounded-xl border border-hairline bg-surface p-4 transition-colors hover:border-teal/40 hover:bg-teal/[0.03] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal focus-visible:ring-offset-2 focus-visible:ring-offset-ivory"
    >
      <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-teal/[0.07] text-teal">
        <FileText className="size-5" />
      </span>
      <span className="min-w-0 flex-1">
        <span className="flex items-center gap-2">
          <span className="truncate text-body font-medium text-ink">{doc.title}</span>
          <ArrowUpRight className="size-4 shrink-0 text-muted transition-colors group-hover:text-teal" />
        </span>
        <span className="mt-1 flex flex-wrap items-center gap-2 text-tiny text-muted">
          <Badge variant="neutral">{titleCase(doc.type)}</Badge>
          <span>Created {relativeDay(doc.createdAt)}</span>
          {typeof doc.qualityScore === "number" && (
            <span aria-label={`Quality score ${doc.qualityScore} out of 100`}>
              · Quality {doc.qualityScore}/100
            </span>
          )}
        </span>
      </span>
    </Link>
  );
}
