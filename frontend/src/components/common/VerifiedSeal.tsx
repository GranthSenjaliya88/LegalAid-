import { BadgeCheck } from "lucide-react";
import { cn } from "@/lib/utils";

type SealTone = "verified" | "neutral";

interface VerifiedSealProps {
  /** Optional label rendered beside the seal. */
  label?: string;
  tone?: SealTone;
  size?: "sm" | "md";
  className?: string;
}

/**
 * The signature trust emblem. A small gold-ringed seal used to mark
 * source-grounded / citation-verified content throughout the app.
 * Gold is reserved for exactly this kind of "verified" emphasis.
 */
export function VerifiedSeal({ label, tone = "verified", size = "md", className }: VerifiedSealProps) {
  const dim = size === "sm" ? "size-6" : "size-8";
  const icon = size === "sm" ? "size-3.5" : "size-4";

  return (
    <span className={cn("inline-flex items-center gap-2", className)}>
      <span
        className={cn(
          "flex items-center justify-center rounded-full ring-1",
          dim,
          tone === "verified"
            ? "bg-gold/[0.14] text-gold-deep ring-gold/40"
            : "bg-teal/[0.06] text-teal ring-hairline",
        )}
      >
        <BadgeCheck className={icon} strokeWidth={2} />
      </span>
      {label && (
        <span
          className={cn(
            "text-tiny font-semibold uppercase tracking-wide",
            tone === "verified" ? "text-gold-deep" : "text-muted",
          )}
        >
          {label}
        </span>
      )}
    </span>
  );
}
