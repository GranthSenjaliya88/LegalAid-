import { Link } from "react-router-dom";
import { FileText } from "lucide-react";
import { useLibraryStore } from "@/store/libraryStore";
import { useAppStore } from "@/store/appStore";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/ui/button";
import { DocumentCard } from "@/components/document/DocumentCard";

/** Drafts created in this browser. */
export function DocumentsPage() {
  const documents = useLibraryStore((s) => s.documents);
  const hi = useAppStore((s) => s.language) === "hi";

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow={hi ? "मेरे दस्तावेज" : "My Documents"}
        title={hi ? "आपके ड्राफ्ट" : "Your drafts"}
        description={
          hi
            ? "संपादन जारी रखने, पूर्वावलोकन करने या PDF डाउनलोड करने के लिए ड्राफ्ट खोलें।"
            : "Open a draft to keep editing, preview it, or download a PDF."
        }
      />

      {documents.length === 0 ? (
        <EmptyState
          icon={FileText}
          title={hi ? "अभी कोई दस्तावेज नहीं" : "No documents yet"}
          description={
            hi
              ? "मामले का विश्लेषण करने के बाद आप कानूनी नोटिस या शिकायत का ड्राफ्ट बना सकते हैं। वह यहाँ दिखाई देगा।"
              : "After you analyze a case, you can generate a legal notice or complaint draft. It will show up here."
          }
          action={
            <Button asChild variant="gold">
              <Link to="/">{hi ? "कानूनी प्रश्न पूछें" : "Start a legal question"}</Link>
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
