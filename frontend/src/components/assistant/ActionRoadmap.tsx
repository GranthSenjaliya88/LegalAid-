import { ArrowRight, FileText, Route } from "lucide-react";
import type { ActionRoadmapResponse } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

/**
 * Action roadmap (Part 16). A calm, numbered sequence of concrete next steps,
 * with any document each step needs and an optional urgency banner.
 */
export function ActionRoadmap({ roadmap }: { roadmap: ActionRoadmapResponse }) {
  const { steps, urgent_warning } = roadmap;
  if (!steps || steps.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Route className="size-5 text-teal" />
          Your next steps
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {urgent_warning && (
          <div className="rounded-lg border border-warning/35 bg-warning/[0.08] px-4 py-3 text-small leading-relaxed text-[#7a5a12]">
            {urgent_warning}
          </div>
        )}

        <ol className="space-y-0">
          {steps.map((step, i) => {
            const last = i === steps.length - 1;
            return (
              <li key={step.step_number ?? i} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-teal text-small font-semibold text-ivory-soft">
                    {step.step_number ?? i + 1}
                  </span>
                  {!last && <span className="my-1 w-px flex-1 bg-hairline" aria-hidden="true" />}
                </div>
                <div className={last ? "pb-0" : "pb-6"}>
                  <p className="text-body font-semibold text-ink">{step.title}</p>
                  <p className="mt-1 text-small leading-relaxed text-muted">{step.description}</p>
                  <div className="mt-2 flex flex-wrap items-center gap-3">
                    {step.required_document && (
                      <Badge variant="neutral">
                        <FileText className="size-3" />
                        {step.required_document}
                      </Badge>
                    )}
                    {step.next_action && (
                      <span className="inline-flex items-center gap-1 text-tiny text-teal">
                        <ArrowRight className="size-3" />
                        {step.next_action}
                      </span>
                    )}
                  </div>
                </div>
              </li>
            );
          })}
        </ol>
      </CardContent>
    </Card>
  );
}
