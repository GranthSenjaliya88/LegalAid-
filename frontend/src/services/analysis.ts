import { apiClient } from "./apiClient";
import type {
  ActionRoadmapResponse,
  AnalyzeResponse,
  ApplicabilityResponse,
  ClarifyRequest,
  ClarifyResponse,
  ClassifyResponse,
  CompareResponse,
  EvidenceResponse,
  ExplainResponse,
  RetrievalResponse,
  VerifyResponse,
} from "@/types";

const base = (caseId: string) => `/api/cases/${encodeURIComponent(caseId)}`;

export const analysisService = {
  analyze: (caseId: string, signal?: AbortSignal) =>
    apiClient.post<AnalyzeResponse>(`${base(caseId)}/analyze`, undefined, undefined, signal),

  classify: (caseId: string, signal?: AbortSignal) =>
    apiClient.post<ClassifyResponse>(`${base(caseId)}/classify`, undefined, undefined, signal),

  retrieve: (caseId: string, signal?: AbortSignal) =>
    apiClient.post<RetrievalResponse>(`${base(caseId)}/retrieve`, undefined, undefined, signal),

  clarify: (caseId: string, signal?: AbortSignal) =>
    apiClient.post<ClarifyResponse>(`${base(caseId)}/clarify`, undefined, undefined, signal),

  clarifyRespond: (caseId: string, body: ClarifyRequest, signal?: AbortSignal) =>
    apiClient.post<RetrievalResponse>(`${base(caseId)}/clarify/respond`, body, undefined, signal),

  explain: (caseId: string, signal?: AbortSignal) =>
    apiClient.post<ExplainResponse>(`${base(caseId)}/explain`, undefined, undefined, signal),

  evidence: (caseId: string, signal?: AbortSignal) =>
    apiClient.get<EvidenceResponse>(`${base(caseId)}/evidence`, undefined, signal),

  roadmap: (caseId: string, signal?: AbortSignal) =>
    apiClient.get<ActionRoadmapResponse>(`${base(caseId)}/roadmap`, undefined, signal),

  verify: (caseId: string, signal?: AbortSignal) =>
    apiClient.post<VerifyResponse>(`${base(caseId)}/verify`, undefined, undefined, signal),

  applicability: (caseId: string, signal?: AbortSignal) =>
    apiClient.post<ApplicabilityResponse>(`${base(caseId)}/applicability`, undefined, undefined, signal),

  compare: (caseId: string, signal?: AbortSignal) =>
    apiClient.post<CompareResponse>(`${base(caseId)}/compare`, undefined, undefined, signal),
};
