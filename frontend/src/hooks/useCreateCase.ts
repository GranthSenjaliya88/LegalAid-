import { useMutation } from "@tanstack/react-query";
import { casesService } from "@/services/cases";
import { useLibraryStore } from "@/store/libraryStore";
import type { CreateCaseRequest } from "@/types";

/**
 * Creates a case and records it in the local library (the backend has no
 * list-cases endpoint, so we track ids client-side and refetch by id).
 */
export function useCreateCase() {
  const upsertCase = useLibraryStore((s) => s.upsertCase);

  return useMutation({
    mutationFn: (body: CreateCaseRequest) => casesService.create(body),
    onSuccess: (res, variables) => {
      upsertCase({
        caseId: res.case_id,
        title: variables.text.trim().slice(0, 90) || "Untitled case",
        status: res.status ?? "new",
        createdAt: res.created_at ?? new Date().toISOString(),
        stepsCompleted: 0,
      });
    },
  });
}
