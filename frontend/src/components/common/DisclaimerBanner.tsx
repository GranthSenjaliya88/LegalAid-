import { Scale } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/store/appStore";

/**
 * Global "information, not advice" disclaimer (Part 26/37). Rendered in the
 * app footer and at the end of result flows. Calm, never a scary red banner.
 */
export function DisclaimerBanner({ className }: { className?: string }) {
  const language = useAppStore((s) => s.language);
  return (
    <div
      className={cn(
        "flex items-start gap-3 rounded-lg border border-hairline bg-teal/[0.03] px-4 py-3 text-small text-muted",
        className,
      )}
      role="note"
    >
      <Scale className="mt-0.5 size-4 shrink-0 text-teal/70" strokeWidth={1.7} />
      <p className="leading-relaxed">
        {language === "hi"
          ? "LegalAId सत्यापित स्रोतों पर आधारित सामान्य कानूनी जानकारी देता है—यह कानूनी सलाह नहीं है। अपनी स्थिति से जुड़े निर्णयों के लिए किसी लाइसेंस प्राप्त अधिवक्ता से सलाह लें।"
          : "LegalAId provides general legal information grounded in verified sources—not legal advice. For decisions about your specific situation, consult a licensed advocate."}
      </p>
    </div>
  );
}
