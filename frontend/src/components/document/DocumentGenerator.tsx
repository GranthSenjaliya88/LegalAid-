import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FileText, Loader2, PenLine } from "lucide-react";
import { toast } from "sonner";
import type { Domain } from "@/types";
import { DOCUMENT_TYPES } from "@/lib/constants";
import { useCreateDocument } from "@/hooks/useDocument";
import { useLibraryStore } from "@/store/libraryStore";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PrivacyNote } from "@/components/common/PrivacyNote";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface DocumentGeneratorProps {
  caseId: string;
  domain?: Domain | null;
}

/**
 * Document generation entry point (Part 17). Offers only the draft types that
 * fit the case's domain. The draft itself is produced by the backend from the
 * verified case record — nothing is fabricated here.
 */
export function DocumentGenerator({ caseId, domain }: DocumentGeneratorProps) {
  const navigate = useNavigate();
  const upsertDocument = useLibraryStore((s) => s.upsertDocument);
  const create = useCreateDocument();

  const options = DOCUMENT_TYPES.filter((d) => !domain || d.domains.includes(domain));
  const fallback = options[0]?.type ?? DOCUMENT_TYPES[0].type;
  const [docType, setDocType] = useState<string>(fallback);

  const selected = DOCUMENT_TYPES.find((d) => d.type === docType);

  const handleGenerate = () => {
    create.mutate(
      { caseId, docType },
      {
        onSuccess: (doc) => {
          upsertDocument({
            documentId: doc.document_id,
            caseId: doc.case_id,
            type: doc.type,
            title: doc.title,
            createdAt: doc.created_at ?? new Date().toISOString(),
            qualityScore: doc.quality_score,
          });
          toast.success("Draft ready to review");
          navigate(`/documents/${doc.document_id}`);
        },
        onError: () => toast.error("Couldn't generate the draft. Please try again."),
      },
    );
  };

  return (
    <Card>
      <CardHeader className="space-y-1.5">
        <CardTitle className="flex items-center gap-2">
          <PenLine className="size-5 text-teal" />
          Prepare a document
        </CardTitle>
        <CardDescription>
          Turn this case into a formal draft you can review, edit, and download. You always have the
          final say over the wording.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3 sm:grid-cols-[1fr_auto] sm:items-end">
          <div className="space-y-1.5">
            <label htmlFor="doc-type" className="text-small font-medium text-ink">
              Document type
            </label>
            <Select value={docType} onValueChange={setDocType}>
              <SelectTrigger id="doc-type" className="w-full">
                <SelectValue placeholder="Choose a document" />
              </SelectTrigger>
              <SelectContent>
                {options.map((d) => (
                  <SelectItem key={d.type} value={d.type}>
                    {d.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button
            onClick={handleGenerate}
            disabled={create.isPending}
            className="sm:w-auto bg-teal hover:bg-teal-dark text-white font-semibold shadow-soft hover:shadow-lift transition-all"
          >
            {create.isPending ? (
              <>
                <Loader2 className="size-4 animate-spin" />
                Drafting…
              </>
            ) : (
              <>
                <FileText className="size-4 text-gold" />
                Generate draft
              </>
            )}
          </Button>
        </div>

        {selected && <p className="text-small leading-relaxed text-muted">{selected.description}</p>}

        <PrivacyNote />
      </CardContent>
    </Card>
  );
}
