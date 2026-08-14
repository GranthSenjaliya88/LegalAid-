import { ShieldCheck } from "lucide-react";
import type { ExplainResponse } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAppStore } from "@/store/appStore";

/**
 * "Your rights" panel. Lists the plain-language rights the user may have and,
 * for each detailed right, the exact statutory citations it rests on.
 */
export function RightsList({ explain }: { explain: ExplainResponse }) {
  const hi = useAppStore((s) => s.language) === "hi";
  const { possible_rights, rights } = explain;
  if ((!possible_rights || possible_rights.length === 0) && (!rights || rights.length === 0)) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ShieldCheck className="size-5 text-teal" />
          {hi ? "आपके अधिकार" : "Your rights"}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        {possible_rights && possible_rights.length > 0 && (
          <ul className="space-y-2">
            {possible_rights.map((right, i) => (
              <li key={i} className="flex items-start gap-2.5 text-body text-ink">
                <span className="mt-2 size-1.5 shrink-0 rounded-full bg-gold" aria-hidden="true" />
                <span className="leading-relaxed">{right}</span>
              </li>
            ))}
          </ul>
        )}

        {rights && rights.length > 0 && (
          <div className="space-y-3">
            {rights.map((right, i) => (
              <div key={i} className="rounded-lg border border-hairline bg-ivory/60 p-4">
                <p className="text-small leading-relaxed text-ink">{right.explanation}</p>
                {right.why_applies && (
                  <p className="mt-2 text-tiny leading-relaxed text-muted">{right.why_applies}</p>
                )}
                {right.citations && right.citations.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {right.citations.map((c, ci) => (
                      <Badge key={ci} variant="neutral" title={c.source_reference ?? undefined}>
                        {[c.act, c.section && `§${c.section}`].filter(Boolean).join(" ")}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
