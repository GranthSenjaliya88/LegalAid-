import { ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/store/appStore";

/**
 * Inline privacy reminder shown near any free-text input (Part 30).
 * Explicitly discourages entering passwords/OTPs/PINs.
 */
export function PrivacyNote({ className }: { className?: string }) {
  const language = useAppStore((s) => s.language);
  return (
    <p className={cn("flex items-center gap-1.5 text-tiny text-muted", className)}>
      <ShieldCheck className="size-3.5 shrink-0 text-success" strokeWidth={1.9} />
      <span>
        {language === "hi"
          ? "पासवर्ड, OTP, PIN या अनावश्यक संवेदनशील जानकारी दर्ज न करें।"
          : "Don't enter passwords, OTPs, PINs, or unnecessary sensitive information."}
      </span>
    </p>
  );
}
