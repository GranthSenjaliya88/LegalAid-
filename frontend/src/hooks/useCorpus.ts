import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { queryKeys } from "@/lib/queryClient";
import { corpusService } from "@/services/corpus";

export function useCorpusStats() {
  return useQuery({
    queryKey: queryKeys.corpusStats,
    queryFn: ({ signal }) => corpusService.stats(signal),
  });
}

export function useActs() {
  return useQuery({
    queryKey: queryKeys.acts,
    queryFn: ({ signal }) => corpusService.acts(signal),
  });
}

export interface CorpusSearchParams {
  q: string;
  domain?: string;
  limit?: number;
}

export function useCorpusSearch(params: CorpusSearchParams, enabled: boolean) {
  return useQuery({
    queryKey: queryKeys.search(params),
    queryFn: ({ signal }) => corpusService.search(params, signal),
    enabled: enabled && params.q.trim().length > 0,
    placeholderData: keepPreviousData,
  });
}

export function useAuthorities(domain?: string) {
  return useQuery({
    queryKey: queryKeys.authorities(domain),
    queryFn: ({ signal }) => corpusService.authorities(domain, signal),
  });
}
