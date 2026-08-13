import { apiClient } from "./apiClient";
import type { CaseState, CreateCaseRequest, CreateCaseResponse } from "@/types";

export const casesService = {
  create: (body: CreateCaseRequest, signal?: AbortSignal) =>
    apiClient.post<CreateCaseResponse>("/api/cases", body, undefined, signal),

  get: (caseId: string, signal?: AbortSignal) =>
    apiClient.get<CaseState>(`/api/cases/${encodeURIComponent(caseId)}`, undefined, signal),

  remove: (caseId: string, signal?: AbortSignal) =>
    apiClient.del<{ message?: string }>(`/api/cases/${encodeURIComponent(caseId)}`, signal),
};
