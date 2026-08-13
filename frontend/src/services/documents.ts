import { apiClient } from "./apiClient";
import type { DocumentData, UpdateDocumentRequest } from "@/types";

export const documentsService = {
  create: (caseId: string, docType: string, signal?: AbortSignal) =>
    apiClient.post<DocumentData>(
      `/api/cases/${encodeURIComponent(caseId)}/document`,
      undefined,
      { doc_type: docType },
      signal,
    ),

  get: (documentId: string, signal?: AbortSignal) =>
    apiClient.get<DocumentData>(`/api/documents/${encodeURIComponent(documentId)}`, undefined, signal),

  update: (documentId: string, body: UpdateDocumentRequest, signal?: AbortSignal) =>
    apiClient.put<DocumentData>(`/api/documents/${encodeURIComponent(documentId)}`, body, signal),

  /** Fetch the generated PDF as a Blob for download / preview. */
  pdf: (documentId: string, signal?: AbortSignal) =>
    apiClient.blob(`/api/documents/${encodeURIComponent(documentId)}/pdf`, undefined, signal),
};
