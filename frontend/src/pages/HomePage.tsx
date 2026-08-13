import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { useT } from "@/lib/i18n";
import { useCreateCase } from "@/hooks/useCreateCase";
import { LegalInput } from "@/components/assistant/LegalInput";
import { ExampleCards } from "@/components/assistant/ExampleCards";
import { Reveal } from "@/components/common/Reveal";

/**
 * Legal Assistant home (Parts 6–7). A calm, editorial hero with a single
 * highlighted word, the primary input, and example prompts. Submitting creates
 * a case on the backend and moves into the case workspace.
 */
export function HomePage() {
  const { t, lang } = useT();
  const navigate = useNavigate();
  const create = useCreateCase();
  const [text, setText] = useState("");

  const deva = lang === "hi" && "font-deva";

  const submit = () => {
    const trimmed = text.trim();
    if (trimmed.length < 15 || create.isPending) return;
    create.mutate(
      { text: trimmed, language: lang },
      {
        onSuccess: (res) => navigate(`/case/${res.case_id}`),
        onError: () =>
          toast.error("Couldn't start your case. Please check your connection and try again."),
      },
    );
  };

  return (
    <div className="mx-auto max-w-3xl px-1 sm:pt-6">
      <Reveal as="header" className="text-center">
        <p className={cn("text-small font-medium uppercase tracking-[0.14em] text-gold-deep", deva)}>
          {t("hero.eyebrow")}
        </p>
        <h1 className={cn("mt-4 font-display text-h1 leading-[1.08] text-teal", deva)}>
          {t("hero.titleLead")} <span className="text-gold-deep">{t("hero.titleHighlight")}</span>
        </h1>
        <p className={cn("mx-auto mt-4 max-w-xl text-body leading-relaxed text-muted", deva)}>
          {t("hero.subtitle")}
        </p>
        <p
          className={cn(
            "mt-5 inline-flex items-center gap-2 rounded-full border border-hairline bg-surface px-4 py-1.5 text-tiny text-muted",
            deva,
          )}
        >
          <ArrowRight className="size-3.5 text-teal" />
          {t("hero.flow")}
        </p>
      </Reveal>

      <Reveal delay={0.08} className="mt-9">
        <LegalInput value={text} onChange={setText} onSubmit={submit} pending={create.isPending} />
      </Reveal>

      <Reveal delay={0.16} className="mt-8">
        <ExampleCards onPick={setText} />
      </Reveal>
    </div>
  );
}
