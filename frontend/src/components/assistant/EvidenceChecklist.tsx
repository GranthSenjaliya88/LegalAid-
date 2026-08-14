import { useState } from "react";
import { ClipboardList } from "lucide-react";
import type { EvidenceResponse } from "@/types";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { useAppStore } from "@/store/appStore";

/**
 * Evidence checklist (Part 15). A personal, tickable list of documents that
 * strengthen the user's case. Checked state is local — a private tracker, not
 * sent anywhere.
 */
export function EvidenceChecklist({ evidence }: { evidence: EvidenceResponse }) {
  const hi = useAppStore((s) => s.language) === "hi";
  const { claim_summary, checklist } = evidence;
  const [checked, setChecked] = useState<Record<number, boolean>>(() =>
    Object.fromEntries(checklist.map((item, i) => [i, item.available])),
  );

  if (!checklist || checklist.length === 0) return null;

  const doneCount = Object.values(checked).filter(Boolean).length;

  return (
    <Card>
      <CardHeader className="space-y-1">
        <CardTitle className="flex items-center gap-2">
          <ClipboardList className="size-5 text-teal" />
          {hi ? "इकट्ठा करने योग्य सबूत" : "Evidence to gather"}
        </CardTitle>
        {claim_summary && <p className="text-small text-muted">{claim_summary}</p>}
        <p className="text-tiny text-muted">
          {checklist.length} में से {doneCount} {hi ? "तैयार" : "ready"}
        </p>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2.5">
          {checklist.map((item, i) => {
            const id = `evidence-${i}`;
            const isChecked = checked[i] ?? false;
            const essential = String(item.importance).toLowerCase().includes("essential");
            return (
              <li
                key={i}
                className={cn(
                  "flex items-start gap-3 rounded-lg border border-hairline p-3 transition-colors",
                  isChecked ? "bg-success/[0.05]" : "bg-surface",
                )}
              >
                <Checkbox
                  id={id}
                  checked={isChecked}
                  onCheckedChange={(v) => setChecked((prev) => ({ ...prev, [i]: v === true }))}
                  className="mt-0.5"
                />
                <label htmlFor={id} className="min-w-0 flex-1 cursor-pointer">
                  <span className="flex flex-wrap items-center gap-2">
                    <span
                      className={cn(
                        "text-small font-medium text-ink",
                        isChecked && "text-muted line-through",
                      )}
                    >
                      {item.document_name}
                    </span>
                    <Badge variant={essential ? "verified" : "neutral"}>
                      {essential ? (hi ? "आवश्यक" : "Essential") : hi ? "सहायक" : "Supporting"}
                    </Badge>
                  </span>
                  <span className="mt-1 block text-tiny leading-relaxed text-muted">
                    {item.why_it_matters}
                  </span>
                </label>
              </li>
            );
          })}
        </ul>
      </CardContent>
    </Card>
  );
}
