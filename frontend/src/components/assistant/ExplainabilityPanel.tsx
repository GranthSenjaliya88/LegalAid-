import type { ExplainResponse } from "@/types";
import { cn } from "@/lib/utils";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAppStore } from "@/store/appStore";

/**
 * Explainability panel (Parts 12 & 14): "other laws considered and excluded"
 * plus the side-by-side comparison table. Kept collapsed by default — this is
 * supporting detail for users who want to understand the reasoning.
 */
export function ExplainabilityPanel({ explain }: { explain: ExplainResponse }) {
  const hi = useAppStore((s) => s.language) === "hi";
  const hasWhyNot = explain.why_not_this_law && explain.why_not_this_law.length > 0;
  const hasComparison = explain.law_comparison_table && explain.law_comparison_table.length > 0;
  if (!hasWhyNot && !hasComparison) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-h4">
          {hi ? "ये कानून क्यों—और दूसरे क्यों नहीं" : "Why these laws—and not others"}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Accordion type="single" collapsible className="border-t border-hairline">
          {hasComparison && (
            <AccordionItem value="comparison">
              <AccordionTrigger>{hi ? "कानूनों की तुलना" : "Law comparison"}</AccordionTrigger>
              <AccordionContent>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse text-small">
                    <thead>
                      <tr className="border-b border-hairline text-left text-tiny uppercase tracking-wide text-muted">
                        <th className="py-2 pr-4 font-medium">{hi ? "कानून" : "Law"}</th>
                        <th className="py-2 pr-4 font-medium">{hi ? "लागू है?" : "Applies?"}</th>
                        <th className="py-2 font-medium">{hi ? "कारण" : "Reason"}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {explain.law_comparison_table.map((row, i) => (
                        <tr key={i} className="border-b border-hairline/60 align-top">
                          <td className="py-2.5 pr-4 font-medium text-ink">{row.law}</td>
                          <td className="py-2.5 pr-4">
                            <span
                              className={cn(
                                "font-medium",
                                /yes|applies|likely/i.test(row.applies) ? "text-success" : "text-muted",
                              )}
                            >
                              {row.applies}
                            </span>
                          </td>
                          <td className="py-2.5 leading-relaxed text-muted">{row.reason}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </AccordionContent>
            </AccordionItem>
          )}

          {hasWhyNot && (
            <AccordionItem value="excluded">
              <AccordionTrigger>
                {hi ? "अन्य कानून जिन पर विचार करके अलग रखा गया" : "Other laws considered and set aside"}
              </AccordionTrigger>
              <AccordionContent>
                <ul className="space-y-3">
                  {explain.why_not_this_law.map((entry, i) => (
                    <li key={i} className="rounded-lg border border-hairline bg-ivory/60 p-3">
                      <p className="text-small font-medium text-ink">{entry.law}</p>
                      <p className="mt-1 text-tiny leading-relaxed text-muted">{entry.reason}</p>
                    </li>
                  ))}
                </ul>
              </AccordionContent>
            </AccordionItem>
          )}
        </Accordion>
      </CardContent>
    </Card>
  );
}
