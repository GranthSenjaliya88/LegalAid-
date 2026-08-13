import { GitBranch } from "lucide-react";
import type { ReasoningStep } from "@/types";
import { cn } from "@/lib/utils";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";

function dotClass(status: string): string {
  const s = status.toLowerCase();
  if (s.includes("pass") || s.includes("complete") || s.includes("done") || s.includes("ok") || s.includes("verified"))
    return "bg-success";
  if (s.includes("warn") || s.includes("partial") || s.includes("review")) return "bg-warning";
  if (s.includes("fail") || s.includes("miss") || s.includes("error")) return "bg-danger";
  return "bg-teal/40";
}

/**
 * The auditable Legal Reasoning Map (Part 12). Each step exposes how the
 * pipeline moved from facts to law, so the process is transparent, not a
 * black box. Collapsed by default.
 */
export function ReasoningMap({ steps }: { steps: ReasoningStep[] }) {
  if (!steps || steps.length === 0) return null;

  return (
    <Card>
      <CardContent className="p-0">
        <Accordion type="single" collapsible>
          <AccordionItem value="reasoning" className="border-b-0">
            <AccordionTrigger className="px-6">
              <span className="flex items-center gap-2">
                <GitBranch className="size-4 text-teal" />
                How we reached this ({steps.length} steps)
              </span>
            </AccordionTrigger>
            <AccordionContent className="px-6">
              <ol className="space-y-3">
                {steps.map((s, i) => (
                  <li key={i} className="flex gap-3">
                    <span className="mt-1.5 flex flex-col items-center">
                      <span className={cn("size-2 shrink-0 rounded-full", dotClass(s.status))} />
                      {i < steps.length - 1 && <span className="mt-1 w-px flex-1 bg-hairline" />}
                    </span>
                    <div className="pb-1">
                      <p className="text-small font-medium text-ink">{s.step}</p>
                      {s.detail && <p className="mt-0.5 text-tiny leading-relaxed text-muted">{s.detail}</p>}
                    </div>
                  </li>
                ))}
              </ol>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </CardContent>
    </Card>
  );
}
