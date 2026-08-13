import { ArrowUpRight } from "lucide-react";
import { DOMAINS, EXAMPLE_DOMAINS } from "@/lib/constants";
import { useT } from "@/lib/i18n";
import { useAppStore } from "@/store/appStore";
import { cn } from "@/lib/utils";

/**
 * Example situation chips (Part 6). Selecting one drops a sample description
 * into the input so first-time users understand what to write. These are
 * sample phrasings only — never legal claims.
 */
export function ExampleCards({ onPick }: { onPick: (text: string) => void }) {
  const { t } = useT();
  const lang = useAppStore((s) => s.language);

  return (
    <section aria-labelledby="examples-title" className="space-y-3">
      <h3 id="examples-title" className={cn("text-small font-medium text-muted", lang === "hi" && "font-deva")}>
        {t("examples.title")}
      </h3>
      <div className="grid gap-3 sm:grid-cols-2">
        {EXAMPLE_DOMAINS.map((key) => {
          const meta = DOMAINS[key];
          const Icon = meta.icon;
          const label = lang === "hi" ? meta.labelHi : meta.label;
          const example = lang === "hi" ? meta.exampleHi : meta.example;
          return (
            <button
              key={key}
              type="button"
              onClick={() => onPick(example)}
              className={cn(
                "group flex items-start gap-3 rounded-xl border border-hairline bg-surface p-4 text-left transition-all",
                "hover:border-teal/30 hover:bg-teal/[0.03] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal focus-visible:ring-offset-2 focus-visible:ring-offset-ivory",
              )}
            >
              <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-lg bg-teal/[0.06] text-teal">
                <Icon className="size-[1.15rem]" strokeWidth={1.8} />
              </span>
              <span className="min-w-0 flex-1 space-y-1">
                <span className="flex items-center justify-between gap-2">
                  <span className={cn("text-small font-semibold text-ink", lang === "hi" && "font-deva")}>
                    {label}
                  </span>
                  <ArrowUpRight className="size-4 shrink-0 text-muted transition-colors group-hover:text-teal" />
                </span>
                <span className={cn("line-clamp-2 text-tiny leading-relaxed text-muted", lang === "hi" && "font-deva")}>
                  {example}
                </span>
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}
