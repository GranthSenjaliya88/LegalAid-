import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      gcTime: 5 * 60_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export const queryKeys = {
  health: ["health"] as const,
  corpusStats: ["corpus", "stats"] as const,
  acts: ["corpus", "acts"] as const,
  sections: (params: unknown) => ["corpus", "sections", params] as const,
  search: (params: unknown) => ["corpus", "search", params] as const,
  authorities: (domain?: string) => ["corpus", "authorities", domain ?? "all"] as const,
  judgments: (domain?: string) => ["corpus", "judgments", domain ?? "all"] as const,
  corpusVerify: ["corpus", "verify"] as const,
  case: (id: string) => ["case", id] as const,
  document: (id: string) => ["document", id] as const,
};
