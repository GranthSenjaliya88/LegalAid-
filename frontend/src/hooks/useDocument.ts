import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/queryClient";
import { documentsService } from "@/services/documents";
import type { DocumentData, UpdateDocumentRequest } from "@/types";

export function useDocument(documentId?: string) {
  return useQuery({
    queryKey: queryKeys.document(documentId ?? "none"),
    queryFn: ({ signal }) => documentsService.get(documentId as string, signal),
    enabled: Boolean(documentId),
  });
}

export function useCreateDocument() {
  return useMutation({
    mutationFn: ({ caseId, docType }: { caseId: string; docType: string }) =>
      documentsService.create(caseId, docType),
  });
}

export function useUpdateDocument(documentId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: UpdateDocumentRequest) => documentsService.update(documentId, body),
    onSuccess: (data: DocumentData) => {
      qc.setQueryData(queryKeys.document(documentId), data);
    },
  });
}

/** Download the generated PDF for a document. Triggers a browser save. */
export async function downloadDocumentPdf(documentId: string, filename: string): Promise<void> {
  const blob = await documentsService.pdf(documentId);
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename.endsWith(".pdf") ? filename : `${filename}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
