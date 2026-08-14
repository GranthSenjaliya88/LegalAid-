import { useEffect } from "react";
import { useAppStore } from "@/store/appStore";
import type { Language } from "@/types";
import { cn } from "@/lib/utils";

const OPTIONS: { value: Language; label: string; a11y: string }[] = [
  { value: "en", label: "EN", a11y: "Switch to English" },
  { value: "hi", label: "हिंदी", a11y: "हिंदी में बदलें" },
];

/**
 * Segmented English / Hindi toggle. Language is persisted in the app store
 * and drives all bilingual copy across the app.
 */
export function LanguageSwitcher({ className }: { className?: string }) {
  const language = useAppStore((s) => s.language);
  const setLanguage = useAppStore((s) => s.setLanguage);

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border border-hairline bg-surface p-0.5",
        className,
      )}
      role="radiogroup"
      aria-label={language === "hi" ? "भाषा" : "Language"}
    >
      {OPTIONS.map((opt) => {
        const active = language === opt.value;
        return (
          <button
            key={opt.value}
            type="button"
            role="radio"
            aria-checked={active}
            aria-label={opt.a11y}
            onClick={() => setLanguage(opt.value)}
            className={cn(
              "rounded-full px-3 py-1 text-tiny font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal focus-visible:ring-offset-1 focus-visible:ring-offset-ivory",
              opt.value === "hi" && "font-deva",
              active ? "bg-teal text-ivory-soft" : "text-muted hover:text-ink",
            )}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}
