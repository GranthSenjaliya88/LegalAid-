import { Lock, Trash2, EyeOff, ShieldCheck, ScrollText } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { PageHeader } from "@/components/common/PageHeader";
import { Reveal } from "@/components/common/Reveal";
import { PRIVACY_REMINDER } from "@/lib/constants";

const SECTIONS: { icon: LucideIcon; title: string; body: string }[] = [
  {
    icon: Lock,
    title: "Never enter sensitive credentials",
    body: `${PRIVACY_REMINDER} LegalAId never needs them to explain your rights, and they are never required to use any feature.`,
  },
  {
    icon: EyeOff,
    title: "We minimize what we handle",
    body: "Only the details needed to understand your situation are processed. Sensitive credentials are never logged, and internal traces are redacted.",
  },
  {
    icon: ScrollText,
    title: "What stays on this device",
    body: "A lightweight list of the cases and drafts you've created is kept in your browser so you can find them again. No legal content is stored there.",
  },
  {
    icon: Trash2,
    title: "Deleting a case removes it",
    body: "When you delete a case, its record and associated documents are removed from the backend, and it disappears from this device too.",
  },
];

/**
 * Privacy & Safety (Part 30). Plain-language explanation of how data is handled
 * and a prominent reminder never to enter passwords, OTPs, or PINs.
 */
export function PrivacyPage() {
  return (
    <div className="space-y-10">
      <PageHeader
        eyebrow="Privacy & Safety"
        title="Your privacy comes first"
        description="LegalAId is built to help you understand your rights without putting your personal security at risk."
      />

      <Reveal className="flex items-start gap-3 rounded-xl border border-gold/30 bg-gold-soft/40 p-5">
        <Lock className="mt-0.5 size-5 shrink-0 text-gold-deep" />
        <div>
          <p className="font-semibold text-ink">A quick safety reminder</p>
          <p className="mt-1 text-small leading-relaxed text-ink/90">{PRIVACY_REMINDER}</p>
        </div>
      </Reveal>

      <div className="grid gap-4 sm:grid-cols-2">
        {SECTIONS.map((s, i) => (
          <Reveal key={s.title} delay={i * 0.05}>
            <div className="flex h-full gap-4 rounded-xl border border-hairline bg-surface p-5">
              <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-teal/[0.07] text-teal">
                <s.icon className="size-5" />
              </span>
              <div>
                <h2 className="text-body font-semibold text-ink">{s.title}</h2>
                <p className="mt-1 text-small leading-relaxed text-muted">{s.body}</p>
              </div>
            </div>
          </Reveal>
        ))}
      </div>

      <Reveal className="rounded-xl border border-teal/20 bg-teal/[0.04] p-6">
        <p className="flex items-center gap-2 font-display text-h4 text-teal">
          <ShieldCheck className="size-5 text-gold-deep" />
          Information, not legal advice
        </p>
        <p className="mt-2 max-w-3xl text-small leading-relaxed text-ink/90">
          LegalAId provides general legal information grounded in verified sources — not legal
          advice. For decisions about your specific situation, consult a licensed advocate.
        </p>
      </Reveal>
    </div>
  );
}
