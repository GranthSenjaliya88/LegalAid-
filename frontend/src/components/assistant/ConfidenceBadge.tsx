import { Badge, type BadgeProps } from "@/components/ui/badge";
import type { Confidence } from "@/types";
import { useAppStore } from "@/store/appStore";

function normalize(value: string): "high" | "medium" | "low" | "insufficient" {
  const v = value.toString().trim().toUpperCase();
  if (v.startsWith("HIGH")) return "high";
  if (v.startsWith("MED")) return "medium";
  if (v.startsWith("LOW")) return "low";
  return "insufficient";
}

const MAP: Record<
  ReturnType<typeof normalize>,
  { variant: BadgeProps["variant"]; label: string }
> = {
  high: { variant: "success", label: "High confidence" },
  medium: { variant: "warning", label: "Medium confidence" },
  low: { variant: "neutral", label: "Low confidence" },
  insufficient: { variant: "outline", label: "Needs more information" },
};

/**
 * Renders the model's self-reported confidence as a calm badge. Low confidence
 * is deliberately neutral (not red) so users aren't discouraged from continuing.
 */
export function ConfidenceBadge({ confidence }: { confidence: Confidence | string }) {
  const { variant, label } = MAP[normalize(String(confidence))];
  const hi = useAppStore((s) => s.language) === "hi";
  const hindiLabel: Record<ReturnType<typeof normalize>, string> = {
    high: "उच्च विश्वसनीयता",
    medium: "मध्यम विश्वसनीयता",
    low: "कम विश्वसनीयता",
    insufficient: "और जानकारी चाहिए",
  };
  return <Badge variant={variant}>{hi ? hindiLabel[normalize(String(confidence))] : label}</Badge>;
}
