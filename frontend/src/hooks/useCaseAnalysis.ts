import { useCallback, useEffect, useRef, useState } from "react";
import { analysisService } from "@/services/analysis";
import { casesService } from "@/services/cases";
import { ApiError } from "@/types";
import type {
  ActionRoadmapResponse,
  AnalyzeResponse,
  AnswerValue,
  CaseFacts,
  ClarifyResponse,
  ClassifyResponse,
  EvidenceResponse,
  ExplainResponse,
  VerifyResponse,
} from "@/types";

export type FlowStatus = "idle" | "running" | "awaiting_clarification" | "insufficient_information" | "done" | "error";
export type FlowPhase = "classify" | "clarify" | "explain" | "enrich" | null;
export type VerifyStatus = "idle" | "loading" | "done" | "error";

/** Maximum wall-clock time (ms) to wait for the full analysis pipeline before forcing an error state. */
const ANALYSIS_TIMEOUT_MS = 90_000;

export interface AnalysisState {
  status: FlowStatus;
  phase: FlowPhase;
  classify?: ClassifyResponse;
  clarify?: ClarifyResponse;
  explain?: ExplainResponse;
  evidence?: EvidenceResponse;
  roadmap?: ActionRoadmapResponse;
  facts?: CaseFacts;
  error?: { phase: string; message: string };
  verify?: VerifyResponse;
  verifyStatus: VerifyStatus;
}

const initialState: AnalysisState = {
  status: "idle",
  phase: null,
  verifyStatus: "idle",
};

function messageOf(err: unknown): string {
  if (err instanceof ApiError) return err.message;
  if (err instanceof Error) return err.message;
  return "Something went wrong. Please try again.";
}

function isAbort(err: unknown): boolean {
  return err instanceof DOMException && err.name === "AbortError";
}

/**
 * Orchestrates the source-grounded analysis pipeline for a single case.
 * Integrates unified backend orchestration with graceful step fallback and
 * robust React 18 async lifecycle management.
 */
export function useCaseAnalysis(caseId: string | undefined) {
  const [state, setState] = useState<AnalysisState>(initialState);
  const activeControllerRef = useRef<AbortController | null>(null);
  const activeCaseIdRef = useRef<string | undefined>(caseId);
  activeCaseIdRef.current = caseId;

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      activeControllerRef.current?.abort();
      activeControllerRef.current = null;
    };
  }, []);

  const patch = useCallback((partial: Partial<AnalysisState>) => {
    setState((prev) => ({ ...prev, ...partial }));
  }, []);

  const getSignal = useCallback(() => {
    if (activeControllerRef.current) {
      activeControllerRef.current.abort();
    }
    const ac = new AbortController();
    activeControllerRef.current = ac;
    return ac.signal;
  }, []);

  const analyzeOrchestration = useCallback(
    async (id: string, signal: AbortSignal) => {
      // Safety timeout: force error state if pipeline takes too long.
      // This guarantees the UI is never permanently stuck on "Working on your case...".
      let timeoutId: ReturnType<typeof setTimeout> | null = null;
      const timeoutPromise = new Promise<never>((_, reject) => {
        timeoutId = setTimeout(() => {
          if (!signal.aborted) {
            reject(new Error(`Analysis timed out after ${ANALYSIS_TIMEOUT_MS / 1000}s. Please retry.`));
          }
        }, ANALYSIS_TIMEOUT_MS);
      });

      const runPipeline = async () => {
        try {
          if (import.meta.env.DEV) {
            console.log(`[LegalAId Pipeline] Starting orchestration for case: ${id}`);
          }
          patch({ status: "running", phase: "classify", error: undefined });

          // Call unified backend orchestration
          let res: AnalyzeResponse;
          try {
            res = await analysisService.analyze(id, signal);
          } catch (backendErr) {
            if (isAbort(backendErr) || signal.aborted) return;
            // Fallback to step-by-step calls if analyze endpoint is unavailable
            if (import.meta.env.DEV) {
              console.warn("[LegalAId Pipeline] Backend analyze endpoint failed, falling back to sequential calls:", backendErr);
            }
            const classify = await analysisService.classify(id, signal);
            patch({ classify, facts: classify.facts, phase: "clarify" });

            let clarify: ClarifyResponse | undefined;
            try {
              clarify = await analysisService.clarify(id, signal);
            } catch {
              clarify = undefined;
            }
            if (clarify) patch({ clarify });

            if (clarify?.needs_clarification && clarify.questions.length > 0) {
              patch({ status: "awaiting_clarification", phase: null });
              return;
            }

            patch({ phase: "explain" });
            const explain = await analysisService.explain(id, signal);
            patch({ explain, phase: "enrich" });

            const [evidence, roadmap] = await Promise.all([
              analysisService.evidence(id, signal),
              analysisService.roadmap(id, signal),
            ]);
            patch({ evidence, roadmap, phase: null, status: "done" });
            return;
          }

          if (signal.aborted || activeCaseIdRef.current !== id) return;

          // Apply facts from backend
          if (res.facts) {
            patch({ facts: res.facts });
          }

          if (res.status === "needs_clarification" && res.clarification && res.clarification.questions?.length > 0) {
            if (import.meta.env.DEV) {
              console.log(`[LegalAId Pipeline] Clarification REQUIRED (${res.clarification.questions.length} questions)`);
            }
            patch({
              status: "awaiting_clarification",
              phase: null,
              clarify: res.clarification,
              facts: res.facts ?? undefined,
            });
            return;
          }

          if (res.status === "insufficient_information") {
            if (import.meta.env.DEV) {
              console.log("[LegalAId Pipeline] INSUFFICIENT_INFORMATION returned");
            }
            patch({
              status: "insufficient_information",
              phase: null,
              explain: res.explain ?? undefined,
              evidence: res.evidence ?? undefined,
              roadmap: res.roadmap ?? undefined,
              facts: res.facts ?? undefined,
            });
            return;
          }

          if (import.meta.env.DEV) {
            console.log("[LegalAId Pipeline] Case analysis completed: PASS");
            console.log(`[LegalAId Pipeline] Sources: ${res.explain?.relevant_law?.length ?? 0}, Rights: ${res.explain?.rights?.length ?? 0}`);
          }

          patch({
            status: "done",
            phase: null,
            explain: res.explain ?? undefined,
            evidence: res.evidence ?? undefined,
            roadmap: res.roadmap ?? undefined,
            facts: res.facts ?? undefined,
          });
        } catch (err) {
          if (isAbort(err) || signal.aborted) return;
          if (import.meta.env.DEV) {
            console.error("[LegalAId Pipeline ERROR]", err);
          }
          patch({
            status: "error",
            phase: null,
            error: { phase: "analyze", message: messageOf(err) },
          });
        }
      };

      try {
        await Promise.race([runPipeline(), timeoutPromise]);
      } catch (timeoutErr) {
        // Only fires if the timeout rejected first
        if (!signal.aborted) {
          if (import.meta.env.DEV) {
            console.error("[LegalAId Pipeline TIMEOUT]", timeoutErr);
          }
          patch({
            status: "error",
            phase: null,
            error: { phase: "analyze", message: messageOf(timeoutErr) },
          });
        }
      } finally {
        if (timeoutId !== null) clearTimeout(timeoutId);
      }
    },
    [patch],
  );

  const start = useCallback(async () => {
    if (!caseId) return;
    const signal = getSignal();
    await analyzeOrchestration(caseId, signal);
  }, [caseId, getSignal, analyzeOrchestration]);

  /** Submit clarification answers (also used to correct AI-extracted facts). */
  const applyAnswers = useCallback(
    async (answers: Record<string, AnswerValue>) => {
      if (!caseId) return;
      const signal = getSignal();
      try {
        patch({ status: "running", phase: "explain", error: undefined });
        await analysisService.clarifyRespond(caseId, { answers }, signal);
        try {
          const refreshed = await casesService.get(caseId, signal);
          if (refreshed.facts) {
            patch({ facts: refreshed.facts });
          }
        } catch {
          /* keep existing facts if refresh fails */
        }
        await analyzeOrchestration(caseId, signal);
      } catch (err) {
        if (isAbort(err) || signal.aborted) return;
        patch({
          status: "error",
          phase: null,
          error: { phase: "clarify", message: messageOf(err) },
        });
      }
    },
    [caseId, getSignal, patch, analyzeOrchestration],
  );

  const skipClarification = useCallback(async () => {
    if (!caseId) return;
    const signal = getSignal();
    patch({ status: "running", phase: "explain", error: undefined });
    try {
      const explain = await analysisService.explain(caseId, signal);
      patch({ explain, phase: "enrich" });
      const [evidence, roadmap] = await Promise.all([
        analysisService.evidence(caseId, signal),
        analysisService.roadmap(caseId, signal),
      ]);
      patch({ evidence, roadmap, phase: null, status: "done" });
    } catch (err) {
      if (isAbort(err) || signal.aborted) return;
      patch({
        status: "error",
        phase: null,
        error: { phase: "explain", message: messageOf(err) },
      });
    }
  }, [caseId, getSignal, patch]);

  const retry = useCallback(() => {
    void start();
  }, [start]);

  const runVerify = useCallback(async () => {
    if (!caseId) return;
    patch({ verifyStatus: "loading" });
    try {
      const verify = await analysisService.verify(caseId);
      patch({ verify, verifyStatus: "done" });
    } catch {
      patch({ verifyStatus: "error" });
    }
  }, [caseId, patch]);

  return { state, start, applyAnswers, skipClarification, retry, runVerify };
}
