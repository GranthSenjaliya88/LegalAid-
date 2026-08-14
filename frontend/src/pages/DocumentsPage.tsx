import { Link } from "react-router-dom";
import { FileText } from "lucide-react";
import { useLibraryStore } from "@/store/libraryStore";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/ui/button";
import { DocumentCard } from "@/components/document/DocumentCard";

/**
 * My Documents (Part 20). Lists drafts created in this browser. The document
 * body itself is always re-fetched from the backend when opened.
 */
export function DocumentsPage() {
  const documents = useLibraryStore((s) => s.documents);

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="My Documents"
        title="Your drafts"
        description="Open a draft to keep editing, preview it, or download a PDF."
      />

      {documents.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No documents yet"
          description="After you analyze a case, you can generate a legal notice or complaint draft. It will show up here."
          action={
            <Button asChild variant="gold">
              <Link to="/">Start a legal question</Link>
            </Button>
          }
        />
      ) : (
        <ul className="grid gap-3 sm:grid-cols-2">
          {documents.map((doc) => (
            <li key={doc.documentId}>
              <DocumentCard doc={doc} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
