import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { toast } from "sonner";
import { ArrowLeft, CheckCircle2, Download, AlertTriangle } from "lucide-react";
import { useDocument, useUpdateDocument, downloadDocumentPdf } from "@/hooks/useDocument";
import type { UpdateDocumentRequest } from "@/types";
import { PanelSkeleton } from "@/components/common/LoadingState";
import { ErrorState } from "@/components/common/ErrorState";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DocumentEditor } from "@/components/document/DocumentEditor";
import { DocumentPreview } from "@/components/document/DocumentPreview";

/**
 * Document editor & preview (Part 17). Users edit the draft, preview it as a
 * finished page, see a quality indicator, and download a PDF.
 */
export function DocumentEditorPage() {
  const { id } = useParams<{ id: string }>();
  const docQuery = useDocument(id);
  const update = useUpdateDocument(id ?? "none");
  const [downloading, setDownloading] = useState(false);

  const doc = docQuery.data;

  const handleSave = (body: UpdateDocumentRequest) => {
    update.mutate(body, {
      onSuccess: () => toast.success("Changes saved"),
      onError: () => toast.error("Couldn't save your changes. Please try again."),
    });
  };

  const handleDownload = async () => {
    if (!doc) return;
    setDownloading(true);
    try {
      await downloadDocumentPdf(doc.document_id, doc.title);
    } catch {
      toast.error("Couldn't download the PDF. Please try again.");
    } finally {
      setDownloading(false);
    }
  };

  const warnings = doc?.quality_warnings?.length ?? 0;

  return (
    <div className="space-y-6">
      <Link
        to="/documents"
        className="inline-flex items-center gap-1.5 text-small font-medium text-muted transition-colors hover:text-teal"
      >
        <ArrowLeft className="size-4" />
        My Documents
      </Link>

      {docQuery.isLoading && <PanelSkeleton />}

      {docQuery.isError && (
        <ErrorState
          title="We couldn't open this document"
          description="It may have been deleted, or the connection dropped."
          onRetry={() => docQuery.refetch()}
        />
      )}

      {doc && (
        <>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div className="min-w-0">
              <h1 className="font-display text-h2 leading-tight text-ink">{doc.title}</h1>
              <div className="mt-2 flex flex-wrap items-center gap-2">
                {warnings === 0 ? (
                  <Badge variant="success">
                    <CheckCircle2 className="size-3" />
                    Ready to review
                  </Badge>
                ) : (
                  <Badge variant="warning">
                    <AlertTriangle className="size-3" />
                    {warnings} item{warnings > 1 ? "s" : ""} to review
                  </Badge>
                )}
                {typeof doc.quality_score === "number" && (
                  <span className="text-tiny text-muted">Quality score {doc.quality_score}/100</span>
                )}
              </div>
            </div>
            <Button variant="outline" onClick={handleDownload} disabled={downloading} className="shrink-0">
              <Download className="size-4" />
              {downloading ? "Preparing…" : "Download PDF"}
            </Button>
          </div>

          <Tabs defaultValue="edit" className="space-y-5">
            <TabsList>
              <TabsTrigger value="edit">Edit</TabsTrigger>
              <TabsTrigger value="preview">Preview</TabsTrigger>
            </TabsList>
            <TabsContent value="edit">
              <DocumentEditor document={doc} onSave={handleSave} saving={update.isPending} />
            </TabsContent>
            <TabsContent value="preview">
              <DocumentPreview document={doc} />
            </TabsContent>
          </Tabs>
        </>
      )}
    </div>
  );
}
