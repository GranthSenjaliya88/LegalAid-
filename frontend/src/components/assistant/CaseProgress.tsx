import { Check } from "lucide-react";
import { PIPELINE_STEPS, type PipelineStepId } from "@/lib/constants";
import { useAppStore } from "@/store/appStore";
import { cn } from "@/lib/utils";

type StepState = "done" | "current" | "todo";

interface CaseProgressProps {
  current?: PipelineStepId | null;
  completed?: PipelineStepId[];
  currentStep?: number;
  orientation?: "vertical" | "horizontal";
  className?: string;
}

const defaultSteps = [
  "Situation",
  "Facts",
  "Law",
  "Rights",
  "Evidence",
  "Action",
  "Document",
];

function stateFor(id: PipelineStepId, current: PipelineStepId | null, completed: PipelineStepId[]): StepState {
  if (completed.includes(id)) return "done";
  if (id === current) return "current";
  return "todo";
}

function circleClass(state: StepState): string {
  if (state === "done") return "border-teal bg-teal text-ivory-soft";
  if (state === "current") return "border-gold bg-gold text-teal-dark ring-4 ring-gold/20";
  return "border-hairline bg-surface text-muted";
}

export function CaseProgress({ current, completed = [], currentStep, orientation = "vertical", className }: CaseProgressProps) {
  const lang = useAppStore((s) => s.language);

  if (currentStep !== undefined) {
    return (
      <div className="flex items-center gap-2 overflow-x-auto py-3">
        {defaultSteps.map((step, index) => {
          const number = index + 1;
          const isCompleted = number < currentStep;
          const active = number === currentStep;

          return (
            <div key={step} className="flex min-w-max items-center gap-2">
              <div
                className={[
                  "flex h-9 w-9 items-center justify-center rounded-full text-sm font-semibold transition-colors",
                  isCompleted
                    ? "bg-emerald-600 text-white"
                    : active
                      ? "bg-amber-400 text-slate-900 ring-4 ring-amber-400/20"
                      : "bg-slate-200 text-slate-500",
                ].join(" ")}
              >
                {isCompleted ? "✓" : number}
              </div>

              <span className="text-sm font-medium text-slate-800">
                {step}
              </span>

              {number !== defaultSteps.length && (
                <div className="h-px w-8 bg-slate-200" />
              )}
            </div>
          );
        })}
      </div>
    );
  }

  if (orientation === "horizontal") {
    const currentIndex = PIPELINE_STEPS.findIndex((s) => s.id === current);
    const currentStepObj = currentIndex >= 0 ? PIPELINE_STEPS[currentIndex] : undefined;
    return (
      <div className={cn("space-y-2", className)}>
        {currentStepObj && (
          <p className="text-tiny font-medium text-muted">
            <span className="text-teal">
              Step {currentIndex + 1} of {PIPELINE_STEPS.length}
            </span>
            {" · "}
            <span className={cn("font-semibold text-ink", lang === "hi" && "font-deva")}>
              {lang === "hi" ? currentStepObj.labelHi : currentStepObj.label}
            </span>
          </p>
        )}
        <ol className="flex items-center" aria-label="Case progress">
          {PIPELINE_STEPS.map((step, i) => {
            const state = stateFor(step.id, current || null, completed);
            const last = i === PIPELINE_STEPS.length - 1;
            return (
              <li key={step.id} className={cn("flex items-center", !last && "flex-1")}>
                <span
                  className={cn(
                    "flex size-6 shrink-0 items-center justify-center rounded-full border text-tiny font-semibold",
                    circleClass(state),
                  )}
                  aria-current={state === "current" ? "step" : undefined}
                >
                  {state === "done" ? <Check className="size-3.5" strokeWidth={3} /> : i + 1}
                </span>
                {!last && (
                  <span
                    className={cn("mx-1 h-px flex-1", state === "done" ? "bg-teal/40" : "bg-hairline")}
                    aria-hidden="true"
                  />
                )}
              </li>
            );
          })}
        </ol>
      </div>
    );
  }

  return (
    <ol className={cn("flex flex-col", className)} aria-label="Case progress">
      {PIPELINE_STEPS.map((step, i) => {
        const state = stateFor(step.id, current || null, completed);
        const last = i === PIPELINE_STEPS.length - 1;
        return (
          <li key={step.id} className="flex gap-3">
            <div className="flex flex-col items-center">
              <span
                className={cn(
                  "flex size-8 shrink-0 items-center justify-center rounded-full border text-small font-semibold transition-colors",
                  circleClass(state),
                )}
                aria-current={state === "current" ? "step" : undefined}
              >
                {state === "done" ? <Check className="size-4" strokeWidth={3} /> : i + 1}
              </span>
              {!last && (
                <span
                  className={cn("my-1 w-px flex-1", state === "done" ? "bg-teal/40" : "bg-hairline")}
                  aria-hidden="true"
                />
              )}
            </div>
            <div className={cn("pb-6", last && "pb-0")}>
              <span className={cn("text-small font-semibold text-ink block", lang === "hi" && "font-deva")}>
                {lang === "hi" ? step.labelHi : step.label}
              </span>
              <span className={cn("text-tiny text-muted block", lang === "hi" && "font-deva")}>
                {lang === "hi" ? step.descriptionHi : step.description}
              </span>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
