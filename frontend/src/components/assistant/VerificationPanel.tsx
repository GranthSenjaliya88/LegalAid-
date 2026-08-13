import { CheckCircle2, ShieldQuestion, XCircle } from "lucide-react";
import type { VerificationCard, VerifyResponse } from "@/types";
import type { VerifyStatus } from "@/hooks/useCaseAnalysis";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { VerifiedSeal } from "@/components/common/VerifiedSeal";
import { ConfidenceBadge } from "./ConfidenceBadge";

interface VerificationPanelProps {
  card?: VerificationCard | null;
  verify?: VerifyResponse;
  verifyStatus: VerifyStatus;
  onVerify: () => void;
}

function Stat({ label, value, tone }: { label: string; value: number; tone: "ok" | "warn" | "neutral" }) {
  return (
    <div className="flex-1 rounded-lg border border-hairline bg-ivory/60 px-3 py-2.5 text-center">
      <p
        className={cn(
          "text-h3 font-semibold leading-none",
          tone === "ok" && "text-success",
          tone === "warn" && "text-danger",
          tone === "neutral" && "text-teal",
        )}
      >
        {value}
      </p>
      <p className="mt-1 text-tiny text-muted">{label}</p>
    </div>
  );
}

/**
 * Trust / verification card (Part 13). Summarizes how many claims were checked
 * against verified sources, and lets the user run a full citation check on
 * demand. Gold accents are reserved for this "verified" surface.
 */
export function VerificationPanel({ card, verify, verifyStatus, onVerify }: VerificationPanelProps) {
  const hasCard = Boolean(card);
  if (!hasCard && !verify) {
    // Still offer the manual check even when the explainer didn't attach a card.
    return (
      <Card>
        <CardContent className="flex flex-col items-start gap-3 pt-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <VerifiedSeal />
            <div>
              <p className="text-body font-medium text-ink">Check the citations</p>
              <p className="text-small text-muted">Verify every legal reference against the source corpus.</p>
            </div>
          </div>
          <Button variant="outline" onClick={onVerify} disabled={verifyStatus === "loading"}>
            {verifyStatus === "loading" ? "Checking…" : "Run citation check"}
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-gold/30">
      <CardHeader className="flex-row items-center justify-between gap-3 space-y-0">
        <CardTitle className="flex items-center gap-2">
          <VerifiedSeal label="Source-checked" />
        </CardTitle>
        {card?.confidence_badge && <ConfidenceBadge confidence={card.confidence_badge} />}
      </CardHeader>
      <CardContent className="space-y-4">
        {card && (
          <div className="flex gap-3">
            <Stat label="Claims checked" value={card.claims_checked ?? 0} tone="neutral" />
            <Stat label="Sources verified" value={card.sources_verified ?? 0} tone="ok" />
            <Stat
              label="Unsupported"
              value={card.unsupported_claims ?? 0}
              tone={card.unsupported_claims > 0 ? "warn" : "ok"}
            />
          </div>
        )}

        {card?.status_note && <p className="text-small leading-relaxed text-muted">{card.status_note}</p>}

        <div className="flex items-center justify-between gap-3">
          <p className="text-tiny text-muted">
            Every statutory reference is checked against the verified corpus, never invented.
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={onVerify}
            disabled={verifyStatus === "loading"}
            className="shrink-0"
          >
            {verifyStatus === "loading" ? "Checking…" : verify ? "Re-check" : "Run citation check"}
          </Button>
        </div>

        {verifyStatus === "error" && (
          <p className="text-small text-danger">Couldn't complete the citation check. Please try again.</p>
        )}

        {verify && (
          <div className="space-y-2">
            <Separator />
            <div className="flex flex-wrap items-center gap-2 pt-1 text-small">
              {verify.all_verified ? (
                <span className="inline-flex items-center gap-1.5 font-medium text-success">
                  <CheckCircle2 className="size-4" /> All {verify.total_citations} citations verified
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 font-medium text-[#8a6416]">
                  <ShieldQuestion className="size-4" />
                  {verify.verified_count} of {verify.total_citations} verified
                </span>
              )}
            </div>
            <ul className="divide-y divide-hairline/70">
              {verify.items.map((item, i) => (
                <li key={i} className="flex items-start gap-2.5 py-2">
                  {item.is_valid ? (
                    <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-success" />
                  ) : (
                    <XCircle className="mt-0.5 size-4 shrink-0 text-danger" />
                  )}
                  <div className="min-w-0">
                    <p className="text-small font-medium text-ink">{item.citation_text}</p>
                    {item.status_note && <p className="text-tiny text-muted">{item.status_note}</p>}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
