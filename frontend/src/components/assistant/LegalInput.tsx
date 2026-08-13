import { useEffect, useRef, useState } from "react";
import { Mic, Sparkles, Square } from "lucide-react";
import { useT } from "@/lib/i18n";
import { useAppStore } from "@/store/appStore";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { PrivacyNote } from "@/components/common/PrivacyNote";
import { LanguageSwitcher } from "@/components/common/LanguageSwitcher";

const MIN_LENGTH = 15;

interface LegalInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  pending?: boolean;
}

/**
 * Hero input (Part 6). A single calm textarea where the user describes their
 * situation in plain language. Optional voice dictation appears only when the
 * browser supports it. Privacy reminder sits directly beneath the field.
 */
export function LegalInput({ value, onChange, onSubmit, pending = false }: LegalInputProps) {
  const { t, lang } = useT();
  const [touched, setTouched] = useState(false);
  const { supported, listening, toggle } = useSpeechInput(lang, (chunk) =>
    onChange(value ? `${value} ${chunk}`.trim() : chunk),
  );

  const tooShort = value.trim().length > 0 && value.trim().length < MIN_LENGTH;
  const showError = touched && tooShort;

  const handleSubmit = () => {
    setTouched(true);
    if (value.trim().length < MIN_LENGTH) return;
    onSubmit();
  };

  return (
    <Card className="overflow-hidden">
      <div className="flex items-center justify-between gap-3 border-b border-hairline px-5 py-3.5">
        <h2 className={cn("text-h4 font-semibold text-ink", lang === "hi" && "font-deva")}>
          {t("input.title")}
        </h2>
        <LanguageSwitcher />
      </div>

      <div className="space-y-3 p-5">
        <p className={cn("text-small text-muted", lang === "hi" && "font-deva")}>{t("input.hint")}</p>

        <div className="relative">
          <Textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onBlur={() => setTouched(true)}
            placeholder={t("input.placeholder")}
            className={cn(
              "min-h-[9.5rem] pr-12 text-body-lg",
              lang === "hi" && "font-deva",
              showError && "border-danger focus-visible:ring-danger/50",
            )}
            aria-invalid={showError}
            aria-describedby={showError ? "legal-input-error" : undefined}
            disabled={pending}
          />
          {supported && (
            <button
              type="button"
              onClick={toggle}
              disabled={pending}
              aria-label={listening ? "Stop dictation" : t("input.speak")}
              aria-pressed={listening}
              className={cn(
                "absolute right-3 top-3 flex size-9 items-center justify-center rounded-full border transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal",
                listening
                  ? "border-danger/40 bg-danger/10 text-danger"
                  : "border-hairline bg-surface text-muted hover:text-teal",
              )}
            >
              {listening ? <Square className="size-4" /> : <Mic className="size-4" />}
            </button>
          )}
        </div>

        {showError && (
          <p id="legal-input-error" className="text-tiny text-danger" role="alert">
            {t("input.tooShort")}
          </p>
        )}

        <div className="flex flex-col-reverse items-stretch gap-3 pt-1 sm:flex-row sm:items-center sm:justify-between">
          <PrivacyNote />
          <Button size="lg" onClick={handleSubmit} disabled={pending} className="sm:min-w-[13rem]">
            <Sparkles className="size-4" />
            {pending ? t("input.analyzing") : t("input.analyze")}
          </Button>
        </div>
      </div>
    </Card>
  );
}

/* ------------------------------------------------------------------ *
 * Optional voice dictation via the Web Speech API. Feature-detected;
 * no-ops (and hides the mic) on browsers that don't support it.
 * ------------------------------------------------------------------ */
function useSpeechInput(lang: string, onResult: (text: string) => void) {
  const [supported, setSupported] = useState(false);
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const w = window as any;
    const SR = w.SpeechRecognition || w.webkitSpeechRecognition;
    if (SR) setSupported(true);
    return () => {
      try {
        recognitionRef.current?.stop();
      } catch {
        /* ignore */
      }
    };
  }, []);

  const toggle = () => {
    const w = window as any;
    const SR = w.SpeechRecognition || w.webkitSpeechRecognition;
    if (!SR) return;

    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
      return;
    }

    const recognition = new SR();
    recognition.lang = lang === "hi" ? "hi-IN" : "en-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results as ArrayLike<any>)
        .map((r) => r[0]?.transcript ?? "")
        .join(" ")
        .trim();
      if (transcript) onResult(transcript);
    };
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);
    recognitionRef.current = recognition;
    try {
      recognition.start();
      setListening(true);
    } catch {
      setListening(false);
    }
  };

  return { supported, listening, toggle };
}
