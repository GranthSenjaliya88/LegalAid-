import { useCallback, useEffect, useRef, useState } from "react";
import { analysisService } from "@/services/analysis";
import { casesService } from "@/services/cases";
import { ApiError } from "@/types";
import type {
  ActionRoadmapResponse,
  AnswerValue,
  CaseFacts,
  ClarifyResponse,
  ClassifyResponse,
  EvidenceResponse,
  ExplainResponse,
  VerifyResponse,
} from "@/types";

export type FlowStatus = "idle" | "running" | "awaiting_clarification" | "done" | "error";
export type FlowPhase = "classify" | "clarify" | "explain" | "enrich" | null;
export type VerifyStatus = "idle" | "loading" | "done" | "error";

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
 * The LLM never invents provisions — each phase calls the backend, which
 * retrieves from the verified corpus before generating explanations.
 */
export function useCaseAnalysis(caseId: string | undefined) {
  const [state, setState] = useState<AnalysisState>(initialState);
  const mounted = useRef(true);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      abortRef.current?.abort();
    };
  }, []);

  const patch = useCallback((partial: Partial<AnalysisState>) => {
    if (mounted.current) setState((prev) => ({ ...prev, ...partial }));
  }, []);

  const newSignal = useCallback(() => {
    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;
    return ac.signal;
  }, []);

  const analyze = useCallback(
    async (id: string, signal: AbortSignal) => {
      try {
        patch({ status: "running", phase: "explain", error: undefined });
        const explain = await analysisService.explain(id, signal);
        patch({ explain, phase: "enrich" });

        const [evidence, roadmap] = await Promise.all([
          analysisService.evidence(id, signal),
          analysisService.roadmap(id, signal),
        ]);
        patch({ evidence, roadmap, phase: null, status: "done" });
      } catch (err) {
        if (isAbort(err) || signal.aborted) return;
        patch({ status: "error", phase: null, error: { phase: "explain", message: messageOf(err) } });
      }
    },
    [patch],
  );

  const start = useCallback(async () => {
    if (!caseId) return;
    const signal = newSignal();
    try {
      patch({
        status: "running",
        phase: "classify",
        error: undefined,
        explain: undefined,
        evidence: undefined,
        roadmap: undefined,
        verify: undefined,
        verifyStatus: "idle",
      });

      const classify = await analysisService.classify(caseId, signal);
      patch({ classify, facts: classify.facts, phase: "clarify" });

      let clarify: ClarifyResponse | undefined;
      try {
        clarify = await analysisService.clarify(caseId, signal);
      } catch (err) {
        if (isAbort(err) || signal.aborted) return;
        // Clarification is best-effort; never block the pipeline on it.
        clarify = undefined;
      }
      if (clarify) patch({ clarify });

      if (clarify?.needs_clarification && clarify.questions.length > 0) {
        patch({ status: "awaiting_clarification", phase: null });
        return;
      }

      await analyze(caseId, signal);
    } catch (err) {
      if (isAbort(err) || signal.aborted) return;
      patch({ status: "error", phase: null, error: { phase: "classify", message: messageOf(err) } });
    }
  }, [caseId, analyze, newSignal, patch]);

  /** Submit clarification answers (also used to correct AI-extracted facts). */
  const applyAnswers = useCallback(
    async (answers: Record<string, AnswerValue>) => {
      if (!caseId) return;
      const signal = newSignal();
      try {
        patch({ status: "running", phase: "explain", error: undefined });
        await analysisService.clarifyRespond(caseId, { answers }, signal);
        try {
          const refreshed = await casesService.get(caseId, signal);
          patch({ facts: refreshed.facts ?? undefined });
        } catch {
          /* keep existing facts if refresh fails */
        }
        await analyze(caseId, signal);
      } catch (err) {
        if (isAbort(err) || signal.aborted) return;
        patch({ status: "error", phase: null, error: { phase: "clarify", message: messageOf(err) } });
      }
    },
    [caseId, analyze, newSignal, patch],
  );

  const skipClarification = useCallback(async () => {
    if (!caseId) return;
    const signal = newSignal();
    await analyze(caseId, signal);
  }, [caseId, analyze, newSignal]);

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
