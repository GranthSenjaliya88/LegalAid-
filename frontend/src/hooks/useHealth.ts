import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "@/lib/queryClient";
import { healthService } from "@/services/health";

export function useHealth() {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: ({ signal }) => healthService.check(signal),
    refetchInterval: 60_000,
    staleTime: 30_000,
    retry: 1,
  });
}
