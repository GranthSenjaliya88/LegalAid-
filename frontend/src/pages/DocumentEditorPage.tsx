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
import { useAppStore } from "@/store/appStore";

/**
 * Document editor & preview (Part 17). Users edit the draft, preview it as a
 * finished page, see a quality indicator, and download a PDF.
 */
export function DocumentEditorPage() {
  const hi = useAppStore((s) => s.language) === "hi";
  const { id } = useParams<{ id: string }>();
  const docQuery = useDocument(id);
  const update = useUpdateDocument(id ?? "none");
  const [downloading, setDownloading] = useState(false);

  const doc = docQuery.data;

  const handleSave = (body: UpdateDocumentRequest) => {
    update.mutate(body, {
      onSuccess: () => toast.success(hi ? "बदलाव सहेज दिए गए" : "Changes saved"),
      onError: () => toast.error(hi ? "बदलाव सहेजे नहीं जा सके। कृपया फिर कोशिश करें।" : "Couldn't save your changes. Please try again."),
    });
  };

  const handleDownload = async () => {
    if (!doc) return;
    setDownloading(true);
    try {
      await downloadDocumentPdf(doc.document_id, doc.title);
    } catch {
      toast.error(hi ? "PDF डाउनलोड नहीं हो सका। कृपया फिर कोशिश करें।" : "Couldn't download the PDF. Please try again.");
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
        {hi ? "मेरे दस्तावेज" : "My Documents"}
      </Link>

      {docQuery.isLoading && <PanelSkeleton />}

      {docQuery.isError && (
        <ErrorState
          title={hi ? "यह दस्तावेज खुल नहीं सका" : "We couldn't open this document"}
          description={hi ? "यह हटाया जा चुका हो सकता है या कनेक्शन टूट गया है।" : "It may have been deleted, or the connection dropped."}
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
                    {hi ? "समीक्षा के लिए तैयार" : "Ready to review"}
                  </Badge>
                ) : (
                  <Badge variant="warning">
                    <AlertTriangle className="size-3" />
                    {hi ? `${warnings} बिंदु जाँचने हैं` : `${warnings} item${warnings > 1 ? "s" : ""} to review`}
                  </Badge>
                )}
                {typeof doc.quality_score === "number" && (
                  <span className="text-tiny text-muted">{hi ? "गुणवत्ता स्कोर" : "Quality score"} {doc.quality_score}/100</span>
                )}
              </div>
            </div>
            <Button variant="outline" onClick={handleDownload} disabled={downloading} className="shrink-0">
              <Download className="size-4" />
              {downloading ? (hi ? "तैयार हो रहा है…" : "Preparing…") : hi ? "PDF डाउनलोड करें" : "Download PDF"}
            </Button>
          </div>

          <Tabs defaultValue="edit" className="space-y-5">
            <TabsList>
              <TabsTrigger value="edit">{hi ? "संपादित करें" : "Edit"}</TabsTrigger>
              <TabsTrigger value="preview">{hi ? "पूर्वावलोकन" : "Preview"}</TabsTrigger>
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
