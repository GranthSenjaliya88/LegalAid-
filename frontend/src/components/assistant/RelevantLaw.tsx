import { Scale } from "lucide-react";
import type { WhyThisLaw } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LawCard } from "./LawCard";
import { useAppStore } from "@/store/appStore";

/**
 * "Relevant law" section — the statutory provisions the backend retrieved for
 * this case, each rendered as a source-grounded LawCard.
 */
export function RelevantLaw({ laws }: { laws: WhyThisLaw[] }) {
  const hi = useAppStore((s) => s.language) === "hi";
  if (!laws || laws.length === 0) return null;
  return (
    <Card>
      <CardHeader className="space-y-1">
        <CardTitle className="flex items-center gap-2">
          <Scale className="size-5 text-teal" />
          {hi ? "संबंधित कानून" : "Relevant law"}
        </CardTitle>
        <p className="text-small text-muted">
          {hi
            ? "सत्यापित कानूनी स्रोतों से आपकी स्थिति से मेल खाने वाले प्रावधान।"
            : "Provisions matched to your situation from verified legal sources."}
        </p>
      </CardHeader>
      <CardContent className="space-y-3">
        {laws.map((law, i) => (
          <LawCard key={`${law.act}-${law.section}-${i}`} law={law} />
        ))}
      </CardContent>
    </Card>
  );
}
