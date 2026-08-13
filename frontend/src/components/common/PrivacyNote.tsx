import { ShieldCheck } from "lucide-react";
import { PRIVACY_REMINDER } from "@/lib/constants";
import { cn } from "@/lib/utils";

/**
 * Inline privacy reminder shown near any free-text input (Part 30).
 * Explicitly discourages entering passwords/OTPs/PINs.
 */
export function PrivacyNote({ className }: { className?: string }) {
  return (
    <p className={cn("flex items-center gap-1.5 text-tiny text-muted", className)}>
      <ShieldCheck className="size-3.5 shrink-0 text-success" strokeWidth={1.9} />
      <span>{PRIVACY_REMINDER}</span>
    </p>
  );
}
