import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Domain } from "@/types";

/**
 * The backend has no per-user "list my cases/documents" endpoint (there is no
 * auth layer). We therefore keep a lightweight local index of what this browser
 * has created, and always re-fetch the authoritative record by id from the API
 * when a case or document is opened. No legal content is stored here.
 */

export interface CaseSummary {
  caseId: string;
  title: string;
  domain?: Domain | null;
  status: string;
  createdAt: string;
  stepsCompleted: number;
}

export interface DocSummary {
  documentId: string;
  caseId: string;
  type: string;
  title: string;
  createdAt: string;
  qualityScore?: number;
}

interface LibraryState {
  cases: CaseSummary[];
  documents: DocSummary[];
  upsertCase: (c: CaseSummary) => void;
  removeCase: (caseId: string) => void;
  upsertDocument: (d: DocSummary) => void;
  removeDocument: (documentId: string) => void;
}

export const useLibraryStore = create<LibraryState>()(
  persist(
    (set) => ({
      cases: [],
      documents: [],
      upsertCase: (c) =>
        set((state) => {
          const rest = state.cases.filter((x) => x.caseId !== c.caseId);
          return { cases: [c, ...rest] };
        }),
      removeCase: (caseId) =>
        set((state) => ({
          cases: state.cases.filter((x) => x.caseId !== caseId),
          documents: state.documents.filter((d) => d.caseId !== caseId),
        })),
      upsertDocument: (d) =>
        set((state) => {
          const rest = state.documents.filter((x) => x.documentId !== d.documentId);
          return { documents: [d, ...rest] };
        }),
      removeDocument: (documentId) =>
        set((state) => ({
          documents: state.documents.filter((x) => x.documentId !== documentId),
        })),
    }),
    { name: "legalaid-library" },
  ),
);
