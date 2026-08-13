import { apiClient } from "./apiClient";
import type {
  CorpusAct,
  CorpusAuthority,
  CorpusJudgment,
  CorpusSearchResult,
  CorpusSection,
  CorpusStats,
  CorpusVerifyReport,
} from "@/types";

export const corpusService = {
  stats: (signal?: AbortSignal) => apiClient.get<CorpusStats>("/api/corpus/stats", undefined, signal),

  acts: (signal?: AbortSignal) => apiClient.get<CorpusAct[]>("/api/corpus/acts", undefined, signal),

  sections: (params: { act_id?: number; domain?: string; limit?: number } = {}, signal?: AbortSignal) =>
    apiClient.get<CorpusSection[]>("/api/corpus/sections", params, signal),

  search: (params: { q: string; domain?: string; limit?: number }, signal?: AbortSignal) =>
    apiClient.get<CorpusSearchResult>("/api/corpus/search", params, signal),

  authorities: (domain?: string, signal?: AbortSignal) =>
    apiClient.get<CorpusAuthority[]>("/api/corpus/authorities", { domain }, signal),

  judgments: (domain?: string, signal?: AbortSignal) =>
    apiClient.get<CorpusJudgment[]>("/api/corpus/judgments", { domain }, signal),

  verify: (signal?: AbortSignal) =>
    apiClient.get<CorpusVerifyReport>("/api/corpus/verify", undefined, signal),
};
