import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "@/lib/queryClient";
import { casesService } from "@/services/cases";

export function useCase(caseId?: string) {
  return useQuery({
    queryKey: queryKeys.case(caseId ?? "none"),
    queryFn: ({ signal }) => casesService.get(caseId as string, signal),
    enabled: Boolean(caseId),
  });
}
