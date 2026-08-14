import { Badge, type BadgeProps } from "@/components/ui/badge";
import { useAppStore } from "@/store/appStore";

function classify(status: string): { variant: BadgeProps["variant"]; label: string } {
  const v = status.toString().trim().toLowerCase();
  if (v.includes("repeal")) return { variant: "danger", label: "Repealed" };
  if (v.includes("histor") || v.includes("supersed") || v.includes("replaced"))
    return { variant: "warning", label: "Historical reference" };
  if (v.includes("amend")) return { variant: "warning", label: "Amended" };
  if (v.includes("force") || v.includes("current") || v.includes("active"))
    return { variant: "success", label: "In force" };
  // Fall back to a title-cased version of whatever the backend sent.
  return { variant: "neutral", label: status ? status[0].toUpperCase() + status.slice(1) : "Status unknown" };
}

/**
 * Displays the legal status of a statute/section exactly as classified by the
 * backend corpus (never inferred client-side). Historical/repealed provisions
 * are surfaced honestly rather than hidden.
 */
export function LawStatusBadge({ status }: { status: string }) {
  const { variant, label } = classify(status);
  const hi = useAppStore((s) => s.language) === "hi";
  const labelHi: Record<string, string> = {
    Repealed: "निरस्त",
    "Historical reference": "ऐतिहासिक संदर्भ",
    Amended: "संशोधित",
    "In force": "लागू",
    "Status unknown": "स्थिति अज्ञात",
  };
  return <Badge variant={variant}>{hi ? (labelHi[label] ?? label) : label}</Badge>;
}
