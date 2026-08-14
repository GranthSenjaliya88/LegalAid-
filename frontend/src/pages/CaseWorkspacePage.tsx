import { useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { DOMAINS } from "@/lib/constants";
import { useCase } from "@/hooks/useCase";
import { useCaseAnalysis } from "@/hooks/useCaseAnalysis";
import { useAppStore } from "@/store/appStore";
import { Badge } from "@/components/ui/badge";
import { Reveal } from "@/components/common/Reveal";
import { ErrorState } from "@/components/common/ErrorState";
import { PanelSkeleton } from "@/components/common/LoadingState";
import { CaseProgress } from "@/components/assistant/CaseProgress";
import { FactCard } from "@/components/assistant/FactCard";
import { ClarificationCard } from "@/components/assistant/ClarificationCard";
import { PipelineLoader } from "@/components/assistant/PipelineLoader";
import { SummaryCard } from "@/components/assistant/SummaryCard";
import { RightsList } from "@/components/assistant/RightsList";
import { RelevantLaw } from "@/components/assistant/RelevantLaw";
import { ExplainabilityPanel } from "@/components/assistant/ExplainabilityPanel";
import { ReasoningMap } from "@/components/assistant/ReasoningMap";
import { EvidenceChecklist } from "@/components/assistant/EvidenceChecklist";
import { ActionRoadmap } from "@/components/assistant/ActionRoadmap";
import { UrgentCard } from "@/components/assistant/UrgentCard";
import { VerificationPanel } from "@/components/assistant/VerificationPanel";
import { DocumentGenerator } from "@/components/document/DocumentGenerator";
import type { PipelineStepId } from "@/lib/constants";

/**
 * Case workspace (Parts 7–16). Orchestrates the source-grounded analysis
 * pipeline for one case and reveals each stage progressively, with the calm
 * progress spine tracking where the user is.
 */
export function CaseWorkspacePage() {
  const { id } = useParams<{ id: string }>();
  const lang = useAppStore((s) => s.language);
  const hi = lang === "hi";
  const caseQuery = useCase(id);
  const { state, start, applyAnswers, skipClarification, retry, runVerify } = useCaseAnalysis(id);

  // Kick off analysis whenever id is present.
  useEffect(() => {
    if (id) {
      void start();
    }
  }, [id, start]);

  const caseData = caseQuery.data;
  const activeDomain = caseData?.domain ?? state.classify?.domain ?? undefined;
  const domainMeta = activeDomain ? DOMAINS[activeDomain] : null;
  const running = state.status === "running";
  const { explain } = state;

  // Derive the progress spine from what the pipeline has produced so far.
  const completed: PipelineStepId[] = ["situation"];
  if (state.classify || state.facts) completed.push("facts");
  if (explain) completed.push("law", "rights");
  if (state.evidence) completed.push("evidence");
  if (state.roadmap) completed.push("action");

  let current: PipelineStepId | null = "situation";
  if (state.status === "done" || state.status === "insufficient_information") current = "document";
  else if (state.phase === "explain") current = "law";
  else if (state.phase === "enrich") current = "evidence";
  else if (state.phase === "classify" || state.phase === "clarify" || state.status === "awaiting_clarification")
    current = "facts";

  const laws = explain?.relevant_law?.length ? explain.relevant_law : explain?.why_this_law ?? [];

  return (
    <div>
      <Link
        to="/"
        className="inline-flex items-center gap-1.5 text-small font-medium text-muted transition-colors hover:text-teal"
      >
        <ArrowLeft className="size-4" />
        {hi ? "नया प्रश्न" : "New question"}
      </Link>

      <div className="mt-5 grid gap-8 lg:grid-cols-[minmax(0,1fr)_15rem]">
        {/* Main column */}
        <div className="order-2 min-w-0 space-y-6 lg:order-1">
          {caseQuery.isLoading && <PanelSkeleton />}

          {caseQuery.isError && (
            <ErrorState
              title={hi ? "यह मामला खुल नहीं सका" : "We couldn't load this case"}
              description={hi ? "मामला समाप्त हो गया हो सकता है या कनेक्शन टूट गया है।" : "The case may have expired or the connection dropped."}
              onRetry={() => caseQuery.refetch()}
            />
          )}

          {caseData && (
            <>
              <Reveal as="section" aria-labelledby="situation-heading">
                <div className="rounded-xl border border-hairline bg-surface p-5">
                  <div className="flex flex-wrap items-center gap-2">
                    <h1 id="situation-heading" className="text-small font-semibold uppercase tracking-wide text-teal">
                      {hi ? "आपकी स्थिति" : "Your situation"}
                    </h1>
                    {domainMeta && (
                      <Badge variant="neutral">
                        <domainMeta.icon className="size-3" />
                        {lang === "hi" ? domainMeta.labelHi : domainMeta.label}
                      </Badge>
                    )}
                  </div>
                  <p className="mt-3 whitespace-pre-wrap text-body leading-relaxed text-ink">
                    {caseData.original_text}
                  </p>
                </div>
              </Reveal>

              {state.facts && (
                <Reveal as="section">
                  <FactCard facts={state.facts} onApply={applyAnswers} pending={running} />
                </Reveal>
              )}

              {state.status === "awaiting_clarification" && state.clarify && (
                <Reveal as="section">
                  <ClarificationCard
                    questions={state.clarify.questions}
                    facts={state.facts}
                    onSubmit={applyAnswers}
                    onSkip={skipClarification}
                  />
                </Reveal>
              )}

              {running && !explain && state.status !== "awaiting_clarification" && (
                <PipelineLoader phase={state.phase} />
              )}

              {state.status === "error" && (
                <ErrorState
                  title={hi ? "विश्लेषण पूरा नहीं हुआ" : "Analysis didn't finish"}
                  description={state.error?.message}
                  onRetry={retry}
                />
              )}

              {explain && (
                <div className="space-y-6">
                  {explain.emergency_plan && (
                    <Reveal as="section">
                      <UrgentCard plan={explain.emergency_plan} />
                    </Reveal>
                  )}
                  <Reveal as="section">
                    <SummaryCard explain={explain} />
                  </Reveal>
                  <Reveal as="section" delay={0.04}>
                    <RightsList explain={explain} />
                  </Reveal>
                  {laws.length > 0 && (
                    <Reveal as="section" delay={0.08}>
                      <RelevantLaw laws={laws} />
                    </Reveal>
                  )}
                  <Reveal as="section" delay={0.1}>
                    <ExplainabilityPanel explain={explain} />
                  </Reveal>
                  <Reveal as="section" delay={0.12}>
                    <ReasoningMap steps={explain.reasoning_map} />
                  </Reveal>

                  {running && state.phase === "enrich" && (!state.evidence || !state.roadmap) && <PanelSkeleton />}
                  {state.evidence && (
                    <Reveal as="section" delay={0.14}>
                      <EvidenceChecklist evidence={state.evidence} />
                    </Reveal>
                  )}
                  {state.roadmap && (
                    <Reveal as="section" delay={0.16}>
                      <ActionRoadmap roadmap={state.roadmap} />
                    </Reveal>
                  )}

                  <Reveal as="section" delay={0.18}>
                    <VerificationPanel
                      card={explain.verification_card}
                      verify={state.verify}
                      verifyStatus={state.verifyStatus}
                      onVerify={runVerify}
                    />
                  </Reveal>

                  {id && (
                    <Reveal as="section" delay={0.2}>
                      <DocumentGenerator caseId={id} domain={activeDomain} />
                    </Reveal>
                  )}
                </div>
              )}
            </>
          )}
        </div>

        {/* Progress rail */}
        <aside className="order-1 lg:order-2">
          <div className="space-y-4 lg:sticky lg:top-6">
            <div className="lg:hidden">
              <CaseProgress current={current} completed={completed} orientation="horizontal" />
            </div>
            <div className={cn("hidden rounded-xl border border-hairline bg-surface p-5 lg:block")}>
              <p className="mb-4 flex items-center gap-1.5 text-small font-semibold text-teal">
                <Sparkles className="size-4 text-gold-deep" />
                {hi ? "मामले की प्रगति" : "Case progress"}
              </p>
              <CaseProgress current={current} completed={completed} orientation="vertical" />
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
