import { Check, Loader2 } from "lucide-react";
import type { FlowPhase } from "@/hooks/useCaseAnalysis";
import { useAppStore } from "@/store/appStore";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/card";

interface PhaseCopy {
  id: Exclude<FlowPhase, null>;
  en: string;
  hi: string;
}

const PHASES: PhaseCopy[] = [
  { id: "classify", en: "Understanding your situation", hi: "आपकी स्थिति समझ रहे हैं" },
  { id: "clarify", en: "Reviewing what we understood", hi: "हमने जो समझा उसकी जाँच" },
  { id: "explain", en: "Finding the relevant law and your rights", hi: "संबंधित कानून और आपके अधिकार खोज रहे हैं" },
  { id: "enrich", en: "Preparing evidence and next steps", hi: "साक्ष्य और अगले कदम तैयार कर रहे हैं" },
];

const ORDER: Record<Exclude<FlowPhase, null>, number> = {
  classify: 0,
  clarify: 1,
  explain: 2,
  enrich: 3,
};

/**
 * Calm, phase-aware loader shown while the source-grounded pipeline runs.
 * Communicates *what* is happening so the wait feels considered, not stuck.
 */
export function PipelineLoader({ phase }: { phase: FlowPhase }) {
  const lang = useAppStore((s) => s.language);
  const activeIndex = phase ? ORDER[phase] : 0;

  return (
    <Card className="p-6">
      <div className="mb-5 flex items-center gap-2 text-small font-medium text-teal">
        <Loader2 className="size-4 animate-spin" />
        <span className={cn(lang === "hi" && "font-deva")}>
          {lang === "hi" ? "आपके मामले पर काम हो रहा है…" : "Working on your case…"}
        </span>
      </div>
      <ol className="space-y-3">
        {PHASES.map((p, i) => {
          const done = i < activeIndex;
          const active = i === activeIndex;
          return (
            <li key={p.id} className="flex items-center gap-3">
              <span
                className={cn(
                  "flex size-6 shrink-0 items-center justify-center rounded-full border text-tiny",
                  done && "border-teal bg-teal text-ivory-soft",
                  active && "border-gold bg-gold/15 text-gold-deep",
                  !done && !active && "border-hairline bg-surface text-muted",
                )}
              >
                {done ? (
                  <Check className="size-3.5" strokeWidth={3} />
                ) : active ? (
                  <Loader2 className="size-3.5 animate-spin" />
                ) : (
                  i + 1
                )}
              </span>
              <span
                className={cn(
                  "text-small",
                  active ? "font-medium text-ink" : done ? "text-muted" : "text-muted/70",
                  lang === "hi" && "font-deva",
                )}
              >
                {lang === "hi" ? p.hi : p.en}
              </span>
            </li>
          );
        })}
      </ol>
    </Card>
  );
}
